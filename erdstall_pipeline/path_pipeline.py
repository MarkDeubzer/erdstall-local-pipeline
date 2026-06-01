from __future__ import annotations

import asyncio
import logging
import shutil
from pathlib import Path

from erdstall_admin_gui.workers.cancelable_worker import TaskCancelled
from erdstall_pipeline.csv_to_json import csv_to_json_file
import pymeshlab
from collections.abc import Callable

from erdstall_pipeline.config import (
    DATA_DIR,
    WORK_DIRNAME,
    FINAL_MESH,
    PATH_POINTS_FILENAME,
    PATH_OUTPUT_FILENAME,
    RAW_FROM_PLY_FILENAME,
    VOLUME_FILENAME,
    PATH_JSON_FILENAME,
    SKELETON_FILENAME,
    PATH_MESH_FILENAME,
    FILES_DIR
)
from erdstall_pipeline.ply_to_raw import convert_ply_to_raw
from erdstall_pipeline.run_imagej import run_imagej
from erdstall_pipeline.skeleton_pipeline import merge_raws
from erdstall_pipeline.path_finding_from_raw import compute_skeleton_csv


logger = logging.getLogger(__name__)
LogCallback = Callable[[str], None] | None
CancelCallback = Callable[[], None] | None

def _check_cancelled(cancel_callback: CancelCallback) -> None:
    if cancel_callback is not None:
        cancel_callback()

def get_project_dir(mesh_id: str) -> Path:
    """
    Return the project directory for one mesh/cave.
    Example:
        data/ply/ERDSTALL_001
    """
    
    return Path(DATA_DIR) / "ply" / mesh_id


def get_work_dir() -> Path:
    """
    Temporary working directory used during path calculation.
    """
    return Path(DATA_DIR) / WORK_DIRNAME


def cleanup_files_dir() -> None:
    """
    Remove all temporary files from the working directory.
    """
    work_dir = get_work_dir()

    if not work_dir.exists():
        return

    for entry in work_dir.iterdir():
        try:
            if entry.is_file() or entry.is_symlink():
                entry.unlink()
            elif entry.is_dir():
                shutil.rmtree(entry)
        except Exception:
            logger.exception("Failed to remove temporary path: %s", entry)


def validate_inputs(mesh_id: str) -> tuple[Path, Path, Path]:
    """
    Validate that the required input files exist.

    Expected:
        data/ply/<mesh_id>/mesh.ply
        data/ply/<mesh_id>/path_points.csv
    """
    project_dir = get_project_dir(mesh_id)
    mesh_path = project_dir / FINAL_MESH
    path_points_path = project_dir / PATH_POINTS_FILENAME

    if not project_dir.exists():
        raise FileNotFoundError(f"Project folder not found: {project_dir}")

    if not mesh_path.exists():
        raise FileNotFoundError(f"Mesh file not found: {mesh_path}")

    if not path_points_path.exists():
        raise FileNotFoundError(f"Path points file not found: {path_points_path}")

    return project_dir, mesh_path, path_points_path


def prepare_work_dir() -> Path:
    """
    Create and clean the temp work directory.
    """
    work_dir = get_work_dir()
    work_dir.mkdir(parents=True, exist_ok=True)
    cleanup_files_dir()
    return work_dir


def copy_inputs_to_workdir(mesh_path: Path, path_points_path: Path, work_dir: Path) -> tuple[Path, Path]:
    """
    Copy mesh and path_points.csv into the temp work directory.
    """
    target_mesh = work_dir / FINAL_MESH
    target_points = work_dir / PATH_POINTS_FILENAME

    shutil.copy2(mesh_path, target_mesh)
    shutil.copy2(path_points_path, target_points)
    return target_mesh, target_points



def ensure_exists(path: str | Path, message: str) -> None:
    """
    Raise an error if a required file does not exist.
    """
    p = Path(path)
    if not p.exists():
        raise RuntimeError(message)

def reduce_for_path(file_path: str,cancel_callback: CancelCallback = None) -> str:
    _check_cancelled(cancel_callback)
    ms = pymeshlab.MeshSet()
    ms.load_new_mesh(file_path)
    _check_cancelled(cancel_callback)

    original_faces = ms.current_mesh().face_number()

    target_faces = max(int(original_faces * 0.03), 150000)
    _check_cancelled(cancel_callback)
    ms.meshing_decimation_quadric_edge_collapse(
        targetfacenum=target_faces,
        preserveboundary=True,
        preservenormal=True,
        preservetopology=True,
        optimalplacement=True,
        planarquadric=False,
        qualityweight=False,
        autoclean=True
    )
    _check_cancelled(cancel_callback)

    ms.meshing_remove_duplicate_faces()
    ms.meshing_remove_duplicate_vertices()
    _check_cancelled(cancel_callback)
    output_path = str(FILES_DIR / PATH_MESH_FILENAME)
    ms.save_current_mesh(output_path)
    _check_cancelled(cancel_callback)
    return output_path


async def run_full_pipeline(mesh_id: str, log_callback: LogCallback = None , cancel_callback: CancelCallback = None ) -> tuple[Path, Path]:
    """
    Run the complete path calculation pipeline.

    Steps:
        1. Validate inputs
        2. Copy mesh.ply and path_points.csv into temp folder
        3. Convert PLY to RAW voxel volume
        4. Run ImageJ processing
        5. Merge volume and skeleton
        6. Compute path.csv
        7. Copy path.csv back into the mesh project folder
        8. Cleanup temp files

    Returns:
        Path to the final path.csv in the project folder
    """

    def log(message: str) -> None:
        if log_callback is not None:
            log_callback(message)
        else:
            print(message)

    logger.info("Starting path pipeline for %s", mesh_id)

    work_dir = get_work_dir()
    final_output = get_project_dir(mesh_id) / PATH_OUTPUT_FILENAME
    final_json_output = get_project_dir(mesh_id) / PATH_JSON_FILENAME

    try:
            # Step 1: Validate project inputs
        log("Validate project inputs ...")
        _check_cancelled(cancel_callback)
        project_dir, mesh_path, path_points_path = validate_inputs(mesh_id)
        logger.info("Validated inputs for %s", mesh_id)
        _check_cancelled(cancel_callback)
        log("Validate projects inputs done")

        # Step 2: Prepare temp folder
        log("Preparing temp folder ...")
        _check_cancelled(cancel_callback)
        await asyncio.to_thread(prepare_work_dir)
        logger.info("Prepared work directory: %s", work_dir)
        _check_cancelled(cancel_callback)
        log("Preparing temp folder done.")

        # Step 3: Copy files into temp folder
        log("Copy files into temp folder ...")
        _check_cancelled(cancel_callback)
        temp_mesh, _temp_points = await asyncio.to_thread(
            copy_inputs_to_workdir,
            mesh_path,
            path_points_path,
            work_dir,
        )
        logger.info("Copied inputs to work directory")
        _check_cancelled(cancel_callback)
        log("Copy files into temp folder done")

        # Step 4: Reduce copied temp mesh for pathfinding
        log("Reducing mesh size...")
        _check_cancelled(cancel_callback)
        path_mesh = await asyncio.to_thread(
            reduce_for_path,
            str(temp_mesh),
            cancel_callback=cancel_callback,
         )
        logger.info("Reduced mesh for pathfinding: %s", path_mesh)
        _check_cancelled(cancel_callback)
        log("Reducing mesh size done")

        # Step 5: Convert reduced mesh to RAW
        log("Converting PLY to RAW ...")
        _check_cancelled(cancel_callback)
        await asyncio.to_thread(convert_ply_to_raw, str(path_mesh))

        raw_from_ply = work_dir / RAW_FROM_PLY_FILENAME
        ensure_exists(raw_from_ply, f"PLY to RAW conversion failed: {raw_from_ply}")
        logger.info("PLY to RAW conversion finished")
        log("Converting PLY to RAW done")
        _check_cancelled(cancel_callback)
        # Step 5: Run ImageJ
        log("Running Imagej ...")
        _check_cancelled(cancel_callback)
        await run_imagej()
        logger.info("ImageJ processing finished")

        skeleton_raw = work_dir / SKELETON_FILENAME
        ensure_exists(skeleton_raw, f"ImageJ did not create skeleton file: {skeleton_raw}")
        _check_cancelled(cancel_callback)
        # Reuse the filled raw written by convert_ply_to_raw as volume.raw
        volume_raw = work_dir / VOLUME_FILENAME
        await asyncio.to_thread(shutil.copy2, raw_from_ply, volume_raw)
        ensure_exists(volume_raw, f"Could not prepare volume file: {volume_raw}")
        _check_cancelled(cancel_callback)
        log("Running ImageJ done")

        log("Merging skeleton with volume ...")
        _check_cancelled(cancel_callback)
        merged_raw = await asyncio.to_thread(merge_raws)
        logger.info("Merged skeleton with volume: %s", merged_raw)
        _check_cancelled(cancel_callback)
        log("Merging skeleton with volume done")


        # Step 7: Compute path
        log("Compute path ...")
        _check_cancelled(cancel_callback)
        path_csv = await asyncio.to_thread(compute_skeleton_csv)
        path_csv_path = Path(path_csv)
        ensure_exists(path_csv_path, f"Path CSV was not created: {path_csv_path}")
        logger.info("Computed path CSV")
        _check_cancelled(cancel_callback)
        await asyncio.to_thread(shutil.copy2, path_csv_path, final_output)
        ensure_exists(final_output, f"Could not copy path CSV to project folder: {final_output}")
        logger.info("Copied final path CSV to %s", final_output)
        json_output = await asyncio.to_thread(csv_to_json_file, final_output, final_json_output)
        ensure_exists(json_output, f"Could not create path JSON: {json_output}")
        logger.info("Created final path JSON at %s", json_output)
        _check_cancelled(cancel_callback)
        log("Compute path done")
        return final_output, json_output

    except TaskCancelled:
        logger.info("Path pipeline cancelled for %s", mesh_id)
        log("Path pipeline cancelled.")
        raise

    except Exception:
        logger.exception("Path pipeline failed for %s", mesh_id)
        raise

    finally:
        try:
            await asyncio.to_thread(cleanup_files_dir)
            logger.info("Cleaned up temporary work directory")
        except Exception:
            logger.exception("Failed to clean up work directory")
    
