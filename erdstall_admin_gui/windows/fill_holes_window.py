from __future__ import annotations

from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from erdstall_pipeline.settings.fill_holes_settings import FillHolesSettings


class FillHolesWindow(QDialog):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self.setWindowTitle("Fill Holes Settings")
        self.resize(520, 420)

        self._build_ui()
        self._load_defaults()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)

        point_cloud_group = QGroupBox("Point Cloud Reconstruction")
        point_cloud_form = QFormLayout(point_cloud_group)

        self.point_cloud_depth = self._spinbox(1, 20)
        self.point_cloud_fulldepth = self._spinbox(1, 20)
        self.point_cloud_scale = self._doublespinbox(0.1, 10.0, 0.1, 2)
        self.point_cloud_samplespernode = self._doublespinbox(0.1, 20.0, 0.1, 2)
        self.point_cloud_pointweight = self._doublespinbox(0.1, 20.0, 0.1, 2)
        self.point_cloud_iters = self._spinbox(1, 50)
        self.point_cloud_preclean = QCheckBox()

        point_cloud_form.addRow("Depth:", self.point_cloud_depth)
        point_cloud_form.addRow("Full depth:", self.point_cloud_fulldepth)
        point_cloud_form.addRow("Scale:", self.point_cloud_scale)
        point_cloud_form.addRow("Samples per node:", self.point_cloud_samplespernode)
        point_cloud_form.addRow("Point weight:", self.point_cloud_pointweight)
        point_cloud_form.addRow("Iterations:", self.point_cloud_iters)
        point_cloud_form.addRow("Preclean:", self.point_cloud_preclean)

        poisson_group = QGroupBox("Poisson Reconstruction")
        poisson_form = QFormLayout(poisson_group)

        self.poisson_depth = self._spinbox(1, 20)
        self.poisson_fulldepth = self._spinbox(1, 20)
        self.poisson_cgdepth = self._spinbox(0, 20)
        self.poisson_scale = self._doublespinbox(0.1, 10.0, 0.1, 2)
        self.poisson_samplespernode = self._doublespinbox(0.1, 20.0, 0.1, 2)
        self.poisson_pointweight = self._doublespinbox(0.1, 20.0, 0.1, 2)
        self.poisson_iters = self._spinbox(1, 50)
        self.poisson_preclean = QCheckBox()

        poisson_form.addRow("Depth:", self.poisson_depth)
        poisson_form.addRow("Full depth:", self.poisson_fulldepth)
        poisson_form.addRow("CG depth:", self.poisson_cgdepth)
        poisson_form.addRow("Scale:", self.poisson_scale)
        poisson_form.addRow("Samples per node:", self.poisson_samplespernode)
        poisson_form.addRow("Point weight:", self.poisson_pointweight)
        poisson_form.addRow("Iterations:", self.poisson_iters)
        poisson_form.addRow("Preclean:", self.poisson_preclean)

        self.transfer_texture = QCheckBox("Transfer texture to vertex colors")
        self.transfer_texture.setChecked(True)

        buttons = QHBoxLayout()
        buttons.addStretch()

        self.cancel_button = QPushButton("Cancel")
        self.run_button = QPushButton("Run")

        self.cancel_button.clicked.connect(self.reject)
        self.run_button.clicked.connect(self.accept)

        buttons.addWidget(self.cancel_button)
        buttons.addWidget(self.run_button)

        layout.addWidget(point_cloud_group)
        layout.addWidget(poisson_group)
        layout.addWidget(self.transfer_texture)
        layout.addLayout(buttons)

    def _load_defaults(self) -> None:
        defaults = FillHolesSettings()

        self.point_cloud_depth.setValue(defaults.point_cloud_depth)
        self.point_cloud_fulldepth.setValue(defaults.point_cloud_fulldepth)
        self.point_cloud_scale.setValue(defaults.point_cloud_scale)
        self.point_cloud_samplespernode.setValue(defaults.point_cloud_samplespernode)
        self.point_cloud_pointweight.setValue(defaults.point_cloud_pointweight)
        self.point_cloud_iters.setValue(defaults.point_cloud_iters)
        self.point_cloud_preclean.setChecked(defaults.point_cloud_preclean)

        self.poisson_depth.setValue(defaults.poisson_depth)
        self.poisson_fulldepth.setValue(defaults.poisson_fulldepth)
        self.poisson_cgdepth.setValue(defaults.poisson_cgdepth)
        self.poisson_scale.setValue(defaults.poisson_scale)
        self.poisson_samplespernode.setValue(defaults.poisson_samplespernode)
        self.poisson_pointweight.setValue(defaults.poisson_pointweight)
        self.poisson_iters.setValue(defaults.poisson_iters)
        self.poisson_preclean.setChecked(defaults.poisson_preclean)

        self.transfer_texture.setChecked(defaults.transfer_texture_to_vertex_colors)

    def get_settings(self) -> FillHolesSettings:
        return FillHolesSettings(
            point_cloud_depth=self.point_cloud_depth.value(),
            point_cloud_fulldepth=self.point_cloud_fulldepth.value(),
            point_cloud_scale=self.point_cloud_scale.value(),
            point_cloud_samplespernode=self.point_cloud_samplespernode.value(),
            point_cloud_pointweight=self.point_cloud_pointweight.value(),
            point_cloud_iters=self.point_cloud_iters.value(),
            point_cloud_preclean=self.point_cloud_preclean.isChecked(),
            poisson_depth=self.poisson_depth.value(),
            poisson_fulldepth=self.poisson_fulldepth.value(),
            poisson_cgdepth=self.poisson_cgdepth.value(),
            poisson_scale=self.poisson_scale.value(),
            poisson_samplespernode=self.poisson_samplespernode.value(),
            poisson_pointweight=self.poisson_pointweight.value(),
            poisson_iters=self.poisson_iters.value(),
            poisson_preclean=self.poisson_preclean.isChecked(),
            transfer_texture_to_vertex_colors=self.transfer_texture.isChecked(),
        )

    @staticmethod
    def _spinbox(minimum: int, maximum: int) -> QSpinBox:
        box = QSpinBox()
        box.setRange(minimum, maximum)
        return box

    @staticmethod
    def _doublespinbox(
        minimum: float,
        maximum: float,
        step: float,
        decimals: int,
    ) -> QDoubleSpinBox:
        box = QDoubleSpinBox()
        box.setRange(minimum, maximum)
        box.setSingleStep(step)
        box.setDecimals(decimals)
        return box