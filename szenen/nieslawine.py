import math
import random

from PyQt6.QtCore import QPointF, QRectF
from PyQt6.QtGui import QColor

from zeichnen.figur import Pose
from zeichnen.grundlagen import WEISS, blinzeln, stern
from zeichnen.requisiten import zeichne_schneehaufen

from .basis import Erschrecke, Gehe, Jeweils, Renne, Schritt, Setze, Springe, Stehe, Szene, Tu, Wandel, Warte

SCHNEE = [WEISS, QColor('#E4EEF8')]


class Rutschen(Schritt):
    """Haufen und Weihnachtsmann rutschen gemeinsam seitlich hinaus."""

    def __init__(self, tempo):
        self.tempo = tempo

    def beginn(self, sz):
        self.seite = sz.naechster_rand()

    def weiter(self, sz, u, dt):
        v = self.seite * sz.tempo * self.tempo * min(1.0, u * 3 + 0.3) * dt
        sz.x += v
        sz.hx += v

    def fertig(self, sz, u):
        return not sz.grenzen().intersects(sz.geo)


class Nieslawine(Szene):
    """In der Ecke landet ihm eine winzige Flocke auf der Nase. Er niest so gewaltig, dass vom
    Rand eine Schneelawine herabrutscht und ihn begräbt; nur die unbeeindruckte Mütze schaut
    heraus. Dann lugen die Augen hervor, er hüpft heraus und schüttelt sich."""
    name, titel, reihenfolge = 'nieslawine', 'Nieslawine', 35

    def vorbereiten(self):
        self.hx = 0.0
        self.hoehe = 0.0            # Schneehaufen in Einheiten
        self.flocke = None
        self.lawine = False

    def nase(self):
        q = QPointF(self.x + self.richtung * 36 * self.s, self.y - self.hopp - 183 * self.s)
        return q.x(), q.y()

    def ablauf(self):
        r, s = self.richtung, self.s
        self.x = self.aussen(-r)
        ziel = self.vom_rand(random.uniform(0.06, 0.08))
        self.hx = ziel

        def flug(sz, u):
            f = min(1.0, u / 2.2)
            nx, ny = sz.nase()
            sz.flocke = (nx + math.sin(u * 3) * 25 * s * (1 - f), ny - 260 * s * (1 - f))

        return [
            Gehe(bis=ziel),
            Setze(richtung=-r),
            Stehe(0.4),
            Setze(richtung=r),
            Stehe(2.2, lambda sz, u: Pose(kopf_vorn=u > 0.6, blick_y=-1 + u * 0.8, auge_zu=blinzeln(sz.t))),
            Jeweils(0.01, flug),
            Jeweils(2.2, lambda sz, u: (flug(sz, u), setattr(sz, 'pose', Pose(kopf_vorn=True, blick_y=-0.8)))),
            Stehe(1.0, lambda sz, u: Pose(kopf_vorn=True, blick_y=0.6, sorge=u, mund_offen=u > 0.4,
                                         auge_zu=u > 0.7)),
            Setze(flocke=None),
            Tu(lambda sz: sz.niesen()),
            Erschrecke(0.3, 25),
            Jeweils(1.0, lambda sz, u: setattr(sz, 'hoehe', 208 * min(1.0, u / 0.8))),
            Setze(lawine=False),
            Stehe(1.6, lambda sz, u: Pose(wipp=math.sin(u * 4) * 3)),
            Wandel(0.3, hoehe=178),
            Stehe(1.6, lambda sz, u: Pose(kopf_vorn=True, sorge=0.5, blick_x=math.sin(u * 3),
                                         auge_zu=0.5 < u < 0.65 or 1.2 < u < 1.35)),
            Jeweils(0.5, lambda sz, u: setattr(sz, 'neigung', math.sin(u * 40) * 4)),
            Setze(neigung=0),
            Tu(lambda sz: sz.streue(sz.x, sz.boden - 150 * s, 22, SCHNEE, tempo=220, dauer=0.8, r=(4, 8))),
            Springe(lambda sz: (sz.x - r * 110 * s, sz.boden), 0.55, 140),
            Wandel(0.4, hoehe=120),
            Jeweils(0.5, lambda sz, u: setattr(sz, 'neigung', math.sin(u * 50) * 8)),
            Setze(neigung=0),
            Tu(lambda sz: sz.streue(sz.x, sz.boden - 120 * s, 16, SCHNEE, tempo=160, dauer=0.6, r=(3, 6))),
            Renne(zum='rand', tempo=2.4),
            Wandel(0.6, hoehe=0.0),
        ]

    def schreck_ablauf(self):
        self.nebenbei.clear()
        self.flocke = None
        if self.hoehe > 170:
            return [Setze(hoehe=178, pose=Pose(kopf_vorn=True, schreck=1.0), striche=True), Warte(0.3),
                    Setze(striche=False), Rutschen(3.4)]
        neu = [Setze(neigung=0)]
        if self.zeige_figur and self.figur_sichtbar():
            neu += [Erschrecke(0.3, 45), Renne(zum='rand')]
        return neu + [Setze(zeige_figur=False), Wandel(0.3, hoehe=0.0)]

    def niesen(self):
        nx, ny = self.nase()
        s = self.s
        self.streue(nx, ny, 10, SCHNEE, tempo=140, dauer=0.5, r=(2, 4))
        kante = self.geo.left() if self.richtung > 0 else self.geo.right()
        for _ in range(26):
            self.streue(kante, self.boden - random.uniform(300, 520) * s, 1, SCHNEE, tempo=380, dauer=1.0,
                        r=(6, 14), schwer=True, richtung=math.atan2(1.4, self.richtung), streuung=0.3)

    def zeichne_vorn(self, p):
        zeichne_schneehaufen(p, self.hx, self.boden, 250 * self.s, self.hoehe * self.s)
        if self.flocke:
            p.setBrush(QColor(255, 255, 255, 240))
            stern(p, *self.flocke, 4 * self.s)

    def grenzen_extra(self):
        s = self.s
        k = QRectF(self.hx - 130 * s, self.boden - (self.hoehe + 10) * s, 260 * s, (self.hoehe + 10) * s)
        if self.flocke:
            k = k.united(QRectF(self.flocke[0] - 8 * s, self.flocke[1] - 8 * s, 16 * s, 16 * s))
        return k
