# simulation/anomaly.py
"""Classe Anomaly — anomalie injectable dans un capteur."""
import random
from enum import Enum
from typing import Optional


class AnomalyType(str, Enum):
    """Catalogue des types d'anomalies disponibles."""
    SPIKE = "Pic (Spike)"
    DRIFT = "Dérive (Drift)"
    NOISE = "Bruit (Noise)"
    STUCK = "Valeur bloquée (Stuck)"


class Anomaly:
    """
    Anomalie injectable dans un capteur pour la génération de données anormales.

    Paramètres
    ----------
    name          : identifiant de l'anomalie
    anomaly_type  : catégorie (AnomalyType)
    start_time    : instant d'activation en secondes
    duration      : durée de l'anomalie en secondes
    magnitude     : amplitude de la perturbation
    """

    def __init__(
        self,
        name: str,
        anomaly_type: AnomalyType,
        start_time: float,
        duration: float,
        magnitude: float,
    ):
        self.name: str = name
        self.anomaly_type: AnomalyType = anomaly_type
        self.start_time: float = start_time
        self.duration: float = duration
        self.magnitude: float = magnitude
        self._stuck_value: Optional[float] = None

    def is_active(self, t: float) -> bool:
        """Retourne True si l'anomalie est active au temps t."""
        return self.start_time <= t <= (self.start_time + self.duration)

    def apply(self, value: float, t: float) -> float:
        """Applique la perturbation à la valeur nominale."""
        if self.anomaly_type == AnomalyType.SPIKE:
            return value + self.magnitude

        if self.anomaly_type == AnomalyType.DRIFT:
            ratio = (t - self.start_time) / self.duration if self.duration > 0 else 1.0
            return value + self.magnitude * ratio

        if self.anomaly_type == AnomalyType.NOISE:
            return value + random.gauss(0.0, abs(self.magnitude))

        if self.anomaly_type == AnomalyType.STUCK:
            if self._stuck_value is None:
                self._stuck_value = value
            return self._stuck_value

        return value

    def reset(self) -> None:
        """Réinitialise l'état interne (à appeler avant chaque simulation)."""
        self._stuck_value = None

    @classmethod
    def create_random(cls, name: str, total_duration: float) -> "Anomaly":
        """UC34 — Génère une anomalie avec des paramètres aléatoires."""
        return cls(
            name=name,
            anomaly_type=random.choice(list(AnomalyType)),
            start_time=round(random.uniform(0.0, total_duration * 0.65), 2),
            duration=round(random.uniform(0.5, max(0.5, total_duration * 0.25)), 2),
            magnitude=round(random.uniform(10.0, 150.0), 2),
        )

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "type": self.anomaly_type.value,
            "start_time": self.start_time,
            "duration": self.duration,
            "magnitude": self.magnitude,
        }

    def __repr__(self) -> str:
        return (
            f"Anomaly('{self.name}', {self.anomaly_type.value}, "
            f"t={self.start_time}s, dur={self.duration}s, mag={self.magnitude})"
        )
