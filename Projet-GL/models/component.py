# models/component.py
"""Classe abstraite Component — base de tout composant d'un système LambdaSys."""
from abc import ABC, abstractmethod
from typing import Dict, List, TYPE_CHECKING

if TYPE_CHECKING:
    from models.sensor import Sensor


class Component(ABC):
    """
    Classe mère abstraite pour tout composant d'un système technique.
    Tout fichier système importé doit définir des sous-classes de Component.
    """

    def __init__(self, name: str):
        self.name: str = name
        self.is_operational: bool = True
        self.outputs: Dict[str, float] = {}   # Grandeurs physiques mesurables
        self.sensors: List["Sensor"] = []     # Capteurs attachés

    @abstractmethod
    def update_state(self, dt: float, t: float) -> None:
        """Met à jour l'état interne du composant à chaque pas de temps."""

    def add_sensor(self, sensor: "Sensor") -> None:
        """Attache un capteur à ce composant."""
        if sensor not in self.sensors:
            self.sensors.append(sensor)
            sensor.component = self

    def remove_sensor(self, sensor: "Sensor") -> None:
        """Détache un capteur de ce composant."""
        if sensor in self.sensors:
            self.sensors.remove(sensor)
            sensor.component = None

    def __repr__(self) -> str:
        return f"Component(name='{self.name}', operational={self.is_operational})"
