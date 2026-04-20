# systeme-invalide.py
# Ce fichier est volontairement invalide pour LambdaSys :
# la classe ci-dessous n'hérite pas de Component.
# L'importation déclenchera une ValueError dans SystemFileInput.

class MoteurBidon:
    def __init__(self):
        self.outputs = {"temperature_C": 90.0}

    def update_state(self, dt, t):
        pass
