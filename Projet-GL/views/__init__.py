# views/__init__.py
"""Package View — réexporte les classes publiques."""
from views.main_window_gui import MainWindowGUI
from views.properties_panel import PropertiesPanel
from views.simulation_panel import SimulationPanel
from views.data_panel import DataPanel
from views.sensor_dialog import SensorDialog
from views.anomaly_dialog import AnomalyDialog
from views.simulation_config_dialog import SimulationConfigDialog

__all__ = [
    "MainWindowGUI",
    "PropertiesPanel",
    "SimulationPanel",
    "DataPanel",
    "SensorDialog",
    "AnomalyDialog",
    "SimulationConfigDialog",
]
