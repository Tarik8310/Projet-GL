# controllers/simulation_controller.py
"""SimulationController — orchestration du cycle de simulation."""
from typing import Any, Dict, List, Optional, TYPE_CHECKING

from PyQt5.QtWidgets import QDialog, QMessageBox

from controllers.simulation_worker import SimulationWorker
from simulation.engine import SimulationEngine
from views.simulation_config_dialog import SimulationConfigDialog

if TYPE_CHECKING:
    from controllers.main_window_controller import MainWindowController


class SimulationController:
    """
    UC15 — Lancer une simulation.
    UC16 — Arrêter une simulation.
    UC17 — Mettre en pause / Reprendre.
    """

    def __init__(self, main_ctrl: "MainWindowController"):
        """
        Initialise le contrôleur sans worker actif.

        :param main_ctrl: Référence au contrôleur principal.
        """
        self._main = main_ctrl
        self._worker: Optional[SimulationWorker] = None
        self._paused: bool = False

    def launch(self):
        """Configure et démarre la simulation dans un thread dédié."""
        system = self._main.system_ctrl.system
        if not system:
            QMessageBox.warning(self._main.gui, "Simulation", "Aucun système chargé.")
            return

        dialog = SimulationConfigDialog(self._main.gui)
        if dialog.exec_() != QDialog.Accepted:
            return

        config = dialog.get_config()
        self._main.anomaly_ctrl.sim_duration = config["duration"]

        engine = SimulationEngine(system, config["duration"], config["step"])
        self._worker = SimulationWorker(engine)

        self._worker.progress_updated.connect(
            self._main.gui.sim_panel.update_progress
        )
        self._worker.data_generated.connect(self._main.data_ctrl.on_row_received)
        self._worker.simulation_finished.connect(self._on_finished)
        self._worker.simulation_error.connect(self._on_error)

        self._main.data_ctrl.clear()
        self._main.gui.sim_panel.init_charts(system.components)
        self._main.gui.sim_panel.set_status("Simulation en cours...", "#e67e22")
        self._main.gui.sim_panel.update_progress(0)
        self._main.gui.tabs.setCurrentIndex(1)  # Onglet Simulation

        self._set_running_state(True)
        self._worker.start()

    def pause_resume(self):
        """UC17 — Alterne entre pause et reprise."""
        if not self._worker or not self._worker.isRunning():
            return
        sim_panel = self._main.gui.sim_panel
        if self._paused:
            self._worker.resume_sim()
            self._main.gui.action_sim_pause.setText("⏸  Pause / Reprendre")
            sim_panel.btn_pause.setText("⏸  Pause / Reprendre")
            sim_panel.set_status("Simulation en cours...", "#e67e22")
            self._paused = False
        else:
            self._worker.pause_sim()
            self._main.gui.action_sim_pause.setText("▶  Reprendre")
            sim_panel.btn_pause.setText("▶  Reprendre")
            sim_panel.set_status("Simulation en pause ⏸", "#f39c12")
            self._paused = True

    def stop(self):
        """UC16 — Arrête la simulation."""
        if self._worker:
            self._worker.stop_sim()

    # ------------------------------------------------------------------
    # Callbacks internes
    # ------------------------------------------------------------------

    def _on_finished(self, data: List[Dict[str, Any]]):
        """
        Callback appelé par le worker à la fin normale de la simulation.

        :param data: Historique complet des enregistrements.
        """
        self._set_running_state(False)
        self._main.data_ctrl.on_simulation_finished(data)

    def _on_error(self, msg: str):
        """
        Callback appelé par le worker en cas d'exception dans le moteur.

        :param msg: Message d'erreur à afficher.
        """
        self._set_running_state(False)
        self._main.gui.sim_panel.set_status(f"Erreur : {msg}", "#e74c3c")
        QMessageBox.critical(self._main.gui, "Erreur de simulation", msg)

    def _set_running_state(self, running: bool):
        """
        Active ou désactive les actions de menu et les boutons du panneau.

        :param running: True si une simulation est en cours, False sinon.
        """
        gui = self._main.gui
        gui.action_sim_launch.setEnabled(not running)
        gui.action_sim_pause.setEnabled(running)
        gui.action_sim_stop.setEnabled(running)
        gui.action_import.setEnabled(not running)
        gui.sim_panel.btn_pause.setEnabled(running)
        gui.sim_panel.btn_stop.setEnabled(running)
        if not running:
            gui.action_sim_pause.setText("⏸  Pause / Reprendre")
            gui.sim_panel.btn_pause.setText("⏸  Pause / Reprendre")
            self._paused = False
