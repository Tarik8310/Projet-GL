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
        self.filepath: str = filepath

    def write(self, data: List[Dict[str, Any]]) -> bool:
        """Écrit les données dans le fichier CSV. Retourne True si succès."""
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
        """Raccourci : instancie et écrit en une seule ligne."""
        return cls(filepath).write(data)
