# simulation.py

class SimulationEngine:
    def __init__(self, composants, duree_totale=10.0, pas_de_temps=0.1):
        self.composants = composants
        self.duree_totale = duree_totale
        self.pas_de_temps = pas_de_temps
        self.temps_actuel = 0.0
        self.historique_donnees = []  # Va stocker toutes nos lignes de données

    def run(self):
        """Lance la boucle de simulation."""
        print(f"--- Début de la simulation (Durée: {self.duree_totale}s, Pas: {self.pas_de_temps}s) ---")
        self.temps_actuel = 0.0
        self.historique_donnees.clear()

        # Boucle temporelle principale
        while self.temps_actuel <= self.duree_totale:
            # 1. On prépare la ligne de données pour cet instant t
            donnees_instant_t = {"Temps_s": round(self.temps_actuel, 3)}

            # 2. On met à jour chaque composant et on lit ses capteurs
            for comp in self.composants:
                comp.update_state(self.pas_de_temps, self.temps_actuel)
                
                # Si le composant a des sorties (capteurs), on les enregistre
                if hasattr(comp, 'outputs'):
                    for nom_capteur, valeur in comp.outputs.items():
                        # On crée un nom de colonne clair (ex: "Pompe_pression_sortie")
                        nom_colonne = f"{comp.name}_{nom_capteur}"
                        donnees_instant_t[nom_colonne] = valeur

            # 3. On sauvegarde la ligne et on avance le temps
            self.historique_donnees.append(donnees_instant_t)
            self.temps_actuel += self.pas_de_temps

        print(f"--- Simulation terminée : {len(self.historique_donnees)} points générés ---")
        return self.historique_donnees