from __future__ import annotations
from PySide6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QLineEdit, QPlainTextEdit, QDialogButtonBox


class CreateXmlWindow(QDialog):
    def __init__(self, default_id: str | None = None, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Create XML")
        self.resize(700,600)

        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.id_input = QLineEdit(default_id or "")
        self.name_input = QLineEdit()
        self.database_input = QLineEdit("OÖ Landesarchiv, Ö Bundesdenkmalamt")

        self.discovery_input = QPlainTextEdit()
        self.first_2d_input = QPlainTextEdit()

        self.first_3d_date_input = QLineEdit()
        self.first_3d_person_input = QLineEdit()

        self.latitude_input = QLineEdit()
        self.longitude_input = QLineEdit()

        self.type_short_input = QLineEdit("B")
        self.type_long_input = QLineEdit("Mehrkammer mit Schlupfen")

        self.description_input = QPlainTextEdit()

        self.length_input = QLineEdit()
        self.depth_input = QLineEdit()
        self.volume_input = QLineEdit()

        self.link_input = QLineEdit("https://ooe-erdstallzentrum.at/wp/")
        self.carrier_input = QLineEdit("OÖ Erdstallzentrum Tollet Unterstetten")


        form.addRow("ID:", self.id_input)
        form.addRow("Name:", self.name_input)
        form.addRow("Datenbankeinträge:", self.database_input)
        form.addRow("Entdeckung:", self.discovery_input)
        form.addRow("Erst 2D Daten:", self.first_2d_input)
        form.addRow("Erst 3D Datum (dd.mm.yyyy):", self.first_3d_date_input)
        form.addRow("Erst 3D Personen:", self.first_3d_person_input)
        form.addRow("Latitude:", self.latitude_input)
        form.addRow("Longitude:", self.longitude_input)
        form.addRow("Type kurz:", self.type_short_input)
        form.addRow("Type lang:", self.type_long_input)
        form.addRow("Beschreibung:", self.description_input)
        form.addRow("Länge:", self.length_input)
        form.addRow("Tiefe:", self.depth_input)
        form.addRow("Volumen:", self.volume_input)
        form.addRow("Link:", self.link_input)
        form.addRow("Träger:", self.carrier_input)


        layout.addLayout(form)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout.addWidget(buttons)

    def get_settings(self) -> dict[str, str]:
        return {
            "id": self.id_input.text().strip(),
            "name": self.name_input.text().strip(),
            "database_entries": self.database_input.text().strip(),
            "discovery": self.discovery_input.toPlainText().strip(),
            "first_2d_data": self.first_2d_input.toPlainText().strip(),
            "first_3d_date": self.first_3d_date_input.text().strip(),
            "first_3d_person": self.first_3d_person_input.text().strip(),
            "latitude": self.latitude_input.text().strip(),
            "longitude": self.longitude_input.text().strip(),
            "type_short": self.type_short_input.text().strip(),
            "type_long": self.type_long_input.text().strip(),
            "description": self.description_input.toPlainText().strip(),
            "length": self.length_input.text().strip(),
            "depth": self.depth_input.text().strip(),
            "volume": self.volume_input.text().strip(),
            "link": self.link_input.text().strip(),
            "carrier": self.carrier_input.text().strip(),

        }
