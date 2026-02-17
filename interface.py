import sys
from PyQt5.QtWidgets import QApplication, QWidget, QFrame, QPushButton


# Subclass QMainWindow to customize your application's main window
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Widgets")
        self.resize(300, 200)        
        
        # Création de la frame
        frame = QFrame(self)
        frame.setGeometry(50, 50, 200, 150)  # x, y, largeur, hauteur
        frame.setFrameShape(QFrame.Box)     # forme de la frame
        frame.setFrameShadow(QFrame.Raised) # style d'ombre
        frame.addWidget(QPushButton("capteur"))
        frame.addWidget(QPushButton("Center"))
        frame.addWidget(QPushButton("Right"))
app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()
