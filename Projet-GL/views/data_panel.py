# views/data_panel.py
"""DataPanel — onglet d'affichage des données générées (tableau)."""
from typing import Any, Dict, List

from PyQt5.QtWidgets import (
    QHeaderView, QLabel, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget,
)


class DataPanel(QWidget):
    """
    Affiche les données de simulation sous forme de tableau.
    Chargé en une seule fois à la fin de la simulation.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)

        info = QLabel(
            "Les données apparaissent ici après la fin de la simulation. "
            "Utilisez Fichier → Exporter CSV pour les sauvegarder."
        )
        info.setStyleSheet("color:#7f8c8d; font-size:11px;")
        layout.addWidget(info)

        self.table = QTableWidget()
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setStyleSheet("font-family:monospace; font-size:11px;")
        layout.addWidget(self.table)

        self._headers: List[str] = []

    def load_data(self, data: List[Dict[str, Any]]) -> None:
        """Charge toutes les données dans le tableau (appelé après simulation)."""
        if not data:
            return
        self._headers = list(data[0].keys())
        self.table.setColumnCount(len(self._headers))
        self.table.setHorizontalHeaderLabels(self._headers)
        self.table.setRowCount(len(data))
        for r, row in enumerate(data):
            for c, key in enumerate(self._headers):
                self.table.setItem(r, c, QTableWidgetItem(str(row.get(key, ""))))

    def clear_data(self) -> None:
        self.table.setRowCount(0)
        self.table.setColumnCount(0)
        self._headers = []
