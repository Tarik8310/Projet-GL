import sys
import importlib.util
import inspect
import os
from models import Component
from simulation import SimulationEngine
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, QDockWidget, 
                             QAction, QToolBar, QTreeWidget, QTreeWidgetItem, 
                             QFileDialog, QWidget, QFormLayout, QLineEdit, 
                             QPushButton, QTextEdit)
from PyQt5.QtCore import Qt

# ==========================================
# VUE (View)
# ==========================================
class MainWindowGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LambdaSys")
        self.resize(1200, 800)
        self.setup_ui()

    def setup_ui(self):
        # 1. Zone Centrale (Visualisation)
        self.central_widget = QTextEdit()
        self.central_widget.setReadOnly(True) # Pour que l'utilisateur ne tape pas dedans
        self.central_widget.setText("Visualisation du Système\n(Veuillez importer un modèle)")
        self.central_widget.setStyleSheet("background-color: #f0f0f0; border: 1px solid #cccccc; font-size: 14px; padding: 10px;")
        
        self.setCentralWidget(self.central_widget)

        # 2. Barre de menus
        menu_bar = self.menuBar()
        self.file_menu = menu_bar.addMenu("&Fichier")
        
        # 3. Barre d'outils (Haut)
        self.toolbar = QToolBar("Barre d'outils principale")
        self.addToolBar(self.toolbar)
        
        self.action_load = QAction("📂 Importer un Système", self)
        self.action_play = QAction("▶ Lancer Simulation", self)
        self.action_stop = QAction("⏹ Arrêter", self)
        
        self.toolbar.addAction(self.action_load)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.action_play)
        self.toolbar.addAction(self.action_stop)

        # 4. Panneau latéral gauche : Explorateur de Système (Arborescence)
        self.dock_explorer = self.create_dock("Explorateur de Système", Qt.LeftDockWidgetArea)
        self.system_tree = QTreeWidget()
        self.system_tree.setHeaderLabels(["Composants du modèle"])
        self.dock_explorer.setWidget(self.system_tree)

        # 5. Panneau latéral droit : Propriétés
        self.dock_properties = self.create_dock("Propriétés & Capteurs", Qt.RightDockWidgetArea)

    def create_dock(self, title, area):
        dock = QDockWidget(title, self)
        dock.setAllowedAreas(Qt.AllDockWidgetAreas)
        content = QLabel(f"Sélectionnez un élément...", alignment=Qt.AlignCenter)
        dock.setWidget(content)
        self.addDockWidget(area, dock)
        return dock
    
    def afficher_formulaire_proprietes(self, nom_element, type_element):
        """Remplace le contenu du dock droit par un formulaire éditable."""
        
        # Créer un widget conteneur et son layout
        container = QWidget()
        layout = QFormLayout()
        
        # Titre
        titre = QLabel(f"<b>{nom_element}</b> ({type_element})")
        titre.setStyleSheet("font-size: 14px; margin-bottom: 10px;")
        layout.addRow(titre)
        
        # Champs dynamiques selon le type
        if type_element == "Composant":
            layout.addRow("État :", QLabel("Opérationnel 🟢"))
            btn_anomalie = QPushButton("Injecter une anomalie")
            btn_anomalie.setStyleSheet("background-color: #ffcccc;")
            layout.addRow("", btn_anomalie)
            
        elif type_element == "Capteur":
            self.input_frequence = QLineEdit("10") # 10 Hz par défaut
            self.input_unite = QLineEdit("-")
            layout.addRow("Fréquence (Hz) :", self.input_frequence)
            layout.addRow("Unité :", self.input_unite)
            
            btn_sauvegarder = QPushButton("Enregistrer la configuration")
            layout.addRow("", btn_sauvegarder)

        container.setLayout(layout)
        self.dock_properties.setWidget(container)

# ==========================================
# CONTRÔLEUR (Controller)
# ==========================================
class MainWindowController:
    def __init__(self):
        self.gui = MainWindowGUI()
        self.composants_actifs = []
        self.connect_signals()

    def connect_signals(self):
        self.gui.action_load.triggered.connect(self.importer_systeme)
        self.gui.action_play.triggered.connect(self.lancer_simulation)
        self.gui.action_stop.triggered.connect(self.arreter_simulation)
        self.gui.system_tree.itemClicked.connect(self.on_tree_item_clicked)
    
    def on_tree_item_clicked(self, item, column):
        """Gère l'affichage des propriétés quand on clique sur l'arbre."""
        texte_item = item.text(0)
        
        # On détermine basiquement si c'est un composant ou un capteur
        if "Capteur" in texte_item:
            self.gui.afficher_formulaire_proprietes(texte_item, "Capteur")
        elif "Modèle importé" not in texte_item:
            self.gui.afficher_formulaire_proprietes(texte_item, "Composant")
        else:
            # C'est la racine (le nom du fichier), on met un texte vide
            self.gui.dock_properties.setWidget(QLabel("Sélectionnez un composant ou un capteur.", alignment=Qt.AlignCenter))

    def importer_systeme(self):
        """Ouvre une boîte de dialogue, charge un fichier .py et inspecte son contenu."""
        
        # 1. Ouvrir l'explorateur de fichiers
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(
            self.gui,
            "Importer un modèle physique (.py)",
            "",
            "Fichiers Python (*.py);;Tous les fichiers (*)",
            options=options
        )

        if not file_path:
            return  # L'utilisateur a cliqué sur "Annuler"

        print(f"[Logique] Chargement du fichier : {file_path}")

        try:
            # 2. Chargement dynamique du module Python (Magie de importlib)
            module_name = os.path.basename(file_path).replace(".py", "")
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # 3. Introspection : Chercher les composants dans le fichier
            composants_trouves = []
            
            # inspect.getmembers parcourt tout ce qu'il y a dans le fichier .py
            for name, obj in inspect.getmembers(module, inspect.isclass):
                # On veut uniquement les classes qui héritent de 'Component'
                # (et on exclut la classe mère elle-même si elle a été importée dans le fichier)
                if issubclass(obj, Component) and obj is not Component:
                    composants_trouves.append(obj)

            # 4. Mise à jour de l'Interface Graphique
            self.gui.system_tree.clear()
            root = QTreeWidgetItem(self.gui.system_tree, [f"Modèle importé : {module_name}"])

            self.composants_actifs.clear() # On vide l'ancienne configuration
            for cls in composants_trouves:
                instance = cls()
                self.composants_actifs.append(instance) # NOUVEAU : On sauvegarde l'objet
                
                item_comp = QTreeWidgetItem(root, [instance.name])
                if hasattr(instance, 'outputs'):
                    for out_name in instance.outputs.keys():
                        QTreeWidgetItem(item_comp, [f"Capteur ➜ {out_name}"])

            self.gui.system_tree.expandAll()
            self.gui.central_widget.setText(f"Succès : {len(composants_trouves)} composant(s) chargé(s) depuis {module_name}.py")

        except Exception as e:
            print(f"[Erreur] Impossible de charger le fichier : {e}")
            self.gui.central_widget.setText(f"Erreur d'importation :\n{e}")

    def lancer_simulation(self):
        """Déclenchée par le bouton Play de la barre d'outils."""
        if not self.composants_actifs:
            print("[Erreur] Aucun système chargé. Veuillez importer un modèle d'abord.")
            return

        print("[Logique] Lancement de la simulation demandé...")
        
        # On instancie le moteur avec nos composants (ex: 5 secondes, pas de 0.5s)
        moteur = SimulationEngine(self.composants_actifs, duree_totale=5.0, pas_de_temps=0.5)
        
        # On récupère les données
        resultats = moteur.run()
        
        # On affiche un petit résumé dans l'interface
        self.gui.central_widget.setText(
            f"Simulation terminée avec succès !\n"
            f"Durée : 5.0s\n"
            f"Lignes de données générées : {len(resultats)}\n"
            f"Dernière valeur enregistrée : {resultats[-1]}"
        )

    def arreter_simulation(self):
        print("[Logique] Arrêt de la simulation demandé...")

    def run(self):
        self.gui.show()

# ==========================================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion") 
    main_controller = MainWindowController()
    main_controller.run()
    sys.exit(app.exec_())