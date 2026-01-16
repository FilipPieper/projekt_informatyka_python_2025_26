from PyQt5.QtWidgets import QWidget, QPushButton, QLabel
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPainter, QColor, QPen


class SideScreen(QWidget):
    def __init__(self, main_screen):
        super().__init__()
        self.main_screen = main_screen

        self.setWindowTitle("Side Screen - Zbiornik 1 (podgląd)")
        self.setFixedSize(800, 600)
        self.setStyleSheet("background-color: #2b2b2b;")

        # Ten sam zbiornik co na MainScreen (Zbiornik 1)
        self.zb = self.main_screen.zbiorniki[0]

        # Opis
        lbl = QLabel("Podgląd: Zbiornik 1", self)
        lbl.setStyleSheet("color: white; font-size: 18px;")
        lbl.setAlignment(Qt.AlignCenter)
        lbl.setGeometry(200, 20, 400, 40)

        # Przycisk powrotu
        btn_back = QPushButton("⬅ Powrót", self)
        btn_back.setGeometry(300, 540, 200, 40)
        btn_back.clicked.connect(self.go_back)

        # Odświeżanie widoku (żeby podziałka i poziom żyły)
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.update)
        self.refresh_timer.start(50)  # 20 FPS

    def go_back(self):
        self.close()
        self.main_screen.show()

    # ----------------------------
    # RYSOWANIE
    # ----------------------------
    def paintEvent(self, event):
        p = QPainter(self)
        try:
            p.setRenderHint(QPainter.Antialiasing)

            # Duży zbiornik (pozycja + rozmiar na SideScreen)
            x, y, w, h = 220, 90, 260, 400

            self.draw_big_tank(p, x, y, w, h)
            self.draw_scale(p, x, y, w, h)

        finally:
            p.end()

    def draw_big_tank(self, p: QPainter, x: int, y: int, w: int, h: int):
        """
        Rysuje duży zbiornik 1: ciecz + obrys + podpisy.
        """
        poziom = self.zb.poziom  # 0..1

        # Ciecz
        if poziom > 0:
            h_cieczy = int(h * poziom)
            if h_cieczy >= 4:
                y0 = y + h - h_cieczy
                p.setPen(Qt.NoPen)
                p.setBrush(QColor(0, 120, 255, 200))
                p.drawRect(x + 4, y0 + 2, w - 8, h_cieczy - 4)

        # Obrys
        p.setPen(QPen(Qt.white, 3))
        p.setBrush(Qt.NoBrush)
        p.drawRect(x, y, w, h)

        # Napisy
        p.setPen(Qt.white)
        p.drawText(x, y - 10, self.zb.nazwa)
        p.drawText(x, y + h + 25, f"{poziom * 100:.0f}%")

    def draw_scale(self, p: QPainter, x: int, y: int, w: int, h: int):
        """
        Podziałka po prawej stronie zbiornika:
        - małe kreski co 10%
        - większe co 20% + opis (0..100)
        """
        scale_x = x + w + 40  # gdzie rysujemy podziałkę (na prawo od zbiornika)

        # Linia podziałki
        p.setPen(QPen(Qt.white, 2))
        p.drawLine(scale_x, y, scale_x, y + h)

        for percent in range(0, 101, 10):
            # percent=0 na dole, percent=100 na górze
            yy = int(y + h - (percent / 100.0) * h)

            is_major = (percent % 20 == 0)
            tick_len = 18 if is_major else 10

            # kreska
            p.setPen(QPen(Qt.white, 2))
            p.drawLine(scale_x - tick_len, yy, scale_x, yy)

            # opis dla większych
            if is_major:
                p.setPen(Qt.white)
                p.drawText(scale_x + 8, yy + 5, f"{percent}%")
