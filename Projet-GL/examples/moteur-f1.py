# moteur-f1.py
"""
Exemple de système technique : Moteur-fusée F1.
Ce fichier est importable par LambdaSys via Fichier → Importer un système.

Chaque classe hérite de Component et définit :
  - self.outputs  : dict des grandeurs mesurables
  - update_state  : loi physique simplifiée mise à jour à chaque pas de temps
"""
import math
from models import Component


class PompeLOX(Component):
    """Pompe à oxygène liquide (LOX)."""

    def __init__(self):
        super().__init__("Pompe à Oxygène Liquide (LOX)")
        self.outputs = {
            "pression_sortie_bar": 0.0,
            "debit_massique_kg_s": 0.0,
            "temperature_C": 0.0,
        }
        self._vitesse_rotation = 0.0   # tr/min interne

    def update_state(self, dt: float, t: float) -> None:
        # Montée en régime progressive sur les 2 premières secondes
        regime = min(1.0, t / 2.0)
        self._vitesse_rotation = 30_000 * regime

        self.outputs["pression_sortie_bar"] = 150.0 * regime
        self.outputs["debit_massique_kg_s"] = 2_000.0 * regime
        # Légère variation thermique sinusoïdale
        self.outputs["temperature_C"] = -183.0 + 5.0 * math.sin(t * 0.5)


class PompeRP1(Component):
    """Pompe à kérosène (RP-1)."""

    def __init__(self):
        super().__init__("Pompe Kérosène (RP-1)")
        self.outputs = {
            "pression_sortie_bar": 0.0,
            "debit_massique_kg_s": 0.0,
        }

    def update_state(self, dt: float, t: float) -> None:
        regime = min(1.0, t / 2.0)
        self.outputs["pression_sortie_bar"] = 140.0 * regime
        self.outputs["debit_massique_kg_s"] = 900.0 * regime


class ChambrePoussee(Component):
    """Chambre de combustion et tuyère de poussée principale."""

    def __init__(self):
        super().__init__("Chambre de Poussée Principale")
        self.outputs = {
            "temperature_combustion_C": 0.0,
            "poussee_kN": 0.0,
            "pression_chambre_bar": 0.0,
        }

    def update_state(self, dt: float, t: float) -> None:
        regime = min(1.0, t / 2.5)
        self.outputs["temperature_combustion_C"] = 3_300.0 * regime
        self.outputs["poussee_kN"] = 6_770.0 * regime
        self.outputs["pression_chambre_bar"] = 70.0 * regime


class TurbopompeGaz(Component):
    """Turbine à gaz chaud entraînant les deux pompes."""

    def __init__(self):
        super().__init__("Turbopompe à Gaz Chaud")
        self.outputs = {
            "vitesse_rotation_rpm": 0.0,
            "temperature_gaz_entree_C": 0.0,
        }

    def update_state(self, dt: float, t: float) -> None:
        regime = min(1.0, t / 2.0)
        self.outputs["vitesse_rotation_rpm"] = 36_000.0 * regime
        # Petites oscillations thermiques simulées
        self.outputs["temperature_gaz_entree_C"] = (
            700.0 * regime + 10.0 * math.sin(t * 2.0)
        )
