# models/sensor.py
"""Classe Sensor — capteur attaché à un composant."""
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from models.component import Component


class Sensor:
    """
    Capteur attaché à un composant.
    Lit une sortie spécifique du composant à la fréquence configurée.
    Les anomalies sont portées par le composant et appliquées lors de
    l'échantillonnage dans DataGen.

    Entre deux instants d'échantillonnage, la dernière valeur mesurée est
    conservée (comportement sample-and-hold).
    """

    def __init__(
        self,
        name: str,
        target_output: str,
        unit: str = "-",
        frequency: float = 10.0,
    ):
        """
        Initialise le capteur sans composant associé.

        :param name: Identifiant du capteur.
        :param target_output: Clé dans ``component.outputs`` à mesurer.
        :param unit: Unité physique affichée (ex : 'bar', '°C').
        :param frequency: Fréquence d'échantillonnage en Hz.
        """
        self.name: str = name
        self.target_output: str = target_output   # Clé dans component.outputs
        self.unit: str = unit
        self.frequency: float = frequency          # Hz
        self.component: Optional["Component"] = None

        # État interne d'échantillonnage
        self._last_value: float = float("nan")
        self._next_sample_t: float = 0.0

    def should_sample(self, t: float) -> bool:
        """
        Détermine si le capteur doit être échantillonné à l'instant t.

        Met à jour l'instant du prochain échantillonnage si True est retourné.
        Si la fréquence est supérieure à celle de la simulation (1/dt),
        le capteur est échantillonné à chaque pas de temps.

        :param t: Instant courant de la simulation en secondes.
        :return: True si une nouvelle mesure doit être prise.
        """
        if self.frequency <= 0:
            return False
        if t >= self._next_sample_t - 1e-9:
            period = 1.0 / self.frequency
            self._next_sample_t = t + period
            return True
        return False

    def reset(self):
        """Réinitialise la valeur mémorisée et le prochain instant d'échantillonnage."""
        self._last_value = float("nan")
        self._next_sample_t = 0.0

    def __repr__(self) -> str:
        return (
            f"Sensor('{self.name}' → '{self.target_output}', "
            f"unit='{self.unit}', freq={self.frequency} Hz)"
        )
