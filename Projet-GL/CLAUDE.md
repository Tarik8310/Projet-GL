# CLAUDE.md — LambdaSys / GADMAPS

## Présentation du projet

**LambdaSys** (nom d'application : **GADMAPS** — Générateur d'Anomalies et de Données pour la MAintenance Prédictive de Systèmes) est un logiciel de simulation générique de systèmes techniques.

Il permet de :
1. Importer un modèle de système technique (fichier `.py` externe)
2. Configurer des capteurs virtuels sur les composants
3. Injecter des anomalies maîtrisées sur les capteurs
4. Lancer une simulation temporelle et visualiser les données en temps réel
5. Exporter les données générées au format CSV (pour l'entraînement de modèles d'IA)

**Contexte** : Projet Génie Logiciel 2025-2026 — Université de Toulon  
**Équipe** : EL MAKHLOUFI Tarik, BOURGER Léo, JAZIRI Jihène  
**Encadrant** : FRANCISCI Dominique

---

## Règles absolues

- **Ne jamais modifier les fichiers du dossier `UML/`** — ce dossier contient uniquement les diagrammes et scripts PlantUML de conception ; il est en lecture seule.
- **Seuls les fichiers `.py`** du projet peuvent être modifiés (hors dossier `UML/`).
- L'architecture **MVC** doit être strictement respectée : la Vue n'a aucune logique métier, les Controllers orchestrent, les Models encapsulent l'état.

---

## Architecture

Le projet suit un pattern **MVC strict** en Python Orienté Objet avec PyQt5.

```
Projet-GL/
├── main.py                  # Point d'entrée — lance MainWindowController
├── config.json              # Configuration persistante (thème, etc.)
├── models/                  # Couche Modèle
│   ├── component.py         # Classe abstraite Component (base de tout composant)
│   ├── system.py            # Conteneur de composants
│   └── sensor.py            # Capteur virtuel attaché à un composant
├── views/                   # Couche Vue (PyQt5 — affichage uniquement)
│   ├── main_window_gui.py   # Fenêtre principale (arbre + onglets + barre de menus)
│   ├── properties_panel.py  # Panneau de propriétés (droite)
│   ├── simulation_panel.py  # Panneau de simulation
│   ├── data_panel.py        # Affichage des données en temps réel
│   ├── sensor_dialog.py     # Dialogue d'ajout/configuration de capteur
│   ├── anomaly_dialog.py    # Dialogue d'ajout d'anomalie
│   ├── simulation_config_dialog.py
│   └── settings_dialog.py
├── controllers/             # Couche Contrôleur
│   ├── main_window_controller.py  # Contrôleur principal, coordonne tous les autres
│   ├── system_controller.py
│   ├── sensor_controller.py
│   ├── anomaly_controller.py
│   ├── simulation_controller.py
│   ├── data_controller.py
│   ├── file_controller.py
│   └── simulation_worker.py       # QThread pour la boucle de simulation
├── simulation/              # Moteur de simulation
│   ├── engine.py            # SimulationEngine — boucle temporelle (dans un QThread)
│   ├── data_gen.py          # DataGen — échantillonnage des sorties à chaque pas
│   ├── system_update.py     # SystemUpdate — appelle update_state() sur chaque composant
│   └── anomaly.py           # Classe Anomaly — injection de défauts sur les capteurs
├── input/
│   └── system_file_input.py # SystemFileInput — chargement dynamique par introspection
├── output/
│   └── csv_file_output.py   # CSVfileOutput — export des données simulées
├── examples/                # Fichiers systèmes exemples importables par l'utilisateur
│   ├── moteur-voiture.py
│   ├── moteur-f1.py
│   ├── moteur-fusee.py
│   ├── moteur-moto.py
│   └── voiture-electrique.py
├── themes/                  # Gestion des thèmes (clair / sombre)
├── UML/                     # [LECTURE SEULE] Diagrammes et scripts PlantUML
└── script/                  # Scripts UML et scénarios nominaux (documentation)
```

---

## Mécanisme central : chargement par introspection

C'est la fonctionnalité générique clé du projet.  
`SystemFileInput` (dans `input/system_file_input.py`) charge dynamiquement n'importe quel fichier `.py` fourni par l'utilisateur via `importlib` et `inspect`, détecte toutes les sous-classes concrètes de `Component`, les instancie et construit un objet `System`.

**Pour créer un nouveau système compatible**, un fichier doit :
- Importer `Component` depuis `models`
- Définir une ou plusieurs classes héritant de `Component`
- Implémenter la méthode abstraite `update_state(self, dt: float, t: float) -> None`
- Renseigner `self.outputs` (dict des grandeurs physiques mesurables)
- Ne **pas** appeler `sys.exit()` au niveau module

```python
# Exemple minimal
from models import Component

class MaChaudiere(Component):
    def __init__(self):
        super().__init__("Chaudière")
        self.outputs = {"temperature_C": 20.0, "pression_bar": 1.0}

    def update_state(self, dt: float, t: float) -> None:
        self.outputs["temperature_C"] = 20.0 + 80.0 * min(1.0, t / 60.0)
        self.outputs["pression_bar"]  = 1.0 + 5.0 * min(1.0, t / 60.0)
```

---

## Moteur de simulation

- `SimulationEngine` orchestre la boucle temporelle. Il doit être exécuté dans un `QThread` (via `SimulationWorker`) pour ne pas bloquer l'interface PyQt5.
- À chaque pas de temps `dt`, il appelle `SystemUpdate.update()` puis `DataGen.sample()`.
- Des callbacks permettent de notifier la vue : `set_progress_callback()` et `set_data_callback()`.
- La pause/reprise et l'arrêt sont thread-safe via des flags `_paused` / `_running`.

---

## Modélisation UML (documentation de conception)

Les diagrammes sont dans `UML/` (ne pas modifier) et les scripts PlantUML dans `script/`.

| Axe | Fichier | Contenu |
|-----|---------|---------|
| Fonctionnel (cas d'utilisation) | `UML/Diag_UC.pdf` | Importer système, Configurer capteurs, Lancer simulation, Exporter CSV |
| Statique (classes) | `UML/UMLClasses5.png` + `script/ScriptUMLClasses` | Architecture MVC complète avec packages Model, View, Controller, Simulation, Input, Output |
| Dynamique (séquences) | `UML/Diag_Seq_Classes_*.pdf` | Scénarios : gestion capteurs, injection anomalie, boucle de simulation |

### Scénarios nominaux documentés (dans `script/`)

**Gérer un système** (`script/SN`) :
1. L'utilisateur ouvre l'application
2. Importe un modèle (via `Fichier → Importer`)
3. Gère les capteurs (ajout, configuration d'unité, assignation à un composant, suppression)
4. Enregistre le système (optionnel)

**Gérer une simulation** (`script/SN 2`) :
1. Lancer → Le moteur initialise et démarre la boucle temporelle
2. Pause / Reprise / Arrêt possibles à tout moment
3. En fin de simulation, l'utilisateur peut exporter les données en CSV

---

## Exigences logicielles

### Fonctionnelles
| Exigence | Description |
|----------|-------------|
| MODELISATION | Importation de modèles externes (.py), visualisation de l'arborescence |
| CAPTEUR | Capteurs virtuels configurables (type, fréquence, unité) par composant |
| SIMULATION | Durée totale et pas de temps configurables, valeurs nominales à chaque itération |
| ANOMALIE | Injection de défauts maîtrisés sur les capteurs pour dégrader leur comportement |
| EXPORT | Export CSV des données pour l'entraînement de modèles d'IA |

### Interface et non-fonctionnelles
| Exigence | Description |
|----------|-------------|
| REQ-UI | Interface en panneaux ancrables (docks) : explorateur gauche, propriétés droite, zone centrale |
| REQ-TECH | Python POO, architecture MVC, versionné sous Git |

---

## Lancement

```bash
# Depuis le dossier Projet-GL/
python -m venv env          # Si l'environnement n'existe pas encore
source env/bin/activate     # Linux/Mac
pip install PyQt5
python main.py
```

> **Note Linux** : les conflits PEP 668 lors de l'installation de PyQt5 sont résolus en utilisant un `venv` dédié (dossier `env/`).

---

## Choix techniques notables

- **Introspection** (`importlib` + `inspect`) : permet la généricité totale — aucun composant métier n'est codé en dur dans le logiciel.
- **QThread** pour la simulation : la boucle temporelle tourne en parallèle de l'interface sans la bloquer.
- **QTextEdit** pour l'affichage des données (et non QLabel) : évite l'étirement non désiré de la fenêtre sur de gros dictionnaires de données.
- **ThemeManager** : gestion d'un thème clair/sombre persisté dans `config.json`.
