# views/language_dialog.py
"""LanguageDialog — sélection de la langue au démarrage de LambdaSys."""
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QButtonGroup, QDialog, QDialogButtonBox,
    QLabel, QRadioButton, QVBoxLayout,
)


class LanguageDialog(QDialog):
    """
    Dialogue modal affiché une seule fois au lancement.
    L'utilisateur choisit la langue de l'interface ; ce choix est
    verrouillé pour toute la durée de la session.
    """

    LANGUAGES = ["Français", "English"]

    def __init__(self, default_lang: str = "Français", parent=None):
        super().__init__(parent)
        self.setWindowTitle("LambdaSys — Choix de la langue / Language")
        self.setMinimumWidth(320)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self._selected = default_lang
        self._build()

    def _build(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        title = QLabel("<b>Choisissez votre langue / Choose your language</b>")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("", 11))
        layout.addWidget(title)

        self._btn_group = QButtonGroup(self)
        for lang in self.LANGUAGES:
            btn = QRadioButton(lang)
            btn.setFont(QFont("", 11))
            if lang == self._selected:
                btn.setChecked(True)
            btn.toggled.connect(lambda checked, l=lang: self._on_toggle(checked, l))
            self._btn_group.addButton(btn)
            layout.addWidget(btn)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok)
        buttons.accepted.connect(self.accept)
        layout.addWidget(buttons)

    def _on_toggle(self, checked: bool, lang: str) -> None:
        if checked:
            self._selected = lang

    @property
    def selected_language(self) -> str:
        return self._selected
