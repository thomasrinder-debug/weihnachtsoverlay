import math
import random

from PyQt6.QtCore import QPointF, QRectF
from PyQt6.QtGui import QColor

from zeichnen.figur import Pose
from zeichnen.figuren import Tannenbaum
from zeichnen.grundlagen import GRUEN, GRUEN_DUNKEL, kreis, radial

from .basis import Erschrecke, Gehe, Mit, Renne, Setze, Stehe, Szene, Tu, WarteBis

NADELN = [GRUEN, GRUEN_DUNKEL, QColor('#3A9A5C')]


def schleichen(pose, d):
    return Pose(bein_v=pose.bein_v * 1.6, bein_h=pose.bein_h * 1.6, hub=pose.hub * 2.5,
                kopf_vorn=True, blick_x=0.8, sorge=0.3, auge_zu=pose.auge_zu)


class TannenbaumSzene(Szene):
    """Ein geschmückter Tannenbaum schleicht auf Stiefelchen herein und erstarrt
    unauffällig. Zwei Kugeln fallen herunter; er schaut betreten und schleicht davon,
    die Kugeln kullern ihm hinterher."""
    name, titel, reihenfolge = 'tannenbaum', 'Wandernder Tannenbaum', 17

    def vorbereiten(self):
        self.zeige_figur = False
        self.tb = self.dazu('tb', Tannenbaum, groesse=0.8,
                            kugeln=[list(k) for k in Tannenbaum.KUGELN])
        self.unten = []      # heruntergefallene Kugeln: [x, y, vy, farbe, rollt]

    def ablauf(self):
        umschauen = lambda d, u: Pose(kopf_vorn=True, blick_x=math.sin(u * 3.2) * 1.0,  # noqa: E731
                                      auge_zu=0.95 < u < 1.08)
        betreten = lambda d, u: Pose(kopf_vorn=True, blick_y=0.9, blick_x=0.5, sorge=0.9)  # noqa: E731
        return [
            Mit('tb', Gehe(bis=self.vom_rand(random.uniform(0.13, 0.18)), tempo=0.55, haltung=schleichen)),
            Mit('tb', Stehe(2.0, umschauen)),
            Tu(lambda sz: sz.fallen(1)),
            Mit('tb', Stehe(1.3, betreten)),
            Tu(lambda sz: sz.fallen(2)),
            Mit('tb', Stehe(0.4, Pose(kopf_vorn=True, schreck=0.5, sorge=1.0, blick_y=0.9))),
            Mit('tb', Stehe(1.4, lambda d, u: Pose(kopf_vorn=True, sorge=1.0, blick_x=0.0,
                                                   auge_zu=0.7 < u < 0.82))),
            Setze(rollen=True),
            Mit('tb', Gehe(bis=self.aussen(-self.richtung), tempo=0.9, haltung=schleichen)),
            WarteBis(lambda sz: not sz.unten),
        ]

    def schreck_ablauf(self):
        self.nebenbei.clear()
        tb = self.tb
        self.rollen = True
        if not tb.figur_sichtbar():
            return [WarteBis(lambda sz: not sz.unten)]
        x, y = tb.trafo().map(QPointF(0, -130)).x(), tb.trafo().map(QPointF(0, -130)).y()
        self.streue(x, y, 30, NADELN, tempo=260, dauer=1.0, r=(2, 4), schwer=True)
        return [Mit('tb', Erschrecke(0.35, 60)), Tu(lambda sz: setattr(sz, 'flucht', tb.naechster_rand())),
                Mit('tb', Renne(zum='rand', tempo=3.4)), WarteBis(lambda sz: not sz.unten)]

    def fallen(self, i):
        tb = self.tb
        x, y, farbe = tb.kugeln.pop(i)
        q = tb.trafo().map(QPointF(x, y))
        self.unten.append([q.x(), q.y(), 0.0, farbe, 0.0])

    rollen = False
    flucht = None

    def weiter(self, dt):
        s, r = self.s, self.tb.s * 6.5
        boden = self.boden - r
        for k in self.unten:
            if k[1] < boden or k[2] < 0:
                k[2] += 1500 * s * dt
                k[1] += k[2] * dt
                if k[1] >= boden:
                    k[1] = boden
                    k[2] = -k[2] * 0.4 if abs(k[2]) > 150 * s else 0.0
            if self.rollen:
                tb = self.tb
                ziel = tb.x - tb.richtung * 50 * s if self.flucht is None else self.aussen(self.flucht)
                if abs(ziel - k[0]) < 4 * s:
                    continue
                seite = 1 if ziel > k[0] else -1
                k[0] += seite * self.tempo * (1.3 if self.flucht is None else 3.5) * dt
                k[4] += seite * 600 * dt
        self.unten = [k for k in self.unten if self.geo.adjusted(-30, 0, 30, 0).contains(QPointF(k[0], k[1]))
                      or not self.rollen]

    def zeichne_vorn(self, p):
        r = 6.5 * self.tb.s
        for x, y, _, farbe, dreh in self.unten:
            p.setBrush(radial(x - r * 0.4, y - r * 0.45, r * 1.4, farbe.lighter(160), farbe.darker(130)))
            kreis(p, x, y, r)
            w = math.radians(dreh)
            p.setBrush(QColor(255, 255, 255, 180))
            kreis(p, x - r * 0.3, y - r * 0.35, r * 0.25)
            p.setBrush(QColor('#C9A23A'))
            kreis(p, x + math.cos(w) * r * 0.85, y + math.sin(w) * r * 0.85, r * 0.3)

    def grenzen_extra(self):
        k = QRectF()
        r = 10 * self.tb.s
        for x, y, *_ in self.unten:
            k = k.united(QRectF(x - r, y - r, 2 * r, 2 * r))
        return k
