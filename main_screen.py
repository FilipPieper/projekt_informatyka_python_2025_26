from PyQt5.QtWidgets import QWidget, QSlider, QLabel, QPushButton
from PyQt5.QtCore import Qt, QPointF, QTimer
from PyQt5.QtGui import QPainter, QColor, QPen, QPainterPath

from elements import Zbiornik, Rura, Grzalka
from process_logic import ProcessLogic
from SideScreen import SideScreen
from alarm_list import AlarmType, AlarmsMenager
from Alarm_screen import AlarmScreen


class MainScreen(QWidget):
    # --------------------------------------------------
    # USTAWIENIA / STAŁE UI
    # --------------------------------------------------
    WINDOW_W, WINDOW_H = 1080, 800
    PANEL_X = 720
    PANEL_W = 300

    SLIDER_START_Y = 20
    SLIDER_ROW_H = 60

    FLOW_TICK_MS = 30

    def __init__(self):
        super().__init__()

        # --------------------------------------------------
        # SETUP OKNA
        # --------------------------------------------------
        self._setup_window()

        # --------------------------------------------------
        # ALARMY
        # --------------------------------------------------
        self.alarmy = AlarmsMenager()
        self.alarm_screen = None

        # --------------------------------------------------
        # MODEL PROCESU
        # --------------------------------------------------
        self.zbiorniki = self._create_tanks()
        self.logic = ProcessLogic(self.zbiorniki)
        self.zb1, self.zb2, self.zb3, self.zb4 = self.zbiorniki

        # --------------------------------------------------
        # ELEMENTY INSTALACJI (RURY, GRZAŁKI)
        # --------------------------------------------------
        self.rurki = self._create_pipes()
        self.grzalka1, self.grzalka2, self.grzalka3, self.grzalka4 = self._create_heaters()

        # --------------------------------------------------
        # UI: INFO / FLOW / SUWAKI
        # --------------------------------------------------
        self.lbl_info = QLabel("Grzałki:", self)
        self.lbl_info.setGeometry(845, 310, 300, 30)
        self.lbl_info.setStyleSheet("color: white; font-size: 14px;")

        self.btn_flow = self._create_flow_button()
        self.sliders, self.slider_labels = self._create_sliders_panel()

        # --------------------------------------------------
        # UI: NAWIGACJA
        # --------------------------------------------------
        self.btn_side_screen = QPushButton("Otwórz drugi ekran", self)
        self.btn_side_screen.setGeometry(720, 700, 300, 35)
        self.btn_side_screen.setStyleSheet("background:#555; color:white;")
        self.btn_side_screen.clicked.connect(self.open_side_screen)

        self.btn_alarm_screen = QPushButton("ALARMY", self)
        self.btn_alarm_screen.setGeometry(720, 550, 300, 35)
        self.btn_alarm_screen.setStyleSheet("background:#555; color:white;")
        self.btn_alarm_screen.clicked.connect(self.open_alarm_screen)

        self.btn_reset = QPushButton("RESET (poziom + temperatura)", self)
        self.btn_reset.setGeometry(720, 600, 300, 35)
        self.btn_reset.setStyleSheet("background:#7a2b2b; color:white;")
        self.btn_reset.clicked.connect(self.wylej_zbiorniki_wszystkie)

        # --------------------------------------------------
        # UI: PRZYCISKI GRZAŁEK
        # --------------------------------------------------
        self.heater_buttons = []

        btn_start_y = 280 + 60
        for i in range(4):
            btn = QPushButton(f"Włącz {i + 1}", self)
            btn.setGeometry(720, btn_start_y + i * 45, 300, 35)
            btn.setStyleSheet("background:#444; color:white;")
            btn.clicked.connect(lambda _, idx=i: self.toggle_heater(idx))
            self.heater_buttons.append(btn)

        # --------------------------------------------------
        # TIMERY
        # --------------------------------------------------
        self.flow_timer = QTimer(self)
        self.flow_timer.timeout.connect(self.on_flow_tick)
        self.flow_running = False

        self.heater_timer = QTimer(self)
        self.heater_timer.timeout.connect(self.on_heater_tick)
        self.heater_timer.start(200)

    # ==========================================================
    # SETUP / KONSTRUKCJE
    # ==========================================================

    def _setup_window(self):
        self.setWindowTitle("SCADA ")
        self.setFixedSize(self.WINDOW_W, self.WINDOW_H)
        self.setStyleSheet("background-color: #1e1e1e;")

    def _create_tanks(self):
        return [
            Zbiornik(40, 40, pojemnosc=100.0, nazwa="Zbiornik 1", width=140, height=160),
            Zbiornik(200, 220, pojemnosc=100.0, nazwa="Zbiornik 2", width=140, height=160),
            Zbiornik(360, 400, pojemnosc=100.0, nazwa="Zbiornik 3", width=140, height=160),
            Zbiornik(520, 580, pojemnosc=100.0, nazwa="Zbiornik 4", width=140, height=160),
        ]

    def _create_pipes(self):
        return [
            Rura([(180, 185), (290, 185), (290, 220)]),
            Rura([(340, 365), (450, 365), (450, 400)]),
            Rura([(500, 545), (610, 545), (610, 580)]),
        ]

    def _create_heaters(self):
        return (
            Grzalka(nazwa="Grzałka 1", moc=5.0),
            Grzalka(nazwa="Grzałka 2", moc=5.0),
            Grzalka(nazwa="Grzałka 3", moc=5.0),
            Grzalka(nazwa="Grzałka 4", moc=5.0),
        )

    def _create_flow_button(self):
        btn = QPushButton("START/STOP przepływu", self)
        btn.setGeometry(self.PANEL_X, 280, self.PANEL_W, 35)
        btn.setStyleSheet("background:#444; color:white;")
        btn.clicked.connect(self.toggle_flow)
        return btn

    def _create_sliders_panel(self):
        sliders = []
        labels = []

        for i, zb in enumerate(self.zbiorniki):
            y = self.SLIDER_START_Y + i * self.SLIDER_ROW_H

            lbl = QLabel(f"{zb.nazwa}: 0%", self)
            lbl.setStyleSheet("color: white;")
            lbl.setGeometry(self.PANEL_X, y, self.PANEL_W, 20)
            labels.append(lbl)

            s = QSlider(Qt.Horizontal, self)
            s.setGeometry(self.PANEL_X, y + 22, self.PANEL_W, 25)
            s.setMinimum(0)
            s.setMaximum(100)
            s.setValue(int(zb.aktualna_ilosc))
            s.valueChanged.connect(lambda val, idx=i: self.on_slider_change(idx, val))
            sliders.append(s)

        return sliders, labels

    # ==========================================================
    # NAWIGACJA EKRANÓW
    # ==========================================================

    def open_side_screen(self):
        self.side_screen = SideScreen(self)
        self.side_screen.show()
        self.hide()

    def open_alarm_screen(self):
        if self.alarm_screen is None:
            self.alarm_screen = AlarmScreen(self.alarmy)

        self.alarm_screen.show()
        self.alarm_screen.raise_()
        self.alarm_screen.activateWindow()

    # ==========================================================
    # STEROWANIE: FLOW / GRZAŁKI / RESET
    # ==========================================================

    def toggle_flow(self):
        self.flow_running = not self.flow_running

        if self.flow_running:
            self.btn_flow.setText("STOP przepływu")
            self.flow_timer.start(self.FLOW_TICK_MS)
            return

        self.btn_flow.setText("START przepływu")
        self.flow_timer.stop()

        for r in self.rurki:
            r.czy_plynie = False

        self.update()

    def toggle_heater(self, idx: int):
        heaters = [self.grzalka1, self.grzalka2, self.grzalka3, self.grzalka4]
        g = heaters[idx]

        if g.czy_wlaczona:
            g.wylacz()
            self.heater_buttons[idx].setText(f"Włącz {idx + 1}")
        else:
            g.wlacz()
            self.heater_buttons[idx].setText(f"Wyłącz {idx + 1}")

        self.update()

    def wylej_zbiorniki_wszystkie(self):
        for zb in self.zbiorniki:
            zb.aktualna_ilosc = 0.0

        self.grzalka1.temperatura = 20.0
        self.grzalka2.temperatura = 20.0
        self.grzalka3.temperatura = 20.0
        self.grzalka4.temperatura = 20.0

        self.sync_sliders_from_tanks()
        self.update()

    # ==========================================================
    # TIMERY: HEATER / FLOW
    # ==========================================================

    def on_heater_tick(self):
        dt = 0.2

        pairs = [
            (self.zb1, self.grzalka1),
            (self.zb2, self.grzalka2),
            (self.zb3, self.grzalka3),
            (self.zb4, self.grzalka4),
        ]

        for zb, g in pairs:
            if zb.czy_pusty():
                g.wylacz()

            if g.czy_wlaczona:
                g.grzej(dt)
            else:
                g.chlodz(dt)

            if g.temperatura > 40.0 and g.temperatura < 110.0:
                self.alarmy.raise_alarm(zb.nazwa, "Temperatura powyżej 90", AlarmType.WARNING)
            elif g.temperatura > 110.0:
                self.alarmy.raise_alarm(zb.nazwa, "Temperatura osiąga temperaturę krytyczną", AlarmType.CRITICAL)

        self.update()

    def on_flow_tick(self):
        moved = self.logic.step()

        for i, m in enumerate(moved):
            self.rurki[i].czy_plynie = (m > 0)

        self.sync_sliders_from_tanks()
        self.update()

    # ==========================================================
    # SUWAKI
    # ==========================================================

    def sync_sliders_from_tanks(self):
        for i, zb in enumerate(self.zbiorniki):
            val = int(round(zb.aktualna_ilosc))

            self.sliders[i].blockSignals(True)
            self.sliders[i].setValue(val)
            self.sliders[i].blockSignals(False)

            percent = 100 * zb.aktualna_ilosc / zb.pojemnosc if zb.pojemnosc else 0
            self.slider_labels[i].setText(f"{zb.nazwa}: {percent:.0f}%")

    def on_slider_change(self, idx: int, value: int):
        zb = self.zbiorniki[idx]

        if value > 0:
            zb.byl_napelniany = True

        if zb.byl_napelniany:
            min_percent = int(zb.min_poziom * 100)
            if value < min_percent:
                value = min_percent

        zb.aktualna_ilosc = float(value)
        self.slider_labels[idx].setText(f"{zb.nazwa}: {value}%")
        self.update()

    # ==========================================================
    # RYSOWANIE
    # ==========================================================

    def paintEvent(self, event):
        p = QPainter(self)
        try:
            p.setRenderHint(QPainter.Antialiasing)

            for r in self.rurki:
                self.draw_rura(p, r)

            for zb in self.zbiorniki:
                self.draw_zbiornik(p, zb)

            self.draw_grzalka_pod_zbiornikiem(p, self.zb1, self.grzalka1)
            self.draw_grzalka_pod_zbiornikiem(p, self.zb2, self.grzalka2)
            self.draw_grzalka_pod_zbiornikiem(p, self.zb3, self.grzalka3)
            self.draw_grzalka_pod_zbiornikiem(p, self.zb4, self.grzalka4)

        finally:
            p.end()

    # --------------------------------------------------
    # RYSOWANIE: ZBIORNIK
    # --------------------------------------------------

    def draw_zbiornik(self, p: QPainter, zb: Zbiornik):
        poziom = zb.poziom

        if poziom > 0:
            h_cieczy = int(zb.height * poziom)

            if h_cieczy >= 6:
                y0 = zb.y + zb.height - h_cieczy

                w = zb.width - 8
                h = h_cieczy - 4

                if w > 0 and h > 0:
                    p.setPen(Qt.NoPen)
                    p.setBrush(QColor(0, 120, 255, 200))
                    p.drawRect(int(zb.x + 4), int(y0 + 2), int(w), int(h))

        p.setPen(QPen(Qt.white, 3))
        p.setBrush(Qt.NoBrush)
        p.drawRect(int(zb.x), int(zb.y), int(zb.width), int(zb.height))

        p.setPen(Qt.white)
        p.drawText(int(zb.x), int(zb.y - 10), zb.nazwa)
        p.drawText(int(zb.x), int(zb.y + zb.height + 20), f"{poziom * 100:.0f}%")

    # --------------------------------------------------
    # RYSOWANIE: RURA
    # --------------------------------------------------

    def draw_rura(self, p: QPainter, rura: Rura):
        if len(rura.punkty) < 2:
            return

        pts = [QPointF(x, y) for x, y in rura.punkty]

        path = QPainterPath()
        path.moveTo(pts[0])
        for pt in pts[1:]:
            path.lineTo(pt)

        pen_outer = QPen(Qt.gray, 12)
        pen_outer.setCapStyle(Qt.FlatCap)
        pen_outer.setJoinStyle(Qt.MiterJoin)
        p.setPen(pen_outer)
        p.drawPath(path)

        if rura.czy_plynie:
            pen_inner = QPen(QColor(0, 180, 255), 8)
            pen_inner.setCapStyle(Qt.FlatCap)
            pen_inner.setJoinStyle(Qt.MiterJoin)
            p.setPen(pen_inner)
            p.drawPath(path)

    # --------------------------------------------------
    # RYSOWANIE: GRZAŁKA
    # --------------------------------------------------

    def draw_grzalka_pod_zbiornikiem(self, p: QPainter, zb: Zbiornik, grzalka: Grzalka):
        w = 60
        h = 18
        gap = 12

        x = int(zb.x + (zb.width - w) / 2)
        y = int(zb.y + zb.height + gap)

        kolor = QColor(255, 0, 0) if grzalka.czy_wlaczona else QColor(255, 255, 255)

        p.setPen(QPen(Qt.white, 2))
        p.setBrush(kolor)
        p.drawRect(x, y, w, h)

        p.setPen(Qt.white)
        p.drawText(x - 30, y + h + 16, f"{grzalka.nazwa} Tempe: {grzalka.temperatura}")
