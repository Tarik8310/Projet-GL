# views/simulation_panel.py
"""SimulationPanel — onglet d'affichage en cours de simulation."""
from typing import Any, Dict

from PyQt5.QtWidgets import (
    QLabel, QProgressBar, QTextEdit, QVBoxLayout, QWidget,
)


class SimulationPanel(QWidget):
    """
    Affiche la progression (barre), le statut et les dernières valeurs
    générées en temps réel pendant la simulation.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        self.status_label = QLabel("En attente — aucune simulation lancée.")
        self.status_label.setStyleSheet(
            "font-size:13px; font-weight:bold; color:#2c3e50;"
        )
        layout.addWidget(self.status_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFixedHeight(22)
        layout.addWidget(self.progress_bar)

        layout.addWidget(QLabel("<b>Dernières valeurs générées :</b>"))

        self.live_text = QTextEdit()
        self.live_text.setReadOnly(True)
        self.live_text.setMaximumHeight(220)
        self.live_text.setStyleSheet(
            "background:#f8f9fa; font-family:monospace;"
            "font-size:11px; border:1px solid #ddd;"
        )
        layout.addWidget(self.live_text)

        layout.addStretch()

    def set_status(self, text: str, color: str = "#2c3e50") -> None:
        self.status_label.setText(text)
        self.status_label.setStyleSheet(
            f"font-size:13px; font-weight:bold; color:{color};"
        )

    def update_progress(self, value: int) -> None:
        self.progress_bar.setValue(value)

    def update_live_data(self, data: Dict[str, Any]) -> None:
        lines = [f"{k:<45} = {v}" for k, v in data.items()]
        self.live_text.setText("\n".join(lines))
