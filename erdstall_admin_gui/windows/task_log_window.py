from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QLabel,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class TaskLogWindow(QDialog):
    def __init__(self, title: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self._running = True

        self.setWindowTitle(title)
        self.resize(700, 500)
        self.setModal(True)

        self.status_label = QLabel("Running...")
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)

        self.close_button = QPushButton("Close")
        self.close_button.setEnabled(False)
        self.close_button.clicked.connect(self.accept)

        layout = QVBoxLayout(self)
        layout.addWidget(self.status_label)
        layout.addWidget(self.log_output)
        layout.addWidget(self.close_button, 0, Qt.AlignRight)

    def append_log(self, text: str) -> None:
        self.log_output.append(text)

    def set_running(self, text: str = "Running...") -> None:
        self._running = True
        self.status_label.setText(text)
        self.close_button.setEnabled(False)

    def set_success(self, text: str = "Done") -> None:
        self._running = False
        self.status_label.setText(text)
        self.close_button.setEnabled(True)

    def set_error(self, text: str = "Failed") -> None:
        self._running = False
        self.status_label.setText(text)
        self.close_button.setEnabled(True)

    def reject(self) -> None:
        if self._running:
            return
        super().reject()