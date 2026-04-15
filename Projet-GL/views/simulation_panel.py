# views/simulation_panel.py
"""SimulationPanel — graphiques temps réel par composant (PyQtGraph, 30 fps sans saccade)."""
from typing import Any, Dict, List

import numpy as np
import pyqtgraph as pg
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QLabel, QProgressBar, QScrollArea, QSizePolicy,
    QVBoxLayout, QWidget,
)

# Antialiasing global, pas d'OpenGL requis
pg.setConfigOptions(antialias=True, useOpenGL=False)

# Palette de courbes
_COLORS = [
    "#e74c3c", "#3498db", "#2ecc71", "#f39c12",
    "#9b59b6", "#1abc9c", "#e67e22", "#00bcd4",
    "#e91e63", "#cddc39",
]

_THEME: Dict[str, Dict[str, str]] = {
    "dark": {
        "bg":     "#1e2d3a",
        "fg":     "#ecf0f1",
        "grid":   "#2c3e50",
        "axis":   "#bdc3c7",
        "legend": "#ecf0f1",
    },
    "light": {
        "bg":     "#f4f6f8",
        "fg":     "#2c3e50",
        "grid":   "#ced4da",
        "axis":   "#555555",
        "legend": "#2c3e50",
    },
}


def _tcfg(theme: str) -> Dict[str, str]:
    return _THEME.get(theme, _THEME["light"])


# ---------------------------------------------------------------------------
# Widget graphique d'un composant
# ---------------------------------------------------------------------------

class ComponentChart(QWidget):
    """
    Un PlotWidget PyQtGraph par composant.
    Les points sont bufferisés (push_data) et rendus en lot (flush)
    par un QTimer externe — jamais plus d'un dessin par frame.
    """

    def __init__(
        self,
        comp_name: str,
        columns: List[str],
        theme: str = "light",
        parent=None,
    ):
        super().__init__(parent)
        self.comp_name = comp_name
        self.columns = columns
        cfg = _tcfg(theme)

        height_px = max(260, 170 + 32 * len(columns))

        # --- PlotWidget ---
        self.plot = pg.PlotWidget(background=cfg["bg"])
        self.plot.setMinimumHeight(height_px)
        self.plot.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        # Axes
        for side in ("bottom", "left"):
            axis = self.plot.getAxis(side)
            axis.setTextPen(pg.mkPen(cfg["axis"]))
            axis.setPen(pg.mkPen(cfg["axis"], width=1))
        self.plot.getAxis("bottom").setLabel(
            "Temps (s)", color=cfg["fg"], size="9pt"
        )
        self.plot.showGrid(x=True, y=True, alpha=0.18)

        # Titre
        self._set_title(cfg)

        # Légende
        self._legend = self.plot.addLegend(
            offset=(10, 10),
            labelTextSize="8pt",
        )
        self._legend.setLabelTextColor(pg.mkColor(cfg["legend"]))

        # Courbes
        self._curves: Dict[str, pg.PlotDataItem] = {}
        for i, col in enumerate(columns):
            label = col.replace(f"{comp_name}_", "", 1)
            curve = self.plot.plot(
                [],
                [],
                name=label,
                pen=pg.mkPen(color=_COLORS[i % len(_COLORS)], width=2.2),
                connect="finite",
            )
            self._curves[col] = curve

        # Buffer et données accumulées
        self._x: List[float] = []
        self._y: Dict[str, List[float]] = {col: [] for col in columns}
        self._pending: List[tuple] = []

        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 4, 6, 6)
        layout.addWidget(self.plot)

    # ------------------------------------------------------------------
    # API publique
    # ------------------------------------------------------------------

    def push_data(self, t: float, values: Dict[str, float]) -> None:
        """Empile un point dans le buffer (thread-safe pour le thread Qt principal)."""
        self._pending.append((t, values))

    def flush(self) -> None:
        """Traite le buffer et redessine une seule fois (appelé par le QTimer 30 fps)."""
        if not self._pending:
            return
        for t, values in self._pending:
            self._x.append(t)
            for col in self.columns:
                self._y[col].append(values.get(col, float("nan")))
        self._pending.clear()

        x = np.asarray(self._x, dtype=np.float64)
        for col, curve in self._curves.items():
            curve.setData(x, np.asarray(self._y[col], dtype=np.float64))

    def clear(self) -> None:
        self._x.clear()
        for col in self._y:
            self._y[col].clear()
        self._pending.clear()
        for curve in self._curves.values():
            curve.setData([], [])

    def set_theme(self, theme: str) -> None:
        cfg = _tcfg(theme)
        self.plot.setBackground(cfg["bg"])
        for side in ("bottom", "left"):
            ax = self.plot.getAxis(side)
            ax.setTextPen(pg.mkPen(cfg["axis"]))
            ax.setPen(pg.mkPen(cfg["axis"], width=1))
        self.plot.getAxis("bottom").setLabel("Temps (s)", color=cfg["fg"], size="9pt")
        self._legend.setLabelTextColor(pg.mkColor(cfg["legend"]))
        self._set_title(cfg)

    # ------------------------------------------------------------------

    def _set_title(self, cfg: Dict[str, str]) -> None:
        self.plot.setTitle(
            f"<span style='color:{cfg['fg']}; font-size:10pt; font-weight:600;'>"
            f"{self.comp_name}</span>",
        )


# ---------------------------------------------------------------------------
# Panneau principal
# ---------------------------------------------------------------------------

class SimulationPanel(QWidget):
    """
    Onglet de simulation : statut, barre de progression,
    et graphiques PyQtGraph 30 fps par composant.
    """

    def __init__(self, theme: str = "light", parent=None):
        super().__init__(parent)
        self._theme = theme
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

        # --- Statut ---
        self.status_label = QLabel("En attente — aucune simulation lancée.")
        font = QFont()
        font.setPointSize(11)
        font.setBold(True)
        self.status_label.setFont(font)
        layout.addWidget(self.status_label)

        # --- Barre de progression ---
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFixedHeight(24)
        layout.addWidget(self.progress_bar)

        # --- Zone déroulante ---
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setFrameShape(QScrollArea.NoFrame)

        self._charts_container = QWidget()
        self._charts_layout = QVBoxLayout(self._charts_container)
        self._charts_layout.setSpacing(14)
        self._charts_layout.setContentsMargins(0, 4, 0, 4)

        self._placeholder = QLabel(
            "<center style='color:#7f8c8d; font-size:12px; padding:50px;'>"
            "Les graphiques par composant apparaîtront ici<br>"
            "au démarrage de la simulation.</center>"
        )
        self._charts_layout.addWidget(self._placeholder)
        self._charts_layout.addStretch()

        self._scroll.setWidget(self._charts_container)
        layout.addWidget(self._scroll)

        self._component_charts: Dict[str, ComponentChart] = {}

        # --- Timer 30 fps ---
        self._refresh_timer = QTimer(self)
        self._refresh_timer.setInterval(33)   # ~30 fps
        self._refresh_timer.timeout.connect(self._flush_all)

    # ------------------------------------------------------------------
    # Interface publique
    # ------------------------------------------------------------------

    def set_status(self, text: str, color: str = "#2c3e50") -> None:
        self.status_label.setText(text)
        self.status_label.setStyleSheet(
            f"font-size:13px; font-weight:bold; color:{color};"
        )

    def update_progress(self, value: int) -> None:
        self.progress_bar.setValue(value)

    def init_charts(self, components) -> None:
        """Crée un graphique par composant juste avant le lancement."""
        self._refresh_timer.stop()

        # Vider le layout
        while self._charts_layout.count():
            item = self._charts_layout.takeAt(0)
            w = item.widget()
            if w is not None:
                w.deleteLater()
        self._component_charts.clear()

        for comp in components:
            cols: List[str] = [f"{comp.name}_{k}" for k in comp.outputs]
            cols += [f"{comp.name}_{s.name}[{s.unit}]" for s in comp.sensors]
            if not cols:
                continue
            chart = ComponentChart(comp.name, cols, theme=self._theme)
            self._component_charts[comp.name] = chart
            self._charts_layout.addWidget(chart)

        if not self._component_charts:
            self._charts_layout.addWidget(
                QLabel(
                    "<center style='color:#7f8c8d;'>"
                    "Aucun composant avec des données à afficher.</center>"
                )
            )

        self._charts_layout.addStretch()
        self._refresh_timer.start()

    def update_live_data(self, data: Dict[str, Any]) -> None:
        """Reçoit un point depuis DataController et l'empile dans les charts."""
        t = data.get("Temps_s", 0.0)
        for chart in self._component_charts.values():
            values = {col: data[col] for col in chart.columns if col in data}
            chart.push_data(t, values)

    def set_theme(self, theme: str) -> None:
        self._theme = theme
        for chart in self._component_charts.values():
            chart.set_theme(theme)

    # ------------------------------------------------------------------

    def _flush_all(self) -> None:
        for chart in self._component_charts.values():
            chart.flush()
