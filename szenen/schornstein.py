import math
import random

from PyQt6.QtCore import QRectF
from PyQt6.QtGui import QColor

from zeichnen.figur import Pose
from zeichnen.grundlagen import Teilchen, blinzeln, glatt, teilchen_kasten, teilchen_schritt, zeichne_teilchen
from zeichnen.requisiten import zeichne_schornstein

from .basis import (Ducke, Erschrecke, Falle, Gehe, Nebenbei, Setze, Springe, Stehe, Szene, Tu, Wandel,
                    Warte, WarteBis)


def zeige_pose(sz, u):
    f = glatt(u / 0.3)
    return Pose(arm_v=-125 * f, arm_v_x=18, wipp=math.sin(sz.t * 6) * 3, auge_zu=blinzeln(sz.t))


class Schornstein(Szene):
    """Ein Schornstein wächst in einer unteren Ecke aus dem Rand, er kommt von
    der Seite, nimmt Anlauf und springt hinein. Heraus kommt eine Rußwolke."""
    name, titel, reihenfolge = 'schornstein', 'Schornstein', 6
    HOEHE = 175

    def vorbereiten(self):
        abstand = self.geo.width() * random.uniform(0.1, 0.15) + 60 * self.s
        self.xc = self.geo.left() + abstand if self.richtung > 0 else self.geo.right() - abstand
        self.hoch = 0.0
        self.raucht = False
        self.drin = False           # er ist im Schornstein verschwunden
        self.im_sprung = False
        self.rauch, self.russ = [], []
        self.teilchen = [self.russ]   # der Rauch liegt hinter dem Schornstein
        self.naechster_rauch = 0.0

    @property
    def kante(self):
        """Oberkante des Schornsteins."""
        return self.boden - self.HOEHE * self.s * glatt(self.hoch)

    def ablauf(self):
        self.x = self.aussen(-self.richtung)
        return [Nebenbei(Wandel(1.0, hoch=1.0)), Setze(raucht=True),
                Gehe(bis=self.xc - self.richtung * 150 * self.s),
                Stehe(0.9, zeige_pose), Ducke(0.3), *self.hinein(0.95), Warte(3.6), *self.weg(1.0)]

    def hinein(self, dauer):
        return [Setze(im_sprung=True), Springe(nach=lambda sz: (sz.xc, sz.kante), dauer=dauer),
                Falle(bis=lambda sz: sz.y - 262 * sz.s > sz.kante), Tu(Schornstein.puff),
                Setze(zeige_figur=False, drin=True, im_sprung=False)]

    def weg(self, dauer):
        return [Setze(raucht=False), Wandel(dauer, hoch=0.0), WarteBis(lambda sz: not sz.rauch)]

    def schreck_ablauf(self):
        self.raucht = False
        for w in self.rauch:            # Rauch verfliegt rasch
            w.dauer = min(w.dauer, w.alter + 0.5)
        if self.im_sprung:              # Sprung zu Ende bringen, dann schnell weg
            bis_drin = next(i for i, s in enumerate(self.schritte) if isinstance(s, Warte))
            self.schritte = self.schritte[:bis_drin] + [Warte(0.3), *self.weg(0.4)]
            return None
        if self.drin:
            return [Warte(0.3), *self.weg(0.4)]
        return [Erschrecke(0.32, hoehe=40), *self.hinein(0.55), Warte(0.5), *self.weg(0.4)]

    @staticmethod
    def puff(sz):
        s = sz.s
        for _ in range(18):
            w = random.uniform(-math.pi * 0.85, -math.pi * 0.15)
            v = random.uniform(60, 170) * s
            sz.russ.append(Teilchen(sz.xc + random.uniform(-30, 30) * s, sz.kante - 6 * s, math.cos(w) * v,
                                    math.sin(w) * v, random.uniform(1.0, 1.8), 12 * s,
                                    random.uniform(26, 40) * s, QColor(55, 55, 62, 210), 'wolke'))
        for _ in range(10):
            w = random.uniform(-math.pi * 0.9, -math.pi * 0.1)
            v = random.uniform(120, 260) * s
            sz.russ.append(Teilchen(sz.xc, sz.kante - 10 * s, math.cos(w) * v, math.sin(w) * v,
                                    random.uniform(0.6, 1.1), 6 * s, 2 * s, QColor(255, 214, 90, 240), 'stern'))

    def weiter(self, dt):
        s = self.s
        if self.raucht and self.hoch > 0.8 and self.t > self.naechster_rauch:
            self.naechster_rauch = self.t + 0.3
            self.rauch.append(Teilchen(self.xc + random.uniform(-25, 25) * s, self.kante - 8 * s,
                                       random.uniform(-6, 14) * s, -random.uniform(30, 45) * s,
                                       3.0, 10 * s, 28 * s, QColor(225, 225, 232, 110), 'wolke'))
        teilchen_schritt(self.rauch, dt)
        teilchen_schritt(self.russ, dt, bremse=1.8)

    def zeichne_hinten(self, p):
        zeichne_teilchen(p, self.rauch)

    def zeichne_figur(self, p, zwischen=None):
        p.save()
        if self.im_sprung and self.aktuell.__class__ is Falle:
            # was in den Schornstein fällt, verschwindet hinter der Kante
            g = self.geo
            p.setClipRect(QRectF(g.left(), g.top() - 2000, g.width(), self.kante - g.top() + 2000 - 4 * self.s))
        super().zeichne_figur(p)
        p.restore()

    def zeichne_vorn(self, p):
        if self.hoch > 0:
            zeichne_schornstein(p, self.xc, self.kante, self.boden, self.s)

    def grenzen_extra(self):
        s = self.s
        k = QRectF(self.xc - 80 * s, self.kante - 30 * s, 160 * s, self.boden - self.kante + 40 * s)
        return k.united(teilchen_kasten(self.rauch))
