# views/main_window_gui.py
"""MainWindowGUI — fenêtre principale de GADMAPS."""
from PyQt5.QtWidgets import (
    QAction, QDockWidget, QLabel, QMainWindow,
    QTabWidget, QToolBar, QTreeWidget,
)
from PyQt5.QtCore import Qt

from views.properties_panel import PropertiesPanel
from views.simulation_panel import SimulationPanel
from views.data_panel import DataPanel
from themes import ThemeManager


class MainWindowGUI(QMainWindow):
    """
    Fenêtre principale : barre de menus (MenuBarGUI), barre d'outils,
    dock gauche (SystemGUI — arbre), dock droit (PropertiesPanel),
    zone centrale avec onglets (SimulationGUI, DataGUI).
    """

    def __init__(self, theme: str = "light"):
        super().__init__()
        self._theme = theme
        self.setWindowTitle(
            "GADMAPS — Générateur d'Anomalies et de Données "
            "pour la Maintenance Prédictive"
        )
        self.resize(1440, 860)
        self.setMinimumSize(960, 640)
        self._build_menu()
        self._build_toolbar()
        self._build_docks()
        self._build_central()
        self._apply_stylesheet()

    # ------------------------------------------------------------------
    # Construction
    # ------------------------------------------------------------------

    def _build_menu(self) -> None:
        menu = self.menuBar()

        # ---- Fichier ----
        file_menu = menu.addMenu("&Fichier")
        self.action_import = QAction("📂  Importer un système...", self)
        self.action_import.setShortcut("Ctrl+O")

        self.action_export_csv = QAction("💾  Exporter les données CSV...", self)
        self.action_export_csv.setShortcut("Ctrl+S")
        self.action_export_csv.setEnabled(False)

        self.action_quit = QAction("Quitter", self)
        self.action_quit.setShortcut("Ctrl+Q")

        file_menu.addAction(self.action_import)
        file_menu.addAction(self.action_export_csv)
        file_menu.addSeparator()
        file_menu.addAction(self.action_quit)

        # ---- Capteurs ----
        sensor_menu = menu.addMenu("&Capteurs")
        self.action_add_sensor = QAction("＋  Ajouter un capteur", self)
        self.action_add_sensor.setEnabled(False)
        sensor_menu.addAction(self.action_add_sensor)

        # ---- Anomalies ----
        anomaly_menu = menu.addMenu("&Anomalies")
        self.action_add_anomaly = QAction("⚠  Créer une anomalie", self)
        self.action_add_anomaly.setEnabled(False)
        anomaly_menu.addAction(self.action_add_anomaly)

        # ---- Simulation ----
        sim_menu = menu.addMenu("&Simulation")
        self.action_sim_launch = QAction("▶  Lancer la simulation...", self)
        self.action_sim_launch.setShortcut("F5")
        self.action_sim_launch.setEnabled(False)

        self.action_sim_pause = QAction("⏸  Pause / Reprendre", self)
        self.action_sim_pause.setShortcut("F6")
        self.action_sim_pause.setEnabled(False)

        self.action_sim_stop = QAction("⏹  Arrêter", self)
        self.action_sim_stop.setShortcut("F7")
        self.action_sim_stop.setEnabled(False)

        sim_menu.addAction(self.action_sim_launch)
        sim_menu.addSeparator()
        sim_menu.addAction(self.action_sim_pause)
        sim_menu.addAction(self.action_sim_stop)

        # ---- Affichage ----
        view_menu = menu.addMenu("&Affichage")
        self.action_settings = QAction("⚙  Paramètres...", self)
        self.action_settings.setShortcut("Ctrl+,")
        view_menu.addAction(self.action_settings)

        # ---- Aide ----
        help_menu = menu.addMenu("&Aide")
        self.action_about = QAction("À propos de GADMAPS", self)
        help_menu.addAction(self.action_about)

    def _build_toolbar(self) -> None:
        toolbar = QToolBar("Barre principale")
        toolbar.setMovable(False)
        toolbar.setStyleSheet("QToolBar { spacing:5px; padding:3px; }")
        self.addToolBar(toolbar)

        toolbar.addAction(self.action_import)
        toolbar.addSeparator()
        toolbar.addAction(self.action_add_sensor)
        toolbar.addAction(self.action_add_anomaly)
        toolbar.addSeparator()
        toolbar.addAction(self.action_sim_launch)
        toolbar.addAction(self.action_sim_pause)
        toolbar.addAction(self.action_sim_stop)
        toolbar.addSeparator()
        toolbar.addAction(self.action_export_csv)

    def _build_docks(self) -> None:
        # ---- Dock gauche : arbre du système (SystemGUI) ----
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Système GADMAPS"])
        self.tree.setMinimumWidth(260)
        self.tree.setAnimated(True)
        self.tree.setStyleSheet(
            "QTreeWidget { border:none; font-size:12px; }"
            "QTreeWidget::item { padding:3px; }"
            "QTreeWidget::item:selected { background:#3498db; color:white; }"
        )
        dock_left = QDockWidget("Explorateur du système", self)
        dock_left.setAllowedAreas(Qt.LeftDockWidgetArea)
        dock_left.setFeatures(QDockWidget.DockWidgetMovable)
        dock_left.setWidget(self.tree)
        self.addDockWidget(Qt.LeftDockWidgetArea, dock_left)

        # ---- Dock droit : propriétés ----
        self.properties_panel = PropertiesPanel()
        self.properties_panel.setMinimumWidth(290)
        dock_right = QDockWidget("Propriétés", self)
        dock_right.setAllowedAreas(Qt.RightDockWidgetArea)
        dock_right.setFeatures(QDockWidget.DockWidgetMovable)
        dock_right.setWidget(self.properties_panel)
        self.addDockWidget(Qt.RightDockWidgetArea, dock_right)

    def _welcome_html(self, theme: str) -> str:
        if theme == "dark":
            title_color   = "#ecf0f1"
            sub_color     = "#bdc3c7"
            steps_color   = "#95a5a6"
        else:
            title_color   = "#2c3e50"
            sub_color     = "#7f8c8d"
            steps_color   = "#95a5a6"
        return (
            "<center>"
            f"<h2 style='color:{title_color};'>Bienvenue dans GADMAPS</h2>"
            f"<p style='color:{sub_color}; font-size:14px;'>"
            "Générateur d'Anomalies et de Données<br>"
            "pour la MAintenance Prédictive de Systèmes"
            "</p><br>"
            f"<p style='color:{steps_color};'>"
            "<b>Étape 1</b> — Importez un système (Fichier → Importer...)<br>"
            "<b>Étape 2</b> — Ajoutez des capteurs aux composants<br>"
            "<b>Étape 3</b> — Configurez des anomalies (optionnel)<br>"
            "<b>Étape 4</b> — Lancez la simulation (F5)<br>"
            "<b>Étape 5</b> — Exportez les données CSV"
            "</p></center>"
        )

    def _build_central(self) -> None:
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)

        # Onglet Accueil
        self._welcome_label = QLabel(self._welcome_html(self._theme))
        bg = "#1e2d3a" if self._theme == "dark" else "white"
        self._welcome_label.setStyleSheet(f"background:{bg};")
        self.tabs.addTab(self._welcome_label, "🏠  Accueil")

        # Onglet Simulation (SimulationGUI)
        self.sim_panel = SimulationPanel()
        self.tabs.addTab(self.sim_panel, "⚙  Simulation")

        # Onglet Données (DataGUI)
        self.data_panel = DataPanel()
        self.tabs.addTab(self.data_panel, "📊  Données")

        self.setCentralWidget(self.tabs)
        self.statusBar().showMessage("Prêt — Aucun système chargé.")

    def _apply_stylesheet(self) -> None:
        self.setStyleSheet(ThemeManager.get_stylesheet(self._theme))
        self.tree.setStyleSheet(ThemeManager.get_tree_stylesheet(self._theme))

    def apply_theme(self, theme: str) -> None:
        """Applique dynamiquement un nouveau thème à la fenêtre."""
        self._theme = theme
        self._apply_stylesheet()
        bg = "#1e2d3a" if theme == "dark" else "white"
        self._welcome_label.setStyleSheet(f"background:{bg};")
        self._welcome_label.setText(self._welcome_html(theme))
