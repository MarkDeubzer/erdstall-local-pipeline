from __future__ import annotations

import asyncio

from erdstall_admin_gui.workers.cancelable_worker import (
    CancelableWorker,
    CancellationToken,
)


class PathFullPipelineWorker(CancelableWorker):
    def __init__(
        self,
        mesh_id: str,
        cancel_token: CancellationToken | None = None,
    ) -> None:
        super().__init__(cancel_token)
        self.mesh_id = mesh_id

    def execute(self) -> str:
        from erdstall_pipeline.path_pipeline import run_full_pipeline

        self.write_log(f"Starting full path pipeline for project: {self.mesh_id}")

        self.check_cancelled()

        csv_output, json_output = asyncio.run(
            run_full_pipeline(
                self.mesh_id,
                log_callback=self.log.emit,
                cancel_callback=self.check_cancelled,
            )
        )

        self.check_cancelled()

        self.write_log(f"Path CSV created: {csv_output}")
        self.write_log(f"Path JSON created: {json_output}")

        return (
            "Full pipeline completed.\n"
            f"Path CSV: {csv_output}\n"
            f"Path JSON: {json_output}"
        )