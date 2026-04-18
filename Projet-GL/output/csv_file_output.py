# output/csv_file_output.py
"""Classe CSVFileOutput — export des données de simulation en CSV."""
import csv
from typing import Any, Dict, List


class CSVFileOutput:
    """
    UC18 — Enregistrer les données de simulation.
    Exporte une liste de dictionnaires dans un fichier CSV.
    """

    def __init__(self, filepath: str):
        """
        Initialise l'exporteur avec le chemin de destination.

        :param filepath: Chemin complet du fichier CSV à créer.
        """
        self.filepath: str = filepath

    def write(self, data: List[Dict[str, Any]]) -> bool:
        """
        Écrit les données dans le fichier CSV.

        :param data: Liste de dictionnaires colonne → valeur à exporter.
        :return: True si l'export s'est déroulé sans erreur, False sinon.
        """
        if not data:
            print("[CSV] Aucune donnée à exporter.")
            return False
        try:
            with open(self.filepath, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=list(data[0].keys()))
                writer.writeheader()
                writer.writerows(data)
            print(f"[CSV] Export réussi : {self.filepath} ({len(data)} lignes)")
            return True
        except OSError as e:
            print(f"[CSV] Erreur d'export : {e}")
            return False

    @classmethod
    def export(cls, data: List[Dict[str, Any]], filepath: str) -> bool:
        """
        Raccourci d'export : instancie CSVFileOutput et écrit en une seule ligne.

        :param data: Liste de dictionnaires colonne → valeur.
        :param filepath: Chemin du fichier CSV de destination.
        :return: True si l'export réussit, False sinon.
        """
        return cls(filepath).write(data)
