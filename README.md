# LambdaSys — Simulateur de Systèmes Techniques

> Générateur d'Anomalies et de Données pour la MAintenance Prédictive de Systèmes

LambdaSys est un logiciel de simulation générique de systèmes techniques.  
Il permet de générer des jeux de données réalistes (nominaux et dégradés) destinés à l'entraînement de modèles d'intelligence artificielle pour la maintenance prédictive.

---

## Fonctionnalités

| # | Fonctionnalité | Description |
|---|---------------|-------------|
| 1 | **Import de système** | Chargement dynamique de tout fichier `.py` contenant des sous-classes de `Component` |
| 2 | **Capteurs virtuels** | Ajout de capteurs configurables (sortie mesurée, unité, fréquence d'échantillonnage) |
| 3 | **Injection d'anomalies** | Injection de défauts maîtrisés sur les composants (Spike, Drift, Noise, Stuck) |
| 4 | **Simulation temporelle** | Boucle temps réel avec pause, reprise et arrêt, affichage de graphiques PyQtGraph 30 fps |
| 5 | **Export CSV** | Export des données simulées avec label binaire `_anomalie` pour l'entraînement IA |
| 6 | **Thème clair / sombre** | Interface PyQt5 avec thème persistant dans `config.json` |
| 7 | **Multilingue** | Interface disponible en Français et en English |

---

## Architecture

Le projet suit un pattern **MVC strict** en Python Orienté Objet avec PyQt5.

```
Projet-GL/
├── main.py                        # Point d'entrée
├── config.json                    # Thème et langue persistants
├── models/                        # Couche Modèle
│   ├── component.py               # Classe abstraite Component
│   ├── sensor.py                  # Capteur virtuel
│   └── system.py                  # Conteneur de composants
├── views/                         # Couche Vue (PyQt5)
│   ├── main_window_gui.py         # Fenêtre principale
│   ├── properties_panel.py        # Panneau de propriétés
│   ├── simulation_panel.py        # Graphiques temps réel
│   ├── data_panel.py              # Tableau de données
│   ├── sensor_dialog.py           # Dialogue capteur
│   ├── anomaly_dialog.py          # Dialogue anomalie
│   ├── simulation_config_dialog.py
│   ├── settings_dialog.py
│   └── language_dialog.py
├── controllers/                   # Couche Contrôleur
│   ├── main_window_controller.py  # Contrôleur principal
│   ├── system_controller.py
│   ├── sensor_controller.py
│   ├── anomaly_controller.py
│   ├── simulation_controller.py
│   ├── data_controller.py
│   ├── file_controller.py
│   └── simulation_worker.py       # QThread simulation
├── simulation/                    # Moteur de simulation
│   ├── engine.py                  # Boucle temporelle
│   ├── data_gen.py                # Échantillonnage
│   ├── system_update.py           # Mise à jour des composants
│   └── anomaly.py                 # Injection de défauts
├── input/
│   └── system_file_input.py       # Chargement par introspection
├── output/
│   └── csv_file_output.py         # Export CSV
├── examples/                      # Systèmes exemples fournis
│   ├── moteur-voiture.py
│   ├── moteur-f1.py
│   ├── moteur-fusee.py
│   ├── moteur-moto.py
│   └── voiture-electrique.py
└── themes/                        # Gestion des thèmes
```

---

## Installation

### Prérequis

- Python 3.10 ou supérieur
- pip

### Étapes

```bash
# 1. Cloner le dépôt
git clone <url-du-depot>
cd Projet-GL

# 2. Créer un environnement virtuel
python3 -m venv env

# 3. Activer l'environnement
source env/bin/activate          # Linux / macOS
env\Scripts\activate             # Windows

# 4. Installer les dépendances
pip install PyQt5 pyqtgraph pandas
```

> **Note Linux (PEP 668)** : si pip refuse d'installer dans l'environnement système,
> l'utilisation du `venv` ci-dessus résout le problème.

---

## Lancement

```bash
# Depuis le dossier Projet-GL/
python main.py
```

Au premier lancement, un dialogue de sélection de langue s'affiche.
Ce choix est verrouillé pour la durée de la session.

---

## Utilisation pas à pas

### Étape 1 — Importer un système

`Fichier → Importer un système…`

Sélectionnez un fichier `.py` (voir [exemples fournis](#exemples-fournis) ou
[créer votre propre système](#créer-un-système-personnalisé)).

L'arborescence gauche affiche automatiquement les composants, leurs sorties,
leurs capteurs et leurs anomalies.

### Étape 2 — Configurer des capteurs

Cliquez sur un composant dans l'arbre, puis sur **＋ Ajouter un capteur**.

Paramètres disponibles :

| Paramètre | Description |
|-----------|-------------|
| Nom | Identifiant du capteur |
| Sortie mesurée | Grandeur physique du composant à lire |
| Unité | Unité affichée dans le CSV (ex : `°C`, `bar`, `tr/min`) |
| Fréquence | Fréquence d'échantillonnage en Hz (sample-and-hold entre deux instants) |

### Étape 3 — Injecter des anomalies (optionnel)

Cliquez sur un composant, puis sur **⚠ Ajouter une anomalie**.

#### Types d'anomalies

| Type | Comportement |
|------|-------------|
| **Spike** | Ajoute une valeur fixe constante à toutes les sorties du composant |
| **Drift** | Dérive linéaire croissante jusqu'à la fin de la durée |
| **Noise** | Bruit gaussien centré sur zéro |
| **Stuck** | Gèle chaque sortie à sa valeur au moment de l'activation |

#### Modes de magnitude

| Mode | Interprétation |
|------|---------------|
| **Absolue** | Perturbation dans l'unité physique brute (ex : +50 °C) |
| **Relative (%)** | Perturbation en pourcentage de la valeur nominale (ex : +20 %) |

> L'anomalie affecte **toutes les sorties** du composant simultanément,
> simulant une défaillance physique globale plutôt qu'une erreur de mesure isolée.

Le bouton **🎲 Générer aléatoirement** crée une anomalie avec des paramètres aléatoires.

### Étape 4 — Lancer la simulation

`Simulation → Lancer la simulation…`

Configurez la durée totale et le pas de temps, puis cliquez sur **▶ Lancer**.

- Les graphiques PyQtGraph s'affichent en temps réel par composant.
- Les plages d'anomalies actives sont visualisées en zones rouges semi-transparentes.
- La pause (`⏸`) et l'arrêt (`⏹`) sont disponibles à tout moment.

### Étape 5 — Consulter et exporter les données

L'onglet **📊 Données** affiche le tableau complet après simulation.

Fonctionnalités du tableau :

- **Filtrage texte** en temps réel sur toutes les colonnes
- **Filtre anomalies uniquement** — affiche uniquement les lignes où au moins une anomalie est active
- **Tri** par colonne (numérique et lexicographique)
- **En-têtes colorés** par type : bleu (temps), vert (sortie brute), orange (capteur), rouge foncé (label anomalie)
- **Lignes colorées** en rouge pour les instants anomaux

Exportez via `Fichier → Exporter les données CSV…`.

---

## Format du CSV exporté

Chaque ligne correspond à un instant de simulation.

| Colonne | Description |
|---------|-------------|
| `Temps_s` | Instant courant en secondes |
| `<Composant>_<sortie>` | Valeur nominale perturbée par les anomalies actives |
| `<Composant>_anomalie` | **Label binaire** : `1` si une anomalie est active, `0` sinon |
| `<Composant>_<capteur>[<unité>]` | Valeur lue par le capteur (sample-and-hold à sa fréquence propre) |

Exemple de colonnes pour un moteur avec un capteur de température :

```
Temps_s, Moteur_temperature_C, Moteur_anomalie, Moteur_T_eau[°C]
0.0,      20.0,                 0,              20.0
0.1,      20.5,                 0,              20.0
...
5.0,      68.3,                 1,              68.3
```

---

## Créer un système personnalisé

Tout fichier `.py` respectant les règles suivantes est importable dans LambdaSys :

```python
# mon_systeme.py
from models import Component

class BlocSysteme(Component):
    """Bloc système générique avec débit, pression et température."""

    def __init__(self):
        super().__init__("Bloc Système")
        self.outputs = {
            "debit_L_min":    0.0,
            "pression_bar":   0.0,
            "temperature_C":  20.0,
        }

    def update_state(self, dt: float, t: float):
        self.outputs["debit_L_min"]   = 120.0 * min(1.0, t / 30.0)
        self.outputs["pression_bar"]  = 4.5   * min(1.0, t / 20.0)
        self.outputs["temperature_C"] = 20.0  + 15.0 * min(1.0, t / 60.0)
```

**Règles à respecter :**

- Importer `Component` depuis `models`
- Hériter de `Component` et implémenter `update_state(self, dt, t)`
- Alimenter `self.outputs` avec les grandeurs physiques mesurables
- Ne **pas** appeler `sys.exit()` au niveau module

Un fichier peut définir **plusieurs composants** — ils seront tous chargés et listés dans l'arbre.

---

## Exemples fournis

| Fichier | Système | Composants |
|---------|---------|-----------|
| `moteur-voiture.py` | Moteur thermique 2.0 T 180 kW | Bloc moteur, Injection haute pression, Turbocompresseur, Refroidissement |
| `moteur-f1.py` | Moteur F1 hybride 1.6 V6 Turbo | Bloc F1, MGU-K, ERS, Transmission |
| `moteur-fusee.py` | Moteur-fusée LOX / Kérosène | Chambre de combustion, Pompes, Tuyère, Régulation |
| `moteur-moto.py` | Moteur moto 4-temps 600 cc | Bloc moto, Embrayage, Boîte de vitesses |
| `voiture-electrique.py` | Groupe motopropulseur électrique | Moteur électrique, Batterie, Onduleur, Thermique |

---

## Dépendances

| Bibliothèque | Version minimale | Usage |
|-------------|-----------------|-------|
| Python | 3.10 | Langage principal |
| PyQt5 | 5.15 | Interface graphique |
| PyQtGraph | 0.13 | Graphiques temps réel |
| pandas | 2.0 | Modèle de données du tableau (filtrage, tri, export) |
| NumPy | 1.24 | Tableaux de données pour les courbes PyQtGraph |

---

## Contexte académique

**Projet Génie Logiciel 2025-2026 — Université de Toulon**

| Rôle | Nom |
|------|-----|
| Développeur | EL MAKHLOUFI Tarik |
| Développeur | BOURGER Léo |
| Développeur | JAZIRI Jihène |
| Encadrant | FRANCISCI Dominique |

