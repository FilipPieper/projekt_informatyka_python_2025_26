from elements import Zbiornik


class ProcessLogic:
    def __init__(self, zbiorniki):
        self.zbiorniki = zbiorniki
        self.flow_speed = 0.6

    def step(self):
        moved = []

        for i in range(len(self.zbiorniki) - 1):
            moved.append(
                self._transfer(self.zbiorniki[i], self.zbiorniki[i + 1])
            )

        return moved

    def _transfer(self, z_from: Zbiornik, z_to: Zbiornik) -> float:
        if z_from.czy_pusty() or z_to.czy_pelny():
            return 0.0

        taken = z_from.usun_ciecz(self.flow_speed)
        given = z_to.dodaj_ciecz(taken)

        if given < taken:
            z_from.dodaj_ciecz(taken - given)

        return given
