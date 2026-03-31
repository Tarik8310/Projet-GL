# voiture-electrique.py
"""
Exemple de système technique : Voiture électrique à batterie (type berline ~250 kW).
Ce fichier est importable par GADMAPS via Fichier → Importer un système.

Chaque classe hérite de Component et définit :
  - self.outputs  : dict des grandeurs mesurables
  - update_state  : loi physique simplifiée mise à jour à chaque pas de temps
"""
import math
from models import Component


class MoteurElectrique(Component):
    """Moteur synchrone à aimants permanents (MSAP) — traction principale."""

    def __init__(self):
        super().__init__("Moteur Électrique (MSAP)")
        self.outputs = {
            "vitesse_tr_min":   0.0,
            "couple_Nm":        0.0,
            "puissance_kW":     0.0,
            "temperature_C":    25.0,
            "efficacite_pct":   0.0,
        }
        self._vitesse = 0.0

    def update_state(self, dt: float, t: float) -> None:
        # Accélération franche sur 8 s puis régime de croisière
        if t < 8.0:
            cible = 7_000.0 * (t / 8.0)
        else:
            cible = 7_000.0 - 2_000.0 * min(1.0, (t - 8.0) / 5.0)

        self._vitesse += (cible - self._vitesse) * dt * 1.8
        self._vitesse = max(0.0, self._vitesse)

        n = self._vitesse
        # Couple maximal (400 Nm) à basse vitesse, puis décroissance
        if n < 4_000.0:
            couple = 400.0
        else:
            couple = 400.0 * (4_000.0 / n)

        self.outputs["vitesse_tr_min"] = n
        self.outputs["couple_Nm"]      = couple + 2.0 * math.sin(t * 3.0)
        self.outputs["puissance_kW"]   = couple * n * math.pi / 30_000.0
        # Échauffement modéré du moteur électrique
        self.outputs["temperature_C"]  = (
            25.0 + 55.0 * min(1.0, t / 60.0) + 1.0 * math.sin(t * 0.8)
        )
        # Rendement élevé (~94 %) hors décollage
        self.outputs["efficacite_pct"] = (
            94.0 - 10.0 * math.exp(-t / 3.0) + 0.5 * math.sin(t * 1.5)
        )


class BatterieHauteTension(Component):
    """Pack batterie haute tension lithium-ion (400 V / ~80 kWh)."""

    def __init__(self):
        super().__init__("Pack Batterie Haute Tension")
        self.outputs = {
            "tension_V":              400.0,
            "courant_A":               0.0,
            "puissance_W":             0.0,
            "temperature_C":           25.0,
            "etat_de_charge_pct":      90.0,
        }
        self._soc = 90.0          # State of Charge en %
        self._capacite_Wh = 80_000.0

    def update_state(self, dt: float, t: float) -> None:
        charge = min(1.0, max(0.0, t / 8.0))
        # Courant de décharge fort à l'accélération, réduit en croisière
        if t < 8.0:
            courant = 400.0 * charge
        else:
            courant = 180.0 * (1.0 - 0.5 * min(1.0, (t - 8.0) / 5.0))

        courant += 5.0 * math.sin(t * 2.0)
        tension  = 400.0 - 20.0 * (courant / 400.0) + 0.5 * math.sin(t * 0.4)

        # Décharge progressive du SOC
        puissance_W = tension * courant
        energie_Wh  = puissance_W * dt / 3_600.0
        self._soc   = max(0.0, self._soc - energie_Wh / self._capacite_Wh * 100.0)

        self.outputs["tension_V"]           = tension
        self.outputs["courant_A"]           = courant
        self.outputs["puissance_W"]         = puissance_W
        self.outputs["temperature_C"]       = (
            25.0 + 15.0 * min(1.0, t / 90.0) + 0.5 * math.sin(t * 0.6)
        )
        self.outputs["etat_de_charge_pct"]  = self._soc


class Onduleur(Component):
    """Onduleur DC/AC (convertisseur de puissance batterie → moteur)."""

    def __init__(self):
        super().__init__("Onduleur DC/AC")
        self.outputs = {
            "puissance_sortie_kW":  0.0,
            "temperature_C":        25.0,
            "efficacite_pct":       0.0,
            "frequence_commutation_kHz": 8.0,
        }

    def update_state(self, dt: float, t: float) -> None:
        charge = min(1.0, max(0.0, t / 8.0))
        puissance = 250.0 * charge * (1.0 - 0.3 * min(1.0, (t - 8.0) / 5.0))
        puissance = max(0.0, puissance)

        self.outputs["puissance_sortie_kW"] = (
            puissance + 1.0 * math.sin(t * 2.5)
        )
        # Échauffement des IGBT / SiC
        self.outputs["temperature_C"] = (
            25.0 + 45.0 * min(1.0, t / 40.0) + 1.5 * math.sin(t * 1.0)
        )
        self.outputs["efficacite_pct"] = (
            97.5 - 5.0 * math.exp(-t / 2.0) + 0.3 * math.sin(t * 1.8)
        )
        # Fréquence de commutation légèrement variable
        self.outputs["frequence_commutation_kHz"] = (
            8.0 + 0.1 * math.sin(t * 0.5)
        )


class GestionThermiqueBatterie(Component):
    """Système de gestion thermique de la batterie (BTMS — refroidissement liquide)."""

    def __init__(self):
        super().__init__("Gestion Thermique Batterie (BTMS)")
        self.outputs = {
            "temperature_liquide_C":    25.0,
            "debit_pompe_L_min":         0.0,
            "puissance_compresseur_W":   0.0,
            "delta_T_batterie_C":        0.0,
        }

    def update_state(self, dt: float, t: float) -> None:
        charge = min(1.0, t / 10.0)
        # La pompe démarre dès que la batterie se charge
        self.outputs["debit_pompe_L_min"] = (
            12.0 * charge + 0.5 * math.sin(t * 1.2)
        )
        self.outputs["temperature_liquide_C"] = (
            25.0 + 10.0 * min(1.0, t / 120.0) + 0.5 * math.sin(t * 0.7)
        )
        # Le compresseur du climatiseur refroidit le circuit batterie
        self.outputs["puissance_compresseur_W"] = (
            800.0 * charge + 20.0 * math.sin(t * 0.9)
        )
        # Différentiel de température entre entrée et sortie du module
        self.outputs["delta_T_batterie_C"] = (
            5.0 * charge + 0.3 * math.sin(t * 1.5)
        )


class ChargeurEmbarque(Component):
    """Chargeur embarqué AC/DC (OBC — On-Board Charger, 11 kW AC)."""

    def __init__(self):
        super().__init__("Chargeur Embarqué (OBC)")
        self.outputs = {
            "puissance_chargee_kW":  0.0,
            "tension_sortie_V":      0.0,
            "courant_sortie_A":      0.0,
            "temperature_C":         25.0,
            "efficacite_pct":        0.0,
        }

    def update_state(self, dt: float, t: float) -> None:
        # En roulage, le chargeur est inactif (simulation véhicule en déplacement)
        # Il se comporte comme un composant au repos avec légères variations
        self.outputs["puissance_chargee_kW"] = 0.0
        self.outputs["tension_sortie_V"]     = 0.0
        self.outputs["courant_sortie_A"]     = 0.0
        self.outputs["temperature_C"]        = (
            25.0 + 2.0 * math.sin(t * 0.3)
        )
        self.outputs["efficacite_pct"]       = 0.0
