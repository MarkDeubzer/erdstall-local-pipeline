from __future__ import annotations

from pathlib import Path

import trimesh
import numpy as np
from PySide6.QtCore import QObject, Signal, Slot


class PlyToGlbWorker(QObject):
    finished = Signal()
    error = Signal(str)
    log = Signal(str)
    success = Signal(str)

    def __init__(self, mesh_id: str) -> None:
        super().__init__()
        self.mesh_id = mesh_id

    @Slot()
    def run(self) -> None:
        try:
            self.log.emit(f"Starting PLY TO GLB conversion...")
            input_path = Path("data/ply") / f"{self.mesh_id}/mesh.ply"
            output_path = Path("data/ply") / f"{self.mesh_id}/mesh.glb"

            output_path.parent.mkdir(parents=True, exist_ok=True)

            if not input_path.exists():
                raise FileNotFoundError(f"File not found at {input_path}")

            self.log.emit(f"Reading PLY file: {input_path}")
            mesh = trimesh.load(input_path)

            if isinstance(mesh, trimesh.Scene):
                mesh = trimesh.util.concatenate(tuple(mesh.geometry.values()))

            if not isinstance(mesh, trimesh.Trimesh):
                raise ValueError("Loaded file is not a valid mesh.")

            if len(mesh.faces) == 0:
                raise ValueError(
                    "PLY file is only a point cloud. GLB export needs a mesh with faces."
                )

            self.log.emit("Rotating mesh...")
            rotation = trimesh.transformations.rotation_matrix(
                np.radians(-90), [1,0,0]
            )
            mesh.apply_transform(rotation)
            self.log.emit("Rotating mesh done.")


            self.log.emit("Cleaning mesh...")

            mesh.remove_unreferenced_vertices()
            mesh.remove_infinite_values()

            # robust cleanup
            mesh.update_faces(mesh.unique_faces())
            mesh.remove_unreferenced_vertices()

            # remove degenerate faces manually
            mask = mesh.area_faces > 0
            mesh.update_faces(mask)
            mesh.remove_unreferenced_vertices()

            self.log.emit("Fixing normals...")
            mesh.fix_normals()


            self.log.emit("Saving GLB file...")
            mesh.export(output_path)

            self.success.emit(f"Successfully saved GLB file to {output_path}")

        except Exception as e:
            self.error.emit(str(e))
        finally:
            self.finished.emit()