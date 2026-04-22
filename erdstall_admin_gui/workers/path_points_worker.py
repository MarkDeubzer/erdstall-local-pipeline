from __future__ import annotations

from PySide6.QtCore import QObject, Signal, Slot




class PathPointsWorker(QObject):
    finished = Signal()
    success = Signal(str)
    error = Signal(str)

    def __init__(self, mesh_id: str, values: list[float]) -> None:
        super().__init__()
        self.mesh_id = mesh_id
        self.values = values

    @Slot()
    def run(self) -> None:
        try:
            from erdstall_pipeline.write_path_points_csv import write_path_points_csv
            csv_path = write_path_points_csv(self.mesh_id, self.values)
            self.success.emit(f"Path points CSV created: {csv_path}")
        except Exception as e:
            self.error.emit(str(e))
        finally:
            self.finished.emit()