from __future__ import annotations

from pathlib import Path

import open3d as o3d
from erdstall_admin_gui.workers.cancelable_worker import CancelableWorker, CancellationToken
from erdstall_pipeline.config import ORIGINAL_MESH, PLY_DIR, REPAIRED_MESH, CONVERTED_MESH
from erdstall_pipeline.convert_point_cloud import point_cloud_to_mesh
from erdstall_pipeline.settings.point_cloud_settings import PointCloudSettings

class PointCloudToMeshWorker(CancelableWorker):

    def __init__(self,
                 mesh_id: str,
                 settings: PointCloudSettings | None = None,
                 cancel_token: CancellationToken | None = None) -> None:
        super().__init__(cancel_token)
        self.mesh_id = mesh_id
        self.settings = settings or PointCloudSettings()

    def execute(self) -> str:
        project_dir = Path(PLY_DIR) / self.mesh_id
        input_path = project_dir / ORIGINAL_MESH
        output_path = project_dir / CONVERTED_MESH

        self.check_cancelled()

        if not input_path.exists():
            raise FileNotFoundError(f"Original point cloud not found: {input_path}")

        self.write_log(f"Reading point cloud: {input_path}")
        pcd = o3d.io.read_point_cloud(str(input_path))

        self.check_cancelled()

        if pcd.is_empty():
            raise ValueError("Open3D loaded an empty point cloud.")

        self.write_log(f"Point cloud has {len(pcd.points)} points.")

        self.write_log("Converting point cloud to mesh...")
        self.write_log(
            f"Reconstruction method: "
            f"{getattr(self.settings, 'reconstruction_method', 'poisson')}"
        )

        mesh = point_cloud_to_mesh(
            pcd,
            settings=self.settings,
            log_callback=self.write_log,
            cancel_callback=self.check_cancelled,
        )

        self.check_cancelled()

        if mesh.is_empty():
            raise ValueError("Point-cloud conversion produced an empty mesh.")

        self.write_log("Computing vertex normals...")
        mesh.compute_vertex_normals()

        self.check_cancelled()

        output_path.parent.mkdir(parents=True, exist_ok=True)

        self.write_log(f"Saving converted mesh: {output_path}")

        ok = o3d.io.write_triangle_mesh(
            str(output_path),
            mesh,
            write_ascii=False,
            compressed=False,
            write_vertex_normals=True,
            write_vertex_colors=True,
        )

        self.check_cancelled()

        if not ok:
            raise RuntimeError(f"Failed to write mesh: {output_path}")

        return f"Successfully converted mesh: {output_path}"