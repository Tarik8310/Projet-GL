# views/simulation_config_dialog.py
"""SimulationConfigDialog — dialogue de configuration de la simulation."""
from PyQt5.QtWidgets import (
    QDialog, QDialogButtonBox, QDoubleSpinBox,
    QGroupBox, QHBoxLayout, QLabel, QVBoxLayout,
)


class SimulationConfigDialog(QDialog):
    """Configure la durée et le pas de temps avant le lancement."""

    def __init__(self, parent=None):
        """
        Construit le dialogue de configuration de la simulation.

        :param parent: Widget Qt parent (facultatif).
        """
        super().__init__(parent)
        self.setWindowTitle("Configurer la simulation")
        self.setMinimumWidth(380)
        self._build_ui()

    def _build_ui(self):
        """Construit le formulaire avec les champs durée et pas de temps."""
        layout = QVBoxLayout(self)

        group = QGroupBox("Paramètres")
        form = QVBoxLayout(group)

        def row(label: str, widget):
            h = QHBoxLayout()
            lbl = QLabel(label)
            lbl.setFixedWidth(140)
            h.addWidget(lbl)
            h.addWidget(widget)
            form.addLayout(h)

        self.duration_spin = QDoubleSpinBox()
        self.duration_spin.setRange(0.1, 86_400.0)
        self.duration_spin.setSuffix(" s")
        self.duration_spin.setDecimals(1)
        self.duration_spin.setValue(10.0)
        row("Durée totale :", self.duration_spin)

        self.step_spin = QDoubleSpinBox()
        self.step_spin.setRange(0.001, 60.0)
        self.step_spin.setSuffix(" s")
        self.step_spin.setDecimals(3)
        self.step_spin.setValue(0.1)
        row("Pas de temps :", self.step_spin)

        layout.addWidget(group)

        info = QLabel(
            "ℹ  Un pas de temps faible augmente la précision\n"
            "   mais allonge le temps de calcul."
        )
        info.setStyleSheet("color:#7f8c8d; font-size:11px;")
        layout.addWidget(info)

        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.button(QDialogButtonBox.Ok).setText("▶  Lancer")
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)

    def get_config(self) -> dict:
        """
        Retourne la configuration de simulation saisie.

        :return: Dictionnaire avec les clés ``duration`` (s) et ``step`` (s).
        """
        return {
            "duration": self.duration_spin.value(),
            "step": self.step_spin.value(),
        }
