# simulation/anomaly.py
"""Classe Anomaly — anomalie injectable dans un composant."""
import random
from enum import Enum


class AnomalyType(str, Enum):
    """Catalogue des types d'anomalies disponibles."""
    SPIKE = "Pic (Spike)"
    DRIFT = "Dérive (Drift)"
    NOISE = "Bruit (Noise)"
    STUCK = "Valeur bloquée (Stuck)"


class AnomalyMode(str, Enum):
    """Mode d'application de la magnitude."""
    ABSOLUTE = "Absolue"
    RELATIVE = "Relative (%)"


class Anomaly:
    """
    Anomalie injectable dans un composant pour la génération de données anormales.
    Affecte toutes les sorties (outputs) du composant, simulant une défaillance
    physique globale plutôt qu'une erreur de mesure isolée.

    Paramètres
    ----------
    name          : identifiant de l'anomalie
    anomaly_type  : catégorie (AnomalyType)
    start_time    : instant d'activation en secondes
    duration      : durée de l'anomalie en secondes
    magnitude     : amplitude de la perturbation
    mode          : Absolue (unité brute) ou Relative (% de la valeur nominale)
    """

    def __init__(
        self,
        name: str,
        anomaly_type: AnomalyType,
        start_time: float,
        duration: float,
        magnitude: float,
        mode: AnomalyMode = AnomalyMode.ABSOLUTE,
    ):
        """
        Initialise une anomalie injectable.

        :param name: Identifiant de l'anomalie.
        :param anomaly_type: Catégorie de l'anomalie (AnomalyType).
        :param start_time: Instant d'activation en secondes.
        :param duration: Durée de l'anomalie en secondes.
        :param magnitude: Amplitude de la perturbation.
        :param mode: Mode d'interprétation de la magnitude (absolu ou relatif).
        """
        self.name: str = name
        self.anomaly_type: AnomalyType = anomaly_type
        self.start_time: float = start_time
        self.duration: float = duration
        self.magnitude: float = magnitude
        self.mode: AnomalyMode = mode
        # Pour STUCK : une valeur gelée par clé de sortie (output_name → valeur)
        self._stuck_values: dict = {}

    def is_active(self, t: float) -> bool:
        """
        Retourne True si l'anomalie est active au temps t.

        :param t: Instant courant de la simulation en secondes.
        :return: True si start_time ≤ t ≤ start_time + duration.
        """
        return self.start_time <= t <= (self.start_time + self.duration)

    def apply(self, value: float, t: float, key: str = "_default") -> float:
        """
        Applique la perturbation à la valeur nominale d'une sortie.

        En mode Relatif, la magnitude est interprétée comme un pourcentage
        de la valeur nominale (ex: 20 → ±20 % de value).
        En mode Absolu, la magnitude est une valeur brute dans l'unité de la sortie.

        key : identifiant de la sortie (pour que STUCK gèle chaque sortie
              indépendamment).
        """
        # Calcul du delta selon le mode
        if self.mode == AnomalyMode.RELATIVE:
            delta = value * (self.magnitude / 100.0)
        else:
            delta = self.magnitude

        if self.anomaly_type == AnomalyType.SPIKE:
            return value + delta

        if self.anomaly_type == AnomalyType.DRIFT:
            ratio = (t - self.start_time) / self.duration if self.duration > 0 else 1.0
            return value + delta * ratio

        if self.anomaly_type == AnomalyType.NOISE:
            return value + random.gauss(0.0, abs(delta))

        if self.anomaly_type == AnomalyType.STUCK:
            # STUCK : gèle la valeur au premier appel, ignore delta
            if key not in self._stuck_values:
                self._stuck_values[key] = value
            return self._stuck_values[key]

        return value

    def reset(self):
        """Réinitialise les valeurs STUCK mémorisées (à appeler avant chaque simulation)."""
        self._stuck_values = {}

    @classmethod
    def create_random(cls, name: str, total_duration: float) -> "Anomaly":
        """Génère une anomalie avec des paramètres aléatoires."""
        mode = random.choice(list(AnomalyMode))
        if mode == AnomalyMode.RELATIVE:
            magnitude = round(random.uniform(5.0, 50.0), 2)
        else:
            magnitude = round(random.uniform(10.0, 150.0), 2)
        return cls(
            name=name,
            anomaly_type=random.choice(list(AnomalyType)),
            start_time=round(random.uniform(0.0, total_duration * 0.65), 2),
            duration=round(random.uniform(0.5, max(0.5, total_duration * 0.25)), 2),
            magnitude=magnitude,
            mode=mode,
        )

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "type": self.anomaly_type.value,
            "mode": self.mode.value,
            "start_time": self.start_time,
            "duration": self.duration,
            "magnitude": self.magnitude,
        }

    def __repr__(self) -> str:
        return (
            f"Anomaly('{self.name}', {self.anomaly_type.value}, {self.mode.value}, "
            f"t={self.start_time}s, dur={self.duration}s, mag={self.magnitude})"
        )
