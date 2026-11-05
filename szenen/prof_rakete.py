import math
import random

from PyQt6.QtCore import QPointF, QRectF
from PyQt6.QtGui import QColor, QTransform

from zeichnen.figur import Pose
from zeichnen.grundlagen import blinzeln
from zeichnen.labor import zeichne_labortisch
from zeichnen.labor_a import (muetze_trafo, zeichne_fallschirm, zeichne_rakete, zeichne_startrampe,
                              zeichne_streichholz)
from zeichnen.professor import zeichne_muetze_prof

from .basis import Gehe, Jeweils, Setze, Stehe, Tu, Wandel
from .professor import FUNKEN, RAUCH, ProfSzene, triumph_pose, ziehen

TISCH_H = 72
NEIGUNG = 34.0
RG = 1.3        # Größe der Rakete
SG = 1.7        # Größe des Fallschirms
FLUG = 0.95
SINKEN = 2.8


class Rakete(ProfSzene):
    """Die Mini-Rakete zündet nicht, er klopft drauf, nichts. Kaum steht er in der
    Triumph-Pose, startet sie und nimmt seine Mütze mit. Die Mütze schwebt am
    Mini-Fallschirm zurück auf seinen Kopf, und er nickt, als sei das so geplant."""
    name, titel, reihenfolge = 'rakete', 'Mützenrakete', 63

    def vorbereiten(self):
        r, s = self.richtung, self.s
        self.tisch_x = self.vom_rand(0.2) + r * 30 * s
        self.px = self.tisch_x - r * 104 * s
        self.winkel = 0.0
        self.schnur, self.funke = 1.0, False
        self.flamme = 0.0
        self.flug = None          # Startzeit
        self.rakete_da = True
        self.hut_rakete = False
        self.hut_t = None         # Beginn des Sinkflugs
        self.hut_start = (0.0, 0.0)
        self.schirm = 0.0
        self.muetze = True

    # -- Rakete

    def heck0(self):
        return self.tisch_x - self.richtung * 40 * self.s, self.boden - (TISCH_H + 13) * self.s

    def rakete_lage(self):
        """Heck (Welt) und Winkel der Rakete."""
        x0, y0 = self.heck0()
        w = self.winkel
        if self.flug is None:
            return x0, y0, w
        u = self.t - self.flug
        d = 440 * u * u * self.s
        a = math.radians(w)
        return x0 + math.sin(a) * d, y0 - math.cos(a) * d, w

    def nase(self):
        x, y, w = self.rakete_lage()
        a = math.radians(w)
        return x + math.sin(a) * 55 * RG * self.s, y - math.cos(a) * 55 * RG * self.s

    # -- Mütze

    def hut_ziel(self):
        tr = muetze_trafo(self.pose, self.haare, vorn=True) * self.trafo()
        q = tr.map(QPointF(0, -10))
        return tr, q

    def hut_trafo(self):
        tr, q = self.hut_ziel()
        v = min(1.0, (self.t - self.hut_t) / SINKEN)
        pendel = math.sin(v * math.pi * 3.5) * (1 - v)
        dx = self.hut_start[0] * (1 - v) + 40 * self.s * pendel
        dy = self.hut_start[1] * (1 - v) ** 1.15
        f = QTransform()
        f.translate(q.x() + dx, q.y() + dy)
        f.rotate(18 * pendel)
        f.translate(-q.x(), -q.y())
        return tr * f

    def schirm_punkt(self):
        tr = self.hut_trafo() if self.hut_t is not None else self.hut_ziel()[0]
        q = tr.map(QPointF(-4, -30))
        return q.x(), q.y()

    # -- Zeichnen

    def zuendholz(self, p, hx, hy):
        zeichne_streichholz(p, hx, hy, 40, True, self.t)

    def zeichne_requisiten(self, p):
        s = self.s
        p.save()
        p.translate(self.tisch_x, self.boden)
        p.scale(s, s)
        zeichne_labortisch(p)
        p.restore()
        x0, _ = self.heck0()
        p.save()
        p.translate(x0, self.boden - TISCH_H * s)
        p.scale(s, s)
        zeichne_startrampe(p, 0, 0)
        p.restore()

    def zeichne_davor(self, p):
        s, r = self.s, self.richtung
        if self.rakete_da:
            x, y, w = self.rakete_lage()
            p.save()
            p.translate(x, y)
            p.scale(s * RG, s * RG)
            zeichne_rakete(p, 0, 0, w, self.flamme, self.t, self.schnur, self.funke)
            p.restore()
            if self.hut_rakete:
                nx, ny = self.nase()
                p.save()
                p.translate(nx, ny)
                p.rotate(w)
                p.scale(1.12 * s * r, 1.12 * s)
                zeichne_muetze_prof(p, 0, 16, -5)
                p.restore()
        if self.hut_t is not None:
            p.save()
            p.setTransform(self.hut_trafo(), True)
            zeichne_muetze_prof(p, 0, 0, 3 * math.sin(self.t * 4))
            p.restore()
        if self.schirm > 0 and (self.hut_t is not None or self.muetze):
            x, y = self.schirm_punkt()
            p.save()
            p.translate(x, y)
            p.scale(s * SG, s * SG)
            zeichne_fallschirm(p, 0, 0, self.schirm, self.t)
            p.restore()

    def requisiten_kasten(self):
        s = self.s
        k = QRectF(self.tisch_x - 70 * s, self.boden - 150 * s, 140 * s, 150 * s)
        if self.rakete_da:
            x, y, _ = self.rakete_lage()
            nx, ny = self.nase()
            k = k.united(QRectF(min(x, nx) - 40 * s, min(y, ny) - 40 * s,
                                abs(x - nx) + 80 * s, abs(y - ny) + 80 * s))
        if self.hut_t is not None:
            k = k.united(self.hut_trafo().mapRect(QRectF(-40, -60, 80, 72)))
        if self.schirm > 0:
            x, y = self.schirm_punkt()
            k = k.united(QRectF(x - 36 * SG * s, y - 60 * SG * s, 72 * SG * s, 64 * SG * s))
        return k

    # -- Ablauf

    def ablauf(self):
        r, s = self.richtung, self.s
        self.x = self.aussen(-r)

        def zuenden(sz, u):
            x0, y0 = sz.heck0()
            sz.neigung = 14 * min(1.0, u / 0.3)
            return Pose(arm_v=sz.arm_zu(x0 + r * 10 * s, y0 + 4 * s), blick_y=0.7, auge_zu=blinzeln(sz.t))

        def brennen(sz, u):
            sz.schnur = 1.0 - 0.6 * min(1.0, u / 1.1)
            if random.random() < 0.3:
                x0, y0 = sz.heck0()
                sz.streue(x0 + r * 9 * RG * sz.schnur * s, y0 + 6 * RG * sz.schnur * s, 1, FUNKEN, tempo=60, dauer=0.3,
                          r=(2, 3), art='stern')
            return Pose(blick_y=0.7, arm_v=-30, mund_offen=True, auge_zu=blinzeln(sz.t))

        def verpufft(sz):
            x0, y0 = sz.heck0()
            sz.funke = False
            sz.streue(x0 + r * 4 * s, y0 + 2 * s, 5, RAUCH, tempo=25, dauer=0.8, r=(3, 6))

        def klopfen(sz, u):
            nx, ny = sz.nase()
            schlag = abs(math.sin(u * math.pi * 3 / 1.2))
            sz.winkel = -r * NEIGUNG * min(1.0, u / 1.2) + 5 * math.sin(u * 20) * (1 - min(1.0, u / 1.2))
            return Pose(arm_v=sz.arm_zu(nx, ny - 14 * s * schlag), blick_y=0.6, sorge=0.5)

        def start(sz):
            sz.flug, sz.flamme = sz.t, 1.0
            sz.schnur = 0.0

        def fliegen(sz, u):
            x, y, _ = sz.rakete_lage()
            sz.streue(x, y, 1, RAUCH, tempo=20, dauer=0.7, r=(4, 9))
            if not sz.hut_rakete and sz.muetze and (sz.nase()[0] - (sz.x + r * 6 * s)) * r <= 0:
                sz.hut_rakete, sz.muetze = True, False
                sz.streue(sz.x, sz.y - 220 * s, 6, FUNKEN, tempo=120, dauer=0.4, r=(2, 4), art='stern')
            sz.pose = Pose(kopf_vorn=True, schreck=1.0, arm_v=-120, arm_h=-110, arm_v_x=20, blick_y=-0.8,
                           blick_x=-r * 0.5)
            sz.hopp = 10 * s * math.sin(min(1.0, u / 0.4) * math.pi)

        def platzen(sz):
            nx, ny = sz.nase()
            sz.streue(nx, ny, 18, FUNKEN + [QColor('#7CD4FF'), QColor('#FF7CB8')], tempo=240, dauer=0.8,
                      r=(3, 6), art='stern')
            sz.streue(nx, ny, 8, RAUCH, tempo=60, dauer=0.7, r=(6, 12))
            sz.rakete_da = sz.hut_rakete = False
            sz.hopp = 0.0
            sz.pose = Pose(kopf_vorn=True, blick_y=-0.9)
            _, q = sz.hut_ziel()
            sz.hut_start = (nx - q.x(), ny + 12 * s - q.y())
            sz.hut_t = sz.t

        def schauen(sz, u):
            return Pose(kopf_vorn=True, blick_y=-0.9 * (1 - u / SINKEN) ** 0.5,
                        blick_x=0.6 * math.sin(u / SINKEN * math.pi * 3.5) * (1 - u / SINKEN),
                        auge_zu=blinzeln(sz.t), mund_offen=True)

        def landen(sz):
            sz.hut_t, sz.muetze = None, True

        def nicken(sz, u):
            return Pose(kopf_vorn=True, auge_zu=True, arm_v=-60, arm_h=-55, arm_v_x=16,
                        hub=-3 * abs(math.sin(u * 6)), wipp=2 * math.sin(u * 6))

        return [
            Gehe(bis=self.px),
            Setze(richtung=r),
            Stehe(0.5, lambda sz, u: Pose(blick_y=0.6, auge_zu=blinzeln(sz.t))),
            Setze(halt=lambda sz: sz.zuendholz),
            Stehe(0.7, zuenden),
            Setze(funke=True, halt=None),
            Wandel(0.3, neigung=0.0),
            Stehe(1.1, brennen),
            Tu(verpufft),
            Stehe(1.0, lambda sz, u: Pose(blick_y=0.7, sorge=min(1.0, u), auge_zu=0.5 < u < 0.62)),
            Stehe(1.2, klopfen),
            Stehe(0.8, lambda sz, u: Pose(blick_y=0.6, sorge=0.8, arm_v=-20, auge_zu=blinzeln(sz.t))),
            Stehe(0.6, lambda sz, u: Pose(kopf_vorn=True, sorge=0.6, arm_v=-60, arm_h=-60, arm_v_x=16)),
            Stehe(1.1, lambda sz, u: triumph_pose(sz, u)),
            Tu(start),
            Jeweils(FLUG, fliegen),
            Tu(platzen),
            Wandel(0.35, schirm=1.0),
            Stehe(SINKEN - 0.35, schauen),
            Tu(landen),
            Wandel(0.4, schirm=0.0),
            Stehe(1.6, nicken),
            Stehe(0.4, lambda sz, u: Pose(kopf_vorn=True, auge_zu=blinzeln(sz.t))),
            Setze(mitnehmen=('tisch_x',)),
            Gehe(bis=self.aussen(-r) - r * 260 * s, haltung=ziehen),
        ]

    def schreck_ablauf(self):
        s = self.s
        if self.rakete_da and self.flug is not None:
            nx, ny = self.nase()
            self.streue(nx, ny, 12, RAUCH, tempo=90, dauer=0.6, r=(6, 12))
            self.rakete_da = self.hut_rakete = False
        if self.hut_t is not None or self.schirm > 0:
            x, y = self.schirm_punkt()
            self.streue(x, y, 12, RAUCH, tempo=90, dauer=0.6, r=(6, 12))
            self.hut_t, self.schirm = None, 0.0
        self.hopp, self.neigung = 0.0, 0.0
        return self.schreck_puff()
