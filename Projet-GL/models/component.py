# models/component.py
"""Classe abstraite Component — base de tout composant d'un système LambdaSys."""
from abc import ABC, abstractmethod
from typing import Dict, List, TYPE_CHECKING

if TYPE_CHECKING:
    from models.sensor import Sensor
    from simulation.anomaly import Anomaly


class Component(ABC):
    """
    Classe mère abstraite pour tout composant d'un système technique.
    Tout fichier système importé doit définir des sous-classes de Component.
    """

    def __init__(self, name: str):
        """
        Initialise un composant opérationnel sans capteurs ni anomalies.

        :param name: Identifiant lisible du composant.
        """
        self.name: str = name
        self.is_operational: bool = True
        self.outputs: Dict[str, float] = {}   # Grandeurs physiques mesurables
        self.sensors: List["Sensor"] = []     # Capteurs attachés
        self.anomalies: List["Anomaly"] = []  # Anomalies injectées sur ce composant

    @abstractmethod
    def update_state(self, dt: float, t: float):
        """
        Met à jour l'état interne du composant à chaque pas de temps.

        :param dt: Durée du pas de temps en secondes.
        :param t: Instant courant de la simulation en secondes.
        """

    def add_sensor(self, sensor: "Sensor"):
        """
        Attache un capteur à ce composant (sans doublon).

        :param sensor: Capteur à associer.
        """
        if sensor not in self.sensors:
            self.sensors.append(sensor)
            sensor.component = self

    def remove_sensor(self, sensor: "Sensor"):
        """
        Détache un capteur de ce composant.

        :param sensor: Capteur à retirer.
        """
        if sensor in self.sensors:
            self.sensors.remove(sensor)
            sensor.component = None

    def add_anomaly(self, anomaly: "Anomaly"):
        """
        Injecte une anomalie sur ce composant (sans doublon).

        :param anomaly: Anomalie à ajouter.
        """
        if anomaly not in self.anomalies:
            self.anomalies.append(anomaly)

    def remove_anomaly(self, anomaly: "Anomaly"):
        """
        Retire une anomalie de ce composant.

        :param anomaly: Anomalie à supprimer.
        """
        if anomaly in self.anomalies:
            self.anomalies.remove(anomaly)

    def __repr__(self) -> str:
        return f"Component(name='{self.name}', operational={self.is_operational})"
