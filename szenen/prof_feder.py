import math
import random

from PyQt6.QtCore import QPointF, QRectF
from PyQt6.QtGui import QColor

from zeichnen.figur import Pose
from zeichnen.figuren import Pinguin
from zeichnen.grundlagen import WEISS, blinzeln, glatt
from zeichnen.labor_b import waage_schale, zeichne_feder, zeichne_klotz, zeichne_schale, zeichne_waage

from .basis import Gehe, Jeweils, Kurz, Mit, Nebenbei, Setze, Stehe, Tu, Wandel, Warte, WarteBis, WarteNebenbei
from .professor import ProfSzene, denk_pose, schieben

STAUB = [QColor(200, 190, 170, 200), QColor(230, 225, 215, 180)]
ARM = 58
W = 1.2             # Waage etwas größer gezeichnet


class Feder(ProfSzene):
    """Auf der Balkenwaage wiegt die Feder mehr als der dicke Eisenklotz. Er drückt, dann
    stemmt er sich mit ganzem Gewicht auf die Klotzseite: nichts. Ein Pinguin pustet die
    Feder weg, Klotz und Professor plumpsen herunter, der Pinguin fängt die Feder."""
    name, titel, reihenfolge = 'feder', 'Schwergewicht Feder', 69

    def vorbereiten(self):
        r, s = self.richtung, self.s
        self.bx = self.vom_rand(random.uniform(0.14, 0.16))
        self.w = -22.0
        self.feder = 'schale'
        self.fx = self.fy = 0.0
        self.fw = 0.0
        self.flug = None
        self.stemmt = 0             # 1 drücken, 2 stemmen
        self.st0 = 0.0
        self.pg = self.dazu('p', Pinguin, groesse=0.6)
        self.pg.x = self.aussen(-r) - r * 40 * s
        self.pg.tempo = self.tempo * 0.55

    # -- Orte (Waage gespiegelt mit der Richtung, Federseite zum Rand)

    def schale(self, seite):
        sx, sy = waage_schale(self.w, seite, ARM)
        return self.bx + self._r * sx * W * self.s, self.boden + sy * W * self.s

    def klotz_griff(self):
        x, y = self.schale(1)
        return x, y - 34 * W * self.s

    def flosse(self):
        d = self.pg
        a = math.radians(d.pose.arm_v + 20)
        q = d.trafo().map(QPointF(-math.sin(a) * 40, -84 + math.cos(a) * 40 + d.pose.hub))
        return q.x(), q.y()

    def ablauf(self):
        self._r = r = self.richtung
        s = self.s
        self.x = self.aussen(-r)
        stand = self.bx + r * 128 * s
        pg_ziel = self.bx - r * (ARM * 0.93 * W + 46) * s

        def staunen(sz, u):
            return Pose(kopf_vorn=u > 0.9, sorge=min(1.0, u), blick_y=0.4 if u < 0.9 else 0, auge_zu=blinzeln(sz.t))

        def blasen(d, u):
            if u > 0.3 and random.random() < 0.6:
                q = d.trafo().map(QPointF(20, -91))
                d.sz.streue(q.x(), q.y(), 1, [QColor(255, 255, 255, 170)], tempo=120, dauer=0.5, r=(2, 4),
                            richtung=0 if r > 0 else math.pi, streuung=0.35)
            return Pose(mund_offen=u > 0.3, hub=2 * math.sin(u * 20) if u > 0.3 else -3 * min(1, u / 0.3),
                        auge_zu=u > 0.3)

        def fangen(d, u):
            return Pose(arm_v=-150 + 10 * math.sin(u * 6), kopf_vorn=False, blick_x=0.0, mund_offen=True,
                        auge_zu=blinzeln(d.t))

        def benommen(sz, u):
            return Pose(kopf_vorn=True, sorge=0.6, blick_x=math.sin(u * 7) * 0.8, blick_y=math.cos(u * 7) * 0.5,
                        arm_v=-20, arm_h=20, wipp=4 * math.sin(u * 7))

        return [
            Gehe(bis=stand),
            Setze(richtung=-r),
            Stehe(1.4, staunen),
            Stehe(0.8, denk_pose),
            Setze(stemmt=1, st0=lambda sz: sz.t),
            Warte(1.3),
            Nebenbei(Mit('p', Gehe(bis=pg_ziel)), Mit('p', Setze(richtung=r)),
                     Mit('p', Stehe(0.6, lambda d, u: Pose(kopf_vorn=True, auge_zu=blinzeln(d.t))))),
            Setze(stemmt=2, st0=lambda sz: sz.t, haare=0.3),
            WarteNebenbei(),
            Mit('p', Stehe(0.5, lambda d, u: Pose(blick_x=0.3, auge_zu=blinzeln(d.t)))),
            Mit('p', Jeweils(1.1, lambda d, u: setattr(d, 'pose', blasen(d, u)))),
            Tu(lambda sz: sz.feder_los()),
            Nebenbei(Mit('p', Stehe(1.9, fangen))),
            Wandel(0.22, w=24.0),
            Tu(lambda sz: sz.plumps()),
            Wandel(0.18, hopp=0.0, neigung=0.0),
            Tu(lambda sz: sz.aufschlag()),
            Kurz(0.22, stauchen=0.78),
            WarteBis(lambda sz: sz.feder == 'pinguin'),
            Nebenbei(Mit('p', Stehe(1.4, lambda d, u: Pose(kopf_vorn=True, auge_zu=True, arm_v=-150,
                                                         hub=-3 * abs(math.sin(u * 8)))))),
            Stehe(1.4, benommen),
            Setze(brille=0.0),
            Nebenbei(Mit('p', Gehe(bis=self.aussen(-r) - r * 30 * s, tempo=1.0))),
            Stehe(0.5, lambda sz, u: Pose(kopf_vorn=True, sorge=0.3, auge_zu=True, arm_v=-20, arm_h=20)),
            Setze(mitnehmen=('bx',)),
            Gehe(bis=self.aussen(-r) - r * 130 * s, haltung=schieben),
            WarteNebenbei(),
        ]

    # -- Handlung

    def feder_los(self):
        self.feder = 'flug'
        x, y = self.schale(-1)
        self.flug = (self.t, x, y - 4 * self.s)

    def plumps(self):
        self.stemmt = 0
        self.haare = 1.0
        self.pose = Pose(schreck=1.0, arm_v=-150, arm_h=-140, arm_v_x=16, bein_v=-20, bein_h=20)

    def aufschlag(self):
        self.brille = 1.0
        s = self.s
        x, y = self.schale(1)
        self.streue(x, y, 10, STAUB, tempo=110, dauer=0.6, r=(4, 9))
        self.streue(self.x, self.boden - 4 * s, 10, STAUB, tempo=110, dauer=0.6, r=(4, 9))

    def weiter(self, dt):
        super().weiter(dt)
        s = self.s
        if self.stemmt and not self.erschreckt:
            u = self.t - self.st0
            gx, gy = self.klotz_griff()
            if self.stemmt == 1:
                self.w = -22 + 1.5 * math.sin(u * 30) * min(1, u)
                self.pose = Pose(arm_v=self.arm_zu(gx, gy + 4 * s) - self.neigung, arm_h=-30, arm_v_x=16, bein_v=-14, bein_h=22,
                                 sorge=0.6, auge_zu=u > 0.4, wipp=2 * math.sin(u * 30))
                self.neigung = 6 * min(1.0, u / 0.3)
            else:
                f = glatt(u / 0.35)
                self.hopp = 24 * s * f + 1.5 * s * math.sin(u * 25)
                self.neigung = 6 + 10 * f
                self.w = -22 + 2.0 * math.sin(u * 25)
                self.pose = Pose(arm_v=self.arm_zu(gx, gy + 2 * s) - self.neigung, arm_h=-60, arm_v_x=16, bein_v=30 + 12 * math.sin(u * 9),
                                 bein_h=50 - 12 * math.sin(u * 9), sorge=1.0, auge_zu=True, mund_offen=u > 1.0,
                                 hub=-2)
        if self.feder == 'schale':
            x, y = self.schale(-1)
            self.fx, self.fy, self.fw = x - self._r * 22 * s, y - 4 * s, -8
        elif self.feder == 'flug':
            t0, x0, y0 = self.flug
            u = min(1.0, (self.t - t0) / 1.8)
            zx, zy = self.flosse()
            self.fx = x0 + (zx - x0) * glatt(u) + math.sin(u * 9) * 14 * s * (1 - u)
            self.fy = y0 + (zy - y0) * u - 70 * s * math.sin(math.pi * u)
            self.fw = 30 * math.sin(u * 8) - 40 * u
            if u >= 1:
                self.feder = 'pinguin'
        elif self.feder == 'pinguin':
            self.fx, self.fy = self.flosse()
            self.fw = -60

    # -- Zeichnen

    def zeichne_requisiten(self, p):
        s, r = self.s, self._r
        p.save()
        p.translate(self.bx, self.boden)
        p.scale(r * s * W, s * W)
        zeichne_waage(p, self.w, None, None, ARM)
        p.restore()

    def zeichne_davor(self, p):
        x, y = self.schale(1)
        p.save()
        p.translate(x, y)
        p.scale(self._r * self.s * W, self.s * W)
        zeichne_klotz(p, 0, 0)
        zeichne_schale(p, 0, 0)
        p.restore()
        if self.feder == 'weg' or (self.feder == 'pinguin' and not self.pg.zeige_figur):
            return
        p.save()
        if self.feder == 'pinguin':
            p.translate(0, -self.senke)
        p.translate(self.fx, self.fy)
        p.scale(self._r * self.s, self.s)
        zeichne_feder(p, 0, 0, self.fw if self.feder != 'schale' else -6, 46)
        p.restore()

    def requisiten_kasten(self):
        s = self.s
        k = QRectF(self.bx - (ARM + 34) * W * s, self.boden - 134 * W * s, (2 * ARM + 68) * W * s, 134 * W * s)
        if self.feder in ('flug', 'pinguin', 'schale'):
            k = k.united(QRectF(self.fx - 40 * s, self.fy - 40 * s, 80 * s, 80 * s))
        return k

    # -- Schreck

    def schreck_ablauf(self):
        self.stemmt = 0
        self.neigung = 0.0
        if self.feder == 'flug':
            self.streue(self.fx, self.fy, 6, WEISS, tempo=60, dauer=0.4, r=(3, 6))
            self.feder = 'weg'
        if self.hopp > 0:
            self.hopp = 0.0
        return self.schreck_versinken()
