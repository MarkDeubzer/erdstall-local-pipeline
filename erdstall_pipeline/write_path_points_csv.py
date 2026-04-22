from __future__ import annotations
from erdstall_pipeline.config import PATH_POINTS_FILENAME
from pathlib import Path


from erdstall_pipeline.pipeline import (
    PipelineError,
)
from erdstall_pipeline.path_pipeline import get_project_dir
from erdstall_pipeline.config import PATH_POINTS_FILENAME

def write_path_points_csv(mesh_id: str, start_end_values: list[float]) -> Path:
    if len(start_end_values) != 6:
        raise PipelineError(
            "You must provide exactly 6 numbers: "
            "start_x start_y start_z end_x end_y end_z"
        )

    project_dir = get_project_dir(mesh_id)
    project_dir.mkdir(parents=True, exist_ok=True)

    csv_path = project_dir / PATH_POINTS_FILENAME

    with open(csv_path, "w", encoding="utf-8") as f:
        f.write("start_x,start_y,start_z,end_x,end_y,end_z\n")
        f.write(",".join(str(v) for v in start_end_values) + "\n")

    return csv_path