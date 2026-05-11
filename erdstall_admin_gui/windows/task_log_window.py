from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import (
    QDialog,
    QLabel,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class TaskLogWindow(QDialog):

    cancel_requested = Signal()

    def __init__(self, title: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self._running = True
        self._cancel_requested = False

        self.setWindowTitle(title)
        self.resize(700, 500)
        self.setModal(True)

        self.status_label = QLabel("Running...")
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)

        self.close_button = QPushButton("Cancel")
        self.close_button.clicked.connect(self._on_button_clicked)

        layout = QVBoxLayout(self)
        layout.addWidget(self.status_label)
        layout.addWidget(self.log_output)
        layout.addWidget(self.close_button, 0, Qt.AlignmentFlag.AlignRight)

    def append_log(self, text: str) -> None:
        self.log_output.append(text)

    def set_running(self, text: str = "Running...") -> None:
        self._running = True
        self.status_label.setText(text)

        if self._cancel_requested:
            self.close_button.setText("Cancelling...")
            self.close_button.setEnabled(False)
        else:
            self.close_button.setText("Cancel")
            self.close_button.setEnabled(True)

    def set_success(self, text: str = "Done") -> None:
        self._running = False
        self.status_label.setText(text)
        self.close_button.setText("Close")
        self.close_button.setEnabled(True)

    def _on_button_clicked(self) -> None:
        if self._running:
            self._requested_cancel()
            return

        self.accept()

    def _requested_cancel(self) -> None:
        if self._cancel_requested:
            return

        self._cancel_requested = True
        self.status_label.setText("Cancelling...")
        self.close_button.setText("Cancelling...")
        self.close_button.setEnabled(False)

        self.append_log("Cancel requested by user.")
        self.cancel_requested.emit()




    def set_error(self, text: str = "Failed") -> None:
        self._running = False
        self.status_label.setText(text)
        self.close_button.setText("Close")
        self.close_button.setEnabled(True)

    def reject(self) -> None:
        if self._running:
            self._requested_cancel()
            return

        super().reject()

    def closeEvent(self, event: QCloseEvent) -> None:
        if self._running:
            self._requested_cancel()
            event.ignore()
            return

        super().closeEvent(event)