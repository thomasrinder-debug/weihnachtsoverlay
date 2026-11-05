import math
import random

from PyQt6.QtCore import QPointF, QRectF
from PyQt6.QtGui import QColor, QPainterPath

from zeichnen.figur import Pose
from zeichnen.figuren import WichtelSteif
from zeichnen.grundlagen import KEIN_STIFT, ROT, WEISS, blinzeln, linear, stern, stift

from .basis import Erschrecke, Gehe, Jeweils, Mit, Renne, Schritt, Setze, Stehe, Szene, Tu, Wandel, Warte, \
    muetze_richten

A = 30               # Kantenlänge eines Eisblocks, Einheiten
PLAN = [(-1, 0), (0, 0), (1, 0), (-0.5, 1), (0.5, 1), (0, 2)]
GLITZER = [WEISS, QColor('#CFEFFF')]


class Flug(Schritt):
    """Ein Eisblock fliegt vom Rand auf seinen Platz im Schloss."""

    def __init__(self, i, dauer=0.7):
        self.i, self.dauer = i, dauer

    def beginn(self, sz):
        self.x0, self.y0 = sz.aussen(-sz.richtung), sz.boden - 260 * sz.s
        sz.bloecke.append([self.x0, self.y0, 0.0, 0.0, 0.0, False])

    def weiter(self, sz, u, dt):
        x1, y1 = sz.platz(*PLAN[self.i]) if self.i < len(PLAN) else sz.platz(0.2, 3)
        f = min(1.0, u / self.dauer)
        b = sz.bloecke[-1]
        b[0] = self.x0 + (x1 - self.x0) * f
        b[1] = self.y0 + (y1 - self.y0) * f - 120 * sz.s * 4 * f * (1 - f)
        b[4] = 360 * (1 - f)

    def ende(self, sz):
        sz.bloecke[-1][4] = 0.0
        x, y = sz.bloecke[-1][:2]
        sz.streue(x, y + A * sz.s / 2, 5, GLITZER, tempo=70, dauer=0.4, r=(2, 4), art='stern')


class Eispalast(Szene):
    """Ein Wichtel dirigiert Eisblöcke herbei, die vom Rand angeflogen kommen, und stapelt sie
    zu einem kleinen Schloss mit Fähnchen. Ein Block zu viel landet obendrauf, das Schloss
    stürzt über ihm zusammen, er krabbelt heraus und richtet würdevoll seine Mützenspitze."""
    name, titel, reihenfolge = 'eispalast', 'Eispalast', 51

    def vorbereiten(self):
        self.zeige_figur = False
        r = self.richtung
        self.sx = self.vom_rand(random.uniform(0.2, 0.24))
        self.bloecke = []          # [x, y, vx, vy, drehung, fällt]
        self.fahne = False
        self.schmelzen = 0.0
        self.w = self.dazu('w', WichtelSteif, groesse=0.5, knick=1.0, vorn=True)
        self.w.richtung = r
        self.w.x = self.aussen(-r)

    def platz(self, i, reihe):
        s = self.s
        return self.sx + i * A * s * 1.04, self.boden - (A / 2 + reihe * A * 1.02) * s

    def ablauf(self):
        r, s = self.richtung, self.s
        winken = lambda d, u: Pose(arm_v=-150 + 30 * math.sin(u * 12), arm_v_x=10, kopf_vorn=True,  # noqa: E731
                                   mund_offen=(u * 5) % 2 < 1, blick_x=-1)
        bau = []
        for i in range(len(PLAN)):
            bau += [Flug(i, 0.6 if i else 0.8), Mit('w', Stehe(0.25, winken))]
        return [
            Mit('w', Gehe(bis=self.sx + r * 90 * s)),
            Mit('w', Setze(richtung=-r)),
            Mit('w', Setze(pose=Pose(arm_v=-150, arm_v_x=10, kopf_vorn=True, blick_x=-1))),
            *bau,
            Setze(fahne=True),
            Mit('w', Stehe(1.4, lambda d, u: Pose(kopf_vorn=True, arm_v=-120, arm_h=-120, mund_offen=True,
                                                  auge_zu=u > 0.6))),
            Flug(len(PLAN), 0.7),
            Jeweils(0.8, lambda sz, u: sz.wackeln(u)),
            Tu(lambda sz: sz.einsturz()),
            Mit('w', Erschrecke(0.3, 30)),
            Mit('w', Setze(hopp=lambda d: -40 * d.s, pose=Pose(kopf_vorn=True, sorge=1.0, auge_zu=True))),
            Warte(1.4),
            Mit('w', Setze(hopp=0.0)),
            Mit('w', Stehe(0.6, Pose(kopf_vorn=True, sorge=1.0))),
            *muetze_richten('w'),
            Mit('w', Gehe(bis=self.aussen(-r), tempo=0.8)),
            Wandel(0.5, schmelzen=1.0),
        ]

    def schreck_ablauf(self):
        self.nebenbei.clear()
        self.einsturz(stark=True)
        neu = []
        if self.w.figur_sichtbar():
            neu = [Mit('w', Setze(hopp=0.0, knick=1.0)), Mit('w', Erschrecke(0.3, 45)), Mit('w', Renne(zum='rand'))]
        return neu + [Wandel(0.4, schmelzen=1.0)]

    def wackeln(self, u):
        for i, b in enumerate(self.bloecke):
            b[4] = math.sin(u * 30 + i) * 4 * u

    def einsturz(self, stark=False):
        self.fahne = False
        s = self.s
        for b in self.bloecke:
            b[5] = True
            b[2] = random.uniform(-1, 1) * (400 if stark else 160) * s + self.richtung * (60 if not stark else 0) * s
            b[3] = -random.uniform(100, 300 if stark else 200) * s

    def weiter(self, dt):
        s = self.s
        for b in self.bloecke:
            if not b[5]:
                continue
            b[3] += 1300 * s * dt
            b[0] += b[2] * dt
            b[1] += b[3] * dt
            b[4] += b[2] / s * 0.8 * dt
            boden = self.boden - A / 2 * s
            if b[1] > boden:
                b[1] = boden
                b[3] = -b[3] * 0.25 if abs(b[3]) > 100 * s else 0.0
                b[2] *= 0.7

    def zeichne_hinten(self, p):
        s = self.s
        if self.schmelzen >= 1:
            return
        p.save()
        p.setOpacity(1 - self.schmelzen)
        for x, y, _, _, dreh, _ in self.bloecke:
            p.save()
            p.translate(x, y)
            p.rotate(dreh)
            p.scale(s, s)
            p.setBrush(linear(-A / 2, -A / 2, A / 2, A / 2, QColor(225, 245, 255, 230), QColor(120, 185, 230, 230)))
            p.setPen(stift(QColor(255, 255, 255, 200), 1.4))
            p.drawRoundedRect(QRectF(-A / 2, -A / 2, A, A), 4, 4)
            p.setPen(stift(QColor(255, 255, 255, 170), 2.2))
            p.drawLine(QPointF(-A / 2 + 5, -A / 2 + 6), QPointF(-A / 2 + 12, -A / 2 + 6))
            p.setPen(KEIN_STIFT)
            p.restore()
        if self.fahne:
            x, y = self.platz(0, 2)
            y -= A / 2 * s
            p.setPen(stift(QColor('#6B4423'), 1.6 * s))
            p.drawLine(QPointF(x, y), QPointF(x, y - 26 * s))
            p.setPen(KEIN_STIFT)
            fahne = QPainterPath()
            fahne.moveTo(x, y - 26 * s)
            fahne.lineTo(x + 16 * s, y - 21 * s + math.sin(self.t * 8) * 2 * s)
            fahne.lineTo(x, y - 16 * s)
            p.setBrush(ROT)
            p.drawPath(fahne)
        p.restore()

    def grenzen_extra(self):
        s = self.s
        k = QRectF()
        if self.schmelzen < 1:
            for x, y, *_ in self.bloecke:
                k = k.united(QRectF(x - A * s, y - A * s, 2 * A * s, 2 * A * s))
            if self.fahne:
                k = k.united(QRectF(self.sx - 10 * s, self.boden - 140 * s, 40 * s, 140 * s))
        return k

