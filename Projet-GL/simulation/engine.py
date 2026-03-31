# simulation/engine.py
"""Classe SimulationEngine — moteur de simulation principal de GADMAPS."""
import time
from typing import Any, Callable, Dict, List, Optional

from models.component import Component
from models.system import System
from simulation.data_gen import DataGen
from simulation.system_update import SystemUpdate


class SimulationEngine:
    """
    Orchestre la boucle temporelle de simulation.
    Délègue la mise à jour à SystemUpdate et l'échantillonnage à DataGen.
    Doit être exécuté dans un thread dédié pour ne pas bloquer l'interface.
    """

    def __init__(
        self,
        system,
        duree_totale: float = 10.0,
        pas_de_temps: float = 0.1,
    ):
        # Compatibilité : accepte un System ou une liste de composants
        if isinstance(system, System):
            self.system: Optional[System] = system
            self.composants: List[Component] = system.components
        else:
            self.system = None
            self.composants = list(system)

        self.duree_totale: float = duree_totale
        self.pas_de_temps: float = pas_de_temps
        self.temps_actuel: float = 0.0
        self.historique_donnees: List[Dict[str, Any]] = []

        self._running: bool = False
        self._paused: bool = False
        self._progress_callback: Optional[Callable[[int], None]] = None
        self._data_callback: Optional[Callable[[Dict], None]] = None

    # ------------------------------------------------------------------
    # Configuration des callbacks
    # ------------------------------------------------------------------

    def set_progress_callback(self, cb: Callable[[int], None]) -> None:
        """Appelé avec la progression (0–100) à chaque pas de temps."""
        self._progress_callback = cb

    def set_data_callback(self, cb: Callable[[Dict], None]) -> None:
        """Appelé avec le dictionnaire de données à chaque pas de temps."""
        self._data_callback = cb

    # ------------------------------------------------------------------
    # Contrôle depuis un thread externe
    # ------------------------------------------------------------------

    def pause(self) -> None:
        self._paused = True

    def resume(self) -> None:
        self._paused = False

    def stop(self) -> None:
        self._running = False

    # ------------------------------------------------------------------
    # Boucle de simulation
    # ------------------------------------------------------------------

    def _reset_anomalies(self) -> None:
        for comp in self.composants:
            for sensor in getattr(comp, "sensors", []):
                for anomaly in sensor.anomalies:
                    anomaly.reset()

    def run(self) -> List[Dict[str, Any]]:
        """Lance la boucle synchrone. À exécuter dans un QThread."""
        print(
            f"[Simulation] Démarrage — durée={self.duree_totale} s, "
            f"pas={self.pas_de_temps} s"
        )
        self.temps_actuel = 0.0
        self.historique_donnees.clear()
        self._running = True
        self._reset_anomalies()

        while self._running and self.temps_actuel <= self.duree_totale:
            while self._paused and self._running:
                time.sleep(0.02)

            SystemUpdate.update(self.composants, self.pas_de_temps, self.temps_actuel)
            row = DataGen.sample(self.composants, self.temps_actuel)
            self.historique_donnees.append(row)

            if self._data_callback:
                self._data_callback(row)
            if self._progress_callback:
                pct = int((self.temps_actuel / self.duree_totale) * 100)
                self._progress_callback(min(pct, 100))

            self.temps_actuel = round(self.temps_actuel + self.pas_de_temps, 6)

        self._running = False
        print(f"[Simulation] Terminée — {len(self.historique_donnees)} points générés")
        return self.historique_donnees
