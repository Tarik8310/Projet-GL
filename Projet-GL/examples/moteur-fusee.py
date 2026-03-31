# moteur-fusee.py
"""
Exemple de système technique : Moteur-fusée cryogénique (type Vulcain 2 — Ariane 5).
Ergols : LOX (oxygène liquide) + LH2 (hydrogène liquide).
Ce fichier est importable par GADMAPS via Fichier → Importer un système.

Chaque classe hérite de Component et définit :
  - self.outputs  : dict des grandeurs mesurables
  - update_state  : loi physique simplifiée mise à jour à chaque pas de temps
"""
import math
from models import Component


class AlimentationErgols(Component):
    """Système d'alimentation en ergols cryogéniques (LOX + LH2)."""

    def __init__(self):
        super().__init__("Alimentation en Ergols Cryogéniques")
        self.outputs = {
            "debit_LOX_kg_s":          0.0,
            "debit_LH2_kg_s":          0.0,
            "pression_alimentation_bar": 0.0,
            "temperature_LOX_C":       -183.0,
            "temperature_LH2_C":       -253.0,
        }

    def update_state(self, dt: float, t: float) -> None:
        # Séquence de mise à feu : montée en débit sur 4 s
        regime = min(1.0, t / 4.0)
        self.outputs["debit_LOX_kg_s"] = (
            239.0 * regime + 1.5 * math.sin(t * 1.0)
        )
        self.outputs["debit_LH2_kg_s"] = (
            40.0 * regime + 0.3 * math.sin(t * 1.2)
        )
        self.outputs["pression_alimentation_bar"] = (
            130.0 * regime + 2.0 * math.sin(t * 0.8)
        )
        # Légères remontées thermiques dues aux transferts de chaleur
        self.outputs["temperature_LOX_C"] = (
            -183.0 + 3.0 * regime + 0.5 * math.sin(t * 0.5)
        )
        self.outputs["temperature_LH2_C"] = (
            -253.0 + 2.0 * regime + 0.3 * math.sin(t * 0.6)
        )


class TurbopompeCryogenique(Component):
    """Turbopompe haute vitesse entraînant l'alimentation en ergols."""

    def __init__(self):
        super().__init__("Turbopompe Cryogénique")
        self.outputs = {
            "vitesse_rotation_rpm":     0.0,
            "puissance_mecanique_kW":   0.0,
            "temperature_paliers_C":    20.0,
        }

    def update_state(self, dt: float, t: float) -> None:
        regime = min(1.0, t / 4.0)
        self.outputs["vitesse_rotation_rpm"] = (
            34_000.0 * regime + 200.0 * math.sin(t * 2.0)
        )
        self.outputs["puissance_mecanique_kW"] = (
            11_000.0 * regime + 50.0 * math.sin(t * 1.5)
        )
        # Les paliers s'échauffent légèrement même à cryogénie
        self.outputs["temperature_paliers_C"] = (
            -200.0 + 220.0 * regime + 3.0 * math.sin(t * 1.0)
        )


class ChambreCombustionFusee(Component):
    """Chambre de combustion régénérative (LOX/LH2, Isp ≈ 431 s)."""

    def __init__(self):
        super().__init__("Chambre de Combustion")
        self.outputs = {
            "temperature_combustion_C": 20.0,
            "pression_chambre_bar":      0.0,
            "richesse_ergols":           0.0,
        }

    def update_state(self, dt: float, t: float) -> None:
        regime = min(1.0, t / 4.5)
        self.outputs["temperature_combustion_C"] = (
            3_500.0 * regime + 30.0 * math.sin(t * 0.7)
        )
        self.outputs["pression_chambre_bar"] = (
            115.0 * regime + 1.5 * math.sin(t * 0.9)
        )
        # Rapport de mélange LOX/LH2 ≈ 5.9 → richesse ~0.97
        self.outputs["richesse_ergols"] = (
            0.97 + 0.02 * math.sin(t * 0.4)
        )


class TuyereExpansion(Component):
    """Tuyère de Laval à grand rapport d'expansion (type spatiale)."""

    def __init__(self):
        super().__init__("Tuyère d'Expansion")
        self.outputs = {
            "poussee_kN":          0.0,
            "vitesse_ejection_m_s": 0.0,
            "pression_sortie_bar":  0.0,
            "temperature_col_C":    20.0,
        }

    def update_state(self, dt: float, t: float) -> None:
        regime = min(1.0, t / 5.0)
        self.outputs["poussee_kN"]           = (
            1_340.0 * regime + 8.0 * math.sin(t * 0.6)
        )
        self.outputs["vitesse_ejection_m_s"] = (
            4_230.0 * regime + 20.0 * math.sin(t * 0.5)
        )
        # Pression à la sortie tuyère (quasi vide spatial)
        self.outputs["pression_sortie_bar"] = (
            0.0 + 0.3 * math.sin(t * 1.0) * regime
        )
        # Col de tuyère très chaud, refroidi par le LH2
        self.outputs["temperature_col_C"] = (
            800.0 * regime + 15.0 * math.sin(t * 1.2)
        )


class RefroidissementRegen(Component):
    """Refroidissement régénératif des parois chambre/tuyère par le LH2."""

    def __init__(self):
        super().__init__("Refroidissement Régénératif")
        self.outputs = {
            "temperature_paroi_entree_C":  -253.0,
            "temperature_paroi_sortie_C":  -253.0,
            "debit_refrigerant_kg_s":        0.0,
            "flux_thermique_MW_m2":          0.0,
        }

    def update_state(self, dt: float, t: float) -> None:
        regime = min(1.0, t / 4.0)
        self.outputs["debit_refrigerant_kg_s"] = (
            40.0 * regime + 0.3 * math.sin(t * 0.9)
        )
        self.outputs["temperature_paroi_entree_C"] = (
            -253.0 + 30.0 * regime + 1.0 * math.sin(t * 0.7)
        )
        self.outputs["temperature_paroi_sortie_C"] = (
            -253.0 + 280.0 * regime + 5.0 * math.sin(t * 0.8)
        )
        # Flux thermique typique LOX/LH2 : ~100 MW/m²
        self.outputs["flux_thermique_MW_m2"] = (
            100.0 * regime + 2.0 * math.sin(t * 1.1)
        )
