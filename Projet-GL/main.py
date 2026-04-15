# main.py
"""
LambdaSys — Point d'entrée de l'application.
Lance simplement le MainWindowController.
"""
import sys

from PyQt5.QtWidgets import QApplication

from controllers.main_window_controller import MainWindowController
from themes import ThemeManager


def main() -> None:
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
