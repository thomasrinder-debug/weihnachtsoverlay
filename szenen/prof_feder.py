import math
import random

from PyQt6.QtCore import QPointF, QRectF
from PyQt6.QtGui import QColor

from zeichnen.figur import Pose
from zeichnen.figuren import Pinguin
from zeichnen.grundlagen import WEISS, blinzeln, glatt
from zeichnen.labor_b import waage_schale, zeichne_feder, zeichne_riesenklotz, zeichne_waage

from .basis import Gehe, Jeweils, Mit, Nebenbei, Setze, Stehe, Tu, Wandel, WarteBis, WarteNebenbei
from .professor import STAUB, ProfSzene, Publikumsblick, wuerde_pose

ARM = 58
HW = 100            # Höhe der Waage
W = 1.5             # Waage größer gezeichnet
KB, KH = 64, 56     # Riesenklotz (Waage-Einheiten)
FG = 2.6            # Feder vergrößert: 40 · 2,6 ≈ 0,4 H
W_AUS = -22.0       # Federseite unten
W_KIPP = 32.0


def hinke(pose, sz):
    """Humpeln mit Hand im Kreuz, vornübergebeugt."""
    sz.hopp = 4 * sz.s * abs(math.sin(sz.phase * 0.5 * math.pi))
    return Pose(bein_v=pose.bein_v * 0.6, bein_h=6, arm_v=-30, arm_h=60, arm_v_x=14, hub=pose.hub * 2 - 3,
                sorge=0.8, auge_zu=True, mund_offen=(sz.t * 3) % 2 < 1)


class Feder(ProfSzene):
    """Balkenwaage: die Feder wiegt mehr als ein Riesenklotz. Er drückt mit einer Hand,
    stemmt sich mit beiden auf den Klotz, hängt schließlich waagerecht daran und strampelt.
    Der Pinguin pustet die Feder weg, eine Schrecksekunde in der Luft, dann krachen Klotz
    und Professor herunter, die Beine schlagen hoch. Der Pinguin fängt die Feder; er steht
    steif auf, Publikumsblick, Kittel glatt, und humpelt mit der Hand im Kreuz hinaus."""
    name, titel, reihenfolge = 'feder', 'Schwergewicht Feder', 69

    def vorbereiten(self):
        r, s = self.richtung, self.s
        self.bx = self.vom_rand(random.uniform(0.11, 0.13))
        self.w = W_AUS
        self.feder = 'schale'
        self.fx = self.fy = 0.0
        self.fw = 0.0
        self.flug = None
        self.klotz_fall = None          # (t0, x0, y0) sobald er von der Schale stürzt
        self.kx = self.ky = 0.0
        self.kdreh = 0.0
        self.pg = self.dazu('p', Pinguin, groesse=0.6)
        self.pg.x = self.aussen(-r) - r * 40 * s
        self.pg.tempo = self.tempo * 0.9

    # -- Orte (Waage gespiegelt mit der Richtung, Federseite zum Rand)

    def schale(self, seite, w=None):
        sx, sy = waage_schale(self.w if w is None else w, seite, ARM, HW)
        return self.bx + self._r * sx * W * self.s, self.boden + sy * W * self.s

    def klotz_ort(self):
        if self.klotz_fall:
            return self.kx, self.ky
        return self.schale(1)

    def griff(self, art):
        """Weltpunkt am Klotz: 'ecke' (obere Kante zu ihm) oder 'buegel'."""
        x, y = self.klotz_ort()
        k = W * self.s
        if art == 'ecke':
            return x + self._r * (KB * 0.36) * k, y - KH * k
        return x, y - (KH + 13) * k

    def flosse(self):
        d = self.pg
        a = math.radians(d.pose.arm_v + 20)
        q = d.trafo().map(QPointF(-math.sin(a) * 40, -84 + math.cos(a) * 40 + d.pose.hub))
        return q.x(), q.y()

    def an_griff(self, ziel, start, k):
        """Verschiebt ihn so, dass die vordere Hand am Ziel liegt (überblendet mit k)."""
        hx, hy = self.hand()
        x1, hopp1 = self.x + ziel[0] - hx, self.hopp - (ziel[1] - hy)
        self.x = start[0] + (x1 - start[0]) * k
        self.hopp = start[1] + (hopp1 - start[1]) * k

    # -- Ablauf

    def ablauf(self):
        self._r = r = self.richtung
        s = self.s
        self.x = self.aussen(-r)
        stand = self.bx + r * (ARM * W + 78) * s
        pg_ziel = self.bx - r * (ARM * W + 58) * s
        merk = {}

        def start(sz, schluessel):
            if schluessel not in merk:
                merk[schluessel] = (sz.x, sz.hopp, sz.neigung)
            return merk[schluessel]

        def pruefen(sz, u):
            return Pose(blick_y=0.7 if u < 0.45 else -0.7, blick_x=-0.3, arm_v=-150, arm_v_x=12,
                        auge_zu=0.42 < u < 0.5, sorge=0.3 if u > 0.5 else 0)

        def druecken(sz, u):
            gx, gy = sz.griff('ecke')
            sz.hopp = 7 * s * min(1.0, u / 0.2)
            sz.w = W_AUS + 1.2 * math.sin(u * 30) * min(1.0, u / 0.2)
            sz.neigung = 8 * min(1.0, u / 0.2)
            sz.pose = Pose(arm_v=sz.arm_zu(gx, gy) - sz.neigung, arm_h=-30, arm_v_x=16, bein_v=-6, bein_h=16,
                           sorge=0.7, auge_zu=u > 0.3, wipp=2 * math.sin(u * 30), mund_offen=u > 0.5)

        def stemmen(sz, u):
            x0, h0, n0 = start(sz, 'stemmen')
            k = glatt(u / 0.18)
            sz.neigung = n0 + (12 - n0) * k
            b = 30 * math.sin(u * 22)
            sz.pose = Pose(arm_v=-25, arm_h=-20, arm_v_x=16, bein_v=-20 + b, bein_h=30 - b, sorge=1.0,
                           auge_zu=True, mund_offen=True, hub=-2)
            sz.an_griff(sz.griff('ecke'), (x0, h0), k)
            sz.w = W_AUS + 1.5 * math.sin(u * 26)

        def flagge(sz, u):
            x0, h0, n0 = start(sz, 'flagge')
            k = glatt(u / 0.22)
            sz.neigung = n0 + (84 - n0) * k + 3 * math.sin(u * 13)
            b = 40 * math.sin(u * 26)
            sz.pose = Pose(arm_v=-172, arm_h=-165, arm_v_x=12, bein_v=b, bein_h=-b, sorge=1.0,
                           auge_zu=u < 0.9, mund_offen=True, hub=0, kopf_vorn=u > 1.0)
            sz.an_griff(sz.griff('buegel'), (x0, h0), k)
            sz.w = W_AUS + 1.8 * math.sin(u * 26)

        def schrecksekunde(sz, u):
            sz.neigung = 84
            sz.pose = Pose(arm_v=-172, arm_h=-165, arm_v_x=12, bein_v=-4, bein_h=4, schreck=1.0, kopf_vorn=True)
            sz.an_griff(sz.griff('buegel'), (sz.x, sz.hopp), 1.0)

        def sturz(sz, u):
            x0, h0, n0 = start(sz, 'sturz')
            f = min(1.0, u / 0.28)
            sz.w = W_AUS + (W_KIPP + 4 - W_AUS) * glatt(min(1.0, u / 0.2))
            sz.hopp = h0 + (34 * s - h0) * f * f
            sz.x = x0 + r * 20 * s * f
            sz.neigung = n0 + (90 - n0) * f
            sz.pose = Pose(arm_v=-172, arm_h=-160, arm_v_x=12, bein_v=-10 * f, bein_h=10 * f, schreck=1.0,
                           kopf_vorn=True, mund_offen=True)

        def beine_hoch(sz, u):
            """Bauchklatscher: Kopf bleibt am Boden, Hinterteil und Beine schlagen hoch."""
            sz.w = W_KIPP + 4 * math.cos(u * 18) * max(0.0, 1 - u / 0.5)
            if 'kopf' not in merk:
                q = sz.trafo().map(QPointF(4, -205))
                merk['kopf'] = (q.x(), q.y())
            if u < 0.14:
                f = glatt(u / 0.14)
            else:
                v = (u - 0.14) / 0.6
                f = max(0.0, 1 - v) ** 2 + 0.25 * abs(math.sin(v * 8)) * max(0.0, 1 - v)
            sz.neigung = 90 + 38 * f
            sz.pose = Pose(arm_v=-172, arm_h=-160, arm_v_x=12, bein_v=120 * f, bein_h=100 * f, auge_zu=u > 0.25,
                           kopf_vorn=True, schreck=1.0 if u < 0.25 else 0.0)
            q = sz.trafo().map(QPointF(4, -205))
            kx, ky = merk['kopf']
            sz.x += kx - q.x()
            sz.hopp -= ky - q.y()

        def blasen(d, u):
            if u > 0.2 and random.random() < 0.7:
                q = d.trafo().map(QPointF(20, -91))
                d.sz.streue(q.x(), q.y(), 1, [QColor(255, 255, 255, 190)], tempo=160, dauer=0.5, r=(3, 6),
                            richtung=-0.5 if r > 0 else math.pi + 0.5, streuung=0.35)
            return Pose(mund_offen=u > 0.2, hub=-4 * min(1, u / 0.2) if u < 0.2 else 2,
                        auge_zu=u > 0.2)

        def fangen(d, u):
            return Pose(arm_v=-150 + 10 * math.sin(u * 6), blick_x=0.0, blick_y=-0.6, mund_offen=True,
                        auge_zu=blinzeln(d.t))

        def stolz(d, u):
            return Pose(kopf_vorn=True, auge_zu=True, arm_v=-150, hub=-3 * abs(math.sin(u * 8)))

        def aufstehen(sz, u):
            sz.pose = Pose(kopf_vorn=True, arm_v=-8, arm_h=8, auge_zu=False, sorge=0.5)

        return [
            Nebenbei(WarteBis(lambda sz: sz.t > 2.9), Mit('p', Gehe(bis=pg_ziel)), Mit('p', Setze(richtung=r)),
                     Mit('p', Stehe(0.4, lambda d, u: Pose(kopf_vorn=True, auge_zu=blinzeln(d.t), blick_y=0.3)))),
            Gehe(bis=stand, tempo=1.8),
            Setze(richtung=-r),
            Stehe(0.55, pruefen),
            # Versuch 1: eine Hand
            Jeweils(0.8, druecken),
            # Versuch 2: stemmt sich mit beiden Händen auf, Füße in der Luft
            Jeweils(0.8, stemmen),
            # Versuch 3: hängt waagerecht am Bügel und strampelt
            Jeweils(1.2, flagge),
            Mit('p', Stehe(0.25, lambda d, u: Pose(blick_x=0.4, blick_y=0.3, auge_zu=blinzeln(d.t)))),
            Nebenbei(Jeweils(0.55, flagge)),
            Mit('p', Jeweils(0.55, lambda d, u: setattr(d, 'pose', blasen(d, u)))),
            Tu(lambda sz: sz.nebenbei.clear()),
            Tu(lambda sz: sz.feder_los()),
            Nebenbei(Mit('p', Stehe(2.3, fangen)), Mit('p', Stehe(1.2, stolz))),
            Jeweils(0.35, schrecksekunde),
            Jeweils(0.28, sturz),
            Tu(lambda sz: sz.aufschlag()),
            Jeweils(0.9, beine_hoch),
            Wandel(0.25, neigung=0.0, hopp=0.0),
            Stehe(0.05, aufstehen),
            Publikumsblick(1.0),
            Stehe(0.5, wuerde_pose),
            Nebenbei(Mit('p', Gehe(bis=self.aussen(-r) - r * 30 * s, tempo=1.3))),
            Gehe(bis=self.aussen(-r) - r * 40 * s, tempo=1.05, haltung=hinke, neigung=18),
            Tu(lambda sz: sz.weg(STAUB)),
            WarteNebenbei(),
            WarteBis(lambda sz: not sz.wolke and not sz.splitter),
        ]

    # -- Handlung

    def feder_los(self):
        self.feder = 'flug'
        self.flug = (self.t, self.fx, self.fy)

    def aufschlag(self):
        self.brille = 1.0
        self.haare = 1.0
        s = self.s
        x, y = self.kx, self.boden
        self.streue(x, y - 6 * s, 16, STAUB, tempo=170, dauer=0.7, r=(7, 14), richtung=-math.pi / 2, streuung=1.5)
        k = self.figur_kasten()
        for _ in range(12):
            self.streue(random.uniform(k.left(), k.right()), self.boden - 6 * s, 1, STAUB, tempo=130, dauer=0.7,
                        r=(7, 13), richtung=-math.pi / 2, streuung=1.2)

    def weiter(self, dt):
        super().weiter(dt)
        s, r = self.s, self._r
        if self.erschreckt:
            return
        # Klotz rutscht von der kippenden Schale und kracht auf den Boden
        if self.klotz_fall is None and self.w > 10:
            x, y = self.schale(1)
            self.klotz_fall = (self.t, x, y)
            self.kx, self.ky = x, y
        if self.klotz_fall:
            t0, x0, y0 = self.klotz_fall
            u = self.t - t0
            f = min(1.0, (u / 0.2) ** 2)
            self.kx = x0 + r * 26 * s * min(1.0, u / 0.2)
            self.ky = y0 + (self.boden - y0) * f
            self.kdreh = r * (10 * f if u < 0.2 else 6 + 4 * math.cos((u - 0.2) * 25) * max(0.0, 1 - (u - 0.2) / 0.4))
        if self.feder == 'schale':
            x, y = self.schale(-1)
            self.fx, self.fy, self.fw = x - r * 50 * s, y - 6 * s, -6
        elif self.feder == 'flug':
            t0, x0, y0 = self.flug
            u = min(1.0, (self.t - t0) / 2.3)
            zx, zy = self.flosse()
            # hoch hinaus, dann gemächlich pendelnd herab in die Flosse
            cx, cy = x0 + r * 120 * s, self.boden - 360 * s
            a = (1 - u) ** 2
            b = 2 * u * (1 - u)
            c = u * u
            self.fx = a * x0 + b * cx + c * zx + math.sin(u * 14) * 22 * s * math.sin(math.pi * u)
            self.fy = a * y0 + b * cy + c * zy
            self.fw = 35 * math.sin(u * 12) - 50 * u
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
        zeichne_waage(p, self.w, None, None, ARM, HW)
        p.restore()
        x, y = self.klotz_ort()
        p.save()
        p.translate(x, y)
        p.scale(r * s * W, s * W)
        zeichne_riesenklotz(p, 0, 0, KB, KH, self.kdreh * r)
        p.restore()

    def zeichne_davor(self, p):
        if self.feder == 'weg' or (self.feder == 'pinguin' and not self.pg.zeige_figur):
            return
        p.save()
        if self.feder == 'pinguin':
            p.translate(0, -self.senke)
        p.translate(self.fx, self.fy)
        p.scale(self._r * self.s * FG, self.s * FG)
        zeichne_feder(p, 0, 0, self.fw, 40)
        p.restore()

    def requisiten_kasten(self):
        s = self.s
        k = QRectF(self.bx - (ARM + 30) * W * s, self.boden - (HW + 10) * W * s, (2 * ARM + 60) * W * s,
                   (HW + 10) * W * s)
        x, y = self.klotz_ort()
        k = k.united(QRectF(x - KB * 0.75 * W * s, y - (KH + 22) * W * s, KB * 1.5 * W * s, (KH + 24) * W * s))
        if self.feder in ('flug', 'pinguin', 'schale'):
            k = k.united(QRectF(self.fx - 120 * s, self.fy - 120 * s, 240 * s, 240 * s))
        return k

    # -- Schreck

    def schreck_ablauf(self):
        self.nebenbei.clear()
        self.neigung = 0.0
        self.hopp = 0.0
        if self.feder == 'flug':
            self.streue(self.fx, self.fy, 6, WEISS, tempo=60, dauer=0.4, r=(3, 6))
            self.feder = 'weg'
        return self.schreck_versinken()
