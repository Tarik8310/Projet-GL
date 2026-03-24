# fichier: moteur_f1.py
from models import Component

class PompeLOX(Component):
    def __init__(self):
        super().__init__("Pompe à Oxygène Liquide (LOX)")
        # On définit ce que ce composant peut sortir (pour y attacher des capteurs)
        self.outputs = {
            "pression_sortie": 0.0,
            "debit_massique": 0.0
        }

    def update_state(self, dt: float, t: float):
        # Loi physique simplifiée pour la pompe
        self.outputs["pression_sortie"] = 150.0  # bars
        self.outputs["debit_massique"] = 2000.0  # kg/s

class ChambrePoussee(Component):
    def __init__(self):
        super().__init__("Chambre de Poussée Principale")
        self.outputs = {
            "temperature_combustion": 0.0,
            "poussee_generee": 0.0
        }

    def update_state(self, dt: float, t: float):
        self.outputs["temperature_combustion"] = 3300.0 # °C