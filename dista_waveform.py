import math
import random
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QTimer, QRectF
from PyQt6.QtGui import QPainter, QColor, QBrush, QPen

class DistaWaveform(QWidget):
    """
    Dynamic Audio Waveform Visualizer
    Renders pulsating orange and white vertical frequency bars matching the UI design.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(46)
        self.setMinimumWidth(300)
        self.bar_count = 38
        self.is_active = False
        self.phase = 0.0

        # Animation timer (30 FPS)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)
        self.timer.start(33)

    def set_active(self, active: bool):
        self.is_active = active
        self.update()

    def _tick(self):
        self.phase += 0.15
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        w = self.width()
        h = self.height()
        mid_y = h / 2.0

        bar_width = 4.0
        gap = 4.0
        total_width = self.bar_count * (bar_width + gap) - gap
        start_x = (w - total_width) / 2.0

        for i in range(self.bar_count):
            x = start_x + i * (bar_width + gap)

            # Center-weighted bell curve multiplier
            norm_i = (i - self.bar_count / 2.0) / (self.bar_count / 2.0)
            center_weight = math.exp(-3.0 * norm_i * norm_i)

            if self.is_active:
                # Dynamic wave motion
                val = math.sin(self.phase + i * 0.45) * 0.5 + 0.5
                val2 = math.cos(self.phase * 0.8 + i * 0.3) * 0.5 + 0.5
                amplitude = (val * 0.6 + val2 * 0.4) * center_weight
                bar_height = max(4.0, amplitude * (h - 8.0))
            else:
                # Idle subtle breathing
                val = math.sin(self.phase * 0.5 + i * 0.2) * 0.3 + 0.7
                bar_height = max(3.0, (4.0 + val * 6.0) * center_weight)

            top_y = mid_y - bar_height / 2.0

            # Alternating white & orange glow bars
            if i % 3 == 0:
                color = QColor(255, 255, 255, 220)
            elif i % 2 == 0:
                color = QColor(255, 136, 0, 240)
            else:
                color = QColor(255, 107, 0, 255)

            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(color))
            painter.drawRoundedRect(QRectF(x, top_y, bar_width, bar_height), 2.0, 2.0)
