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
        self.resize(520, 360)

        self._build_ui()
        self._load_defaults()
        self._connect()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)

        repair_group = QGroupBox("Mesh Repair")
        repair_form = QFormLayout(repair_group)

        self.close_holes_on_mesh_input = QCheckBox()
        self.close_hole_under_percent = self._doublespinbox(0.0, 1.0, 0.01, 2)

        self.smooth_mesh_input = QCheckBox()
        self.mesh_smoothing_iterations = self._spinbox(0, 50)

        self.transfer_texture = QCheckBox("Transfer texture to vertex colors")
        self.reduce_size = QCheckBox("Reduce file size after repair")

        repair_form.addRow("Close holes:", self.close_holes_on_mesh_input)
        repair_form.addRow(
            "Ignore top percent:",
            self.close_hole_under_percent,
        )
        repair_form.addRow("Smooth mesh:", self.smooth_mesh_input)
        repair_form.addRow(
            "Smoothing iterations:",
            self.mesh_smoothing_iterations,
        )

        poisson_group = QGroupBox("Optional Mesh Poisson Reconstruction")
        poisson_form = QFormLayout(poisson_group)

        self.run_poisson_on_mesh = QCheckBox()

        self.poisson_depth = self._spinbox(1, 14)
        self.poisson_fulldepth = self._spinbox(1, 14)
        self.poisson_cgdepth = self._spinbox(0, 14)
        self.poisson_scale = self._doublespinbox(0.1, 10.0, 0.1, 2)
        self.poisson_samplespernode = self._doublespinbox(0.1, 20.0, 0.1, 2)
        self.poisson_pointweight = self._doublespinbox(0.1, 20.0, 0.1, 2)
        self.poisson_iters = self._spinbox(1, 50)
        self.poisson_preclean = QCheckBox()

        poisson_form.addRow("Run Poisson:", self.run_poisson_on_mesh)
        poisson_form.addRow("Depth:", self.poisson_depth)
        poisson_form.addRow("Full depth:", self.poisson_fulldepth)
        poisson_form.addRow("CG depth:", self.poisson_cgdepth)
        poisson_form.addRow("Scale:", self.poisson_scale)
        poisson_form.addRow("Samples per node:", self.poisson_samplespernode)
        poisson_form.addRow("Point weight:", self.poisson_pointweight)
        poisson_form.addRow("Iterations:", self.poisson_iters)
        poisson_form.addRow("Preclean:", self.poisson_preclean)

        buttons = QHBoxLayout()
        buttons.addStretch()

        self.cancel_button = QPushButton("Cancel")
        self.run_button = QPushButton("Run Fill Holes")

        buttons.addWidget(self.cancel_button)
        buttons.addWidget(self.run_button)

        layout.addWidget(repair_group)
        layout.addWidget(poisson_group)
        layout.addWidget(self.transfer_texture)
        layout.addWidget(self.reduce_size)
        layout.addLayout(buttons)

    def _connect(self) -> None:
        self.cancel_button.clicked.connect(self.reject)
        self.run_button.clicked.connect(self.accept)
        self.run_poisson_on_mesh.toggled.connect(self._set_poisson_enabled)

    def _load_defaults(self) -> None:
        defaults = FillHolesSettings()

        self.run_poisson_on_mesh.setChecked(defaults.run_poisson_on_mesh)

        self.close_holes_on_mesh_input.setChecked(defaults.close_holes_on_mesh_input)
        self.close_hole_under_percent.setValue(defaults.close_hole_under_percent)

        self.smooth_mesh_input.setChecked(defaults.smooth_mesh_input)
        self.mesh_smoothing_iterations.setValue(defaults.mesh_smoothing_iterations)

        self.poisson_depth.setValue(defaults.poisson_depth)
        self.poisson_fulldepth.setValue(defaults.poisson_fulldepth)
        self.poisson_cgdepth.setValue(defaults.poisson_cgdepth)
        self.poisson_scale.setValue(defaults.poisson_scale)
        self.poisson_samplespernode.setValue(defaults.poisson_samplespernode)
        self.poisson_pointweight.setValue(defaults.poisson_pointweight)
        self.poisson_iters.setValue(defaults.poisson_iters)
        self.poisson_preclean.setChecked(defaults.poisson_preclean)

        self.transfer_texture.setChecked(defaults.transfer_texture_to_vertex_colors)
        self.reduce_size.setChecked(defaults.reduce_size)

        self._set_poisson_enabled(defaults.run_poisson_on_mesh)

    def _set_poisson_enabled(self, enabled: bool) -> None:
        widgets = [
            self.poisson_depth,
            self.poisson_fulldepth,
            self.poisson_cgdepth,
            self.poisson_scale,
            self.poisson_samplespernode,
            self.poisson_pointweight,
            self.poisson_iters,
            self.poisson_preclean,
        ]

        for widget in widgets:
            widget.setEnabled(enabled)

    def get_settings(self) -> FillHolesSettings:
        return FillHolesSettings(
            run_poisson_on_mesh=self.run_poisson_on_mesh.isChecked(),
            close_holes_on_mesh_input=self.close_holes_on_mesh_input.isChecked(),
            close_hole_under_percent=self.close_hole_under_percent.value(),
            poisson_depth=self.poisson_depth.value(),
            poisson_fulldepth=self.poisson_fulldepth.value(),
            poisson_cgdepth=self.poisson_cgdepth.value(),
            poisson_scale=self.poisson_scale.value(),
            poisson_samplespernode=self.poisson_samplespernode.value(),
            poisson_pointweight=self.poisson_pointweight.value(),
            poisson_iters=self.poisson_iters.value(),
            poisson_preclean=self.poisson_preclean.isChecked(),
            transfer_texture_to_vertex_colors=self.transfer_texture.isChecked(),
            smooth_mesh_input=self.smooth_mesh_input.isChecked(),
            mesh_smoothing_iterations=self.mesh_smoothing_iterations.value(),
            reduce_size=self.reduce_size.isChecked(),
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