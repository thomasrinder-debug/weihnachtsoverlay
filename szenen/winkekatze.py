import math

from PyQt6.QtGui import QColor

from zeichnen.figur import Pose
from zeichnen.grundlagen import GOLD_HELL, blinzeln

from .basis import Hoppel, Jeweils, Kurz, Mit, Nebenbei, Setze, Stehe, Tu, Wandel, WarteNebenbei
from .ostern import WinkeSzene

RAUCH = QColor(150, 150, 160, 160)


class Winkekatze(WinkeSzene):
    """Eine Winkekatze hüpft in die Ecke und winkt gemächlich. Sie winkt schneller und schneller,
    bis sich die Pfote überschlägt und zum Propeller wird: sie hebt ab, schwebt wackelnd, der
    Propeller stottert, sie plumpst herunter und sieht Sterne. Vorsichtig hebt sie die Pfote
    zu einem winzigen Winken – und schon dreht sie wieder durch und fliegt davon."""
    name, titel, reihenfolge = 'winkekatze', 'Winkekatze', 91

    def vorbereiten(self):
        self.zeige_figur = False
        self.katze(self.aussen(-self.richtung))
        self.zittern = 0.0

    def ablauf(self):
        sz = self
        k = lambda d, u: Pose(kopf_vorn=True, auge_zu=blinzeln(d.t))  # noqa: E731
        return [
            Mit('k', Hoppel(bis=self.vom_rand(0.09), tempo=0.45, hoehe=16)),
            Mit('k', Setze(richtung=self.richtung, pose=Pose(kopf_vorn=True))),
            Mit('k', Stehe(1.2, k)),
            Mit('k', Setze(froh=True)),
            Mit('k', Stehe(0.8, k)),
            Mit('k', Setze(froh=False, pose=Pose(kopf_vorn=True, sorge=0.7, blick_x=-0.8, blick_y=-0.8))),
            Wandel(1.4, wtempo=4.5, wamp=50, zittern=0.5),
            Tu(lambda s: setattr(s, 'propeller', True) or setattr(s, 'pdreh', 1000.0)),
            Mit('k', Setze(pose=Pose(kopf_vorn=True, schreck=0.7, blick_y=-0.8))),
            Nebenbei(Wandel(0.8, pdreh=2200.0, zittern=1.0)),
            Mit('k', Wandel(0.8, hopp=lambda d: 80 * d.s)),
            Setze(zittern=0.0),
            Mit('k', Jeweils(1.1, lambda d, u: setattr(d, 'neigung', 9 * math.sin(u * 8)))),
            Tu(lambda s: s.stottern()),
            Nebenbei(Wandel(0.5, pdreh=150.0)),
            Mit('k', Wandel(0.5, neigung=-20, hopp=lambda d: 95 * d.s)),
            Mit('k', Setze(pose=Pose(kopf_vorn=True, schreck=1.0))),
            Mit('k', Wandel(0.22, hopp=0.0, neigung=0.0)),
            Tu(lambda s: s.gelandet()),
            Mit('k', Kurz(0.16, stauchen=0.72)),
            Mit('k', Stehe(1.3, lambda d, u: Pose(kopf_vorn=True, auge_zu=True, sorge=1.0,
                                                   blick_x=math.sin(u * 6)))),
            Mit('k', Stehe(0.9, lambda d, u: Pose(kopf_vorn=True, auge_zu=0.3 < u < 0.42 or 0.6 < u < 0.72))),
            Wandel(0.7, wmitte=140.0, wamp=6.0, wtempo=1.2),
            Mit('k', Setze(froh=True)),
            Mit('k', Stehe(0.8, k)),
            Mit('k', Setze(froh=False, pose=Pose(kopf_vorn=True, schreck=0.8, blick_y=-0.8))),
            Tu(lambda s: setattr(s, 'propeller', True) or setattr(s, 'pdreh', 2400.0)),
            Mit('k', Wandel(1.1, hopp=lambda d: 230 * d.s, x=lambda d: sz.aussen(-sz.richtung))),
        ]

    def stottern(self):
        k = self.k
        self.streue(k.x - 26 * k.s * k.richtung, k.y - k.hopp - 110 * k.s, 8, RAUCH, tempo=60, dauer=0.9,
                    r=(4, 9))

    def gelandet(self):
        k = self.k
        self.propeller = False
        self.wmitte, self.wamp, self.wtempo = 15.0, 0.0, 1.0
        self.streue(k.x, k.y - 180 * k.s, 7, GOLD_HELL, tempo=50, dauer=1.6, r=(4, 7), art='stern')
        self.streue(k.x, k.y, 10, QColor(255, 255, 255, 200), tempo=90, dauer=0.5, r=(3, 7))

    def weiter(self, dt):
        super().weiter(dt)
        if self.zittern:
            self.k.neigung = math.sin(self.t * 70) * 4 * self.zittern

    def schreck_ablauf(self):
        self.nebenbei.clear()
        self.zittern = 0.0
        return self.katze_flieht() + [WarteNebenbei()]
