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
        """
        Construit la fenêtre principale et connecte tous les sous-contrôleurs.

        Charge le thème et la langue persistés, instancie la vue principale,
        puis relie les signaux de la vue aux gestionnaires métier.
        """
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

    def _connect_signals(self):
        """Connecte tous les signaux Qt de la vue aux méthodes de contrôle."""
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

        # Simulation — menu
        gui.action_sim_launch.triggered.connect(self.sim_ctrl.launch)
        gui.action_sim_pause.triggered.connect(self.sim_ctrl.pause_resume)
        gui.action_sim_stop.triggered.connect(self.sim_ctrl.stop)

        # Simulation — boutons du panneau (même actions)
        gui.sim_panel.btn_pause.clicked.connect(self.sim_ctrl.pause_resume)
        gui.sim_panel.btn_stop.clicked.connect(self.sim_ctrl.stop)

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

    def _on_import(self):
        """Déclenche l'import d'un système et l'affiche si le chargement réussit."""
        system = self.file_ctrl.import_system()
        if system:
            self.system_ctrl.set_system(system)
            self.gui.tabs.setCurrentIndex(0)

    def _on_add_sensor_menu(self):
        """Ajoute un capteur au composant sélectionné (ou au premier disponible)."""
        system = self.system_ctrl.system
        if not system or not system.components:
            return
        comp = self._selected_component()
        self.sensor_ctrl.add_sensor(comp or system.components[0])

    def _on_add_anomaly_menu(self):
        """Ajoute une anomalie au composant sélectionné (ou au premier disponible)."""
        item = self.gui.tree.currentItem()
        if item:
            obj = item.data(0, Qt.UserRole)
            if isinstance(obj, Component):
                self.anomaly_ctrl.add_anomaly(obj)
                return
        system = self.system_ctrl.system
        if system and system.components:
            self.anomaly_ctrl.add_anomaly(system.components[0])

    def _on_tree_item_clicked(self, item: QTreeWidgetItem, _col: int):
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

    def refresh_tree(self):
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

            for anomaly in comp.anomalies:
                a_item = QTreeWidgetItem(
                    comp_item,
                    [f"    ⚠  {anomaly.name}  [{anomaly.anomaly_type.value}]"],
                )
                a_item.setData(0, Qt.UserRole, anomaly)
                a_item.setForeground(0, QColor("#e74c3c"))

            for sensor in comp.sensors:
                s_item = QTreeWidgetItem(
                    comp_item,
                    [f"    📡  {sensor.name}  ({sensor.unit} · {sensor.frequency} Hz)"],
                )
                s_item.setData(0, Qt.UserRole, sensor)
                s_item.setForeground(0, QColor("#2980b9"))

        self.gui.tree.expandAll()

    # ------------------------------------------------------------------

    def _on_settings(self):
        """Ouvre le dialogue de paramètres et connecte le signal de changement de thème."""
        dlg = SettingsDialog(self._theme, self.gui)
        dlg.theme_changed.connect(self._apply_theme)
        dlg.exec_()

    def _apply_theme(self, theme: str):
        """
        Applique un nouveau thème visuel à toute l'application.

        :param theme: Identifiant du thème ('light' ou 'dark').
        """
        from PyQt5.QtWidgets import QApplication
        self._theme = theme
        ThemeManager.save_theme(theme)
        QApplication.instance().setPalette(ThemeManager.get_palette(theme))
        self.gui.apply_theme(theme)

    def _show_about(self):
        """Affiche la boîte de dialogue «À propos / Aide» de LambdaSys."""
        from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QTextEdit, QVBoxLayout
        from PyQt5.QtCore import Qt

        _CONTENT = {
            "Français": (
                "LambdaSys — Simulateur de Systèmes Techniques\n"
                "Projet Génie Logiciel & IA — 2025-2026\n"
                "================================================\n\n"
                "PRÉSENTATION\n"
                "  LambdaSys est un simulateur générique de systèmes techniques destiné\n"
                "  à la génération de données de capteurs pour la maintenance prédictive.\n\n"
                "PRISE EN MAIN RAPIDE\n"
                "  1. Importer un système\n"
                "       Fichier > Importer un système\n"
                "       Chargez un fichier Python décrivant votre système.\n\n"
                "  2. Configurer les capteurs\n"
                "       Capteurs > Ajouter un capteur\n"
                "       Associez des capteurs à chaque composant (type, unité, plage, bruit).\n\n"
                "  3. Injecter des anomalies  (optionnel)\n"
                "       Anomalies > Créer une anomalie\n"
                "       Simulez des défauts en mode absolu ou relatif.\n\n"
                "  4. Lancer la simulation\n"
                "       Simulation > Lancer la simulation\n"
                "       Configurez la durée, le pas de temps et le bruit global.\n\n"
                "  5. Exporter les données\n"
                "       Fichier > Exporter les données CSV\n"
                "       Sauvegardez les séries temporelles générées.\n\n"
                "TYPES D'ANOMALIES\n"
                "  OFFSET   — Décalage constant de la valeur du capteur.\n"
                "  DRIFT    — Dérive progressive au fil du temps.\n"
                "  NOISE    — Augmentation du bruit sur la mesure.\n"
                "  STUCK    — Valeur figée (capteur bloqué).\n"
                "  FAILURE  — Panne franche (valeur nulle ou hors plage).\n\n"
                "GÉNÉRATION ALÉATOIRE\n"
                "  Le bouton « Générer aléatoirement » remplit automatiquement tous les\n"
                "  paramètres d'une anomalie avec des valeurs cohérentes.\n\n"
                "CONSEILS\n"
                "  - Utilisez les exemples fournis (moteur voiture, moto, F1...) comme\n"
                "    point de départ pour créer vos propres systèmes.\n"
                "  - Mode RELATIF : magnitude en % de la valeur nominale.\n"
                "  - Mode ABSOLU  : magnitude dans les unités du capteur.\n"
                "  - La simulation peut être mise en pause sans perdre les données.\n\n"
                "FORMAT DE SYSTÈME IMPORTABLE\n"
                "  Un fichier .py définissant create_system() -> System.\n"
                "  Voir le dossier examples/ pour la syntaxe complète.\n"
            ),
            "English": (
                "LambdaSys — Technical Systems Simulator\n"
                "Software Engineering & AI Project — 2025-2026\n"
                "===============================================\n\n"
                "OVERVIEW\n"
                "  LambdaSys is a generic technical-system simulator designed for\n"
                "  generating sensor data for predictive maintenance.\n\n"
                "QUICK START\n"
                "  1. Import a system\n"
                "       File > Import system\n"
                "       Load a Python file describing your system.\n\n"
                "  2. Configure sensors\n"
                "       Sensors > Add sensor\n"
                "       Attach sensors to each component (type, unit, range, noise).\n\n"
                "  3. Inject anomalies  (optional)\n"
                "       Anomalies > Create anomaly\n"
                "       Simulate faults in absolute or relative mode.\n\n"
                "  4. Launch the simulation\n"
                "       Simulation > Launch simulation\n"
                "       Set duration, time step and global noise.\n\n"
                "  5. Export the data\n"
                "       File > Export CSV data\n"
                "       Save the generated time series.\n\n"
                "ANOMALY TYPES\n"
                "  OFFSET   — Constant shift applied to the sensor value.\n"
                "  DRIFT    — Progressive drift over time.\n"
                "  NOISE    — Increased noise on the measurement.\n"
                "  STUCK    — Frozen value (stuck sensor).\n"
                "  FAILURE  — Hard failure (zero or out-of-range value).\n\n"
                "RANDOM GENERATION\n"
                "  The 'Generate randomly' button auto-fills all anomaly parameters\n"
                "  with coherent values.\n\n"
                "TIPS\n"
                "  - Use the provided examples (car engine, motorbike, F1...) as a\n"
                "    starting point for your own systems.\n"
                "  - RELATIVE mode: magnitude as % of nominal value.\n"
                "  - ABSOLUTE mode: magnitude in sensor units.\n"
                "  - The simulation can be paused without losing generated data.\n\n"
                "IMPORTABLE SYSTEM FORMAT\n"
                "  A .py file defining create_system() -> System.\n"
                "  See the examples/ folder for the full syntax.\n"
            ),
        }

        dlg = QDialog(self.gui)
        dlg.setWindowTitle(
            "À propos de LambdaSys" if self._lang == "Français" else "About LambdaSys"
        )
        dlg.setWindowFlags(dlg.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        dlg.resize(620, 500)

        layout = QVBoxLayout(dlg)
        layout.setContentsMargins(16, 16, 16, 12)

        text = QTextEdit()
        text.setReadOnly(True)
        text.setPlainText(_CONTENT.get(self._lang, _CONTENT["Français"]))
        text.setFrameShape(QTextEdit.NoFrame)
        layout.addWidget(text)

        btns = QDialogButtonBox(QDialogButtonBox.Close)
        btns.rejected.connect(dlg.reject)
        layout.addWidget(btns)

        dlg.exec_()

    def run(self):
        """Affiche la fenêtre principale et démarre la boucle d'événements Qt."""
        self.gui.show()
