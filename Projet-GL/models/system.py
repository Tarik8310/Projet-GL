# models/system.py
"""Classe System — conteneur générique de composants."""
from typing import List, Optional
from models.component import Component
from models.sensor import Sensor


class System:
    """Système technique générique, composé de composants."""

    def __init__(self, name: str):
        self.name: str = name
        self.components: List[Component] = []

    def add_component(self, component: Component) -> None:
        if component not in self.components:
            self.components.append(component)

    def remove_component(self, component: Component) -> None:
        if component in self.components:
            for sensor in list(component.sensors):
                component.remove_sensor(sensor)
            self.components.remove(component)

    def get_component_by_name(self, name: str) -> Optional[Component]:
        return next((c for c in self.components if c.name == name), None)

    def get_all_sensors(self) -> List[Sensor]:
        return [s for comp in self.components for s in comp.sensors]

    def __repr__(self) -> str:
        return f"System(name='{self.name}', {len(self.components)} composant(s))"
