from __future__ import annotations
from collections.abc import Callable
from PySide6.QtCore import QObject, QThread, QTimer
from PySide6.QtWidgets import QMessageBox
from erdstall_admin_gui.windows.task_log_window import TaskLogWindow
from erdstall_admin_gui.workers.cancelable_worker import CancellationToken


class LoggedCancelableTaskRunnerMixin:
    def _start_logged_cancelable_task(
        self,
        *,
        task_title: str,
        busy_message: str,
        running_message: str,
        thread_attr: str,
        worker_attr: str,
        cancel_token_attr: str,
        worker_factory: Callable[[CancellationToken], QObject],
        success_status: str,
        error_status: str,
        success_box_title: str,
        error_box_title: str,
        on_success: Callable[None]
    ) -> None:
        if getattr(self, thread_attr) is not None:
            QMessageBox.information(self, "Busy", busy_message)
            return

        log_window = TaskLogWindow(task_title, self)
        log_window.set_running(running_message)

        self._task_log_window = log_window

        cancel_token = CancellationToken()
        setattr(self, cancel_token_attr, cancel_token)

        thread = QThread(self)
        worker = worker_factory(cancel_token)

        setattr(self, thread_attr, thread)
        setattr(self, worker_attr, worker)

        worker.moveToThread(thread)

        thread.started.connect(worker.run)
        worker.log.connect(log_window.append_log)

        worker.success.connect(
            lambda message: self._on_logged_task_success(
                message=message,
                log_window=log_window,
                status_message=success_status,
            )
        )

        worker.error.connect(
            lambda message: self._on_logged_task_error(
                message=message,
                log_window=log_window,
                status_message=error_status,
            )
        )

        worker.cancelled.connect(
            lambda message: self._on_logged_task_cancelled(
                message=message,
                log_window=log_window,
                task_title=success_box_title,
            )
        )

        worker.finished.connect(worker.deleteLater)
        worker.finished.connect(thread.quit)

        thread.finished.connect(
            lambda: self._on_logged_task_finished(
                thread_attr=thread_attr,
                worker_attr=worker_attr,
                cancel_token_attr=cancel_token_attr,
                log_window=log_window,
                success_box_title=success_box_title,
                error_box_title=error_box_title,
                on_success=on_success,
            )
        )

        thread.finished.connect(thread.deleteLater)

        log_window.cancel_requested.connect(
            lambda: self._cancel_logged_task(
                cancel_token_attr=cancel_token_attr,
                log_window=log_window,
                task_title=success_box_title,
            )
        )

        thread.start()
        log_window.show()

    def _cancel_logged_task(
        self,
        *,
        cancel_token_attr: str,
        log_window: TaskLogWindow,
        task_title: str,
    ) -> None:
        cancel_token = getattr(self, cancel_token_attr)

        if cancel_token is None:
            return

        cancel_token.cancel()

        log_window.append_log("Waiting for current operation to stop...")
        log_window.set_running(f"Cancelling {task_title}...")

    def _on_logged_task_success(
        self,
        *,
        message: str,
        log_window: TaskLogWindow,
        status_message: str,
    ) -> None:
        log_window.append_log(f"[SUCCESS] {message}")
        log_window.set_success(status_message)

        log_window.task_result = "success"
        log_window.task_message = message
        log_window.task_auto_close = True

    def _on_logged_task_error(
        self,
        *,
        message: str,
        log_window: TaskLogWindow,
        status_message: str,
    ) -> None:
        log_window.append_log(f"[ERROR] {message}")
        log_window.set_error(status_message)

        log_window.task_result = "error"
        log_window.task_message = message
        log_window.task_auto_close = False

    def _on_logged_task_cancelled(
        self,
        *,
        message: str,
        log_window: TaskLogWindow,
        task_title: str,
    ) -> None:
        if not message:
            message = "Task was cancelled by user."

        log_window.append_log(f"[CANCELLED] {message}")
        log_window.set_success(f"{task_title} cancelled.")

        log_window.task_result = "cancelled"
        log_window.task_message = message
        log_window.task_auto_close = True

    def _on_logged_task_finished(
        self,
        *,
        thread_attr: str,
        worker_attr: str,
        cancel_token_attr: str,
        log_window: TaskLogWindow,
        success_box_title: str,
        error_box_title: str,
        on_success: Callable[[str], None] | None = None,
    ) -> None:
        print(f"Task cleanup: {thread_attr}, {worker_attr}, {cancel_token_attr}")

        result = getattr(log_window, "task_result", None)
        message = getattr(log_window, "task_message", "")
        auto_close = bool(getattr(log_window, "task_auto_close", False))

        setattr(self, thread_attr, None)
        setattr(self, worker_attr, None)
        setattr(self, cancel_token_attr, None)

        if self._task_log_window is log_window:
            self._task_log_window = None

        if result == "success":
            if on_success is not None:
                on_success(message)

            if auto_close:
                QTimer.singleShot(0, log_window.accept)

            QMessageBox.information(self, success_box_title, message)

        elif result == "cancelled":
            if auto_close:
                QTimer.singleShot(0, log_window.accept)

        elif result == "error":
            QMessageBox.critical(self, error_box_title, message)