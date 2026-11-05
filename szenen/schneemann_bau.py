import math
import random

from PyQt6.QtCore import QPointF, QRectF

from zeichnen.figur import Pose
from zeichnen.figuren import Schneemann
from zeichnen.grundlagen import WEISS, blinzeln, glatt

from .basis import Gehe, Jeweils, Mit, Schritt, Setze, Stehe, Szene, Tu, Warte, WarteBis

RADIEN = (50, 36, 28)
MITTEN = ((0, -50), (0, -128), (4, -188))     # Kugelmitten des fertigen Schneemanns


class SchneemannBau(Szene):
    """Drei Schneekugeln rollen nacheinander herein, hüpfen aufeinander und werden
    zum Schneemann, der sich schüttelt, winkt und davonhüpft. Beim Schreck
    fällt er auseinander und die Kugeln kullern in alle Richtungen davon."""
    name, titel, reihenfolge = 'bau', 'Schneemann baut sich', 11

    def vorbereiten(self):
        self.zeige_figur = False
        self.sm = self.dazu('sm', Schneemann, groesse=0.85)
        self.sm.x = self.vom_rand(random.uniform(0.09, 0.14))
        self.sm.richtung = self.richtung
        weit = (abs(self.sm.x - self.aussen(-self.richtung)) + 60 * self.s) / self.sm.s
        # je Kugel: Versatz in Einheiten (x wie die Blickrichtung), auf dem Boden liegend
        self.kx = [-weit, -weit, -weit]
        self.ky = [self.boden_dy(i) for i in range(3)]
        self.aktualisiere()

    @staticmethod
    def boden_dy(i):
        return -RADIEN[i] - MITTEN[i][1]

    def aktualisiere(self):
        self.sm.teile = [(self.kx[i], self.ky[i], math.degrees(self.kx[i] / RADIEN[i])) for i in range(3)]

    def rolle(self, i, bis, dauer):
        def f(sz, u):
            g = glatt(u / dauer) if dauer else 1.0
            sz.kx[i] = sz.start + (bis - sz.start) * g
        return [Tu(lambda sz: setattr(sz, 'start', sz.kx[i])), Jeweils(dauer, f)]

    def springe(self, i, dauer=0.5, hoehe=110):
        def f(sz, u):
            g = min(1.0, u / dauer)
            sz.kx[i] = sz.sx * (1 - g)
            sz.ky[i] = sz.sy * (1 - g) - hoehe * 4 * g * (1 - g)
        return [Tu(lambda sz: sz.merke(i)), Jeweils(dauer, f), Tu(lambda sz: sz.landung(i))]

    def merke(self, i):
        self.sx, self.sy = self.kx[i], self.ky[i]

    def landung(self, i):
        self.kx[i], self.ky[i] = 0.0, 0.0
        x, y = self.welt(*MITTEN[i])
        self.streue(x, y + RADIEN[i] * self.sm.s, 8, WEISS, tempo=90, dauer=0.5, r=(3, 7))

    def welt(self, ux, uy):
        q = self.sm.trafo().map(QPointF(ux, uy))
        return q.x(), q.y()

    def ablauf(self):
        zu = Pose(auge_zu=True)
        return [
            Mit('sm', Setze(pose=zu)),
            *self.rolle(0, 0, 1.6),
            *self.rolle(1, -95, 1.5),
            *self.springe(1),
            Warte(0.3),
            *self.rolle(2, -80, 1.3),
            *self.springe(2, 0.55, 150),
            Warte(0.5),
            # fertig!
            Mit('sm', Stehe(0.5, Pose(auge_zu=True))),
            Mit('sm', Stehe(1.0, lambda d, u: Pose(auge_zu=blinzeln(d.t) or u > 0.8))),
            Mit('sm', Stehe(1.4, lambda d, u: Pose(kopf_vorn=True, sorge=0.3, blick_y=0.2,
                                                    auge_zu=0.5 < u < 0.62))),
            Jeweils(0.6, lambda sz, u: setattr(sz.sm, 'neigung', math.sin(u * 40) * 6 * (1 - u / 0.6))),
            Mit('sm', Setze(neigung=0)),
            Tu(lambda sz: sz.streue(*sz.welt(0, -130), 14, WEISS, tempo=120, dauer=0.6, r=(3, 6))),
            Mit('sm', Stehe(1.8, lambda d, u: Pose(kopf_vorn=True, arm_v=-140, mund_offen=True,
                                                    auge_zu=blinzeln(d.t)))),
            Mit('sm', Gehe(bis=self.aussen(-self.richtung), tempo=1.1)),
        ]

    def schreck_ablauf(self):
        self.nebenbei.clear()
        sm = self.sm
        return [Mit('sm', Setze(neigung=0, striche=True,
                                pose=Pose(kopf_vorn=True, schreck=1.0, arm_v=-115, arm_h=-100))),
                Warte(0.25), Mit('sm', Setze(striche=False)), Kullern(sm.naechster_rand() * sm.richtung),
                Mit('sm', Setze(zeige_figur=False))]

    def kugel_sichtbar(self):
        return self.grenzen_extra().intersects(self.geo)

    def weiter(self, dt):
        if not self.erschreckt:
            self.aktualisiere()

    def grenzen_extra(self):
        k = QRectF()
        for i in range(3):
            x, y = self.welt(MITTEN[i][0] + self.kx[i], MITTEN[i][1] + self.ky[i])
            r = (RADIEN[i] + 60) * self.sm.s
            k = k.united(QRectF(x - r, y - r, 2 * r, 2 * r))
        return k


class Kullern(Schritt):
    """Die Kugeln fallen herunter und kullern verschieden schnell zum Rand."""
    TEMPO = (1500, 1150, 1800)

    def __init__(self, seite):
        self.seite = seite

    def beginn(self, sz):
        self.start = list(sz.ky)

    def weiter(self, sz, u, dt):
        f = glatt(u / 0.25)
        for i in range(3):
            sz.ky[i] = self.start[i] + (sz.boden_dy(i) - self.start[i]) * f
            sz.kx[i] += self.seite * self.TEMPO[i] * (0.3 + min(1.0, u * 2)) * dt
        sz.aktualisiere()

    def fertig(self, sz, u):
        return u > 0.3 and not sz.kugel_sichtbar()
