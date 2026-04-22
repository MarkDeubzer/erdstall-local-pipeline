from __future__ import annotations

import argparse
import shutil
import asyncio
from pathlib import Path

from erdstall_pipeline.change_textures import process_model_textures
from erdstall_pipeline.version_management import (
    get_current_version_path,
    delete_new_version,
)
from erdstall_pipeline.settings.texture_settings import TextureSettings

from erdstall_pipeline.pipeline import (
    PipelineError,
    create_project_structure,
    run_fill,
    run_finalize,
    run_patch_detection,
    initialize_project
)

from erdstall_pipeline.write_path_points_csv import write_path_points_csv
from erdstall_pipeline.path_pipeline import run_full_pipeline
from erdstall_pipeline.path_pipeline import get_project_dir, ensure_exists
from erdstall_pipeline.csv_to_json import csv_to_json_file
from erdstall_pipeline.config import PATH_OUTPUT_FILENAME, PATH_JSON_FILENAME, PATH_POINTS_FILENAME

import logging
logger = logging.getLogger(__name__)


def cmd_adjust_textures(args):
    current = get_current_version_path(args.mesh_id)

    settings = TextureSettings(
        brightness = args.brightness,
        contrast = args.contrast,
        saturation = args.saturation,
        sharpness = args.sharpness,
    )

    process_model_textures(
        current,
        current,
        settings = settings
    )
    print(f'Textures updated in: {current}')


def cmd_restore_textures(args):
    delete_new_version(args.mesh_id)
    print(f'Textures restored for: {args.mesh_id}')


def cmd_init(args):
    base = initialize_project(
        mesh_id=args.mesh_id,
        input_mesh=args.input,
        textures_dir=args.textures,
    )

    print(f"Project ready: {base}")
    print(f"Input mesh path: {base / 'original.ply'}")
    if args.textures:
        print(f"Textures copied to: {base / 'mesh'}")


def cmd_fill(args):
    out = run_fill(args.mesh_id)
    print(f'Repaired mesh created: {out}')


def cmd_patches(args):
    run_patch_detection(args.mesh_id)
    print("Patches detected")


def cmd_finalize(args):
    out = run_finalize(args.mesh_id, args.unused_patch or None)
    print(f'Final mesh created: {out}')
    mobile = out.with_name(out.stem + '_mobile' + out.suffix)
    if mobile.exists():
        print(f'Mobile mesh created: {mobile}')


def cmd_find_path(args):
    try:
        csv_output, json_output = asyncio.run(run_full_pipeline(args.mesh_id))
        print(f'Path CSV created: {csv_output}')
        print(f'Path JSON created: {json_output}')
    except Exception as e:
        raise PipelineError(f'Path calculation failed for {args.mesh_id}: {e}')
    
def cmd_convert_to_json(args):
    try:
        project_dir = get_project_dir(args.mesh_id)
        csv_input = project_dir / PATH_OUTPUT_FILENAME
        json_output = project_dir / PATH_JSON_FILENAME

        ensure_exists(csv_input, f"Path CSV not found: {csv_input}")

        json_output = csv_to_json_file(csv_input, json_output)
        ensure_exists(json_output, f"Could not create path JSON: {json_output}")

        logger.info("Created final path JSON at %s", json_output)
        print(f"Path JSON created: {json_output}")

    except Exception as e:
        raise PipelineError(f"JSON conversion failed for {args.mesh_id}: {e}")

def cmd_run_all(args):
    try:
        if args.input or args.textures:
            base = create_project_structure(args.mesh_id)
            target = base / 'original.ply'

            if args.input:
                src = Path(args.input)
                target.write_bytes(src.read_bytes())

            if args.textures:
                src_textures = Path(args.textures)
                if not src_textures.exists() or not src_textures.is_dir():
                    raise PipelineError(f'Texture folder not found: {src_textures}')

                dst_textures = base / 'mesh'
                dst_textures.mkdir(parents=True, exist_ok=True)

                for file in src_textures.iterdir():
                    if file.is_file():
                        shutil.copy2(file, dst_textures / file.name)

            print(f'Project ready: {base}')
            print(f'Input mesh path: {target}')
            if args.textures:
                print(f'Textures copied to: {base / "mesh"}')

        if args.path_points is not None:
            csv_path = write_path_points_csv(args.mesh_id, args.path_points)
            print(f'Path points CSV created: {csv_path}')

        fill_out = run_fill(args.mesh_id)
        print(f'Repaired mesh created: {fill_out}')

        run_patch_detection(args.mesh_id)
        print("Patches detected")

        final_out = run_finalize(args.mesh_id, args.unused_patch or None)
        print(f'Final mesh created: {final_out}')
        mobile = final_out.with_name(final_out.stem + '_mobile' + final_out.suffix)
        if mobile.exists():
            print(f'Mobile mesh created: {mobile}')

        csv_output, json_output = asyncio.run(run_full_pipeline(args.mesh_id))
        print(f'Path CSV created: {csv_output}')
        print(f'Path JSON created: {json_output}')

    except Exception as e:
        raise PipelineError(f'Run-all failed for {args.mesh_id}: {e}')




def build_parser():
    parser = argparse.ArgumentParser(description='Local Erdstall mesh pipeline')
    sub = parser.add_subparsers(dest='command', required=True)

    p_init = sub.add_parser('init', help='Create project folder and optionally copy original mesh')
    p_init.add_argument('mesh_id')
    p_init.add_argument('--input', help='Path to the source .ply file')
    p_init.add_argument('--textures', help='Path to a folder containing texture files')
    p_init.set_defaults(func=cmd_init)

    p_fill = sub.add_parser('fill', help='Run repaired mesh generation')
    p_fill.add_argument('mesh_id')
    p_fill.set_defaults(func=cmd_fill)

    p_patches = sub.add_parser('patches', help='Detect generated patches and print patches.json')
    p_patches.add_argument('mesh_id')
    p_patches.set_defaults(func=cmd_patches)

    p_finalize = sub.add_parser('finalize', help='Create final mesh and optional mobile version')
    p_finalize.add_argument('mesh_id')
    p_finalize.add_argument('--unused-patch', action='append', help='Patch filename to remove, can be repeated')
    p_finalize.set_defaults(func=cmd_finalize)

    p_json = sub.add_parser('convert-to-json', help='Convert path.csv to path.json')
    p_json.add_argument('mesh_id')
    p_json.set_defaults(func=cmd_convert_to_json)

    p_adjust = sub.add_parser('adjust-textures', help='Adjust texture images in the project')
    p_adjust.add_argument('mesh_id')
    p_adjust.add_argument('--brightness', type=float, default=1.0)
    p_adjust.add_argument('--contrast', type=float, default=1.0)
    p_adjust.add_argument('--saturation', type=float, default=1.0)
    p_adjust.add_argument('--sharpness', type=float, default=1.0)
    p_adjust.set_defaults(func=cmd_adjust_textures)

    p_restore = sub.add_parser('restore-textures', help='Restore original texture images from backup')
    p_restore.add_argument('mesh_id')
    p_restore.set_defaults(func=cmd_restore_textures)

    p_find_path = sub.add_parser('find-path', help='Calculate a path through the cave')
    p_find_path.add_argument('mesh_id')
    p_find_path.set_defaults(func=cmd_find_path)

    p_run_all = sub.add_parser('run-all', help='Run the full pipeline: init/copy, fill, patches, finalize, find-path')
    p_run_all.add_argument('mesh_id')
    p_run_all.add_argument('--input', help='Path to the source .ply file')
    p_run_all.add_argument('--textures', help='Path to a folder containing texture files')
    p_run_all.add_argument('--unused-patch', action='append', help='Patch filename to remove, can be repeated')
    p_run_all.add_argument(
        '--path-points',
        nargs=6,
        type=float,
        metavar=('START_X', 'START_Y', 'START_Z', 'END_X', 'END_Y', 'END_Z'),
        help='Six MeshLab/world coordinates for start and end point'
    )
    p_run_all.set_defaults(func=cmd_run_all)

    return parser



if __name__ == '__main__':
    parser = build_parser()
    args = parser.parse_args()
    try:
        args.func(args)
    except PipelineError as e:
        raise SystemExit(str(e))