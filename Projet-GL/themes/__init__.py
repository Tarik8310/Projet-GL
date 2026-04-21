# themes/__init__.py
"""Gestionnaire de thèmes pour LambdaSys (clair / sombre)."""
import json
import os

from PyQt5.QtGui import QColor, QPalette

_CONFIG_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "config.json",
)

# ---------------------------------------------------------------------------
# Palettes
# ---------------------------------------------------------------------------

def _light_palette() -> QPalette:
    """Construit et retourne la palette Qt pour le thème clair."""
    p = QPalette()
    p.setColor(QPalette.Window,          QColor("#ecf0f1"))
    p.setColor(QPalette.WindowText,      QColor("#2c3e50"))
    p.setColor(QPalette.Base,            QColor("#ffffff"))
    p.setColor(QPalette.AlternateBase,   QColor("#f5f6fa"))
    p.setColor(QPalette.Button,          QColor("#bdc3c7"))
    p.setColor(QPalette.ButtonText,      QColor("#2c3e50"))
    p.setColor(QPalette.Highlight,       QColor("#3498db"))
    p.setColor(QPalette.HighlightedText, QColor("#ffffff"))
    p.setColor(QPalette.Text,            QColor("#2c3e50"))
    return p


def _dark_palette() -> QPalette:
    """Construit et retourne la palette Qt pour le thème sombre."""
    p = QPalette()
    p.setColor(QPalette.Window,          QColor("#1a252f"))
    p.setColor(QPalette.WindowText,      QColor("#ecf0f1"))
    p.setColor(QPalette.Base,            QColor("#1e2d3a"))
    p.setColor(QPalette.AlternateBase,   QColor("#16202a"))
    p.setColor(QPalette.Button,          QColor("#2c3e50"))
    p.setColor(QPalette.ButtonText,      QColor("#ecf0f1"))
    p.setColor(QPalette.Highlight,       QColor("#3498db"))
    p.setColor(QPalette.HighlightedText, QColor("#ffffff"))
    p.setColor(QPalette.Text,            QColor("#ecf0f1"))
    p.setColor(QPalette.BrightText,      QColor("#ffffff"))
    p.setColor(QPalette.ToolTipBase,     QColor("#2c3e50"))
    p.setColor(QPalette.ToolTipText,     QColor("#ecf0f1"))
    p.setColor(QPalette.Link,            QColor("#3498db"))
    p.setColor(QPalette.Disabled, QPalette.Text,       QColor("#566573"))
    p.setColor(QPalette.Disabled, QPalette.ButtonText, QColor("#566573"))
    return p


# ---------------------------------------------------------------------------
# Feuilles de style
# ---------------------------------------------------------------------------

_LIGHT_QSS = """
    QMainWindow { background:#ecf0f1; }
    QMenuBar { background:#2c3e50; color:white; }
    QMenuBar::item:selected { background:#3498db; }
    QMenu { background:#2c3e50; color:white; border:1px solid #34495e; }
    QMenu::item:selected { background:#3498db; }
    QDockWidget::title {
        background:#34495e; color:white;
        padding:6px; font-weight:bold;
    }
    QToolBar { background:#ecf0f1; border-bottom:1px solid #bdc3c7; }
    QProgressBar {
        border:1px solid #bdc3c7; border-radius:4px; text-align:center;
    }
    QProgressBar::chunk { background:#3498db; border-radius:4px; }
    QTabWidget::pane { border:1px solid #bdc3c7; }
    QTabBar::tab {
        background:#dfe6e9; padding:6px 14px;
        border:1px solid #bdc3c7; border-bottom:none; margin-right:2px;
    }
    QTabBar::tab:selected { background:white; }
    QGroupBox {
        border:1px solid #bdc3c7; border-radius:4px;
        margin-top:8px; padding-top:6px;
    }
    QGroupBox::title { subcontrol-origin:margin; left:8px; color:#2c3e50; }
"""

_DARK_QSS = """
    QMainWindow  { background:#1a252f; }
    QWidget      { background:#1a252f; color:#ecf0f1; }
    QMenuBar     { background:#16202a; color:#ecf0f1; }
    QMenuBar::item:selected { background:#3498db; }
    QMenu        { background:#16202a; color:#ecf0f1; border:1px solid #2c3e50; }
    QMenu::item:selected { background:#3498db; }
    QDockWidget  { background:#1a252f; }
    QDockWidget::title {
        background:#16202a; color:#ecf0f1;
        padding:6px; font-weight:bold;
    }
    QToolBar     { background:#16202a; border-bottom:1px solid #2c3e50; }
    QProgressBar {
        border:1px solid #2c3e50; border-radius:4px;
        text-align:center; background:#1e2d3a; color:#ecf0f1;
    }
    QProgressBar::chunk { background:#3498db; border-radius:4px; }
    QTabWidget::pane { border:1px solid #2c3e50; }
    QTabBar::tab {
        background:#16202a; color:#bdc3c7; padding:6px 14px;
        border:1px solid #2c3e50; border-bottom:none; margin-right:2px;
    }
    QTabBar::tab:selected { background:#1e2d3a; color:#ecf0f1; }
    QGroupBox {
        border:1px solid #2c3e50; border-radius:4px;
        margin-top:8px; padding-top:6px; color:#ecf0f1;
    }
    QGroupBox::title { subcontrol-origin:margin; left:8px; color:#bdc3c7; }
    QLabel       { color:#ecf0f1; }
    QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {
        background:#1e2d3a; color:#ecf0f1;
        border:1px solid #2c3e50; border-radius:3px; padding:3px;
    }
    QLineEdit:focus, QSpinBox:focus,
    QDoubleSpinBox:focus, QComboBox:focus { border:1px solid #3498db; }
    QPushButton {
        background:#2c3e50; color:#ecf0f1;
        border:1px solid #34495e; border-radius:4px; padding:5px 12px;
    }
    QPushButton:hover   { background:#34495e; }
    QPushButton:pressed { background:#3498db; }
    QTreeWidget {
        background:#1e2d3a; color:#ecf0f1;
        border:none; font-size:12px;
    }
    QTreeWidget::item          { padding:3px; }
    QTreeWidget::item:selected { background:#3498db; color:white; }
    QScrollBar:vertical {
        background:#16202a; width:10px; border:none;
    }
    QScrollBar::handle:vertical       { background:#2c3e50; border-radius:5px; }
    QScrollBar::handle:vertical:hover { background:#34495e; }
    QScrollBar:horizontal {
        background:#16202a; height:10px; border:none;
    }
    QScrollBar::handle:horizontal       { background:#2c3e50; border-radius:5px; }
    QScrollBar::handle:horizontal:hover { background:#34495e; }
    QHeaderView::section {
        background:#16202a; color:#bdc3c7;
        border:1px solid #2c3e50; padding:3px;
    }
    QTableWidget {
        background:#1e2d3a; color:#ecf0f1; gridline-color:#2c3e50;
    }
    QDialog     { background:#1a252f; color:#ecf0f1; }
    QStatusBar  { background:#16202a; color:#bdc3c7; }
"""

_LIGHT_TREE_QSS = (
    "QTreeWidget { border:none; font-size:12px; }"
    "QTreeWidget::item { padding:3px; }"
    "QTreeWidget::item:selected { background:#3498db; color:white; }"
)

_DARK_TREE_QSS = (
    "QTreeWidget { border:none; font-size:12px;"
    "  background:#1e2d3a; color:#ecf0f1; }"
    "QTreeWidget::item { padding:3px; }"
    "QTreeWidget::item:selected { background:#3498db; color:white; }"
)


# ---------------------------------------------------------------------------
# ThemeManager
# ---------------------------------------------------------------------------

class ThemeManager:
    """Charge, sauvegarde et applique les thèmes de l'application."""

    @staticmethod
    def _read_config() -> dict:
        """
        Lit le fichier config.json et retourne son contenu.

        :return: Dictionnaire de configuration, ou dict vide en cas d'erreur.
        """
        try:
            with open(_CONFIG_PATH, encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    @staticmethod
    def _write_config(config: dict):
        """
        Écrit le dictionnaire de configuration dans config.json.

        :param config: Dictionnaire à sérialiser en JSON.
        """
        with open(_CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

    @staticmethod
    def load_theme() -> str:
        """Retourne le thème sauvegardé ('light' par défaut)."""
        return ThemeManager._read_config().get("theme", "light")

    @staticmethod
    def save_theme(theme: str):
        """Persiste le thème dans config.json."""
        config = ThemeManager._read_config()
        config["theme"] = theme
        ThemeManager._write_config(config)

    @staticmethod
    def load_lang() -> str:
        """Retourne la dernière langue choisie ('Français' par défaut)."""
        return ThemeManager._read_config().get("lang", "Français")

    @staticmethod
    def save_lang(lang: str):
        """Persiste la langue dans config.json."""
        config = ThemeManager._read_config()
        config["lang"] = lang
        ThemeManager._write_config(config)

    @staticmethod
    def get_palette(theme: str) -> QPalette:
        """
        Retourne la palette Qt correspondant au thème.

        :param theme: Identifiant du thème ('light' ou 'dark').
        :return: Instance QPalette configurée.
        """
        if theme == "dark":
            return _dark_palette()
        else:
            return _light_palette()

    @staticmethod
    def get_stylesheet(theme: str) -> str:
        """
        Retourne la feuille de style QSS globale pour le thème.

        :param theme: Identifiant du thème ('light' ou 'dark').
        :return: Chaîne QSS.
        """
        if theme == "dark":
            return _DARK_QSS
        else:
            return _LIGHT_QSS

    @staticmethod
    def get_tree_stylesheet(theme: str) -> str:
        """
        Retourne la feuille de style QSS spécifique à l'arbre latéral.

        :param theme: Identifiant du thème ('light' ou 'dark').
        :return: Chaîne QSS.
        """
        if theme == "dark":
            return _DARK_TREE_QSS
        else:
            return _LIGHT_TREE_QSS
