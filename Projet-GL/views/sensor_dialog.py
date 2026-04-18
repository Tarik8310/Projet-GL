# views/sensor_dialog.py
"""SensorDialog — dialogue de création / modification d'un capteur."""
from typing import Optional

from PyQt5.QtWidgets import (
    QComboBox, QDialog, QDialogButtonBox, QDoubleSpinBox,
    QGroupBox, QHBoxLayout, QLabel, QLineEdit, QMessageBox,
    QVBoxLayout,
)

from models.component import Component
from models.sensor import Sensor


class SensorDialog(QDialog):
    """
    UC20 — Ajouter un capteur.
    UC23 — Modifier les unités d'un capteur.
    """

    def __init__(
        self,
        component: Component,
        parent=None,
        sensor: Optional[Sensor] = None,
    ):
        """
        Construit le dialogue de création ou de modification d'un capteur.

        :param component: Composant auquel le capteur sera attaché.
        :param parent: Widget Qt parent (facultatif).
        :param sensor: Capteur existant à modifier, ou None pour une création.
        """
        super().__init__(parent)
        self.component = component
        self.sensor = sensor
        self.setWindowTitle("Modifier le capteur" if sensor else "Ajouter un capteur")
        self.setMinimumWidth(440)
        self._build_ui()

    def _build_ui(self):
        """Construit le formulaire de saisie des paramètres du capteur."""
        layout = QVBoxLayout(self)

        header = QLabel(f"Composant : <b>{self.component.name}</b>")
        header.setStyleSheet("color:#2c3e50; font-size:13px; margin-bottom:6px;")
        layout.addWidget(header)

        group = QGroupBox("Paramètres du capteur")
        form = QVBoxLayout(group)

        def row(label: str, widget):
            h = QHBoxLayout()
            lbl = QLabel(label)
            lbl.setFixedWidth(140)
            h.addWidget(lbl)
            h.addWidget(widget)
            form.addLayout(h)

        self.name_edit = QLineEdit(self.sensor.name if self.sensor else "")
        self.name_edit.setPlaceholderText("Ex : capteur_pression_1")
        row("Nom :", self.name_edit)

        self.output_combo = QComboBox()
        outputs = list(self.component.outputs.keys())
        if outputs:
            self.output_combo.addItems(outputs)
            if self.sensor and self.sensor.target_output in outputs:
                self.output_combo.setCurrentText(self.sensor.target_output)
        else:
            self.output_combo.addItem("(aucune sortie disponible)")
            self.output_combo.setEnabled(False)
        row("Sortie mesurée :", self.output_combo)

        self.unit_edit = QLineEdit(self.sensor.unit if self.sensor else "")
        self.unit_edit.setPlaceholderText("Ex : bar, °C, kg/s")
        row("Unité :", self.unit_edit)

        self.freq_spin = QDoubleSpinBox()
        self.freq_spin.setRange(0.1, 10_000.0)
        self.freq_spin.setSuffix(" Hz")
        self.freq_spin.setDecimals(1)
        self.freq_spin.setValue(self.sensor.frequency if self.sensor else 10.0)
        row("Fréquence :", self.freq_spin)

        layout.addWidget(group)

        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.button(QDialogButtonBox.Ok).setText(
            "Modifier" if self.sensor else "Ajouter"
        )
        btns.accepted.connect(self._validate)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)

    def _validate(self):
        """Vérifie la saisie et accepte le dialogue si les données sont valides."""
        if not self.name_edit.text().strip():
            QMessageBox.warning(self, "Validation", "Le nom du capteur est requis.")
            return
        if not self.component.outputs:
            QMessageBox.warning(
                self, "Validation", "Ce composant n'a aucune sortie mesurable."
            )
            return
        self.accept()

    def get_data(self) -> dict:
        """
        Retourne les paramètres saisis sous forme de dictionnaire.

        :return: Dictionnaire avec les clés name, target_output, unit, frequency.
        """
        return {
            "name": self.name_edit.text().strip(),
            "target_output": self.output_combo.currentText(),
            "unit": self.unit_edit.text().strip() or "-",
            "frequency": self.freq_spin.value(),
        }
