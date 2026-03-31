# controllers/simulation_worker.py
"""SimulationWorker — exécution de la simulation dans un QThread dédié."""
from typing import Any, Dict, List

from PyQt5.QtCore import QThread, pyqtSignal

from simulation.engine import SimulationEngine


class SimulationWorker(QThread):
    """
    Exécute SimulationEngine dans un thread dédié pour ne pas bloquer l'IHM.
    Émet des signaux vers le SimulationController.
    """

    progress_updated = pyqtSignal(int)       # 0–100
    data_generated = pyqtSignal(dict)        # dernier enregistrement
    simulation_finished = pyqtSignal(list)   # historique complet
    simulation_error = pyqtSignal(str)       # message d'erreur

    def __init__(self, engine: SimulationEngine):
        super().__init__()
        self.engine = engine

    def run(self) -> None:
        try:
            self.engine.set_progress_callback(self.progress_updated.emit)
            self.engine.set_data_callback(self.data_generated.emit)
            results = self.engine.run()
            self.simulation_finished.emit(results)
        except Exception as exc:  # noqa: BLE001
            self.simulation_error.emit(str(exc))

    def pause_sim(self) -> None:
        self.engine.pause()

    def resume_sim(self) -> None:
        self.engine.resume()

    def stop_sim(self) -> None:
        self.engine.stop()
