from __future__ import annotations

import asyncio

from PySide6.QtCore import QObject, Signal, Slot

class PathFullPipelineWorker(QObject):
    finished = Signal()
    log = Signal(str)
    success = Signal(str)
    error = Signal(str)

    def __init__(self, mesh_id: str) -> None:
        super().__init__()
        self.mesh_id = mesh_id

    @Slot()
    def run(self) -> None:
        try:
            from erdstall_pipeline.path_pipeline import run_full_pipeline

            self.log.emit(f"Starting full path pipeline for project: {self.mesh_id}")

            csv_output, json_output = asyncio.run(run_full_pipeline(self.mesh_id,log_callback=self.log.emit))

            self.log.emit(f"Path CSV created: {csv_output}")
            self.log.emit(f"Path JSON created: {json_output}")

            self.success.emit(
                f"Full pipeline completed.\nPath CSV: {csv_output}\nPath JSON: {json_output}"
            )
        except Exception as e:
            self.error.emit(str(e))
        finally:
            self.finished.emit()