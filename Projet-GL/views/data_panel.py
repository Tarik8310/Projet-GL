# views/data_panel.py
"""DataPanel — tableau de données post-simulation avec filtrage, tri et formatage."""
from typing import Any, Dict, List

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtWidgets import (
    QAbstractItemView, QHeaderView, QHBoxLayout, QLabel,
    QLineEdit, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget,
)

# ---------------------------------------------------------------------------
# Couleurs des en-têtes selon le type de colonne
# ---------------------------------------------------------------------------
_COL_TIME    = ("#1a6fa3", "#ffffff")   # bleu  — Temps_s
_COL_OUTPUT  = ("#1a7a5e", "#ffffff")   # vert  — sorties brutes composant
_COL_SENSOR  = ("#a05c00", "#ffffff")   # orange — capteurs (contient "[")

_DARK_STYLE = """
    QTableWidget {
        background:#1e2d3a;
        color:#ecf0f1;
        gridline-color:#2c3e50;
        border:none;
        font-size:12px;
    }
    QTableWidget::item { padding: 4px 8px; }
    QTableWidget::item:selected { background:#3498db; color:#ffffff; }
    QTableWidget::item:alternate { background:#16202a; }
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
    QTableWidget {
        background:#ffffff;
        color:#2c3e50;
        gridline-color:#dee2e6;
        border:none;
        font-size:12px;
    }
    QTableWidget::item { padding: 4px 8px; }
    QTableWidget::item:selected { background:#3498db; color:#ffffff; }
    QTableWidget::item:alternate { background:#f4f6f8; }
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
# Item numérique pour tri correct
# ---------------------------------------------------------------------------

class _NumItem(QTableWidgetItem):
    """QTableWidgetItem qui trie numériquement quand c'est possible."""
    def __lt__(self, other: QTableWidgetItem) -> bool:
        try:
            return float(self.text()) < float(other.text())
        except ValueError:
            return self.text() < other.text()


# ---------------------------------------------------------------------------
# DataPanel
# ---------------------------------------------------------------------------

class DataPanel(QWidget):
    """
    Affiche les données de simulation dans un tableau stylisé.
    Fonctionnalités : filtrage en temps réel, tri par colonne,
    en-têtes colorés par type, compteur de lignes.
    """

    def __init__(self, theme: str = "light", parent=None):
        super().__init__(parent)
        self._theme = theme
        self._all_data: List[Dict[str, Any]] = []
        self._headers: List[str] = []

        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(8, 8, 8, 8)

        # --- Barre de recherche + compteur ---
        bar = QHBoxLayout()
        bar.setSpacing(10)

        self._search = QLineEdit()
        self._search.setPlaceholderText("🔍  Filtrer par valeur ou nom de colonne...")
        self._search.setFixedHeight(32)
        self._search.textChanged.connect(self._apply_filter)
        bar.addWidget(self._search)

        self._counter = QLabel("0 ligne")
        self._counter.setFixedWidth(100)
        self._counter.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        counter_font = QFont()
        counter_font.setPointSize(10)
        self._counter.setFont(counter_font)
        bar.addWidget(self._counter)

        layout.addLayout(bar)

        # --- Tableau ---
        self.table = QTableWidget()
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

    def load_data(self, data: List[Dict[str, Any]]) -> None:
        """Charge toutes les données dans le tableau après la simulation."""
        if not data:
            return
        self._all_data = data
        self._headers = list(data[0].keys())
        self._populate(data)

    def clear_data(self) -> None:
        self._all_data.clear()
        self._headers.clear()
        self.table.setRowCount(0)
        self.table.setColumnCount(0)
        self._search.clear()
        self._counter.setText("0 ligne")

    def set_theme(self, theme: str) -> None:
        self._theme = theme
        self._apply_style()
        # Réappliquer les couleurs d'en-tête si des données sont chargées
        if self._headers:
            self._color_headers()

    # ------------------------------------------------------------------
    # Interne
    # ------------------------------------------------------------------

    def _populate(self, rows: List[Dict[str, Any]]) -> None:
        """Remplit le tableau et applique le style des en-têtes."""
        self.table.setSortingEnabled(False)  # désactiver pendant le remplissage

        self.table.setColumnCount(len(self._headers))
        self.table.setHorizontalHeaderLabels(self._headers)
        self.table.setRowCount(len(rows))

        for r, row in enumerate(rows):
            for c, key in enumerate(self._headers):
                raw = row.get(key, "")
                item = _NumItem(self._fmt(raw))
                item.setTextAlignment(
                    Qt.AlignRight | Qt.AlignVCenter
                    if isinstance(raw, (int, float))
                    else Qt.AlignLeft | Qt.AlignVCenter
                )
                self.table.setItem(r, c, item)

        self._color_headers()
        self.table.setSortingEnabled(True)
        self._update_counter(len(rows))

    def _color_headers(self) -> None:
        """Colorie les cellules d'en-tête selon le type de colonne."""
        header = self.table.horizontalHeader()
        for c, col in enumerate(self._headers):
            item = self.table.horizontalHeaderItem(c)
            if item is None:
                continue
            bg_hex, fg_hex = self._header_colors(col)
            item.setBackground(QColor(bg_hex))
            item.setForeground(QColor(fg_hex))

    def _header_colors(self, col: str):
        if col == "Temps_s":
            return _COL_TIME
        if "[" in col:
            return _COL_SENSOR
        return _COL_OUTPUT

    def _apply_filter(self, text: str) -> None:
        """Affiche uniquement les lignes dont une cellule contient le texte."""
        text = text.strip().lower()
        visible = 0
        for r in range(self.table.rowCount()):
            match = not text or any(
                text in (self.table.item(r, c).text().lower() if self.table.item(r, c) else "")
                for c in range(self.table.columnCount())
            )
            self.table.setRowHidden(r, not match)
            if match:
                visible += 1
        self._update_counter(visible)

    def _update_counter(self, count: int) -> None:
        total = len(self._all_data)
        if count == total:
            self._counter.setText(f"{total:,} ligne{'s' if total > 1 else ''}".replace(",", " "))
        else:
            self._counter.setText(f"{count:,} / {total:,}".replace(",", " "))

    @staticmethod
    def _fmt(value: Any) -> str:
        if isinstance(value, float):
            return f"{value:.6f}"
        return str(value)

    def _apply_style(self) -> None:
        style = _DARK_STYLE if self._theme == "dark" else _LIGHT_STYLE
        self.table.setStyleSheet(style)

        # Couleur du compteur et de la barre de recherche selon le thème
        if self._theme == "dark":
            self._counter.setStyleSheet("color:#bdc3c7;")
        else:
            self._counter.setStyleSheet("color:#7f8c8d;")
