from PyQt5.QtWidgets import QWidget, QPushButton, QLabel
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPainter, QColor, QPen


class SideScreen(QWidget):
    W, H = 800, 600
    REFRESH_MS = 50

    TANK_X, TANK_Y = 220, 90
    TANK_W, TANK_H = 260, 400
    SCALE_OFFSET_X = 40

    def __init__(self, main_screen):
        super().__init__()
        self.main_screen = main_screen
        self.zb = self.main_screen.zbiorniki[0]

        self._setup_window()
        self._setup_widgets()
        self._setup_timer()

    # --------------------------------------------------
    # SETUP
    # --------------------------------------------------

    def _setup_window(self):
        self.setWindowTitle("Side Screen - Zbiornik 1 (podgląd)")
        self.setFixedSize(self.W, self.H)
        self.setStyleSheet("background-color: #2b2b2b;")

    def _setup_widgets(self):
        self.lbl_title = QLabel("Podgląd: Zbiornik 1", self)
        self.lbl_title.setStyleSheet("color: white; font-size: 18px;")
        self.lbl_title.setAlignment(Qt.AlignCenter)
        self.lbl_title.setGeometry(200, 20, 400, 40)

        self.btn_back = QPushButton("Powrót", self)
        self.btn_back.setGeometry(300, 540, 200, 40)
        self.btn_back.clicked.connect(self.go_back)

    def _setup_timer(self):
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.update)
        self.refresh_timer.start(self.REFRESH_MS)

    # --------------------------------------------------
    # NAWIGACJA
    # --------------------------------------------------

    def go_back(self):
        self.close()
        self.main_screen.show()

    # --------------------------------------------------
    # RYSOWANIE
    # --------------------------------------------------

    def paintEvent(self, event):
        p = QPainter(self)
        try:
            p.setRenderHint(QPainter.Antialiasing)

            x, y, w, h = self.TANK_X, self.TANK_Y, self.TANK_W, self.TANK_H
            self._draw_tank(p, x, y, w, h)
            self._draw_scale(p, x, y, w, h)

        finally:
            p.end()

    def _draw_tank(self, p: QPainter, x: int, y: int, w: int, h: int):
        poziom = self.zb.poziom

        if poziom > 0:
            liquid_h = int(h * poziom)
            if liquid_h >= 4:
                liquid_y = y + h - liquid_h
                p.setPen(Qt.NoPen)
                p.setBrush(QColor(0, 120, 255, 200))
                p.drawRect(x + 4, liquid_y + 2, w - 8, liquid_h - 4)

        p.setPen(QPen(Qt.white, 3))
        p.setBrush(Qt.NoBrush)
        p.drawRect(x, y, w, h)

        p.setPen(Qt.white)
        p.drawText(x, y - 10, self.zb.nazwa)
        p.drawText(x, y + h + 25, f"{poziom * 100:.0f}%")

    def _draw_scale(self, p: QPainter, x: int, y: int, w: int, h: int):
        sx = x + w + self.SCALE_OFFSET_X

        p.setPen(QPen(Qt.white, 2))
        p.drawLine(sx, y, sx, y + h)

        for percent in range(0, 101, 10):
            yy = int(y + h - (percent / 100.0) * h)
            major = (percent % 20 == 0)
            tick = 18 if major else 10

            p.setPen(QPen(Qt.white, 2))
            p.drawLine(sx - tick, yy, sx, yy)

            if major:
                p.setPen(Qt.white)
                p.drawText(sx + 8, yy + 5, f"{percent}%")
