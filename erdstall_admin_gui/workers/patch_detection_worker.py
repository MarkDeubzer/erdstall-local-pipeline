from __future__ import annotations

from PySide6.QtCore import QObject, Signal, Slot



class PatchDetectionWorker(QObject):
    finished = Signal()
    log = Signal(str)
    success = Signal(str)
    error = Signal(str)

    def __init__(self, mesh_id: str)-> None:
        super().__init__()
        self.mesh_id = mesh_id

    @Slot()
    def run(self)-> None:
        try:
            from erdstall_pipeline.pipeline import run_patch_detection

            result = run_patch_detection(
                self.mesh_id,
                log_callback=self.log.emit
            )
            count = result.get("total_patches", 0)
            self.success.emit(f"Patch detection completed. Found {count} patches.")
        except Exception as e:
            self.error.emit(str(e))
        finally:
            self.finished.emit()