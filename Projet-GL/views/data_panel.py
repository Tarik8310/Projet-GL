# views/data_panel.py
"""DataPanel — tableau de données post-simulation avec filtrage, tri et formatage (pandas)."""
from typing import List, Optional

import pandas as pd
from PyQt5.QtCore import Qt, QAbstractTableModel, QModelIndex
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtWidgets import (
    QAbstractItemView, QCheckBox, QHeaderView, QHBoxLayout, QLabel,
    QLineEdit, QTableView, QVBoxLayout, QWidget,
)

# ---------------------------------------------------------------------------
# Couleurs des en-têtes selon le type de colonne
# ---------------------------------------------------------------------------
_COL_TIME    = ("#1a6fa3", "#ffffff")   # bleu       — Temps_s
_COL_OUTPUT  = ("#1a7a5e", "#ffffff")   # vert       — sorties brutes composant
_COL_SENSOR  = ("#a05c00", "#ffffff")   # orange     — capteurs (contient "[")
_COL_ANOMALY = ("#7b1a1a", "#ffaaaa")   # rouge foncé — colonnes label _anomalie

# Fond des lignes anomales selon le thème
_ROW_ANOM_DARK  = QColor("#3d1212")
_ROW_ANOM_LIGHT = QColor("#ffe4e4")

_DARK_STYLE = """
    QTableView {
        background:#1e2d3a;
        color:#ecf0f1;
        gridline-color:#2c3e50;
        border:none;
        font-size:12px;
    }
    QTableView::item { padding: 4px 8px; }
    QTableView::item:selected { background:#3498db; color:#ffffff; }
    QTableView::item:alternate { background:#16202a; }
    QHeaderView::section {
        padding: 6px 8px;
        font-weight: 600;
        font-size: 11px;
        border: none;
        border-right: 1px solid #2c3e50;
        border-bottom: 2px solid #2c3e50;
    }
    QScrollBar:vertical { background:#16202a; width:10px; border:none; }
    QScrollBar::handle:vertical { background:#2c3e50; border-radius:5px; }
    QScrollBar:horizontal { background:#16202a; height:10px; border:none; }
    QScrollBar::handle:horizontal { background:#2c3e50; border-radius:5px; }
"""

_LIGHT_STYLE = """
    QTableView {
        background:#ffffff;
        color:#2c3e50;
        gridline-color:#dee2e6;
        border:none;
        font-size:12px;
    }
    QTableView::item { padding: 4px 8px; }
    QTableView::item:selected { background:#3498db; color:#ffffff; }
    QTableView::item:alternate { background:#f4f6f8; }
    QHeaderView::section {
        padding: 6px 8px;
        font-weight: 600;
        font-size: 11px;
        border: none;
        border-right: 1px solid #dee2e6;
        border-bottom: 2px solid #bdc3c7;
    }
    QScrollBar:vertical { background:#f4f6f8; width:10px; border:none; }
    QScrollBar::handle:vertical { background:#bdc3c7; border-radius:5px; }
    QScrollBar:horizontal { background:#f4f6f8; height:10px; border:none; }
    QScrollBar::handle:horizontal { background:#bdc3c7; border-radius:5px; }
"""


# ---------------------------------------------------------------------------
# Modèle pandas → Qt
# ---------------------------------------------------------------------------

def _header_colors(col: str):
    """
    Retourne le couple (couleur fond, couleur texte) pour un en-tête de colonne.

    :param col: Nom de la colonne.
    :return: Tuple (bg_hex, fg_hex).
    """
    if col == "Temps_s":
        return _COL_TIME
    if col.endswith("_anomalie"):
        return _COL_ANOMALY
    if "[" in col:
        return _COL_SENSOR
    return _COL_OUTPUT


class PandasModel(QAbstractTableModel):
    """
    Modèle Qt alimenté par un DataFrame pandas.

    Gère l'affichage, la coloration des lignes anomales,
    la coloration des en-têtes et le tri par colonne.
    """

    def __init__(
        self,
        df: pd.DataFrame,
        anomaly_col_indices: List[int],
        theme: str = "light",
        total_rows: int = 0,
    ):
        """
        Initialise le modèle avec un DataFrame et les métadonnées de thème.

        :param df: DataFrame pandas à afficher (éventuellement filtré).
        :param anomaly_col_indices: Indices des colonnes dont le nom se termine par '_anomalie'.
        :param theme: Thème visuel courant ('light' ou 'dark').
        :param total_rows: Nombre total de lignes avant filtrage (pour le compteur).
        """
        super().__init__()
        self._df = df.reset_index(drop=True)
        self._anomaly_col_indices = anomaly_col_indices
        self._theme = theme
        self.total_rows = total_rows

    # ------------------------------------------------------------------
    # Méthodes obligatoires
    # ------------------------------------------------------------------

    def rowCount(self, parent=QModelIndex()):
        """Retourne le nombre de lignes du DataFrame affiché."""
        return len(self._df)

    def columnCount(self, parent=QModelIndex()):
        """Retourne le nombre de colonnes du DataFrame affiché."""
        return len(self._df.columns)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole):
        """
        Fournit la donnée d'une cellule selon le rôle Qt demandé.

        :param index: Index de la cellule.
        :param role: Rôle Qt (DisplayRole, BackgroundRole, TextAlignmentRole).
        :return: Valeur correspondante, ou None si non applicable.
        """
        if not index.isValid():
            return None

        row, col = index.row(), index.column()
        val = self._df.iat[row, col]

        if role == Qt.DisplayRole:
            if isinstance(val, float):
                return f"{val:.6f}"
            else:
                return str(val)

        if role == Qt.BackgroundRole:
            is_anomalous = any(
                self._df.iat[row, c] == 1
                for c in self._anomaly_col_indices
                if c < len(self._df.columns)
            )
            if is_anomalous:
                if self._theme == "dark":
                    return _ROW_ANOM_DARK
                else:
                    return _ROW_ANOM_LIGHT

        if role == Qt.TextAlignmentRole:
            if isinstance(val, (int, float)):
                return Qt.AlignRight | Qt.AlignVCenter
            return Qt.AlignLeft | Qt.AlignVCenter

        return None

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole):
        """
        Fournit les données des en-têtes horizontaux (nom + couleurs).

        :param section: Indice de la colonne.
        :param orientation: Qt.Horizontal uniquement (les en-têtes verticaux sont masqués).
        :param role: Rôle Qt (DisplayRole, BackgroundRole, ForegroundRole).
        :return: Valeur correspondante, ou None si non applicable.
        """
        if orientation != Qt.Horizontal:
            return None

        col_name = self._df.columns[section]

        if role == Qt.DisplayRole:
            return col_name
        if role == Qt.BackgroundRole:
            return QColor(_header_colors(col_name)[0])
        if role == Qt.ForegroundRole:
            return QColor(_header_colors(col_name)[1])

        return None

    # ------------------------------------------------------------------
    # Tri par colonne
    # ------------------------------------------------------------------

    def sort(self, column: int, order: Qt.SortOrder):
        """
        Trie le DataFrame selon la colonne et l'ordre indiqués.

        :param column: Indice de la colonne de tri.
        :param order: Qt.AscendingOrder ou Qt.DescendingOrder.
        """
        self.layoutAboutToBeChanged.emit()
        col_name = self._df.columns[column]
        self._df = self._df.sort_values(
            col_name,
            ascending=(order == Qt.AscendingOrder),
            ignore_index=True,
        )
        self.layoutChanged.emit()


# ---------------------------------------------------------------------------
# DataPanel
# ---------------------------------------------------------------------------

class DataPanel(QWidget):
    """
    Affiche les données de simulation dans un tableau stylisé (QTableView + pandas).

    Fonctionnalités :
    - Filtrage texte en temps réel via pandas str.contains
    - Filtre «Anomalies uniquement» (lignes où une colonne _anomalie vaut 1)
    - Tri par colonne géré directement dans le DataFrame
    - En-têtes colorés par type (temps / sortie brute / capteur / label anomalie)
    - Lignes anomales colorées en rouge
    - Compteur de lignes visibles / total
    """

    def __init__(self, theme: str = "light", parent=None):
        """
        Construit le panneau de données avec barre de recherche et tableau.

        :param theme: Thème visuel initial ('light' ou 'dark').
        :param parent: Widget Qt parent (facultatif).
        """
        super().__init__(parent)
        self._theme = theme
        self._df_full: Optional[pd.DataFrame] = None       # données complètes
        self._df_current: Optional[pd.DataFrame] = None    # vue filtrée courante
        self._anomaly_col_indices: List[int] = []

        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(8, 8, 8, 8)

        # --- Barre de recherche + filtres + compteur ---
        bar = QHBoxLayout()
        bar.setSpacing(10)

        self._search = QLineEdit()
        self._search.setPlaceholderText("🔍  Filtrer par valeur ou nom de colonne...")
        self._search.setFixedHeight(32)
        self._search.textChanged.connect(self._apply_filter)
        bar.addWidget(self._search)

        self._anom_only = QCheckBox("⚠  Anomalies uniquement")
        self._anom_only.setFixedHeight(32)
        self._anom_only.toggled.connect(self._apply_filter)
        bar.addWidget(self._anom_only)

        self._counter = QLabel("0 ligne")
        self._counter.setFixedWidth(120)
        self._counter.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        counter_font = QFont()
        counter_font.setPointSize(10)
        self._counter.setFont(counter_font)
        bar.addWidget(self._counter)

        layout.addLayout(bar)

        # --- Tableau (QTableView) ---
        self.table = QTableView()
        self.table.setAlternatingRowColors(True)
        self.table.setSortingEnabled(True)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.verticalHeader().setDefaultSectionSize(28)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setMinimumSectionSize(90)
        self.table.setFont(QFont("Monospace", 10))
        layout.addWidget(self.table)

        self._apply_style()

    # ------------------------------------------------------------------
    # Interface publique
    # ------------------------------------------------------------------

    def load_data(self, data: list):
        """
        Charge les données de simulation dans le tableau via un DataFrame pandas.

        :param data: Liste de dictionnaires colonne → valeur produits par DataGen.
        """
        if not data:
            return
        self._df_full = pd.DataFrame(data)
        self._anomaly_col_indices = [
            i for i, col in enumerate(self._df_full.columns)
            if col.endswith("_anomalie")
        ]
        self._show_df(self._df_full)

    def clear_data(self):
        """Vide le tableau et réinitialise tous les états de filtrage."""
        self._df_full = None
        self._df_current = None
        self._anomaly_col_indices = []
        self.table.setModel(None)
        self._search.clear()
        self._anom_only.setChecked(False)
        self._counter.setText("0 ligne")

    def set_theme(self, theme: str):
        """
        Met à jour le thème visuel du tableau et recharge la vue courante.

        :param theme: Thème visuel ('light' ou 'dark').
        """
        self._theme = theme
        self._apply_style()
        if self._df_current is not None:
            self._show_df(self._df_current)

    # ------------------------------------------------------------------
    # Interne
    # ------------------------------------------------------------------

    def _show_df(self, df: pd.DataFrame):
        """
        Crée un PandasModel à partir du DataFrame fourni et l'assigne au tableau.

        :param df: DataFrame à afficher (complet ou filtré).
        """
        self._df_current = df
        if self._df_full is not None:
            total = len(self._df_full)
        else:
            total = 0
        model = PandasModel(df, self._anomaly_col_indices, self._theme, total)
        self.table.setModel(model)
        self._update_counter(len(df))

    def _apply_filter(self, _=None):
        """
        Recharge le tableau avec les lignes correspondant aux filtres actifs.

        Applique successivement :
        1. Le filtre «Anomalies uniquement» (colonnes _anomalie == 1).
        2. Le filtre texte (recherche dans toutes les colonnes converties en str).
        """
        if self._df_full is None:
            return

        df = self._df_full

        # Filtre anomalies uniquement
        if self._anom_only.isChecked() and self._anomaly_col_indices:
            anom_cols = [df.columns[i] for i in self._anomaly_col_indices]
            df = df[(df[anom_cols] == 1).any(axis=1)]

        # Filtre texte
        text = self._search.text().strip().lower()
        if text:
            mask = df.astype(str).apply(
                lambda col: col.str.lower().str.contains(text, regex=False)
            ).any(axis=1)
            df = df[mask]

        self._show_df(df)

    def _update_counter(self, count: int):
        """
        Met à jour le libellé du compteur de lignes visibles.

        :param count: Nombre de lignes actuellement affichées.
        """
        if self._df_full is not None:
            total = len(self._df_full)
        else:
            total = 0
        if count == total:
            if total > 1:
                plural = "s"
            else:
                plural = ""
            self._counter.setText(
                f"{total:,} ligne{plural}".replace(",", " ")
            )
        else:
            self._counter.setText(f"{count:,} / {total:,}".replace(",", " "))

    def _apply_style(self):
        """Applique la feuille de style QSS du tableau selon le thème courant."""
        if self._theme == "dark":
            style = _DARK_STYLE
        else:
            style = _LIGHT_STYLE
        self.table.setStyleSheet(style)

        if self._theme == "dark":
            self._counter.setStyleSheet("color:#bdc3c7;")
            self._anom_only.setStyleSheet("color:#e74c3c; font-weight:600;")
        else:
            self._counter.setStyleSheet("color:#7f8c8d;")
            self._anom_only.setStyleSheet("color:#c0392b; font-weight:600;")
