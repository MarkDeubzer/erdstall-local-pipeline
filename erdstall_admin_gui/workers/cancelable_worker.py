from threading import Event

from PySide6.QtCore import QObject, Signal, Slot


class TaskCancelled(Exception):
    pass

class CancellationToken:
    def __init__(self) -> None:
        self._event = Event()

    def cancel(self) -> None:
        self._event.set()

    def is_cancelled(self) -> bool:
        return self._event.is_set()

    def throw_if_cancelled(self, message: str = "Task was cancelled by user.") -> None:
        if self.is_cancelled():
            raise TaskCancelled(message)


class CancelableWorker(QObject):
    finished = Signal()
    log = Signal(str)
    success = Signal(str)
    error = Signal(str)
    cancelled = Signal(str)

    def __init__(self, cancel_token: CancellationToken | None = None) -> None:
        super().__init__()
        self.cancel_token = cancel_token or CancellationToken()


    def check_cancelled(self) -> None:
        self.cancel_token.throw_if_cancelled()


    def write_log(self, message: str) -> None:
        self.log.emit(message)


    @Slot()
    def request_cancel(self) -> None:
        self.cancel_token.cancel()
        self.log.emit("Cancel requested. Waiting for current operation to stop...")

    @Slot()
    def run(self) -> None:
        try:
            self.check_cancelled()

            message = self.execute()

            if not message:
                message = "Task completed successfully."

            self.success.emit(message)

        except TaskCancelled as e:
            self.cancelled.emit(str(e))

        except Exception as e:
            self.error.emit(str(e))

        finally:
            self.finished.emit()

    def execute(self) -> str:
        raise NotImplementedError("Subclasses must implement execute().")