# simulation/data_gen.py
"""Classe DataGen — génération d'un enregistrement de données à chaque pas."""
from typing import Any, Dict, List
from models.component import Component


class DataGen:
    """
    Échantillonne les sorties des composants et de leurs capteurs à un instant t.

    Comportements :
    - Les anomalies portées par le composant sont appliquées sur les valeurs
      nominales sans modifier comp.outputs en place (le prochain update_state
      repart toujours de l'état physique réel).
    - Chaque capteur est échantillonné à sa propre fréquence (sample-and-hold
      entre deux instants d'échantillonnage).
    - Une colonne binaire <Composant>_anomalie est ajoutée pour chaque composant,
      indiquant si au moins une anomalie est active à l'instant t (label IA).
    """

    @staticmethod
    def sample(components: List[Component], t: float) -> Dict[str, Any]:
        """
        Construit un dictionnaire ``{nom_colonne: valeur}`` pour l'instant t.

        Pour chaque composant :
        - les sorties nominales sont perturbées par les anomalies actives ;
        - une colonne binaire ``<Composant>_anomalie`` signale l'activité ;
        - les capteurs sont lus à leur fréquence propre (sample-and-hold).

        :param components: Liste des composants du système.
        :param t: Instant courant de la simulation (en secondes).
        :return: Dictionnaire colonne → valeur prêt à être enregistré.
        """
        row: Dict[str, Any] = {"Temps_s": round(t, 4)}

        for comp in components:
            # --- Valeurs nominales perturbées par les anomalies actives ---
            affected: Dict[str, float] = {}
            anomaly_active = False
            for out_name, out_val in comp.outputs.items():
                val = float(out_val)
                for anomaly in comp.anomalies:
                    if anomaly.is_active(t):
                        anomaly_active = True
                        val = anomaly.apply(val, t, out_name)
                affected[out_name] = val

            # --- Colonnes des sorties brutes perturbées ---
            for out_name, val in affected.items():
                row[f"{comp.name}_{out_name}"] = round(val, 6)

            # --- Label binaire pour l'entraînement IA ---
            row[f"{comp.name}_anomalie"] = int(anomaly_active)

            # --- Colonnes des capteurs (fréquence respectée, sample-and-hold) ---
            for sensor in comp.sensors:
                col = f"{comp.name}_{sensor.name}[{sensor.unit}]"
                if sensor.should_sample(t):
                    sensor._last_value = affected.get(
                        sensor.target_output, float("nan")
                    )
                row[col] = round(sensor._last_value, 6)

        return row
