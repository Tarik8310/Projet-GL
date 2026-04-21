# views/properties_panel.py
"""PropertiesPanel — panneau de propriétés contextuel (dock droit)."""
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtWidgets import (
    QFrame, QLabel, QPushButton, QScrollArea, QVBoxLayout, QWidget,
)

from models.component import Component
from models.sensor import Sensor
from simulation.anomaly import Anomaly


class PropertiesPanel(QScrollArea):
    """
    Affiche les propriétés de l'élément sélectionné dans l'arbre.
    Émet des signaux vers les contrôleurs pour les actions métier.
    """

    sensor_add_requested = pyqtSignal(object)        # Component
    sensor_delete_requested = pyqtSignal(object)     # Sensor
    anomaly_add_requested = pyqtSignal(object)       # Component
    anomaly_delete_requested = pyqtSignal(object)    # Anomaly
    component_toggle_requested = pyqtSignal(object)  # Component

    def __init__(self, parent=None):
        """
        Construit le panneau de propriétés avec un conteneur déroulant vide.

        :param parent: Widget Qt parent (facultatif).
        """
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._container = QWidget()
        self._layout = QVBoxLayout(self._container)
        self._layout.setAlignment(Qt.AlignTop)
        self._layout.setSpacing(6)
        self.setWidget(self._container)
        self.show_empty()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _clear(self):
        """Supprime tous les widgets du panneau pour préparer un nouvel affichage."""
        while self._layout.count():
            item = self._layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    @staticmethod
    def _sep() -> QFrame:
        """Crée et retourne un séparateur horizontal stylisé."""
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("color:#bdc3c7; margin:4px 0;")
        return sep

    def _btn(self, text: str, color: str) -> QPushButton:
        """
        Crée un bouton coloré standardisé.

        :param text: Libellé du bouton.
        :param color: Couleur de fond en notation hexadécimale.
        :return: Instance de QPushButton stylisée.
        """
        btn = QPushButton(text)
        btn.setStyleSheet(
            f"background-color:{color}; color:white; padding:5px; border-radius:4px;"
        )
        return btn

    # ------------------------------------------------------------------
    # Affichages
    # ------------------------------------------------------------------

    def show_empty(self):
        """Affiche un message invitant l'utilisateur à sélectionner un élément."""
        self._clear()
        lbl = QLabel("Sélectionnez un élément\ndans l'arborescence.")
        lbl.setAlignment(Qt.AlignCenter)
        lbl.setStyleSheet("color:#95a5a6; font-style:italic; padding:20px;")
        self._layout.addWidget(lbl)

    def show_component(self, comp: Component):
        """
        Affiche les propriétés d'un composant et les boutons d'action associés.

        :param comp: Composant sélectionné dans l'arbre.
        """
        self._clear()

        title = QLabel(f"<b>{comp.name}</b>")
        title.setStyleSheet("font-size:14px; color:#2c3e50;")
        self._layout.addWidget(title)
        self._layout.addWidget(QLabel("Type : <i>Composant</i>"))

        if comp.is_operational:
            color = "#27ae60"
            text = "Opérationnel ✔"
            toggle_label = "Mettre hors service"
        else:
            color = "#e74c3c"
            text = "Hors service ✘"
            toggle_label = "Remettre en service"
        self._layout.addWidget(
            QLabel(f"État : <span style='color:{color}'><b>{text}</b></span>")
        )

        btn_toggle = self._btn(
            toggle_label,
            "#e67e22",
        )
        btn_toggle.clicked.connect(lambda: self.component_toggle_requested.emit(comp))
        self._layout.addWidget(btn_toggle)

        self._layout.addWidget(self._sep())
        self._layout.addWidget(QLabel(f"<b>Sorties ({len(comp.outputs)})</b>"))
        for name in comp.outputs:
            self._layout.addWidget(QLabel(f"  • {name}"))

        self._layout.addWidget(self._sep())
        self._layout.addWidget(QLabel(f"<b>Capteurs ({len(comp.sensors)})</b>"))

        btn_add = self._btn("＋  Ajouter un capteur", "#27ae60")
        btn_add.clicked.connect(lambda: self.sensor_add_requested.emit(comp))
        self._layout.addWidget(btn_add)

        self._layout.addWidget(self._sep())
        self._layout.addWidget(QLabel(f"<b>Anomalies ({len(comp.anomalies)})</b>"))

        btn_anom = self._btn("⚠  Ajouter une anomalie", "#e74c3c")
        btn_anom.clicked.connect(lambda: self.anomaly_add_requested.emit(comp))
        self._layout.addWidget(btn_anom)

    def show_sensor(self, sensor: Sensor):
        """
        Affiche les propriétés d'un capteur et le bouton de suppression.

        :param sensor: Capteur sélectionné dans l'arbre.
        """
        self._clear()

        title = QLabel(f"<b>{sensor.name}</b>")
        title.setStyleSheet("font-size:14px; color:#2980b9;")
        self._layout.addWidget(title)
        self._layout.addWidget(QLabel("Type : <i>Capteur</i>"))
        self._layout.addWidget(QLabel(f"Sortie mesurée : {sensor.target_output}"))
        self._layout.addWidget(QLabel(f"Unité : {sensor.unit}"))
        self._layout.addWidget(QLabel(f"Fréquence : {sensor.frequency} Hz"))
        if sensor.component:
            self._layout.addWidget(QLabel(f"Composant : {sensor.component.name}"))

        self._layout.addWidget(self._sep())
        btn_del = self._btn("🗑  Supprimer ce capteur", "#95a5a6")
        btn_del.clicked.connect(lambda: self.sensor_delete_requested.emit(sensor))
        self._layout.addWidget(btn_del)

    def show_anomaly(self, anomaly: Anomaly):
        """
        Affiche les propriétés d'une anomalie et le bouton de suppression.

        :param anomaly: Anomalie sélectionnée dans l'arbre.
        """
        self._clear()

        title = QLabel(f"<b>{anomaly.name}</b>")
        title.setStyleSheet("font-size:14px; color:#e74c3c;")
        self._layout.addWidget(title)
        self._layout.addWidget(QLabel("Type : <i>Anomalie</i>"))
        self._layout.addWidget(QLabel(f"Catégorie : {anomaly.anomaly_type.value}"))
        self._layout.addWidget(QLabel(f"Mode : {anomaly.mode.value}"))
        self._layout.addWidget(QLabel(f"Début : {anomaly.start_time} s"))
        self._layout.addWidget(QLabel(f"Durée : {anomaly.duration} s"))
        if anomaly.mode.value == "Relative (%)":
            suffix = " %"
        else:
            suffix = ""
        self._layout.addWidget(QLabel(f"Magnitude : {anomaly.magnitude}{suffix}"))

        self._layout.addWidget(self._sep())
        btn_del = self._btn("🗑  Supprimer cette anomalie", "#95a5a6")
        btn_del.clicked.connect(lambda: self.anomaly_delete_requested.emit(anomaly))
        self._layout.addWidget(btn_del)
