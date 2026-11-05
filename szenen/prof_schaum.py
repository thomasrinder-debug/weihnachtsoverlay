import math
import random

from PyQt6.QtCore import QPointF, QRectF
from PyQt6.QtGui import QColor

from zeichnen.figur import Pose
from zeichnen.grundlagen import blinzeln, glatt, stift
from zeichnen.labor import zeichne_kolben, zeichne_labortisch
from zeichnen.labor_a import (SCHAUM, SCHAUM_HELL, muetze_trafo, zeichne_paddelarm, zeichne_schaum,
                              zeichne_schaumflocke, zeichne_seifenblase)
from zeichnen.professor import zeichne_muetze_prof

from .basis import Gehe, Jeweils, Setze, Stehe, Tu, Wandel, Warte, WarteBis
from .professor import ProfSzene

ROT_SAFT = QColor('#E0405A')
BLAU_SAFT = QColor('#3E6FE0')
VIOLETT = QColor('#9A55D8')
SCHAUMFARBEN = [SCHAUM_HELL, SCHAUM, QColor(255, 255, 255, 220)]
TISCH_H = 72
BLASE = 60        # Radius der Riesenblase
KINN = 160        # Schaumhöhe bis zum Kinn
BERG = 300        # Schaumhöhe, wenn er verschluckt ist
DRIFT = 2.1       # Dauer der Fahrt zum Rand
LAG = 0.75        # so viel später folgt die Mütze


def mische(a, b, f):
    return QColor(int(a.red() + (b.red() - a.red()) * f), int(a.green() + (b.green() - a.green()) * f),
                  int(a.blue() + (b.blue() - a.blue()) * f))


class Schaum(ProfSzene):
    """Er gießt Rot in Blau, eine einzelne Riesenblase steigt auf. Er drückt sie mit
    beiden Händen herunter, Schaum quillt hervor und steigt ihm bis zum Kinn, trockener
    Blick ins Publikum, dann verschluckt ihn eine Schaumwelle. Nur die Mütze schwimmt
    obenauf, zwei gelbe Handschuhe paddeln heraus, und der ganze Schaumberg treibt mit
    ihm zum Rand hinaus. Die Mütze merkt es erst spät und schaukelt hinterher."""
    name, titel, reihenfolge = 'schaum', 'Schaumberg', 60

    def vorbereiten(self):
        r, s = self.richtung, self.s
        self.tisch_x = self.vom_rand(0.13) + r * 30 * s
        self.px = self.tisch_x - r * 96 * s
        self.b_x = self.tisch_x - r * 34 * s
        self.tisch_da = True
        self.a_fuell, self.b_fuell = 0.7, 0.35
        self.b_mix, self.b_blasen = 0.0, 0.0
        self.giessen = 0.0
        self.blase_r, self.blase_x, self.blase_y = 0.0, self.b_x, self.boden - (TISCH_H + 90) * s
        self.blase_sx, self.blase_sy = 1.0, 1.0
        self.schaum_h, self.schaum_b = 0.0, 0.0
        self.schaum_cx = self.b_x
        self.drift_t = None
        self.sx1 = self.aussen(-r) - r * 200 * s
        self.hut_lose = False
        self.hut_x0 = 0.0
        self.paddeln = 0.0

    # -- Schaum und Mütze

    def schaum_x(self, t=None):
        t = self.t if t is None else t
        if self.drift_t is None or t <= self.drift_t:
            return self.schaum_cx
        u = min(1.0, (t - self.drift_t) / DRIFT)
        return self.schaum_cx + (self.sx1 - self.schaum_cx) * u ** 1.5

    def oberflaeche(self, x):
        """Welt-y der Schaumoberfläche bei Welt-x (Boden, wenn außerhalb)."""
        cx, b = self.schaum_x(), self.schaum_b * self.s
        d = abs(x - cx) / max(1.0, b / 2)
        if d >= 1 or self.schaum_h <= 0:
            return self.boden
        return self.boden - self.schaum_h * self.s * (1 - d * d) ** 0.55

    def hut_ort(self):
        hx = self.hut_x0 + self.schaum_x(self.t - LAG) - self.schaum_cx
        hy = self.oberflaeche(hx)
        if hy >= self.boden - 2:
            hy -= abs(math.sin(self.t * 9)) * 26 * self.s
        else:
            hy += 6 * self.s
        return hx, hy

    def weiter(self, dt):
        super().weiter(dt)
        if not self.hut_lose and self.schaum_h > KINN and self.zeige_figur:
            tr = muetze_trafo(self.pose, self.haare) * self.trafo()
            q = tr.map(QPointF(0, -10))
            if self.oberflaeche(q.x()) < q.y():
                self.hut_lose, self.muetze, self.hut_x0 = True, False, q.x()

    # -- Zeichnen

    def kolben_halt(self, p, hx, hy):
        p.save()
        p.translate(hx, hy)
        p.rotate(105 * self.giessen)
        p.translate(0, 36)
        zeichne_kolben(p, 0, 0, ROT_SAFT, self.a_fuell, 'rund', t=self.t)
        p.restore()

    def zeichne_requisiten(self, p):
        if not self.tisch_da:
            return
        s = self.s
        p.save()
        p.translate(self.tisch_x, self.boden)
        p.scale(s, s)
        zeichne_labortisch(p)
        p.restore()
        p.save()
        p.translate(0, self.boden - TISCH_H * s)
        p.scale(s, s)
        zeichne_kolben(p, self.b_x / s, 0, mische(BLAU_SAFT, VIOLETT, self.b_mix), self.b_fuell, 'erlen',
                       blasen=self.b_blasen, t=self.t)
        p.restore()

    def arm_punkte(self):
        """Schultern der beiden Paddelarme (Welt) und ihre Winkel."""
        r, s = self.richtung, self.s
        x = self.schaum_x() - r * 45 * s
        y = self.oberflaeche(x) + 16 * s
        ph = self.t * 9
        return [(x - r * 20 * s, y, -115 + 75 * math.sin(ph)),
                (x + r * 18 * s, y + 4 * s, -115 + 75 * math.sin(ph + math.pi))]

    def zeichne_davor(self, p):
        s, r = self.s, self.richtung
        if self.giessen > 0.6 and self.halt and self.zeige_figur:
            hx, hy = self.hand()
            bx, by = self.b_x, self.boden - (TISCH_H + 40) * s
            p.setPen(stift(QColor(224, 64, 90, 220), 3.4 * s))
            p.drawLine(QPointF(hx + r * 4 * s, hy + 6 * s), QPointF(bx, by))
            p.setPen(stift(QColor(255, 255, 255, 120), 1.0 * s))
            p.drawLine(QPointF(hx + r * 4 * s, hy + 6 * s), QPointF(bx, by))
        if self.schaum_h > 0:
            p.save()
            p.translate(self.schaum_x(), self.boden)
            p.scale(s, s)
            zeichne_schaum(p, self.schaum_b, self.schaum_h, self.t)
            p.restore()
        if self.paddeln > 0:
            for x, y, w in self.arm_punkte():
                tief = (1 - self.paddeln) * 80 * s
                p.save()
                p.translate(x, y + tief)
                p.scale(-r * 1.6 * s, 1.6 * s)
                zeichne_paddelarm(p, 0, 0, w)
                p.restore()
                p.save()
                p.translate(x, y + tief + 4 * s)
                p.scale(s, s)
                zeichne_schaumflocke(p, 0, 0, 14)
                p.restore()
        if self.blase_r > 0:
            p.save()
            p.translate(self.blase_x, self.blase_y)
            p.scale(s * self.blase_sx, s * self.blase_sy)
            zeichne_seifenblase(p, 0, 0, self.blase_r, self.t)
            p.restore()
        if self.hut_lose:
            hx, hy = self.hut_ort()
            p.save()
            p.translate(hx, hy)
            p.scale(1.15 * s * r, 1.15 * s)
            p.rotate(10 * math.sin(self.t * 4))
            zeichne_muetze_prof(p, 0, -10, 4 * math.sin(self.t * 3))
            if hy < self.boden - 30 * s:
                for dx in (-18, -6, 8, 18):
                    zeichne_schaumflocke(p, dx, 2, 5)
            p.restore()

    def requisiten_kasten(self):
        s = self.s
        k = QRectF()
        if self.tisch_da:
            k = QRectF(self.tisch_x - 70 * s, self.boden - 165 * s, 140 * s, 165 * s)
        if self.schaum_h > 0:
            cx, b = self.schaum_x(), self.schaum_b
            k = k.united(QRectF(cx - (b / 2 + 26) * s, self.boden - (self.schaum_h + 30) * s,
                                (b + 52) * s, (self.schaum_h + 30) * s))
        if self.blase_r > 0:
            rx, ry = (self.blase_r + 6) * s * self.blase_sx, (self.blase_r + 6) * s * self.blase_sy
            k = k.united(QRectF(self.blase_x - rx, self.blase_y - ry, 2 * rx, 2 * ry))
        if self.hut_lose:
            hx, hy = self.hut_ort()
            k = k.united(QRectF(hx - 45 * s, hy - 80 * s, 90 * s, 95 * s))
        if self.paddeln > 0:
            for x, y, _ in self.arm_punkte():
                k = k.united(QRectF(x - 95 * s, y - 95 * s, 190 * s, 190 * s))
        if self.giessen > 0 and self.halt:
            hx, hy = self.hand()
            k = k.united(QRectF(hx - 50 * s, hy - 50 * s, 100 * s, 100 * s))
        return k

    # -- Ablauf

    def ablauf(self):
        r, s = self.richtung, self.s
        self.x = self.aussen(-r)
        b_hals = lambda sz: (sz.b_x - r * 4 * s, sz.boden - (TISCH_H + 84) * s)

        def giesse(sz, u):
            sz.giessen = min(1.0, u / 0.3)
            if u > 0.3:
                f = min(1.0, (u - 0.3) / 0.5)
                sz.a_fuell = 0.7 * (1 - f)
                sz.b_fuell = 0.35 + 0.4 * f
                sz.b_mix = f
            sz.pose = Pose(arm_v=sz.arm_zu(*b_hals(sz)) + 2 * math.sin(u * 9), blick_y=0.6, auge_zu=blinzeln(sz.t))

        def brodeln(sz, u):
            sz.giessen = max(0.0, 1 - u / 0.2)
            sz.b_blasen = min(1.0, u / 0.2)
            return Pose(blick_y=0.6, arm_v=-40, sorge=0.3, auge_zu=blinzeln(sz.t))

        def blase(sz, u):
            f = glatt(u / 0.9)
            sz.blase_r = BLASE * min(1.0, u / 0.7) ** 0.7
            sz.blase_x = sz.b_x + (sz.px + r * 92 * s - sz.b_x) * f
            hals_y = sz.boden - (TISCH_H + 84) * s - sz.blase_r * s
            sz.blase_y = hals_y + (sz.boden - 205 * s - hals_y) * f
            return Pose(arm_v=-30, blick_y=-0.2 - 0.6 * f, schreck=0.4 * f, mund_offen=True, auge_zu=blinzeln(sz.t),
                        hub=2 * f)

        def haende_auf(sz, u):
            top = sz.blase_y - BLASE * s * sz.blase_sy
            x = sz.blase_x - r * 10 * s
            return Pose(arm_v=sz.arm_zu(x, top + 4 * s), arm_h=sz.arm_zu(x + r * 18 * s, top + 4 * s, vorn=False),
                        arm_v_x=16, blick_y=-0.4, sorge=0.2, auge_zu=blinzeln(sz.t))

        def druecken(sz, u):
            f = glatt(u / 0.5)
            sz.blase_sx, sz.blase_sy = 1 + 0.45 * f, 1 - 0.55 * f
            unten = sz.boden - (TISCH_H + 2) * s
            sz.blase_y = (sz.boden - 205 * s) + (unten - BLASE * s * sz.blase_sy - (sz.boden - 205 * s)) * f
            sz.neigung = 10 * f
            top = sz.blase_y - BLASE * s * sz.blase_sy
            x = sz.blase_x - r * 10 * s
            sz.b_fuell = 0.75 * (1 - f)
            return Pose(arm_v=sz.arm_zu(x, top + 4 * s), arm_h=sz.arm_zu(x + r * 18 * s, top + 4 * s, vorn=False),
                        arm_v_x=16, blick_y=0.4, sorge=0.5 * f, mund_offen=f > 0.5, hub=3 * f)

        def plopp(sz):
            sz.streue(sz.blase_x, sz.blase_y, 14, SCHAUMFARBEN, tempo=200, dauer=0.5, r=(5, 9))
            sz.blase_r, sz.blase_sx, sz.blase_sy = 0.0, 1.0, 1.0
            sz.schaum_cx = sz.blase_x
            sz.schaum_h, sz.schaum_b = 30.0, 120.0

        def quellen(sz, u):
            f = 1 - (1 - min(1.0, u / 1.0)) ** 2
            sz.neigung = 10 * max(0.0, 1 - u / 0.2)
            sz.schaum_h = 30 + (KINN - 30) * f
            sz.schaum_b = 120 + 210 * f
            sz.schaum_cx = sz.blase_x + (sz.px + r * 40 * s - sz.blase_x) * f
            if random.random() < 0.3:
                x = sz.schaum_cx + random.uniform(-0.5, 0.5) * sz.schaum_b * s
                sz.streue(x, sz.oberflaeche(x), 1, SCHAUMFARBEN, tempo=50, dauer=0.6, r=(4, 8))
            return Pose(arm_v=-150 - 10 * f, arm_h=-140 - 10 * f, arm_v_x=16, schreck=0.6, sorge=0.8,
                        blick_y=0.6, hub=-2 * abs(math.sin(u * 14)), mund_offen=True)

        def kinn_blick(sz, u):
            return Pose(kopf_vorn=True, arm_v=-160, arm_h=-150, arm_v_x=16, sorge=0.2,
                        auge_zu=0.25 < u < 0.42, blick_y=0.0)

        def welle(sz, u):
            f = min(1.0, u / 0.3)
            sz.schaum_h = KINN + (BERG - KINN) * f ** 0.7
            sz.schaum_b = 330 + 10 * f
            return Pose(kopf_vorn=True, arm_v=-170, arm_h=-165, arm_v_x=16, schreck=1.0)

        def verschluckt(sz):
            sz.zeige_figur, sz.tisch_da = False, False
            sz.streue(sz.schaum_cx, sz.boden - BERG * s, 10, SCHAUMFARBEN, tempo=140, dauer=0.6, r=(6, 12))

        def paddel_spritzer(sz, u):
            if random.random() < 0.35:
                x, y, w = random.choice(sz.arm_punkte())
                a = math.radians(w)
                hx = x - r * math.sin(a) * 83 * s
                sz.streue(hx, sz.oberflaeche(hx), 1, SCHAUMFARBEN, tempo=90, dauer=0.5, r=(4, 8),
                          richtung=-math.pi / 2, streuung=0.9)

        return [
            Setze(halt=lambda sz: sz.kolben_halt),
            Gehe(bis=self.px, tempo=1.8),
            Setze(richtung=r),
            Jeweils(0.85, giesse),
            Stehe(0.3, brodeln),
            Setze(halt=None, giessen=0.0),
            Stehe(0.9, blase),
            Stehe(0.25, haende_auf),
            Stehe(0.5, druecken),
            Tu(plopp),
            Stehe(1.0, quellen),
            Stehe(0.6, kinn_blick),
            Stehe(0.3, welle),
            Tu(verschluckt),
            Warte(0.45),
            Wandel(0.3, paddeln=1.0),
            Jeweils(0.6, paddel_spritzer),
            Tu(lambda sz: setattr(sz, 'drift_t', sz.t)),
            Jeweils(DRIFT + LAG, paddel_spritzer),
            Setze(schaum_h=0.0, paddeln=0.0, hut_lose=False),
            WarteBis(lambda sz: not sz.wolke and not sz.splitter),
        ]

    def schreck_ablauf(self):
        if self.blase_r > 0:
            self.streue(self.blase_x, self.blase_y, 12, SCHAUMFARBEN, tempo=160, dauer=0.5, r=(5, 9))
            self.blase_r = 0.0
        self.neigung = 0.0
        return self.schreck_versinken()
