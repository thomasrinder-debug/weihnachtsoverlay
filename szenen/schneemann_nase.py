import math
import random

from PyQt6.QtCore import QPointF, QRectF

from zeichnen.figur import Pose
from zeichnen.figuren import Schneemann, zeichne_karotte
from zeichnen.grundlagen import WEISS, blinzeln

from .basis import Erschrecke, Gehe, Mit, Nebenbei, Renne, Setze, Stehe, Szene, Tu, Wandel, WarteBis


class SchneemannNase(Szene):
    """Ein Schneemann hüpft herein, niest sich die Möhre aus dem Gesicht, sucht sie
    und steckt sie stolz verkehrt herum wieder an."""
    name, titel, reihenfolge = 'nase', 'Schneemann niest', 10

    def vorbereiten(self):
        self.zeige_figur = False
        self.sm = self.dazu('sm', Schneemann, groesse=0.85, nase=True, nase_dreh=0)
        self.sm.tempo = self.tempo * 0.7
        self.moehre = None          # fliegende Möhre: [x, y, vx, vy, winkel, drehung, liegt]

    def ablauf(self):
        ziel = self.vom_rand(random.uniform(0.1, 0.16))
        return [
            Mit('sm', Gehe(bis=ziel)),
            Mit('sm', Stehe(1.2)),
            # Hatschi!
            Nebenbei(Mit('sm', Wandel(0.7, neigung=-10))),
            Mit('sm', Stehe(0.9, lambda d, u: Pose(auge_zu=u > 0.3, mund_offen=True, sorge=0.5 * u))),
            Mit('sm', Wandel(0.12, neigung=14)),
            Tu(lambda sz: sz.niesen()),
            Mit('sm', Stehe(0.2, Pose(schreck=0.6))),
            Mit('sm', Wandel(0.3, neigung=0)),
            Mit('sm', Stehe(1.6, lambda d, u: Pose(kopf_vorn=True, sorge=0.9, blick_y=0.2,
                                                    auge_zu=blinzeln(d.t)))),
            # hinterher
            WarteBis(lambda sz: sz.moehre[6]),
            Mit('sm', Gehe(bis=lambda d: d.moehre[0] - 40 * d.s * d.richtung, tempo=1.2)),
            Mit('sm', Wandel(0.3, neigung=28)),
            Tu(lambda sz: sz.aufheben()),
            Mit('sm', Wandel(0.3, neigung=0)),
            Mit('sm', Stehe(2.2, lambda d, u: Pose(kopf_vorn=True, auge_zu=blinzeln(d.t, 0.4) or 0.9 < u < 1.4,
                                                    arm_v=-140 if u > 0.6 else 0,
                                                    mund_offen=False))),
            Mit('sm', Gehe(bis=self.aussen(-self.richtung), tempo=1.3)),
        ]

    def schreck_ablauf(self):
        sm = self.sm
        if not sm.figur_sichtbar():
            return [WarteBis(lambda sz: sz.moehre is None or not sz.moehre_sichtbar())]
        self.nebenbei.clear()
        neu = [Mit('sm', Setze(neigung=0)), Mit('sm', Erschrecke(0.35, hoehe=60))]
        if sm.nase:
            neu.insert(1, Tu(lambda sz: sz.niesen(weg=True)))
        elif self.moehre:
            m = self.moehre
            seite = -1 if m[0] - self.geo.left() < self.geo.right() - m[0] else 1
            m[2], m[3], m[5], m[6] = seite * 1600 * self.s, -500 * self.s, seite * 900, False
        return neu + [Mit('sm', Renne(zum='rand', tempo=3.4)),
                      WarteBis(lambda sz: sz.moehre is None or not sz.moehre_sichtbar())]

    def nasen_punkt(self):
        q = self.sm.trafo().map(QPointF(12, -186))
        return q.x(), q.y()

    def niesen(self, weg=False):
        sm, s = self.sm, self.s
        sm.nase = False
        x, y = self.nasen_punkt()
        r = sm.richtung
        if weg:
            seite = sm.naechster_rand()
            self.moehre = [x, y, seite * 1600 * s, -700 * s, 0.0, seite * 900, False]
        else:
            self.moehre = [x, y, r * 190 * s, -560 * s, -8.0, r * 520, False]
        self.streue(x + r * 14 * s, y, 14, WEISS, tempo=160, dauer=0.7, r=(3, 7),
                    richtung=0 if r > 0 else math.pi, streuung=0.7)

    def aufheben(self):
        self.moehre = None
        self.sm.nase = True
        self.sm.nase_dreh = -105      # zeigt jetzt nach oben

    def moehre_sichtbar(self):
        x, y = self.moehre[0], self.moehre[1]
        return self.geo.adjusted(-40, -40, 40, 40).contains(QPointF(x, y))

    def weiter(self, dt):
        m = self.moehre
        if m and not m[6]:
            m[3] += 1500 * self.s * dt
            m[0] += m[2] * dt
            m[1] += m[3] * dt
            m[4] += m[5] * dt
            if m[1] >= self.boden - 5 * self.s and m[3] > 0:
                if self.erschreckt or abs(m[3]) < 120 * self.s:
                    m[1], m[6] = self.boden - 5 * self.s, True
                    m[4] = 180 if math.cos(math.radians(m[4])) < 0 else 0
                else:
                    m[1] = self.boden - 5 * self.s
                    m[3] *= -0.35
                    m[2] *= 0.5
                    m[5] *= 0.5
                    self.streue(m[0], m[1], 5, WEISS, tempo=60, dauer=0.5, r=(2, 5))
                if self.erschreckt:
                    self.moehre = None

    def zeichne_vorn(self, p):
        m = self.moehre
        if not m:
            return
        p.save()
        p.translate(m[0], m[1])
        p.scale(self.sm.s, self.sm.s)
        zeichne_karotte(p, -12, 0, m[4], 24)
        p.restore()

    def grenzen_extra(self):
        if not self.moehre:
            return QRectF()
        r = 34 * self.s
        return QRectF(self.moehre[0] - r, self.moehre[1] - r, 2 * r, 2 * r)

