from PyQt5.QtWidgets import QWidget, QSlider, QLabel, QPushButton
from PyQt5.QtCore import Qt, QPointF, QTimer
from PyQt5.QtGui import QPainter, QColor, QPen, QPainterPath

from elements import Zbiornik, Rura, Grzalka
from process_logic import ProcessLogic
from SideScreen import SideScreen


class MainScreen(QWidget):
    # -------------------------------
    # Ustawienia / stałe UI
    # -------------------------------
    WINDOW_W, WINDOW_H = 1080, 800
    PANEL_X = 720
    PANEL_W = 300

    SLIDER_START_Y = 20
    SLIDER_ROW_H = 60

    FLOW_TICK_MS = 30

    def __init__(self):
        super().__init__()

        # -------------------------------
        # 1) Konfiguracja okna
        # -------------------------------
        self._setup_window()

        # -------------------------------
        # 2) Model procesu (zbiorniki + logika)
        # -------------------------------
        self.zbiorniki = self._create_tanks()
        self.logic = ProcessLogic(self.zbiorniki)

        # Szybkie aliasy (wygodniej w draw_grzalka...)
        self.zb1, self.zb2, self.zb3, self.zb4 = self.zbiorniki

        # -------------------------------
        # 3) Rury i elementy dodatkowe (grzałki)
        # -------------------------------
        self.rurki = self._create_pipes()
        self.grzalka1, self.grzalka2, self.grzalka3, self.grzalka4 = self._create_heaters()

        # -------------------------------
        # 4) UI: przycisk + suwaki + labelki + teksty
        # -------------------------------

        self.lbl_info = QLabel("Grzałki:", self)
        self.lbl_info.setGeometry(845, 310, 300, 30)
        self.lbl_info.setStyleSheet("color: white; font-size: 14px;")

        self.btn_flow = self._create_flow_button()
        self.sliders, self.slider_labels = self._create_sliders_panel()
        # -------------------------------
        # Przycisk przejścia na drugi ekran
        # -------------------------------
        self.btn_side_screen = QPushButton("Otwórz drugi ekran", self)
        self.btn_side_screen.setGeometry(720, 700, 300, 35)
        self.btn_side_screen.setStyleSheet("background:#555; color:white;")
        self.btn_side_screen.clicked.connect(self.open_side_screen)

        self.btn_reset = QPushButton("RESET (poziom + temperatura)", self)
        self.btn_reset.setGeometry(720, 600, 300, 35)
        self.btn_reset.setStyleSheet("background:#7a2b2b; color:white;")
        self.btn_reset.clicked.connect(self.wylej_zbiorniki_wszystkie)

        # -------------------------------
        # Przyciski grzałek (ON/OFF)
        # -------------------------------
        self.heater_buttons = []

        btn_start_y = 280 + 60  # możesz zmienić Y jak chcesz
        for i in range(4):
            btn = QPushButton(f"Włącz {i + 1}", self)
            btn.setGeometry(720, btn_start_y + i * 45, 300, 35)
            btn.setStyleSheet("background:#444; color:white;")
            btn.clicked.connect(lambda _, idx=i: self.toggle_heater(idx))
            self.heater_buttons.append(btn)



        # -------------------------------
        # 5) Timer przepływu
        # -------------------------------
        self.flow_timer = QTimer(self)
        self.flow_timer.timeout.connect(self.on_flow_tick)
        self.flow_running = False

        # Timer do grzania (aktualizacja temperatury)
        self.heater_timer = QTimer(self)
        self.heater_timer.timeout.connect(self.on_heater_tick)
        self.heater_timer.start(200)  # co 200 ms

    # ==========================================================
    # SETUP / KONSTRUKCJE
    # ==========================================================

    def _setup_window(self):
        self.setWindowTitle("SCADA ")
        self.setFixedSize(self.WINDOW_W, self.WINDOW_H)
        self.setStyleSheet("background-color: #1e1e1e;")

    def _create_tanks(self):
        """
        Tworzy zbiorniki: pozycje + wymiary + pojemność.
        Zakładam pojemnosc=100.0 => suwak 0..100 mapuje się 1:1 na ilość.
        """
        return [
            Zbiornik(40, 40, pojemnosc=100.0, nazwa="Zbiornik 1", width=140, height=160),
            Zbiornik(200, 220, pojemnosc=100.0, nazwa="Zbiornik 2", width=140, height=160),
            Zbiornik(360, 400, pojemnosc=100.0, nazwa="Zbiornik 3", width=140, height=160),
            Zbiornik(520, 580, pojemnosc=100.0, nazwa="Zbiornik 4", width=140, height=160),
        ]

    def _create_pipes(self):
        """
        Tworzy listę rur. Każda rura to lista punktów łamanej.
        """
        return [
            Rura([(180, 185), (290, 185), (290, 220)]),
            Rura([(340, 365), (450, 365), (450, 400)]),
            Rura([(500, 545), (610, 545), (610, 580)]),
        ]

    def _create_heaters(self):
        """
        Tworzy 4 grzałki (po jednej pod każdym zbiornikiem).
        """
        return (
            Grzalka(nazwa="Grzałka 1", moc=5.0),
            Grzalka(nazwa="Grzałka 2", moc=5.0),
            Grzalka(nazwa="Grzałka 3", moc=5.0),
            Grzalka(nazwa="Grzałka 4", moc=5.0),
        )

    def _create_flow_button(self):
        """
        Przycisk START/STOP przepływu.
        """
        btn = QPushButton("START/STOP przepływu", self)
        btn.setGeometry(self.PANEL_X, 280, self.PANEL_W, 35)
        btn.setStyleSheet("background:#444; color:white;")
        btn.clicked.connect(self.toggle_flow)
        return btn



    def open_side_screen(self):
        """
        Otwiera drugi ekran i ukrywa MainScreen
        """
        self.side_screen = SideScreen(self)
        self.side_screen.show()
        self.hide()

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



    def _create_sliders_panel(self):
        """
        Panel suwaków: dla każdego zbiornika label + slider.
        """
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
    # STEROWANIE: FLOW + TIMER
    # ==========================================================

    def toggle_flow(self):
        """
        Start/Stop symulacji przepływu.
        """
        self.flow_running = not self.flow_running

        if self.flow_running:
            self.btn_flow.setText("STOP przepływu")
            self.flow_timer.start(self.FLOW_TICK_MS)
        else:
            self.btn_flow.setText("START przepływu")
            self.flow_timer.stop()

            # Gdy stop -> wyłącz wizualizację przepływu w rurach
            for r in self.rurki:
                r.czy_plynie = False

            self.update()

    def wylej_zbiorniki_wszystkie(self):



        for zb in self.zbiorniki:
            zb.aktualna_ilosc = 0.0

        self.grzalka1.temperatura = 20.0
        self.grzalka2.temperatura = 20.0
        self.grzalka3.temperatura = 20.0
        self.grzalka4.temperatura = 20.0

            # jeśli używasz flagi "byl_napelniany" i chcesz prawdziwy reset:
            # zb.byl_napelniany = False

        self.sync_sliders_from_tanks()
        self.update()

    def on_heater_tick(self):
        dt = 0.2  # odpowiada 200 ms timera

        pairs = [
            (self.zb1, self.grzalka1),
            (self.zb2, self.grzalka2),
            (self.zb3, self.grzalka3),
            (self.zb4, self.grzalka4),
        ]

        for zb, g in pairs:
            # WARUNEK 1: nie grzej na sucho
            if zb.czy_pusty():
                g.wylacz()

            # WARUNEK 2: grzanie / stygnięcie
            if g.czy_wlaczona:
                g.grzej(dt)
            else:
                g.chlodz(dt)

        self.update()


    def on_flow_tick(self):
        """
        Tick timera: wykonaj krok logiki procesu.
        """
        moved = self.logic.step()

        # Jeśli moved[i] > 0 => rura i faktycznie "płynie"
        for i, m in enumerate(moved):
            self.rurki[i].czy_plynie = (m > 0)

        # Synchronizacja suwaków z aktualnym stanem zbiorników
        self.sync_sliders_from_tanks()
        self.update()

    def sync_sliders_from_tanks(self):
        """
        Aktualizuje suwaki i etykiety na podstawie stanu modelu (zbiorników).
        Uwaga: blokujemy sygnały suwaków, żeby nie wywoływać on_slider_change.
        """
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

        # jeśli już był napełniany → nie pozwól zejść poniżej 10%
        if zb.byl_napelniany:
            min_percent = int(zb.min_poziom * 100)
            if value < min_percent:
                value = min_percent

        zb.aktualna_ilosc = float(value)
        self.slider_labels[idx].setText(f"{zb.nazwa}: {value}%")
        self.update()

    # ==========================================================
    # RYSOWANIE (PAINT)
    # ==========================================================

    def paintEvent(self, event):
        """
        Główne rysowanie ekranu:
        1) rury (pod spodem)
        2) zbiorniki (na wierzchu)
        3) grzałki (pod zbiornikami)
        """
        p = QPainter(self)
        try:
            p.setRenderHint(QPainter.Antialiasing)

            # 1) Rury
            for r in self.rurki:
                self.draw_rura(p, r)

            # 2) Zbiorniki
            for zb in self.zbiorniki:
                self.draw_zbiornik(p, zb)

            # 3) Grzałki
            self.draw_grzalka_pod_zbiornikiem(p, self.zb1, self.grzalka1)
            self.draw_grzalka_pod_zbiornikiem(p, self.zb2, self.grzalka2)
            self.draw_grzalka_pod_zbiornikiem(p, self.zb3, self.grzalka3)
            self.draw_grzalka_pod_zbiornikiem(p, self.zb4, self.grzalka4)

        finally:
            p.end()

    # -------------------------------
    # Rysowanie: ZBIORNIK
    # -------------------------------
    def draw_zbiornik(self, p: QPainter, zb: Zbiornik):
        """
        Rysuje pojedynczy zbiornik:
        - ciecz w środku wg zb.poziom (0..1)
        - obrys
        - napisy (nazwa, procent)
        """
        poziom = zb.poziom  # 0..1

        # 1) Ciecz (tylko jeśli sensowna wysokość)
        if poziom > 0:
            h_cieczy = int(zb.height * poziom)

            # zabezpieczenie: unikamy ujemnych wymiarów prostokąta
            if h_cieczy >= 6:
                y0 = zb.y + zb.height - h_cieczy

                w = zb.width - 8
                h = h_cieczy - 4
                if w > 0 and h > 0:
                    p.setPen(Qt.NoPen)
                    p.setBrush(QColor(0, 120, 255, 200))
                    p.drawRect(int(zb.x + 4), int(y0 + 2), int(w), int(h))

        # 2) Obrys
        p.setPen(QPen(Qt.white, 3))
        p.setBrush(Qt.NoBrush)
        p.drawRect(int(zb.x), int(zb.y), int(zb.width), int(zb.height))

        # 3) Podpis + procent
        p.setPen(Qt.white)
        p.drawText(int(zb.x), int(zb.y - 10), zb.nazwa)
        p.drawText(int(zb.x), int(zb.y + zb.height + 20), f"{poziom * 100:.0f}%")

    # -------------------------------
    # Rysowanie: RURA
    # -------------------------------
    def draw_rura(self, p: QPainter, rura: Rura):
        """
        Rysuje rurę jako łamaną:
        - obudowa (szara)
        - „woda” w środku (niebieska) gdy rura.czy_plynie == True
        """
        if len(rura.punkty) < 2:
            return

        pts = [QPointF(x, y) for x, y in rura.punkty]
        path = QPainterPath()
        path.moveTo(pts[0])
        for pt in pts[1:]:
            path.lineTo(pt)

        # 1) Obudowa rury (zawsze szara, ostre krawędzie)
        pen_outer = QPen(Qt.gray, 12)
        pen_outer.setCapStyle(Qt.FlatCap)
        pen_outer.setJoinStyle(Qt.MiterJoin)
        p.setPen(pen_outer)
        p.drawPath(path)

        # 2) Przepływ (tylko gdy płynie)
        if rura.czy_plynie:
            pen_inner = QPen(QColor(0, 180, 255), 8)
            pen_inner.setCapStyle(Qt.FlatCap)
            pen_inner.setJoinStyle(Qt.MiterJoin)
            p.setPen(pen_inner)
            p.drawPath(path)

    # -------------------------------
    # Rysowanie: GRZAŁKA
    # -------------------------------
    def draw_grzalka_pod_zbiornikiem(self, p: QPainter, zb: Zbiornik, grzalka: Grzalka):
        """
        Rysuje grzałkę jako prostokąt pod zbiornikiem:
        - kolor czerwony gdy włączona
        - podpis z temperaturą
        """
        w = 60
        h = 18
        gap = 12

        x = int(zb.x + (zb.width - w) / 2)
        y = int(zb.y + zb.height + gap)

        kolor = QColor(255, 0, 0) if grzalka.czy_wlaczona else QColor(255, 255, 255)

        # Obrys + wypełnienie
        p.setPen(QPen(Qt.white, 2))
        p.setBrush(kolor)
        p.drawRect(x, y, w, h)

        # Napis
        p.setPen(Qt.white)
        p.drawText(x-30, y + h + 16, f"{grzalka.nazwa} Tempe: {grzalka.temperatura}")
