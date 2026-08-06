import math
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QTimer, QRectF
from PyQt6.QtGui import QPainter, QColor, QBrush, QPen, QRadialGradient

class DistaAvatar(QWidget):
    """
    Detailed Pixel-Art Humanoid Robot Avatar matching the reference screenshot.
    Renders a 20x20 pixel matrix robot face with glowing orange ring, silver faceplate,
    and state transitions (IDLE, LISTENING, THINKING, SPEAKING).
    """

    IDLE = "idle"
    LISTENING = "listening"
    THINKING = "thinking"
    SPEAKING = "speaking"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(180, 180)
        self.state = self.IDLE
        self.frame = 0
        self.blink_timer = 0
        self.is_blinking = False

        # 30 FPS animation loop
        self.anim_timer = QTimer(self)
        self.anim_timer.timeout.connect(self._on_tick)
        self.anim_timer.start(33)

        # 20x20 Matrix: 1=Dark Outline, 2=Silver Plate, 3=Light Metal, 4=Orange Crest/Collar, 5=Orange Eye, 6=Eye Pupil White, 7=Mouth Line
        self.matrix = [
            [0,0,0,0,0,0,0,4,4,4,4,4,4,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,1,4,4,4,4,4,4,1,0,0,0,0,0,0],
            [0,0,0,0,0,1,2,2,4,4,4,4,2,2,1,0,0,0,0,0],
            [0,0,0,0,1,2,3,3,2,2,2,2,3,3,2,1,0,0,0,0],
            [0,0,0,1,2,3,3,3,3,3,3,3,3,3,3,2,1,0,0,0],
            [0,0,1,2,3,3,3,3,3,3,3,3,3,3,3,3,2,1,0,0],
            [0,0,1,2,3,5,5,5,3,3,3,3,5,5,5,3,2,1,0,0],
            [0,0,1,2,3,5,6,5,3,3,3,3,5,6,5,3,2,1,0,0],
            [0,0,1,2,3,5,5,5,3,3,3,3,5,5,5,3,2,1,0,0],
            [0,0,1,2,3,3,3,3,3,3,3,3,3,3,3,3,2,1,0,0],
            [0,0,1,2,3,3,3,3,2,2,2,2,3,3,3,3,2,1,0,0],
            [0,0,0,1,2,3,3,3,7,7,7,7,3,3,3,2,1,0,0,0],
            [0,0,0,1,2,3,3,3,3,7,7,3,3,3,3,2,1,0,0,0],
            [0,0,0,0,1,2,3,3,3,3,3,3,3,3,2,1,0,0,0,0],
            [0,0,0,0,0,1,2,3,3,3,3,3,3,2,1,0,0,0,0,0],
            [0,0,0,0,0,1,4,2,2,2,2,2,2,4,1,0,0,0,0,0],
            [0,0,0,0,1,4,4,2,2,2,2,2,2,4,4,1,0,0,0,0],
            [0,0,0,1,4,4,4,4,2,2,2,2,4,4,4,4,1,0,0,0],
            [0,0,1,4,4,4,4,4,4,2,2,4,4,4,4,4,4,1,0,0],
            [0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0],
        ]

    def set_state(self, new_state: str):
        if self.state != new_state:
            self.state = new_state
            self.update()

    def _on_tick(self):
        self.frame += 1
        if self.state == self.IDLE:
            self.blink_timer += 1
            if self.blink_timer > 95:
                self.is_blinking = True
                if self.blink_timer > 101:
                    self.is_blinking = False
                    self.blink_timer = 0
        else:
            self.is_blinking = False
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        w = self.width()
        h = self.height()
        cx = w / 2.0
        cy = h / 2.0
        ring_radius = 80.0

        # Outer Glowing Orange Ring (Matching screenshot)
        ring_pen = QPen(QColor(255, 107, 0, 230), 2.5)
        if self.state == self.LISTENING:
            ring_pen = QPen(QColor(0, 229, 255, 240), 3.0)
        elif self.state == self.SPEAKING:
            pulse = int(180 + 70 * math.sin(self.frame * 0.3))
            ring_pen = QPen(QColor(255, 136, 0, pulse), 3.0)

        painter.setPen(ring_pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(QRectF(cx - ring_radius, cy - ring_radius, ring_radius * 2, ring_radius * 2))

        # Soft Ambient Background Glow
        glow_grad = QRadialGradient(cx, cy, ring_radius + 15)
        glow_grad.setColorAt(0.0, QColor(255, 107, 0, 35))
        glow_grad.setColorAt(1.0, QColor(0, 0, 0, 0))
        painter.setBrush(QBrush(glow_grad))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(QRectF(cx - ring_radius - 15, cy - ring_radius - 15, (ring_radius + 15) * 2, (ring_radius + 15) * 2))

        # Render Pixel Robot Grid
        grid_size = 110.0
        pixel_size = grid_size / 20.0
        start_x = cx - grid_size / 2.0
        start_y = cy - grid_size / 2.0 + 4

        # Palette
        c_dark   = QColor(24, 26, 36)
        c_silver = QColor(160, 168, 184)
        c_light  = QColor(215, 222, 235)
        c_orange = QColor(255, 107, 0)
        c_cyan   = QColor(0, 229, 255)
        c_white  = QColor(255, 255, 255)
        c_mouth  = QColor(40, 44, 58)

        mouth_open = (self.frame // 3) % 3 if self.state == self.SPEAKING else 0

        for r in range(20):
            for c in range(20):
                val = self.matrix[r][c]
                if val == 0:
                    continue

                color = c_silver

                if val == 1:
                    color = c_dark
                elif val == 2:
                    color = c_silver
                elif val == 3:
                    color = c_light
                elif val == 4: # Orange Crest/Collar
                    color = c_cyan if self.state == self.LISTENING else c_orange
                elif val == 5: # Eyes
                    if self.is_blinking:
                        color = c_silver
                    elif self.state == self.LISTENING:
                        color = c_cyan
                    else:
                        color = c_orange
                elif val == 6: # Pupil
                    color = c_silver if self.is_blinking else c_white
                elif val == 7: # Mouth
                    if self.state == self.SPEAKING and mouth_open > 0 and r == 12:
                        color = c_orange
                    else:
                        color = c_mouth

                px = start_x + c * pixel_size
                py = start_y + r * pixel_size

                painter.setPen(QPen(QColor(15, 17, 24, 180), 0.4))
                painter.setBrush(QBrush(color))
                painter.drawRect(QRectF(px, py, pixel_size - 0.4, pixel_size - 0.4))
