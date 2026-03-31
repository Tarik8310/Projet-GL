# input/system_file_input.py
"""Classe SystemFileInput — chargement dynamique d'un système depuis un fichier Python."""
import importlib.util
import inspect
import os
import sys
from typing import List, Type

from models.component import Component
from models.system import System

# Racine du projet (dossier parent de input/)
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class SystemFileInput:
    """
    Charge un fichier Python contenant des sous-classes de Component
    et construit un objet System via introspection (importlib + inspect).

    Exemple
    -------
    system = SystemFileInput("moteur-f1.py").load()
    """

    def __init__(self, filepath: str):
        if not os.path.isfile(filepath):
            raise FileNotFoundError(f"Fichier introuvable : {filepath}")
        self.filepath: str = filepath
        self.module_name: str = (
            os.path.basename(filepath).replace("-", "_").replace(".py", "")
        )

    def load(self) -> System:
        """
        Importe le module et instancie chaque sous-classe concrète de Component.
        Lève ValueError si aucun composant concret n'est détecté.
        """
        # Garantit que les packages du projet (models, simulation…) sont importables
        # même si l'application est lancée depuis un répertoire différent.
        if _PROJECT_ROOT not in sys.path:
            sys.path.insert(0, _PROJECT_ROOT)

        spec = importlib.util.spec_from_file_location(self.module_name, self.filepath)
        if spec is None or spec.loader is None:
            raise ImportError(
                f"Impossible de créer un loader pour '{self.filepath}'.\n"
                "Vérifiez que le fichier est un module Python valide (.py)."
            )

        module = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(module)
        except SystemExit as exc:
            raise RuntimeError(
                f"Le fichier a appelé sys.exit() lors du chargement "
                f"(code={exc.code}). Retirez tout appel à sys.exit() du module."
            ) from None

        component_classes: List[Type[Component]] = [
            obj
            for _, obj in inspect.getmembers(module, inspect.isclass)
            if (
                issubclass(obj, Component)
                and obj is not Component
                and not inspect.isabstract(obj)
            )
        ]

        if not component_classes:
            raise ValueError(
                f"Aucune sous-classe concrète de Component trouvée dans "
                f"'{self.filepath}'.\n"
                "Assurez-vous que vos classes héritent de Component et "
                "implémentent update_state()."
            )

        system = System(self.module_name)
        for cls in component_classes:
            system.add_component(cls())

        print(
            f"[Input] Système '{self.module_name}' chargé : "
            f"{len(system.components)} composant(s)"
        )
        return system
