
class Zbiornik:
    def __init__(self,x , y, pojemnosc=100.0, nazwa="", width = 80, height = 100):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.nazwa = nazwa
        self.pojemnosc = pojemnosc

        self.min_poziom = 0.10  # 10%
        self.aktualna_ilosc = 0.0  # START = 0%
        self.byl_napelniany = False

    @property
    def poziom(self) -> float:
        return self.aktualna_ilosc / self.pojemnosc

    def dodaj_ciecz(self, ilosc: float) -> float:
        if ilosc > 0:
            self.byl_napelniany = True

        wolne = self.pojemnosc - self.aktualna_ilosc
        dodano = min(ilosc, wolne)
        self.aktualna_ilosc += dodano
        return dodano

    def usun_ciecz(self, ilosc: float) -> float:
        # jeśli zbiornik nigdy nie był napełniany → można zejść do 0
        if not self.byl_napelniany:
            usunieto = min(ilosc, self.aktualna_ilosc)
            self.aktualna_ilosc -= usunieto
            return usunieto

        # po pierwszym napełnieniu → obowiązuje MIN
        min_ilosc = self.pojemnosc * self.min_poziom
        dostepne = self.aktualna_ilosc - min_ilosc

        if dostepne <= 0:
            return 0.0

        usunieto = min(ilosc, dostepne)
        self.aktualna_ilosc -= usunieto
        return usunieto

    def czy_pusty(self) -> bool:
        if not self.byl_napelniany:
            return self.aktualna_ilosc <= 0.01

        return self.aktualna_ilosc <= self.pojemnosc * self.min_poziom + 0.01

    def czy_pelny(self) -> bool:
        return self.aktualna_ilosc >= self.pojemnosc - 0.1



class Rura:
    def __init__(self, punkty):

        self.punkty = punkty
        self.czy_plynie = False

    def ustaw_przeplyw(self, plynie: bool):
        self.czy_plynie = plynie



class Grzalka:
    def __init__(self, temperatura=20.0, moc=1.0, temp_max=120.0, temp_min=20.0, nazwa=""):
        self.nazwa = nazwa

        self.temperatura = float(temperatura)
        self.moc = float(moc)
        self.temp_max = float(temp_max)
        self.temp_min = float(temp_min)
        self.czy_wlaczona = False

    def wlacz(self):
        self.czy_wlaczona = True

    def wylacz(self):
        self.czy_wlaczona = False

    def grzej(self, dt: float = 1.0):
        if not self.czy_wlaczona:
            return
        self.temperatura += self.moc * dt

        if self.temperatura >= self.temp_max:
            self.temperatura = self.temp_max

        if self.temperatura <= self.temp_min:
            self.temperatura = self.temp_min

    def chlodz(self, dt: float = 1.0, wspolczynnik: float = 0.5):
        """
        Naturalne stygnięcie gdy grzałka wyłączona
        """
        if self.czy_wlaczona:
            return

        self.temperatura -= self.moc * wspolczynnik * dt
        if self.temperatura < self.temp_min:
            self.temperatura = self.temp_min
