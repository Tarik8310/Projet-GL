# views/anomaly_dialog.py
"""AnomalyDialog — dialogue de création d'une anomalie."""
import random

from PyQt5.QtWidgets import (
    QComboBox, QDialog, QDialogButtonBox, QDoubleSpinBox,
    QGroupBox, QHBoxLayout, QLabel, QLineEdit, QMessageBox,
    QPushButton, QVBoxLayout,
)

from simulation.anomaly import AnomalyType


class AnomalyDialog(QDialog):
    """
    UC30 — Créer une anomalie.
    UC34 — Créer aléatoirement.
    UC35 — Paramétrer une anomalie.
    """

    def __init__(self, sim_duration: float, parent=None):
        super().__init__(parent)
        self.sim_duration = sim_duration
        self.setWindowTitle("Créer une anomalie")
        self.setMinimumWidth(460)
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)

        group = QGroupBox("Paramètres de l'anomalie")
        form = QVBoxLayout(group)

        def row(label: str, widget) -> None:
            h = QHBoxLayout()
            lbl = QLabel(label)
            lbl.setFixedWidth(130)
            h.addWidget(lbl)
            h.addWidget(widget)
            form.addLayout(h)

        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Ex : anomalie_pression_1")
        row("Nom :", self.name_edit)

        self.type_combo = QComboBox()
        for atype in AnomalyType:
            self.type_combo.addItem(atype.value, atype)
        row("Type :", self.type_combo)

        self.start_spin = QDoubleSpinBox()
        self.start_spin.setRange(0.0, max(0.0, self.sim_duration - 0.1))
        self.start_spin.setSuffix(" s")
        self.start_spin.setDecimals(2)
        row("Début :", self.start_spin)

        self.duration_spin = QDoubleSpinBox()
        self.duration_spin.setRange(0.01, self.sim_duration)
        self.duration_spin.setSuffix(" s")
        self.duration_spin.setDecimals(2)
        self.duration_spin.setValue(min(1.0, self.sim_duration * 0.2))
        row("Durée :", self.duration_spin)

        self.magnitude_spin = QDoubleSpinBox()
        self.magnitude_spin.setRange(-1_000_000.0, 1_000_000.0)
        self.magnitude_spin.setDecimals(2)
        self.magnitude_spin.setValue(50.0)
        row("Magnitude :", self.magnitude_spin)

        layout.addWidget(group)

        btn_random = QPushButton("🎲  Générer aléatoirement (UC34)")
        btn_random.setStyleSheet(
            "background-color:#3498db; color:white; padding:6px; border-radius:4px;"
        )
        btn_random.clicked.connect(self._randomize)
        layout.addWidget(btn_random)

        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.button(QDialogButtonBox.Ok).setText("Ajouter")
        btns.accepted.connect(self._validate)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)

    def _randomize(self) -> None:
        self.name_edit.setText(f"anomalie_{random.randint(100, 999)}")
        self.type_combo.setCurrentIndex(random.randint(0, self.type_combo.count() - 1))
        self.start_spin.setValue(round(random.uniform(0, self.sim_duration * 0.6), 2))
        self.duration_spin.setValue(
            round(random.uniform(0.5, max(0.5, self.sim_duration * 0.25)), 2)
        )
        self.magnitude_spin.setValue(round(random.uniform(10.0, 200.0), 2))

    def _validate(self) -> None:
        if not self.name_edit.text().strip():
            QMessageBox.warning(self, "Validation", "Le nom de l'anomalie est requis.")
            return
        self.accept()

    def get_data(self) -> dict:
        return {
            "name": self.name_edit.text().strip(),
            "type": self.type_combo.currentData(),
            "start_time": self.start_spin.value(),
            "duration": self.duration_spin.value(),
            "magnitude": self.magnitude_spin.value(),
        }
