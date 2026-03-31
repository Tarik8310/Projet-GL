# controllers/data_controller.py
"""DataController — gestion du stockage et de l'affichage des données générées."""
from typing import Any, Dict, List, TYPE_CHECKING

if TYPE_CHECKING:
    from controllers.main_window_controller import MainWindowController


class DataController:
    """Stocke l'historique de simulation et met à jour les vues DataGUI."""

    def __init__(self, main_ctrl: "MainWindowController"):
        self._main = main_ctrl
        self._data: List[Dict[str, Any]] = []

    def clear(self) -> None:
        self._data.clear()
        self._main.gui.data_panel.clear_data()

    def on_row_received(self, row: Dict[str, Any]) -> None:
        """Appelé en temps réel à chaque nouveau point — met à jour l'affichage live."""
        self._data.append(row)
        self._main.gui.sim_panel.update_live_data(row)

    def on_simulation_finished(self, data: List[Dict[str, Any]]) -> None:
        """Charge les données dans le tableau et active l'export CSV."""
        self._data = data
        self._main.gui.data_panel.load_data(data)
        self._main.gui.action_export_csv.setEnabled(bool(data))
        self._main.gui.sim_panel.set_status(
            f"Simulation terminée ✔ — {len(data)} points de données générés.",
            "#27ae60",
        )
        self._main.gui.tabs.setCurrentIndex(2)  # Basculer vers onglet Données
        self._main.gui.statusBar().showMessage(
            f"Simulation terminée — {len(data)} enregistrements disponibles."
        )

    def get_data(self) -> List[Dict[str, Any]]:
        return self._data
