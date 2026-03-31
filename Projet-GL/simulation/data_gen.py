# simulation/data_gen.py
"""Classe DataGen — génération d'un enregistrement de données à chaque pas."""
from typing import Any, Dict, List
from models.component import Component


class DataGen:
    """
    Échantillonne les sorties des composants et de leurs capteurs
    (avec anomalies éventuelles) à un instant t.
    """

    @staticmethod
    def sample(components: List[Component], t: float) -> Dict[str, Any]:
        """
        Construit un dictionnaire {nom_colonne: valeur} pour l'instant t.
        Les capteurs prennent priorité sur les sorties brutes du composant.
        """
        row: Dict[str, Any] = {"Temps_s": round(t, 4)}

        for comp in components:
            for out_name, out_val in comp.outputs.items():
                row[f"{comp.name}_{out_name}"] = round(float(out_val), 6)
            for sensor in comp.sensors:
                col = f"{comp.name}_{sensor.name}[{sensor.unit}]"
                row[col] = round(sensor.read(t), 6)

        return row
