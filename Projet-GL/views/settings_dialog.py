# views/settings_dialog.py
"""SettingsDialog — dialogue de paramètres (thème de l'interface).
La langue est choisie au démarrage et ne peut pas être modifiée en cours de session.
"""
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import (
    QButtonGroup, QDialog, QDialogButtonBox,
    QGroupBox, QRadioButton, QVBoxLayout,
)


class SettingsDialog(QDialog):
    """Dialogue de paramètres — permet de choisir le thème visuel."""

    theme_changed = pyqtSignal(str)

    def __init__(self, current_theme: str, parent=None):
        """
        Construit le dialogue de paramètres avec le thème courant présélectionné.

        :param current_theme: Thème actif ('light' ou 'dark').
        :param parent: Widget Qt parent (facultatif).
        """
        super().__init__(parent)
        self.setWindowTitle("Paramètres")
        self.setMinimumWidth(300)
        self._current_theme = current_theme
        self._build()

    def _build(self):
        """Construit le formulaire de sélection du thème visuel."""
        layout = QVBoxLayout(self)

        group = QGroupBox("Thème de l'interface")
        group_layout = QVBoxLayout(group)

        self._btn_light = QRadioButton("Clair")
        self._btn_dark  = QRadioButton("Sombre")

        self._btn_group = QButtonGroup(self)
        self._btn_group.addButton(self._btn_light)
        self._btn_group.addButton(self._btn_dark)

        if self._current_theme == "dark":
            self._btn_dark.setChecked(True)
        else:
            self._btn_light.setChecked(True)

        group_layout.addWidget(self._btn_light)
        group_layout.addWidget(self._btn_dark)
        layout.addWidget(group)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _on_accept(self):
        """Émet le signal ``theme_changed`` avec le thème sélectionné et ferme le dialogue."""
        theme = "dark" if self._btn_dark.isChecked() else "light"
        self.theme_changed.emit(theme)
        self.accept()
