import math
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QTimer, QRectF
from PyQt6.QtGui import QPainter, QColor, QBrush, QPen, QRadialGradient

class DistaAvatar(QWidget):
    """
    Interactive Pixel-Art Humanoid Robot Avatar
    Renders a 16x16 pixel matrix humanoid robot face with glowing animations
    and state transitions (IDLE, LISTENING, THINKING, SPEAKING).
    """

    IDLE = "idle"
    LISTENING = "listening"
    THINKING = "thinking"
    SPEAKING = "speaking"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(220, 220)
        self.state = self.IDLE
        self.frame = 0
        self.blink_timer = 0
        self.is_blinking = False

        # 30 FPS animation timer
        self.anim_timer = QTimer(self)
        self.anim_timer.timeout.connect(self._on_tick)
        self.anim_timer.start(33)

        # 16x16 Pixel Art Matrices for Face Components
        # 1 = Outer Frame, 2 = Face Plate, 3 = Eyes (Orange), 4 = Mouth, 5 = Glow/Accent, 6 = Thinking Scan
        self.base_head = [
            [0,0,0,0,5,5,5,5,5,5,5,5,0,0,0,0],
            [0,0,0,1,1,1,1,1,1,1,1,1,1,0,0,0],
            [0,0,1,2,2,2,2,2,2,2,2,2,2,1,0,0],
            [0,1,2,2,2,2,2,2,2,2,2,2,2,2,1,0],
            [0,1,2,3,3,2,2,2,2,2,2,3,3,2,1,0],
            [0,1,2,3,3,2,2,2,2,2,2,3,3,2,1,0],
            [0,1,2,2,2,2,2,2,2,2,2,2,2,2,1,0],
            [0,1,2,2,2,2,2,5,5,2,2,2,2,2,1,0],
            [0,1,2,2,2,2,2,2,2,2,2,2,2,2,1,0],
            [0,1,2,2,4,4,4,4,4,4,4,4,2,2,1,0],
            [0,1,2,2,2,4,4,4,4,4,4,2,2,2,1,0],
            [0,0,1,2,2,2,2,2,2,2,2,2,2,1,0,0],
            [0,0,0,1,1,2,2,2,2,2,2,1,1,0,0,0],
            [0,0,0,0,0,1,2,2,2,2,1,0,0,0,0,0],
            [0,0,0,0,0,1,2,2,2,2,1,0,0,0,0,0],
            [0,0,0,0,1,1,1,1,1,1,1,1,0,0,0,0],
        ]

    def set_state(self, new_state: str):
        if self.state != new_state:
            self.state = new_state
            self.update()

    def _on_tick(self):
        self.frame += 1
        
        # Handle random eye blinks
        if self.state == self.IDLE:
            self.blink_timer += 1
            if self.blink_timer > 90:
                self.is_blinking = True
                if self.blink_timer > 96:
                    self.is_blinking = False
                    self.blink_timer = 0
        else:
            self.is_blinking = False

        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)

        w = self.width()
        h = self.height()
        grid_size = min(w, h) * 0.85
        pixel_size = grid_size / 16.0
        offset_x = (w - grid_size) / 2.0
        offset_y = (h - grid_size) / 2.0

        # Draw Ambient Outer Glow Halo
        glow_color = QColor(255, 107, 0, 45)
        if self.state == self.LISTENING:
            glow_color = QColor(0, 229, 255, 65)
        elif self.state == self.SPEAKING:
            pulse = int(40 + 35 * math.sin(self.frame * 0.3))
            glow_color = QColor(255, 136, 0, pulse + 30)
        elif self.state == self.THINKING:
            glow_color = QColor(255, 184, 0, 50)

        rad_grad = QRadialGradient(w / 2.0, h / 2.0, grid_size * 0.6)
        rad_grad.setColorAt(0.0, glow_color)
        rad_grad.setColorAt(1.0, QColor(0, 0, 0, 0))
        painter.setBrush(QBrush(rad_grad))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(QRectF(offset_x - 20, offset_y - 20, grid_size + 40, grid_size + 40))

        # Color Palette
        c_bg_head  = QColor(20, 20, 28)       # 1 = Outer Border
        c_face     = QColor(32, 34, 46)       # 2 = Face Plate
        c_orange   = QColor(255, 107, 0)      # 3 = Orange Eyes
        c_cyan     = QColor(0, 229, 255)      # Listening Eyes/Accents
        c_dark_m   = QColor(14, 15, 22)       # 4 = Mouth Base
        c_accent   = QColor(255, 136, 0)      # 5 = Crown/Ear Accents

        # Thinking scanline Y offset
        scan_row = (self.frame // 2) % 12 + 2 if self.state == self.THINKING else -1

        # Mouth animation frame for speaking
        mouth_open = (self.frame // 3) % 3 if self.state == self.SPEAKING else 0

        for r in range(16):
            for c in range(16):
                val = self.base_head[r][c]
                if val == 0:
                    continue

                cell_color = c_face

                if val == 1:
                    cell_color = c_bg_head
                elif val == 2:
                    cell_color = c_face
                elif val == 3: # EYES
                    if self.is_blinking:
                        cell_color = c_bg_head
                    elif self.state == self.LISTENING:
                        cell_color = c_cyan
                    elif self.state == self.THINKING:
                        cell_color = QColor(255, 184, 0)
                    else:
                        cell_color = c_orange
                elif val == 4: # MOUTH
                    if self.state == self.SPEAKING:
                        if mouth_open == 1 and r == 9:
                            cell_color = c_orange
                        elif mouth_open == 2 and r in (9, 10):
                            cell_color = c_orange
                        else:
                            cell_color = c_dark_m
                    elif self.state == self.LISTENING:
                        cell_color = c_cyan if r == 9 and c in (7, 8) else c_dark_m
                    else:
                        cell_color = c_dark_m
                elif val == 5: # ACCENT / CROWN
                    if self.state == self.LISTENING:
                        cell_color = c_cyan
                    elif self.state == self.THINKING:
                        cell_color = QColor(255, 184, 0)
                    else:
                        cell_color = c_accent

                # Thinking scanline overlay
                if r == scan_row and val in (2, 5):
                    cell_color = QColor(255, 200, 50)

                # Draw Pixel Box
                px = offset_x + c * pixel_size
                py = offset_y + r * pixel_size

                painter.setPen(QPen(QColor(10, 10, 15, 180), 0.5))
                painter.setBrush(QBrush(cell_color))
                painter.drawRect(QRectF(px, py, pixel_size - 0.5, pixel_size - 0.5))

        # Draw Side Antenna Glow Points
        antenna_color = c_cyan if self.state == self.LISTENING else c_orange
        painter.setBrush(QBrush(antenna_color))
        painter.setPen(Qt.PenStyle.NoPen)

        if self.state in (self.LISTENING, self.SPEAKING):
            size_pulse = 2 + math.sin(self.frame * 0.4) * 2
            painter.drawEllipse(QRectF(offset_x - 6, offset_y + grid_size * 0.3, 6 + size_pulse, 6 + size_pulse))
            painter.drawEllipse(QRectF(offset_x + grid_size, offset_y + grid_size * 0.3, 6 + size_pulse, 6 + size_pulse))
