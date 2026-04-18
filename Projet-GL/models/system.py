# models/system.py
"""Classe System — conteneur générique de composants."""
from typing import List, Optional
from models.component import Component
from models.sensor import Sensor


class System:
    """
    Système technique générique, composé de composants.

    Sert de conteneur principal pour les objets Component.
    Fournit des méthodes de gestion des composants et d'accès aux capteurs.
    """

    def __init__(self, name: str):
        """
        Initialise un système vide.

        :param name: Identifiant du système (généralement le nom du fichier importé).
        """
        self.name: str = name
        self.components: List[Component] = []

    def add_component(self, component: Component):
        """
        Ajoute un composant au système (sans doublon).

        :param component: Instance de Component à ajouter.
        """
        if component not in self.components:
            self.components.append(component)

    def remove_component(self, component: Component):
        """
        Supprime un composant et détache tous ses capteurs avant retrait.

        :param component: Instance de Component à retirer.
        """
        if component in self.components:
            for sensor in list(component.sensors):
                component.remove_sensor(sensor)
            self.components.remove(component)

    def get_component_by_name(self, name: str) -> Optional[Component]:
        """
        Retourne le composant dont le nom correspond, ou None.

        :param name: Nom du composant recherché.
        :return: Instance de Component correspondante, ou None si introuvable.
        """
        return next((c for c in self.components if c.name == name), None)

    def get_all_sensors(self) -> List[Sensor]:
        """
        Retourne la liste de tous les capteurs de tous les composants.

        :return: Liste aplatie des capteurs du système.
        """
        return [s for comp in self.components for s in comp.sensors]

    def __repr__(self) -> str:
        return f"System(name='{self.name}', {len(self.components)} composant(s))"
