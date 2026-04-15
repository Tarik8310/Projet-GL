# views/main_window_gui.py
"""MainWindowGUI — fenêtre principale de LambdaSys."""

from PyQt5.QtWidgets import (
    QAction, QDockWidget, QLabel, QMainWindow,
    QTabWidget, QToolBar, QTreeWidget,
)
from PyQt5.QtCore import Qt

from views.properties_panel import PropertiesPanel
from views.simulation_panel import SimulationPanel
from views.data_panel import DataPanel
from themes import ThemeManager

# ------------------------------------------------------------------
# Dictionnaire de traduction (Internationalisation )
# ------------------------------------------------------------------
TRANSLATIONS = {
    "Français": {
        "title": "LambdaSys — Simulateur de Systèmes Techniques",
        "file": "&Fichier",
        "import": "📂  Importer un système...",
        "export": "💾  Exporter les données CSV...",
        "quit": "Quitter",
        "sensors": "&Capteurs",
        "add_sensor": "＋  Ajouter un capteur",
        "anomalies": "&Anomalies",
        "add_anomaly": "⚠  Créer une anomalie",
        "simulation": "&Simulation",
        "launch": "▶  Lancer la simulation...",
        "pause": "⏸  Pause / Reprendre",
        "stop": "⏹  Arrêter",
        "view": "&Affichage",
        "settings": "⚙  Paramètres...",
        "help": "&Aide",
        "about": "À propos",
        "explorer": "Explorateur du système",
        "properties": "Propriétés",
        "welcome_title": "Bienvenue dans LambdaSys",
        "step1": "<b>Étape 1</b> — 📂  Importez un système <i>(Fichier → Importer un système)</i>",
        "step2": "<b>Étape 2</b> — 📡  Configurez les capteurs sur chaque composant",
        "step3": "<b>Étape 3</b> — ⚠  Injectez des anomalies sur les capteurs <i>(optionnel)</i>",
        "step4": "<b>Étape 4</b> — ▶  Lancez la simulation <i>(Simulation → Lancer)</i>",
        "step5": "<b>Étape 5</b> — 💾  Exportez les données au format CSV",
        "status_ready": "Prêt — Aucun système chargé."
    },
    "English": {
        "title": "LambdaSys — Technical Systems Simulator",
        "file": "&File",
        "import": "📂  Import system...",
        "export": "💾  Export CSV data...",
        "quit": "Quit",
        "sensors": "&Sensors",
        "add_sensor": "＋  Add sensor",
        "anomalies": "&Anomalies",
        "add_anomaly": "⚠  Create anomaly",
        "simulation": "&Simulation",
        "launch": "▶  Launch simulation...",
        "pause": "⏸  Pause / Resume",
        "stop": "⏹  Stop",
        "view": "&View",
        "settings": "⚙  Settings...",
        "help": "&Help",
        "about": "About",
        "explorer": "System Explorer",
        "properties": "Properties",
        "welcome_title": "Welcome to LambdaSys",
        "step1": "<b>Step 1</b> — 📂  Import a system <i>(File → Import system)</i>",
        "step2": "<b>Step 2</b> — 📡  Configure sensors on each component",
        "step3": "<b>Step 3</b> — ⚠  Inject anomalies on sensors <i>(optional)</i>",
        "step4": "<b>Step 4</b> — ▶  Launch the simulation <i>(Simulation → Launch)</i>",
        "step5": "<b>Step 5</b> — 💾  Export the data as CSV",
        "status_ready": "Ready — No system loaded."
    }
}

class MainWindowGUI(QMainWindow):
    def __init__(self, theme: str = "light", lang: str = "Français"):
        super().__init__()
        self._theme = theme
        self._language = lang
        
        self.resize(1440, 860)
        self.setMinimumSize(960, 640)

        # Initialisation des composants
        self._build_menu()
        self._build_toolbar()
        self._build_docks()
        self._build_central()
        
        # Application des textes et styles
        self.retranslate_ui()
        self._apply_stylesheet()

    def _build_menu(self) -> None:
        menu = self.menuBar()
        self.file_menu = menu.addMenu("")
        self.action_import = QAction("", self)
        self.action_export_csv = QAction("", self)
        self.action_quit = QAction("", self)
        self.file_menu.addAction(self.action_import)
        self.file_menu.addAction(self.action_export_csv)
        self.file_menu.addAction(self.action_quit)

        self.sensor_menu = menu.addMenu("")
        self.action_add_sensor = QAction("", self)
        self.sensor_menu.addAction(self.action_add_sensor)

        self.anomaly_menu = menu.addMenu("")
        self.action_add_anomaly = QAction("", self)
        self.anomaly_menu.addAction(self.action_add_anomaly)

        self.sim_menu = menu.addMenu("")
        self.action_sim_launch = QAction("", self)
        self.action_sim_pause = QAction("", self)
        self.action_sim_stop = QAction("", self)
        self.sim_menu.addAction(self.action_sim_launch)
        self.sim_menu.addAction(self.action_sim_pause)
        self.sim_menu.addAction(self.action_sim_stop)

        self.view_menu = menu.addMenu("")
        self.action_settings = QAction("", self)
        self.view_menu.addAction(self.action_settings)

        self.help_menu = menu.addMenu("")
        self.action_about = QAction("", self)
        self.help_menu.addAction(self.action_about)

    def _build_toolbar(self) -> None:
        self.toolbar = QToolBar("Barre principale")
        self.toolbar.setMovable(False)
        self.addToolBar(self.toolbar)
        self.toolbar.addAction(self.action_import)
        self.toolbar.addAction(self.action_add_sensor)
        self.toolbar.addAction(self.action_add_anomaly)
        self.toolbar.addAction(self.action_sim_launch)
        self.toolbar.addAction(self.action_export_csv)

    def _build_docks(self) -> None:
        self.tree = QTreeWidget()
        self.dock_left = QDockWidget("", self)
        self.dock_left.setWidget(self.tree)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.dock_left)

        self.properties_panel = PropertiesPanel()
        self.dock_right = QDockWidget("", self)
        self.dock_right.setWidget(self.properties_panel)
        self.addDockWidget(Qt.RightDockWidgetArea, self.dock_right)

    def _build_central(self) -> None:
        self.tabs = QTabWidget()
        self._welcome_label = QLabel()
        self._welcome_label.setAlignment(Qt.AlignCenter)
        self.tabs.addTab(self._welcome_label, "🏠")
        
        self.sim_panel = SimulationPanel(theme=self._theme)
        self.tabs.addTab(self.sim_panel, "⚙")

        self.data_panel = DataPanel(theme=self._theme)
        self.tabs.addTab(self.data_panel, "📊")
        self.setCentralWidget(self.tabs)

    def retranslate_ui(self) -> None:
        """Met à jour tous les textes selon la langue choisie."""
        t = TRANSLATIONS[self._language]
        
        self.setWindowTitle(t["title"])
        self.file_menu.setTitle(t["file"])
        self.action_import.setText(t["import"])
        self.action_export_csv.setText(t["export"])
        self.action_quit.setText(t["quit"])
        
        self.sensor_menu.setTitle(t["sensors"])
        self.action_add_sensor.setText(t["add_sensor"])
        
        self.anomaly_menu.setTitle(t["anomalies"])
        self.action_add_anomaly.setText(t["add_anomaly"])
        
        self.sim_menu.setTitle(t["simulation"])
        self.action_sim_launch.setText(t["launch"])
        self.action_sim_pause.setText(t["pause"])
        self.action_sim_stop.setText(t["stop"])
        
        self.view_menu.setTitle(t["view"])
        self.action_settings.setText(t["settings"])
        self.help_menu.setTitle(t["help"])
        self.action_about.setText(t["about"])
        
        self.dock_left.setWindowTitle(t["explorer"])
        self.dock_right.setWindowTitle(t["properties"])
        self.tree.setHeaderLabel(t["explorer"])
        
        self._welcome_label.setText(self._welcome_html(self._theme))
        self.statusBar().showMessage(t["status_ready"])

    def _welcome_html(self, theme: str) -> str:
        t = TRANSLATIONS[self._language]
        title_color = "#ecf0f1" if theme == "dark" else "#2c3e50"
        step_color  = "#bdc3c7" if theme == "dark" else "#555555"
        steps = "".join(
            f"<tr><td style='padding:6px 0; color:{step_color};'>{t[k]}</td></tr>"
            for k in ("step1", "step2", "step3", "step4", "step5")
        )
        return (
            f"<center>"
            f"<h2 style='color:{title_color}; margin-bottom:16px;'>{t['welcome_title']}</h2>"
            f"<table align='center' cellspacing='0' cellpadding='0'>"
            f"{steps}"
            f"</table>"
            f"</center>"
        )

    @property
    def language(self) -> str:
        return self._language

    def _apply_stylesheet(self) -> None:
        self.setStyleSheet(ThemeManager.get_stylesheet(self._theme))
        bg = "#1e2d3a" if self._theme == "dark" else "white"
        self._welcome_label.setStyleSheet(f"background:{bg};")

    def apply_theme(self, theme: str) -> None:
        self._theme = theme
        self._apply_stylesheet()
        self.retranslate_ui()
        self.sim_panel.set_theme(theme)
        self.data_panel.set_theme(theme)