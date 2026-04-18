# controllers/sensor_controller.py
"""SensorController — gestion des capteurs (ajout, suppression)."""
from typing import TYPE_CHECKING

from PyQt5.QtWidgets import QDialog, QMessageBox

from models.component import Component
from models.sensor import Sensor
from views.sensor_dialog import SensorDialog

if TYPE_CHECKING:
    from controllers.main_window_controller import MainWindowController


class SensorController:
    """
    UC20 — Ajouter un capteur.
    UC21 — Supprimer un capteur.
    UC23 — Modifier les unités d'un capteur.
    """

    def __init__(self, main_ctrl: "MainWindowController"):
        self._main = main_ctrl

    def add_sensor(self, component: Component):
        """Ouvre SensorDialog et attache le capteur au composant."""
        dialog = SensorDialog(component, self._main.gui)
        if dialog.exec_() != QDialog.Accepted:
            return
        data = dialog.get_data()
        sensor = Sensor(
            name=data["name"],
            target_output=data["target_output"],
            unit=data["unit"],
            frequency=data["frequency"],
        )
        component.add_sensor(sensor)
        self._main.refresh_tree()
        self._main.gui.action_add_anomaly.setEnabled(True)
        self._main.gui.statusBar().showMessage(
            f"Capteur '{sensor.name}' ajouté à '{component.name}'."
        )

    def delete_sensor(self, sensor: Sensor):
        """UC21 — Supprime un capteur après confirmation utilisateur."""
        reply = QMessageBox.question(
            self._main.gui,
            "Supprimer le capteur",
            f"Supprimer le capteur <b>{sensor.name}</b> ?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply == QMessageBox.Yes and sensor.component:
            sensor.component.remove_sensor(sensor)
            self._main.refresh_tree()
            self._main.gui.properties_panel.show_empty()
            self._main.gui.statusBar().showMessage(
                f"Capteur '{sensor.name}' supprimé."
            )
