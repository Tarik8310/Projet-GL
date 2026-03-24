# models.py
from abc import ABC, abstractmethod

class Component(ABC):
    """Classe mère générique pour tous les composants du système."""
    def __init__(self, name: str):
        self.name = name
        self.is_operational = True

    @abstractmethod
    def update_state(self, dt: float, t: float):
        pass
