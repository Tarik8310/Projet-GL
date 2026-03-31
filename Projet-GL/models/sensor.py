# models/sensor.py
"""Classe Sensor — capteur attaché à un composant."""
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from models.component import Component


class Sensor:
    """
    Capteur attaché à un composant.
    Lit une sortie spécifique du composant et applique les anomalies actives.
    """

    def __init__(
        self,
        name: str,
        target_output: str,
        unit: str = "-",
        frequency: float = 10.0,
    ):
        self.name: str = name
        self.target_output: str = target_output   # Clé dans component.outputs
        self.unit: str = unit
        self.frequency: float = frequency          # Hz
        self.component: Optional["Component"] = None
        self.anomalies: list = []                  # Liste d'objets Anomaly

    def read(self, t: float) -> float:
        """Lit la valeur brute et applique les anomalies actives au temps t."""
        if self.component is None or self.target_output not in self.component.outputs:
            return float("nan")
        value: float = self.component.outputs[self.target_output]
        for anomaly in self.anomalies:
            if anomaly.is_active(t):
                value = anomaly.apply(value, t)
        return value

    def add_anomaly(self, anomaly) -> None:
        self.anomalies.append(anomaly)

    def remove_anomaly(self, anomaly) -> None:
        if anomaly in self.anomalies:
            self.anomalies.remove(anomaly)

    def __repr__(self) -> str:
        return (
            f"Sensor('{self.name}' → '{self.target_output}', "
            f"unit='{self.unit}', freq={self.frequency} Hz)"
        )
