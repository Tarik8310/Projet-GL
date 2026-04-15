# controllers/main_window_controller.py
"""MainWindowController — contrôleur principal, coordonne tous les sous-contrôleurs."""
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtWidgets import QMessageBox, QTreeWidgetItem

from controllers.anomaly_controller import AnomalyController
from controllers.data_controller import DataController
from controllers.file_controller import FileController
from controllers.sensor_controller import SensorController
from controllers.simulation_controller import SimulationController
from controllers.system_controller import SystemController
from models.component import Component
from models.sensor import Sensor
from simulation.anomaly import Anomaly
from themes import ThemeManager
from views.language_dialog import LanguageDialog
from views.main_window_gui import MainWindowGUI
from views.settings_dialog import SettingsDialog


class MainWindowController:
    """
    Point de coordination central.
    Instancie la vue principale et tous les sous-contrôleurs,
    puis connecte les signaux de la vue aux actions métier.
    """

    def __init__(self):
        self._theme = ThemeManager.load_theme()

        # Sélection de la langue au démarrage — verrouillée pour la session
        lang_dlg = LanguageDialog(default_lang=ThemeManager.load_lang())
        lang_dlg.exec_()
        self._lang = lang_dlg.selected_language
        ThemeManager.save_lang(self._lang)

        self.gui = MainWindowGUI(theme=self._theme, lang=self._lang)

        self.file_ctrl = FileController(self)
        self.system_ctrl = SystemController(self)
        self.sensor_ctrl = SensorController(self)
        self.anomaly_ctrl = AnomalyController(self)
        self.data_ctrl = DataController(self)
        self.sim_ctrl = SimulationController(self)

        self._connect_signals()

    # ------------------------------------------------------------------
    # Connexion des signaux
    # ------------------------------------------------------------------

    def _connect_signals(self) -> None:
        gui = self.gui

        # Fichier
        gui.action_import.triggered.connect(self._on_import)
        gui.action_export_csv.triggered.connect(
            lambda: self.file_ctrl.export_csv(self.data_ctrl.get_data())
        )
        gui.action_quit.triggered.connect(gui.close)

        # Capteurs
        gui.action_add_sensor.triggered.connect(self._on_add_sensor_menu)

        # Anomalies
        gui.action_add_anomaly.triggered.connect(self._on_add_anomaly_menu)

        # Simulation
        gui.action_sim_launch.triggered.connect(self.sim_ctrl.launch)
        gui.action_sim_pause.triggered.connect(self.sim_ctrl.pause_resume)
        gui.action_sim_stop.triggered.connect(self.sim_ctrl.stop)

        # Affichage
        gui.action_settings.triggered.connect(self._on_settings)

        # Aide
        gui.action_about.triggered.connect(self._show_about)

        # Arbre
        gui.tree.itemClicked.connect(self._on_tree_item_clicked)

        # Panneau de propriétés
        panel = gui.properties_panel
        panel.sensor_add_requested.connect(self.sensor_ctrl.add_sensor)
        panel.sensor_delete_requested.connect(self.sensor_ctrl.delete_sensor)
        panel.anomaly_add_requested.connect(self.anomaly_ctrl.add_anomaly)
        panel.anomaly_delete_requested.connect(self.anomaly_ctrl.delete_anomaly)
        panel.component_toggle_requested.connect(self.system_ctrl.toggle_component)

    # ------------------------------------------------------------------
    # Gestionnaires d'événements
    # ------------------------------------------------------------------

    def _on_import(self) -> None:
        system = self.file_ctrl.import_system()
        if system:
            self.system_ctrl.set_system(system)
            self.gui.tabs.setCurrentIndex(0)

    def _on_add_sensor_menu(self) -> None:
        """Ajoute un capteur au composant sélectionné (ou au premier disponible)."""
        system = self.system_ctrl.system
        if not system or not system.components:
            return
        comp = self._selected_component()
        self.sensor_ctrl.add_sensor(comp or system.components[0])

    def _on_add_anomaly_menu(self) -> None:
        """Ajoute une anomalie au capteur sélectionné (ou au premier disponible)."""
        item = self.gui.tree.currentItem()
        if item:
            obj = item.data(0, Qt.UserRole)
            if isinstance(obj, Sensor):
                self.anomaly_ctrl.add_anomaly(obj)
                return
        system = self.system_ctrl.system
        if system:
            all_sensors = system.get_all_sensors()
            if all_sensors:
                self.anomaly_ctrl.add_anomaly(all_sensors[0])

    def _on_tree_item_clicked(self, item: QTreeWidgetItem, _col: int) -> None:
        """Affiche les propriétés de l'élément cliqué dans le panneau droit."""
        obj = item.data(0, Qt.UserRole)
        if isinstance(obj, Component):
            self.gui.properties_panel.show_component(obj)
        elif isinstance(obj, Sensor):
            self.gui.properties_panel.show_sensor(obj)
        elif isinstance(obj, Anomaly):
            self.gui.properties_panel.show_anomaly(obj)
        else:
            self.gui.properties_panel.show_empty()

    def _selected_component(self):
        """Retourne le Component sélectionné dans l'arbre, ou None."""
        item = self.gui.tree.currentItem()
        if item:
            obj = item.data(0, Qt.UserRole)
            return obj if isinstance(obj, Component) else None
        return None

    # ------------------------------------------------------------------
    # Reconstruction de l'arbre (SystemGUI)
    # ------------------------------------------------------------------

    def refresh_tree(self) -> None:
        """Reconstruit entièrement l'arborescence du système actif."""
        self.gui.tree.clear()
        system = self.system_ctrl.system
        if not system:
            return

        bold = QFont()
        bold.setBold(True)

        root = QTreeWidgetItem(self.gui.tree, [f"🔧  {system.name}"])
        root.setFont(0, bold)

        for comp in system.components:
            icon = "🟢" if comp.is_operational else "🔴"
            comp_item = QTreeWidgetItem(root, [f"{icon}  {comp.name}"])
            comp_item.setData(0, Qt.UserRole, comp)
            comp_item.setFont(0, bold)

            for out_name in comp.outputs:
                out_item = QTreeWidgetItem(comp_item, [f"    ⬡  {out_name}"])
                out_item.setForeground(0, QColor("#95a5a6"))

            for sensor in comp.sensors:
                s_item = QTreeWidgetItem(
                    comp_item,
                    [f"    📡  {sensor.name}  ({sensor.unit} · {sensor.frequency} Hz)"],
                )
                s_item.setData(0, Qt.UserRole, sensor)
                s_item.setForeground(0, QColor("#2980b9"))

                for anomaly in sensor.anomalies:
                    a_item = QTreeWidgetItem(
                        s_item,
                        [f"        ⚠  {anomaly.name}  [{anomaly.anomaly_type.value}]"],
                    )
                    a_item.setData(0, Qt.UserRole, anomaly)
                    a_item.setForeground(0, QColor("#e74c3c"))

        self.gui.tree.expandAll()

    # ------------------------------------------------------------------

    def _on_settings(self) -> None:
        dlg = SettingsDialog(self._theme, self.gui)
        dlg.theme_changed.connect(self._apply_theme)
        dlg.exec_()

    def _apply_theme(self, theme: str) -> None:
        from PyQt5.QtWidgets import QApplication
        self._theme = theme
        ThemeManager.save_theme(theme)
        QApplication.instance().setPalette(ThemeManager.get_palette(theme))
        self.gui.apply_theme(theme)

    def _show_about(self) -> None:
        QMessageBox.about(
            self.gui,
            "À propos de LambdaSys",
            "<h3>LambdaSys</h3>"
            "<p>Simulateur générique de systèmes techniques<br>"
            "pour la génération de données de maintenance prédictive</p>"
            "<p>Projet Génie Logiciel &amp; IA — 2025-2026</p>",
        )

    def run(self) -> None:
        self.gui.show()
