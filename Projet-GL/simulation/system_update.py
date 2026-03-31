# simulation/system_update.py
"""Classe SystemUpdate — mise à jour des composants à chaque pas de temps."""
from typing import List
from models.component import Component


class SystemUpdate:
    """Met à jour l'état de tous les composants opérationnels du système."""

    @staticmethod
    def update(components: List[Component], dt: float, t: float) -> None:
        """Appelle update_state() sur chaque composant opérationnel."""
        for comp in components:
            if comp.is_operational:
                comp.update_state(dt, t)
