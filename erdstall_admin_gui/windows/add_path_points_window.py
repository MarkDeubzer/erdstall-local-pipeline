from __future__ import annotations

from PySide6.QtWidgets import (
    QDialog,
    QDoubleSpinBox,
    QFormLayout,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

class AddPathPointsWindow(QDialog):
    def __init__(self, parent: QWidget | None = None)-> None:
        super().__init__(parent)

        self.setWindowTitle("Add Path Points CSV")
        self.resize(420, 260)

        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)

        info_label = QLabel("Enter start and end coordinated in MeshLab/world coordinates. ")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)

        group = QGroupBox("Path Points")
        grid = QGridLayout(group)

        self.start_x = self._double_spinbox()
        self.start_y = self._double_spinbox()
        self.start_z = self._double_spinbox()

        self.end_x = self._double_spinbox()
        self.end_y = self._double_spinbox()
        self.end_z = self._double_spinbox()

        grid.addWidget(QLabel("Start X:"), 0, 0)
        grid.addWidget(self.start_x, 0, 1)
        grid.addWidget(QLabel("Start Y:"), 1, 0)
        grid.addWidget(self.start_y, 1, 1)
        grid.addWidget(QLabel("Start Z:"), 2, 0)
        grid.addWidget(self.start_z, 2, 1)

        grid.addWidget(QLabel("End X:"), 3, 0)
        grid.addWidget(self.end_x, 3, 1)
        grid.addWidget(QLabel("End Y:"), 4, 0)
        grid.addWidget(self.end_y, 4, 1)
        grid.addWidget(QLabel("End Z:"), 5, 0)
        grid.addWidget(self.end_z, 5, 1)

        layout.addWidget(group)

        buttons = QHBoxLayout()
        buttons.addStretch()

        self.cancel_button = QPushButton("Cancel")
        self.save_button = QPushButton("Save")

        self.cancel_button.clicked.connect(self.reject)
        self.save_button.clicked.connect(self.accept)

        buttons.addWidget(self.cancel_button)
        buttons.addWidget(self.save_button)

        layout.addLayout(buttons)

    def get_values(self)->list[float]:
        return [
            self.start_x.value(),
            self.start_y.value(),
            self.start_z.value(),
            self.end_x.value(),
            self.end_y.value(),
            self.end_z.value(),
        ]

    @staticmethod
    def _double_spinbox() -> QDoubleSpinBox:
        box = QDoubleSpinBox()
        box.setRange(-1_000_000.0, 1_000_000.0)
        box.setDecimals(6)
        box.setSingleStep(0.1)
        return box