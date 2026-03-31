# controllers/anomaly_controller.py
"""AnomalyController — gestion des anomalies (création, suppression)."""
from typing import TYPE_CHECKING

from PyQt5.QtWidgets import QDialog

from models.sensor import Sensor
from simulation.anomaly import Anomaly
from views.anomaly_dialog import AnomalyDialog

if TYPE_CHECKING:
    from controllers.main_window_controller import MainWindowController


class AnomalyController:
    """
    UC30 — Créer une anomalie.
    UC33 — Supprimer une anomalie.
    UC34 — Créer aléatoirement.
    UC35 — Paramétrer une anomalie.
    """

    def __init__(self, main_ctrl: "MainWindowController"):
        self._main = main_ctrl
        self.sim_duration: float = 10.0

    def add_anomaly(self, sensor: Sensor) -> None:
        """
        Ouvre AnomalyDialog, crée l'anomalie et l'injecte dans le capteur.
        Utilise l'introspection (inspect) via la classe Anomaly pour
        récupérer les attributs et les ajouter dynamiquement.
        """
        dialog = AnomalyDialog(self.sim_duration, self._main.gui)
        if dialog.exec_() != QDialog.Accepted:
            return
        data = dialog.get_data()
        anomaly = Anomaly(
            name=data["name"],
            anomaly_type=data["type"],
            start_time=data["start_time"],
            duration=data["duration"],
            magnitude=data["magnitude"],
        )
        sensor.add_anomaly(anomaly)
        self._main.refresh_tree()
        self._main.gui.statusBar().showMessage(
            f"Anomalie '{anomaly.name}' ajoutée au capteur '{sensor.name}'."
        )

    def delete_anomaly(self, anomaly: Anomaly) -> None:
        """UC33 — Recherche et supprime l'anomalie du capteur qui la contient."""
        system = self._main.system_ctrl.system
        if system:
            for sensor in system.get_all_sensors():
                if anomaly in sensor.anomalies:
                    sensor.remove_anomaly(anomaly)
                    break
        self._main.refresh_tree()
        self._main.gui.properties_panel.show_empty()
        self._main.gui.statusBar().showMessage(
            f"Anomalie '{anomaly.name}' supprimée."
        )
