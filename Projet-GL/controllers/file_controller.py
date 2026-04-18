# controllers/file_controller.py
"""FileController — gestion de l'import de systèmes et de l'export CSV."""
from typing import Any, Dict, List, Optional, TYPE_CHECKING

from PyQt5.QtWidgets import QFileDialog, QMessageBox

from input.system_file_input import SystemFileInput
from models.system import System
from output.csv_file_output import CSVFileOutput

if TYPE_CHECKING:
    from controllers.main_window_controller import MainWindowController


class FileController:
    """
    UC1  — Importer un système.
    UC18 — Enregistrer les données de simulation (CSV).
    """

    def __init__(self, main_ctrl: "MainWindowController"):
        self._main = main_ctrl

    def import_system(self) -> Optional[System]:
        """Ouvre un sélecteur de fichier et charge le système Python."""
        filepath, _ = QFileDialog.getOpenFileName(
            self._main.gui,
            "Importer un système",
            "",
            "Fichiers Python (*.py);;Tous les fichiers (*)",
            options=QFileDialog.DontUseNativeDialog,
        )
        if not filepath:
            return None
        try:
            return SystemFileInput(filepath).load()
        except Exception as exc:  # noqa: BLE001
            QMessageBox.critical(
                self._main.gui,
                "Erreur d'import",
                f"Impossible de charger le fichier :\n\n{exc}",
            )
            return None

    def export_csv(self, data: List[Dict[str, Any]]):
        """Ouvre un sélecteur de destination et exporte les données en CSV."""
        if not data:
            QMessageBox.warning(self._main.gui, "Export", "Aucune donnée à exporter.")
            return
        filepath, _ = QFileDialog.getSaveFileName(
            self._main.gui,
            "Exporter les données CSV",
            "simulation_lambdasys.csv",
            "Fichiers CSV (*.csv)",
            options=QFileDialog.DontUseNativeDialog,
        )
        if not filepath:
            return
        if CSVFileOutput.export(data, filepath):
            QMessageBox.information(
                self._main.gui,
                "Export réussi",
                f"Données exportées :\n{filepath}\n({len(data)} enregistrements)",
            )
        else:
            QMessageBox.critical(self._main.gui, "Erreur", "L'export CSV a échoué.")
