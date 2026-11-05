import math
import random
from dataclasses import replace

from PyQt6.QtCore import QPointF, QRectF
from PyQt6.QtGui import QColor

from zeichnen.figur import Pose
from zeichnen.grundlagen import blinzeln, glatt
from zeichnen.labor_b import zeichne_klecks, zeichne_reagenzglas
from zeichnen.professor import HAAR

from .basis import Gehe, Setze, Stehe, Tu
from .professor import ProfSzene, triumph_pose

FARBEN = [QColor('#E8409E'), QColor('#2EC4E6'), QColor('#86D43A')]
KOPF_OBEN = (6, -236)       # Mitte des umgedrehten Glases auf dem Kopf (Figur-Einheiten)
HALB = 18                   # halbe Glaslänge


class Glas:
    def __init__(self, farbe):
        self.farbe = farbe
        self.zustand = 'kaskade'
        self.x = self.y = 0.0
        self.winkel = 0.0
        self.fuell = 0.6
        self.flug = None


class Jonglage(ProfSzene):
    """Er kommt jonglierend mit drei bunten Reagenzgläsern herein, wird übermütig und
    wirft alle hoch: eins landet kopfüber auf seinem Kopf und färbt die Haare. Er macht
    trotzdem die Triumph-Pose, und die beiden anderen landen genau in seinen offenen Händen."""
    name, titel, reihenfolge = 'jonglage', 'Gläserjonglage', 67

    def vorbereiten(self):
        self.glaeser = [Glas(f) for f in FARBEN]
        self.takt = 0.9          # Würfe je Sekunde und Glas
        self.wurf = 52           # Wurfhöhe in Einheiten
        self.jt = 0.0            # Jongliertakt (Phase)
        self.tropfen = 0.0
        self.tropf_farbe = FARBEN[0]
        self.ziel_haar = None

    # -- Orte

    def handort(self, vorn):
        x, y = self.hand(vorn)
        return x, y - (HALB - 2) * self.s

    def kopfort(self):
        q = self.trafo().map(QPointF(*KOPF_OBEN))
        return q.x(), q.y()

    def jongl_arme(self, u):
        w = math.sin(self.jt * 2 * math.pi * 1.5)
        return dict(arm_v=-86 + 14 * w, arm_h=-80 - 14 * w, arm_v_x=22)

    def jongl_pose(self, sz, u):
        return Pose(kopf_vorn=True, auge_zu=blinzeln(sz.t), mund_offen=u > 1.2, blick_y=-0.7, **self.jongl_arme(u))

    def ablauf(self):
        r = self.richtung
        self.x = self.aussen(-r)
        ziel = self.vom_rand(random.uniform(0.15, 0.18))

        def gang(p, sz):
            return replace(p, **sz.jongl_arme(0), blick_y=-0.6)

        def hochschauen(sz, u):
            return Pose(kopf_vorn=True, blick_y=-1.0, mund_offen=True, arm_v=-100, arm_h=-95, arm_v_x=14,
                        sorge=min(1.0, u))

        def starr(sz, u):
            return Pose(kopf_vorn=True, sorge=0.8, auge_zu=0.25 < u < 0.4 or 0.55 < u < 0.7, arm_v=-60, arm_h=-55,
                        arm_v_x=14)

        def tragen(p, sz):
            return replace(p, arm_v=-118, arm_h=-118, arm_v_x=14, kopf_vorn=True, bein_v=p.bein_v * 0.6,
                           bein_h=p.bein_h * 0.6)

        def stolz(sz, u):
            return Pose(kopf_vorn=True, arm_v=-118, arm_h=-118, arm_v_x=14, auge_zu=True, hub=-3 * abs(math.sin(u * 6)))

        return [
            Gehe(bis=ziel, tempo=0.55, haltung=gang),
            Stehe(2.2, self.jongl_pose),
            Setze(takt=1.25, wurf=78),
            Stehe(1.6, lambda sz, u: replace(sz.jongl_pose(sz, u), mund_offen=True, auge_zu=0.6 < u < 0.9)),
            Tu(lambda sz: sz.finale()),
            Stehe(1.35, hochschauen),
            Stehe(0.75, starr),
            Stehe(1.5, triumph_pose),
            Stehe(0.6, lambda sz, u: triumph_pose(sz, 0.8)),
            Stehe(1.2, stolz),
            Gehe(bis=self.aussen(-r), tempo=0.8, haltung=tragen),
        ]

    # -- Gläser

    def finale(self):
        ziele = [(lambda: self.kopfort(), 1.35, 150, 180 + 360),
                 (lambda: self.handort(True), 2.5, 200, 720),
                 (lambda: self.handort(False), 2.95, 230, 360)]
        for g, (ziel, dauer, hoehe, w1) in zip(self.glaeser, ziele):
            g.zustand = 'flug'
            g.flug = dict(t0=self.t, x0=g.x, y0=g.y, w0=g.winkel % 360, ziel=ziel, dauer=dauer, hoehe=hoehe, w1=w1)

    def landung(self, i, g):
        s = self.s
        if i == 0:
            g.zustand = 'kopf'
            g.fuell = 0.0
            self.tropfen = 1.0
            self.tropf_farbe = g.farbe
            self.ziel_haar = (self.t, g.farbe)
            x, y = self.kopfort()
            self.streue(x, y + 10 * s, 14, [g.farbe, g.farbe.lighter(140)], tempo=150, dauer=0.6, r=(2, 4),
                        schwer=True)
        else:
            g.zustand = 'hand_v' if i == 1 else 'hand_h'
            g.winkel = 0.0

    def weiter(self, dt):
        super().weiter(dt)
        self.jt += dt * self.takt
        hv, hh = self.handort(True), self.handort(False)
        for i, g in enumerate(self.glaeser):
            if g.zustand == 'kaskade':
                f = (self.jt + i / 3) % 1
                a, b = (hv, hh) if f < 0.5 else (hh, hv)
                u = (f % 0.5) * 2
                g.x = a[0] + (b[0] - a[0]) * u
                g.y = a[1] + (b[1] - a[1]) * u - self.wurf * self.s * 4 * u * (1 - u)
                g.winkel = (360 * f * 2 + i * 40) % 360
            elif g.zustand == 'flug':
                fl = g.flug
                u = min(1.0, (self.t - fl['t0']) / fl['dauer'])
                zx, zy = fl['ziel']()
                g.x = fl['x0'] + (zx - fl['x0']) * u
                g.y = fl['y0'] + (zy - fl['y0']) * u - fl['hoehe'] * self.s * 4 * u * (1 - u)
                g.winkel = fl['w0'] + (fl['w1'] - fl['w0']) * glatt(u)
                if u >= 1:
                    self.landung(i, g)
            elif g.zustand == 'kopf':
                g.x, g.y = self.kopfort()
                g.winkel = 180 + 6 * math.sin(self.t * 3)
            elif g.zustand in ('hand_v', 'hand_h'):
                g.x, g.y = hv if g.zustand == 'hand_v' else hh
                g.winkel = 0.0
            elif g.zustand == 'kittel':
                fl = g.flug
                u = min(1.0, (self.t - fl['t0']) / 0.22)
                q = self.trafo().map(QPointF(0, -100))
                g.x = fl['x0'] + (q.x() - fl['x0']) * u
                g.y = fl['y0'] + (q.y() - fl['y0']) * u
                if u >= 1:
                    g.zustand = 'weg'
        if self.ziel_haar:
            t0, farbe = self.ziel_haar
            u = min(1.0, (self.t - t0) / 0.7)
            c = QColor(HAAR)
            self.haar_farbe = QColor(int(c.red() + (farbe.red() - c.red()) * u),
                                     int(c.green() + (farbe.green() - c.green()) * u),
                                     int(c.blue() + (farbe.blue() - c.blue()) * u))
        if self.tropfen > 0:
            self.tropfen = max(0.0, self.tropfen - dt * 0.45)

    # -- Zeichnen

    def zeichne_davor(self, p):
        s = self.s
        if self.tropfen > 0 and self.zeige_figur:
            x, y = self.kopfort()
            c = QColor(self.tropf_farbe)
            c.setAlphaF(min(1.0, self.tropfen * 1.5))
            for seite in (-1, 1):
                p.save()
                p.translate(x + seite * 20 * s, y + 16 * s)
                p.scale(s * 0.8, s)
                zeichne_klecks(p, c, laenge=1.0 - self.tropfen * 0.5 + 0.3, t=self.t)
                p.restore()
        for g in self.glaeser:
            if g.zustand == 'weg':
                continue
            if g.zustand in ('kopf', 'hand_v', 'hand_h') and not self.zeige_figur:
                continue
            p.save()
            p.translate(g.x, g.y)
            p.scale(s, s)
            zeichne_reagenzglas(p, g.farbe, g.winkel, g.fuell, self.t)
            p.restore()

    def requisiten_kasten(self):
        k = QRectF()
        s = self.s
        for g in self.glaeser:
            if g.zustand != 'weg':
                k = k.united(QRectF(g.x - 22 * s, g.y - 22 * s, 44 * s, 44 * s))
        return k

    def grenzen_extra(self):
        return self.requisiten_kasten()

    # -- Schreck

    def schreck_ablauf(self):
        for g in self.glaeser:
            if g.zustand != 'weg':
                g.zustand = 'kittel'
                g.flug = dict(t0=self.t, x0=g.x, y0=g.y)
        self.tropfen = 0.0
        if not self.figur_sichtbar():
            for g in self.glaeser:
                g.zustand = 'weg'
        return self.schreck_versinken()

