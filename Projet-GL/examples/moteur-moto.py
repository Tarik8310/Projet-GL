# moteur-moto.py
"""
Exemple de système technique : Moteur de moto (4-cylindres en ligne, 650 cc).
Ce fichier est importable par LambdaSys via Fichier → Importer un système.

Chaque classe hérite de Component et définit :
  - self.outputs  : dict des grandeurs mesurables
  - update_state  : loi physique simplifiée mise à jour à chaque pas de temps
"""
import math
from models import Component


class MoteurMoto(Component):
    """Bloc moteur 4-temps 4-cylindres en ligne (650 cc, ~95 ch)."""

    def __init__(self):
        super().__init__("Bloc Moteur 4 Cylindres")
        self.outputs = {
            "regime_tr_min":    0.0,
            "couple_Nm":        0.0,
            "puissance_kW":     0.0,
            "temperature_C":    20.0,
        }
        self._regime = 0.0

    def update_state(self, dt: float, t: float):
        # Montée en régime : ralenti à 1 200 tr/min puis accélération progressive
        if t < 3.0:
            cible = 1_200.0
        else:
            cible = 1_200.0 + 6_800.0 * min(1.0, (t - 3.0) / 10.0)

        self._regime += (cible - self._regime) * dt * 1.5
        self._regime = max(0.0, self._regime)

        # Couple maximal vers 7 000 tr/min (~63 Nm)
        ratio = self._regime / 10_500.0
        self.outputs["regime_tr_min"] = self._regime
        self.outputs["couple_Nm"]     = 63.0 * 4.0 * ratio * (1.0 - ratio) + \
                                         1.5 * math.sin(t * 3.0)
        self.outputs["puissance_kW"]  = (
            self.outputs["couple_Nm"] * self._regime * math.pi / 30_000.0
        )
        # Échauffement progressif jusqu'à 95 °C + micro-variations
        self.outputs["temperature_C"] = (
            20.0 + 75.0 * min(1.0, t / 60.0) + 1.2 * math.sin(t * 0.8)
        )


class Carburateur(Component):
    """Système d'injection/carburation (alimentation en carburant)."""

    def __init__(self):
        super().__init__("Système d'Injection")
        self.outputs = {
            "pression_alimentation_bar": 0.0,
            "debit_carburant_g_s":       0.0,
            "richesse":                  0.0,
        }

    def update_state(self, dt: float, t: float):
        regime = min(1.0, max(0.0, (t - 3.0) / 10.0))
        self.outputs["pression_alimentation_bar"] = (
            3.5 * min(1.0, t / 2.0) + 0.05 * math.sin(t * 5.0)
        )
        self.outputs["debit_carburant_g_s"] = (
            1.2 + 10.0 * regime + 0.1 * math.sin(t * 4.0)
        )
        # Richesse idéale ≈ 1.0 (stœchiométrique)
        self.outputs["richesse"] = 0.98 + 0.04 * math.sin(t * 0.3)


class SystemeRefroidissementMoto(Component):
    """Circuit de refroidissement liquide (radiateur + pompe à eau)."""

    def __init__(self):
        super().__init__("Circuit de Refroidissement")
        self.outputs = {
            "temperature_liquide_C":  20.0,
            "debit_pompe_L_min":       0.0,
            "temperature_radiateur_C": 20.0,
        }

    def update_state(self, dt: float, t: float):
        regime = min(1.0, t / 5.0)
        self.outputs["debit_pompe_L_min"] = (
            25.0 * regime + 0.8 * math.sin(t * 1.2)
        )
        # Température du liquide suit la montée en charge du moteur
        self.outputs["temperature_liquide_C"] = (
            20.0 + 70.0 * min(1.0, t / 50.0) + 1.5 * math.sin(t * 0.6)
        )
        self.outputs["temperature_radiateur_C"] = (
            self.outputs["temperature_liquide_C"] - 8.0
            + 0.5 * math.sin(t * 0.9)
        )


class EchappementMoto(Component):
    """Ligne d'échappement (collecteur + silencieux)."""

    def __init__(self):
        super().__init__("Ligne d'Échappement")
        self.outputs = {
            "temperature_gaz_C":       20.0,
            "pression_echappement_bar": 1.0,
            "niveau_sonore_dB":         0.0,
        }

    def update_state(self, dt: float, t: float):
        regime = min(1.0, max(0.0, (t - 3.0) / 10.0))
        self.outputs["temperature_gaz_C"] = (
            100.0 + 550.0 * regime + 10.0 * math.sin(t * 1.5)
        )
        self.outputs["pression_echappement_bar"] = (
            1.0 + 0.6 * regime + 0.02 * math.sin(t * 6.0)
        )
        self.outputs["niveau_sonore_dB"] = (
            60.0 + 35.0 * regime + 3.0 * math.sin(t * 2.0)
        )
