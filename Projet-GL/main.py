# main.py
"""
Point d'entrée principal de l'application LambdaSys.

Lance le contrôleur principal après avoir initialisé
l'application Qt et appliqué le thème persistant.
"""
import sys

from PyQt5.QtWidgets import QApplication

from controllers.main_window_controller import MainWindowController
from themes import ThemeManager


def main():
    """Initialiser Qt, appliquer le thème et démarrer l'application.

    Crée l'instance QApplication, charge le thème sauvegardé dans
    ``config.json``, instancie le contrôleur principal et entre
    dans la boucle d'événements Qt.
    """
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setApplicationName("LambdaSys")

    theme = ThemeManager.load_theme()
    app.setPalette(ThemeManager.get_palette(theme))

    controller = MainWindowController()
    controller.run()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
