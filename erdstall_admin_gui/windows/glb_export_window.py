from __future__ import annotations

from pathlib import Path
from typing import cast

from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDoubleSpinBox,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from erdstall_pipeline.settings.glb_export_settings import (
    GlbCompression,
    GlbExportSettings,
)


class GlbExportWindow(QDialog):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self.setWindowTitle("GLB Export Settings")
        self.resize(620, 620)

        self._build_ui()
        self._load_defaults()
        self._connect()

    def _build_ui(self) -> None:
        main_layout = QVBoxLayout(self)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        content = QWidget()
        layout = QVBoxLayout(content)

        # ------------------------------------------------------------
        # Human Scale Reference
        # ------------------------------------------------------------
        human_group = QGroupBox("Human Scale Reference")
        human_form = QFormLayout(human_group)

        self.add_human_scale = QCheckBox("Add human scale model")
        self.add_human_to_mobile = QCheckBox("Also add human model to mobile GLB")

        self.human_model_path = QLineEdit()
        self.human_browse_button = QPushButton("Browse")

        human_path_row = QHBoxLayout()
        human_path_row.addWidget(self.human_model_path)
        human_path_row.addWidget(self.human_browse_button)

        self.human_height = self._doublespinbox(0.1, 10.0, 0.05, 2)
        self.human_floor_offset = self._doublespinbox(-10.0, 10.0, 0.01, 3)

        self.human_up_axis = QComboBox()
        self.human_up_axis.addItems(["x", "y", "z"])

        human_form.addRow("", self.add_human_scale)
        human_form.addRow("", self.add_human_to_mobile)
        human_form.addRow("Human model:", self._wrap(human_path_row))
        human_form.addRow("Human height:", self.human_height)
        human_form.addRow("Floor offset:", self.human_floor_offset)
        human_form.addRow("Human up axis:", self.human_up_axis)

        # ------------------------------------------------------------
        # Export Rotation
        # ------------------------------------------------------------
        rotation_group = QGroupBox("Export Rotation")
        rotation_form = QFormLayout(rotation_group)

        self.rotation_x = self._doublespinbox(-360.0, 360.0, 5.0, 2)
        self.rotation_y = self._doublespinbox(-360.0, 360.0, 5.0, 2)
        self.rotation_z = self._doublespinbox(-360.0, 360.0, 5.0, 2)

        rotation_form.addRow("Rotate X degrees:", self.rotation_x)
        rotation_form.addRow("Rotate Y degrees:", self.rotation_y)
        rotation_form.addRow("Rotate Z degrees:", self.rotation_z)

        # ------------------------------------------------------------
        # Output Options
        # ------------------------------------------------------------
        output_group = QGroupBox("Output Options")
        output_form = QFormLayout(output_group)

        self.create_mobile_glb = QCheckBox("Create Mobile GLB")

        output_form.addRow("", self.create_mobile_glb)

        # ------------------------------------------------------------
        # Optimization Options
        # ------------------------------------------------------------
        optimization_group = QGroupBox("GLB Optimization")
        optimization_form = QFormLayout(optimization_group)

        self.optimize_glb = QCheckBox("Optimize GLB after export")

        self.glb_compression = QComboBox()
        self.glb_compression.addItems(["meshopt", "draco"])

        self.main_include_normals = QCheckBox("Include normals in main GLB")
        self.mobile_include_normals = QCheckBox("Include normals in mobile GLB")

        optimization_form.addRow("", self.optimize_glb)
        optimization_form.addRow("Compression:", self.glb_compression)
        optimization_form.addRow("", self.main_include_normals)
        optimization_form.addRow("", self.mobile_include_normals)

        layout.addWidget(human_group)
        layout.addWidget(rotation_group)
        layout.addWidget(output_group)
        layout.addWidget(optimization_group)
        layout.addStretch()

        scroll_area.setWidget(content)

        # ------------------------------------------------------------
        # Buttons
        # ------------------------------------------------------------
        buttons = QHBoxLayout()
        buttons.addStretch()

        self.cancel_button = QPushButton("Cancel")
        self.export_button = QPushButton("Export GLB")

        buttons.addWidget(self.cancel_button)
        buttons.addWidget(self.export_button)

        main_layout.addWidget(scroll_area)
        main_layout.addLayout(buttons)

    def _connect(self) -> None:
        self.cancel_button.clicked.connect(self.reject)
        self.export_button.clicked.connect(self.accept)

        self.human_browse_button.clicked.connect(self._browse_human_model)

        self.add_human_scale.toggled.connect(self._set_human_settings_enabled)
        self.optimize_glb.toggled.connect(self._set_optimization_settings_enabled)
        self.create_mobile_glb.toggled.connect(self._set_mobile_settings_enabled)

    def _load_defaults(self) -> None:
        defaults = GlbExportSettings()

        self.add_human_scale.setChecked(defaults.add_human_scale)
        self.add_human_to_mobile.setChecked(defaults.add_human_to_mobile)

        self.human_model_path.setText(str(defaults.human_model_path))
        self.human_height.setValue(defaults.human_height)
        self.human_floor_offset.setValue(defaults.human_floor_offset)

        index = self.human_up_axis.findText(defaults.human_up_axis)
        if index >= 0:
            self.human_up_axis.setCurrentIndex(index)

        self.rotation_x.setValue(defaults.rotation_x_degrees)
        self.rotation_y.setValue(defaults.rotation_y_degrees)
        self.rotation_z.setValue(defaults.rotation_z_degrees)

        self.create_mobile_glb.setChecked(defaults.create_mobile_glb)

        self.optimize_glb.setChecked(defaults.optimize_glb)

        compression_index = self.glb_compression.findText(defaults.glb_compression)
        if compression_index >= 0:
            self.glb_compression.setCurrentIndex(compression_index)

        self.main_include_normals.setChecked(defaults.main_include_normals)
        self.mobile_include_normals.setChecked(defaults.mobile_include_normals)

        self._set_human_settings_enabled(defaults.add_human_scale)
        self._set_optimization_settings_enabled(defaults.optimize_glb)
        self._set_mobile_settings_enabled(defaults.create_mobile_glb)

    def _set_human_settings_enabled(self, enabled: bool) -> None:
        self.add_human_to_mobile.setEnabled(enabled)
        self.human_model_path.setEnabled(enabled)
        self.human_browse_button.setEnabled(enabled)
        self.human_height.setEnabled(enabled)
        self.human_floor_offset.setEnabled(enabled)
        self.human_up_axis.setEnabled(enabled)

    def _set_optimization_settings_enabled(self, enabled: bool) -> None:
        self.glb_compression.setEnabled(enabled)

    def _set_mobile_settings_enabled(self, enabled: bool) -> None:
        self.mobile_include_normals.setEnabled(enabled)

        if not enabled:
            self.add_human_to_mobile.setChecked(False)

    def _browse_human_model(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Select human GLB model",
            "",
            "GLB files (*.glb);;GLTF files (*.gltf);;All files (*)",
        )

        if path:
            self.human_model_path.setText(path)

    def get_settings(self) -> GlbExportSettings:
        compression = cast(
            GlbCompression,
            self.glb_compression.currentText(),
        )

        return GlbExportSettings(
            add_human_scale=self.add_human_scale.isChecked(),
            add_human_to_mobile=self.add_human_to_mobile.isChecked(),
            human_model_path=Path(
                self.human_model_path.text().strip() or "public/person.glb"
            ).expanduser(),
            human_height=self.human_height.value(),
            human_floor_offset=self.human_floor_offset.value(),
            human_up_axis=self.human_up_axis.currentText(),
            rotation_x_degrees=self.rotation_x.value(),
            rotation_y_degrees=self.rotation_y.value(),
            rotation_z_degrees=self.rotation_z.value(),
            create_mobile_glb=self.create_mobile_glb.isChecked(),
            optimize_glb=self.optimize_glb.isChecked(),
            glb_compression=compression,
            main_include_normals=self.main_include_normals.isChecked(),
            mobile_include_normals=self.mobile_include_normals.isChecked(),
        )

    def _wrap(self, layout: QHBoxLayout) -> QWidget:
        widget = QWidget()
        widget.setLayout(layout)
        return widget

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