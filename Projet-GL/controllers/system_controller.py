# controllers/system_controller.py
"""SystemController — gestion du modèle System."""
from typing import Optional, TYPE_CHECKING

from models.component import Component
from models.system import System

if TYPE_CHECKING:
    from controllers.main_window_controller import MainWindowController


class SystemController:
    """Stocke le système actif et synchronise la vue (arbre)."""

    def __init__(self, main_ctrl: "MainWindowController"):
        self._main = main_ctrl
        self.system: Optional[System] = None

    def set_system(self, system: System) -> None:
        self.system = system
        self._main.refresh_tree()
        n = len(system.components)
        self._main.gui.statusBar().showMessage(
            f"Système '{system.name}' chargé — {n} composant(s)"
        )
        self._main.gui.action_sim_launch.setEnabled(True)
        self._main.gui.action_add_sensor.setEnabled(True)

    def toggle_component(self, comp: Component) -> None:
        """UC — Basculer l'état opérationnel d'un composant."""
        comp.is_operational = not comp.is_operational
        self._main.refresh_tree()
        self._main.gui.properties_panel.show_component(comp)
        state = "opérationnel" if comp.is_operational else "hors service"
        self._main.gui.statusBar().showMessage(
            f"Composant '{comp.name}' mis {state}."
        )
