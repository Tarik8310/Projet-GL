# moteur-voiture.py
"""
Exemple de système technique : Moteur de voiture thermique (2.0 T, ~180 kW).
Ce fichier est importable par LambdaSys via Fichier → Importer un système.

Chaque classe hérite de Component et définit :
  - self.outputs  : dict des grandeurs mesurables
  - update_state  : loi physique simplifiée mise à jour à chaque pas de temps
"""
import math
from models import Component


class MoteurThermique(Component):
    """Bloc moteur 4-cylindres 2.0 L turbocompressé (~180 kW / 350 Nm)."""

    def __init__(self):
        super().__init__("Bloc Moteur 4 Cylindres 2.0T")
        self.outputs = {
            "regime_tr_min":    0.0,
            "couple_Nm":        0.0,
            "puissance_kW":     0.0,
            "temperature_C":    20.0,
            "pression_huile_bar": 0.0,
        }
        self._regime = 0.0

    def update_state(self, dt: float, t: float) -> None:
        # Démarrage → ralenti 850 tr/min, puis montée en régime
        if t < 2.0:
            cible = 850.0 * min(1.0, t / 1.0)
        else:
            cible = 850.0 + 5_650.0 * min(1.0, (t - 2.0) / 15.0)

        self._regime += (cible - self._regime) * dt * 1.2
        self._regime = max(0.0, self._regime)

        # Couple plat entre 1 800 et 5 000 tr/min (~350 Nm)
        n = self._regime
        if n < 1_500.0:
            couple = 200.0 * (n / 1_500.0)
        elif n < 5_000.0:
            couple = 350.0
        else:
            couple = 350.0 * max(0.0, 1.0 - (n - 5_000.0) / 1_500.0)

        self.outputs["regime_tr_min"]    = n
        self.outputs["couple_Nm"]        = couple + 3.0 * math.sin(t * 2.5)
        self.outputs["puissance_kW"]     = couple * n * math.pi / 30_000.0
        self.outputs["temperature_C"]    = (
            20.0 + 75.0 * min(1.0, t / 120.0) + 1.0 * math.sin(t * 0.5)
        )
        self.outputs["pression_huile_bar"] = (
            1.5 + 3.0 * min(1.0, n / 3_000.0) + 0.1 * math.sin(t * 1.5)
        )


class SystemeInjection(Component):
    """Rail d'injection directe haute pression (common rail)."""

    def __init__(self):
        super().__init__("Injection Directe Haute Pression")
        self.outputs = {
            "pression_rail_bar":    0.0,
            "debit_carburant_g_s":  0.0,
            "richesse":             1.0,
        }

    def update_state(self, dt: float, t: float) -> None:
        charge = min(1.0, max(0.0, (t - 2.0) / 15.0))
        # Pression rail montée rapide dès démarrage (200 → 2 000 bar)
        self.outputs["pression_rail_bar"] = (
            200.0 + 1_800.0 * min(1.0, t / 3.0) + 5.0 * math.sin(t * 3.0)
        )
        self.outputs["debit_carburant_g_s"] = (
            0.5 + 14.0 * charge + 0.2 * math.sin(t * 4.0)
        )
        # Richesse légèrement variable autour de la stœchiométrie
        self.outputs["richesse"] = 1.0 + 0.03 * math.sin(t * 0.7)


class TurboCompresseur(Component):
    """Turbocompresseur (compresseur centrifuge + turbine d'échappement)."""

    def __init__(self):
        super().__init__("Turbocompresseur")
        self.outputs = {
            "pression_suralimentation_bar": 1.0,
            "temperature_air_admis_C":      20.0,
            "vitesse_turbine_tr_min":        0.0,
            "temperature_turbine_C":         20.0,
        }

    def update_state(self, dt: float, t: float) -> None:
        # Le turbo monte en pression à partir de ~1 800 tr/min moteur (t>5 s)
        boost = min(1.0, max(0.0, (t - 5.0) / 8.0))
        self.outputs["pression_suralimentation_bar"] = (
            1.0 + 0.8 * boost + 0.02 * math.sin(t * 5.0)
        )
        # L'air est échauffé par la compression (+50 °C max)
        self.outputs["temperature_air_admis_C"] = (
            20.0 + 50.0 * boost + 2.0 * math.sin(t * 1.0)
        )
        self.outputs["vitesse_turbine_tr_min"] = (
            180_000.0 * boost + 500.0 * math.sin(t * 2.0)
        )
        self.outputs["temperature_turbine_C"] = (
            100.0 + 650.0 * boost + 10.0 * math.sin(t * 0.8)
        )


class SystemeRefroidissementVoiture(Component):
    """Circuit de refroidissement moteur (pompe à eau, radiateur, thermostat)."""

    def __init__(self):
        super().__init__("Circuit de Refroidissement")
        self.outputs = {
            "temperature_liquide_C":   20.0,
            "debit_pompe_L_min":        0.0,
            "pression_circuit_bar":     0.0,
            "temperature_radiateur_C":  20.0,
        }

    def update_state(self, dt: float, t: float) -> None:
        charge = min(1.0, t / 8.0)
        self.outputs["debit_pompe_L_min"]   = (
            40.0 * charge + 2.0 * math.sin(t * 1.3)
        )
        self.outputs["pression_circuit_bar"] = (
            1.2 + 0.6 * charge + 0.05 * math.sin(t * 2.0)
        )
        # Thermostat s'ouvre à 90 °C : stabilisation vers 95 °C
        self.outputs["temperature_liquide_C"] = (
            20.0 + 75.0 * min(1.0, t / 180.0) + 1.5 * math.sin(t * 0.4)
        )
        self.outputs["temperature_radiateur_C"] = (
            self.outputs["temperature_liquide_C"] - 10.0
            + 1.0 * math.sin(t * 0.6)
        )
