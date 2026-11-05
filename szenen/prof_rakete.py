import math
import random

from PyQt6.QtCore import QPointF, QRectF
from PyQt6.QtGui import QColor, QPainterPath, QTransform

from zeichnen.figur import Pose
from zeichnen.grundlagen import KEIN_PINSEL, KEIN_STIFT, blinzeln, glatt, stift
from zeichnen.labor_a import (muetze_trafo, zeichne_ausloeser, zeichne_fallschirm, zeichne_rakete,
                              zeichne_startrampe)
from zeichnen.professor import zeichne_muetze_prof

from .basis import Ducke, Gehe, Jeweils, Setze, Stehe, Tu, Wandel, WarteBis
from .professor import RAUCH, STAUB, Knall, ProfSzene, Publikumsblick, explodiert, wuerde_pose

RG = 2.8          # Größe der Rakete (gut 150 Einheiten lang)
ST = 2.0          # Größe der Startrampe
SG = 2.6          # Größe des Fallschirms
FLUG = 1.0
SINKEN = 1.45
KABEL = 175       # Kabellänge Auslöser – Rampe in Einheiten
KABEL_FARBE = QColor('#2B2622')


class Rakete(ProfSzene):
    """Die große Rakete will nicht: Knopf am Auslöser, Klaps, Tritt gegen die Rampe,
    nichts. Er legt das Ohr an die Rakete, Stille, dann startet sie, spießt seine Mütze
    auf und zischt flach über ihn hinweg aus dem Bild. Rußgesicht, Haare zu Berge, er
    duckt sich zu spät. Die Mütze kehrt am Fallschirm zurück und rutscht ihm über die
    Augen; blind tastet er sich hinaus und schleift die leere Rampe am Kabel hinterher."""
    name, titel, reihenfolge = 'rakete', 'Mützenrakete', 63

    def vorbereiten(self):
        r, s = self.richtung, self.s
        self.rand = -r
        self.rampe_x = self.vom_rand(0.13)
        self.rampe_dreh, self.rampe_hopp = 0.0, 0.0
        self.px = self.rampe_x - r * 80 * s
        self.winkel, self.rk_hopp = 0.0, 0.0
        self.flamme = 0.0
        self.flug = None
        self.rakete_da = True
        self.hut_rakete = False
        self.hut_t = None
        self.schirm = 0.0
        self.tief = False          # Mütze sitzt über den Augen
        self.druck = 0.0
        self.schleift = False

    # -- Rakete

    def heck0(self):
        return self.rampe_x, self.boden - (13 * ST + self.rk_hopp) * self.s

    def bahn(self, v):
        """Punkt und Richtung (Grad) auf der Flugbahn, v 0..1."""
        r, s = self.richtung, self.s
        x0, y0 = self.flug_start
        x1, y1 = self.rampe_x - r * 30 * s, self.boden - 400 * s
        x2, y2 = self.aussen(-r) - r * 260 * s, self.boden - 380 * s
        a, b, c = (1 - v) ** 2, 2 * v * (1 - v), v * v
        x, y = a * x0 + b * x1 + c * x2, a * y0 + b * y1 + c * y2
        dx = 2 * (1 - v) * (x1 - x0) + 2 * v * (x2 - x1)
        dy = 2 * (1 - v) * (y1 - y0) + 2 * v * (y2 - y1)
        return x, y, math.degrees(math.atan2(dx, -dy))

    def rakete_lage(self):
        """Heck (Welt) und Winkel der Rakete."""
        if self.flug is None:
            x0, y0 = self.heck0()
            return x0, y0, self.winkel
        u = min(1.0, (self.t - self.flug) / FLUG)
        return self.bahn(0.03 + 0.97 * u ** 1.7)

    def nase(self):
        x, y, w = self.rakete_lage()
        a = math.radians(w)
        return x + math.sin(a) * 55 * RG * self.s, y - math.cos(a) * 55 * RG * self.s

    def rumpf(self, anteil):
        x, y, w = self.rakete_lage()
        a = math.radians(w)
        d = 55 * RG * self.s * anteil
        return x + math.sin(a) * d, y - math.cos(a) * d

    # -- Mütze

    def hut_kopf(self):
        """Trafo der Mütze auf dem Kopf (Figur-Einheiten → Welt), über den Augen bei self.tief."""
        vorn = self.pose.kopf_vorn
        tr = muetze_trafo(self.pose, 0.0 if self.tief else self.haare, vorn=vorn)
        if self.tief:
            f = QTransform()
            f.translate(0, 25)
            f.scale(1.3, 1.25)
            tr = f * tr
        return tr * self.trafo()

    def hut_trafo(self):
        tr = self.hut_kopf()
        q = tr.map(QPointF(0, -10))
        s, rand = self.s, self.rand
        v = min(1.0, (self.t - self.hut_t) / SINKEN)
        x0, y0 = self.geo.left() if rand < 0 else self.geo.right(), self.boden - 330 * s
        x0 += rand * 30 * s
        g = glatt(v)
        pendel = math.sin(v * math.pi * 3) * (1 - v)
        x = x0 + (q.x() - x0) * g + 50 * s * pendel
        y = y0 + (q.y() - y0) * v ** 1.3
        f = QTransform()
        f.translate(x - q.x(), y - q.y())
        d = QTransform()
        d.translate(q.x(), q.y())
        d.rotate(20 * pendel)
        d.translate(-q.x(), -q.y())
        return tr * d * f

    def schirm_punkt(self):
        tr = self.hut_trafo() if self.hut_t is not None else self.hut_kopf()
        q = tr.map(QPointF(-4, -30))
        return q.x(), q.y()

    # -- Zeichnen

    def ausloeser(self, p, hx, hy):
        zeichne_ausloeser(p, hx, hy + 2, self.druck)

    def kabel_ende(self):
        return self.rampe_x - self.richtung * 32 * self.s, self.boden - 3 * self.s

    def zeichne_requisiten(self, p):
        s = self.s
        p.save()
        p.translate(self.rampe_x, self.boden - self.rampe_hopp * s)
        p.rotate(self.rampe_dreh)
        p.scale(s * ST, s * ST)
        zeichne_startrampe(p, 0, 0)
        p.restore()
        if self.halt_h and self.zeige_figur:
            hx, hy = self.hand(vorn=False)
            kx, ky = self.kabel_ende()
            ky -= self.rampe_hopp * s
            weg = QPainterPath()
            weg.moveTo(hx, hy + 6 * s)
            durch = max(0.0, KABEL * s - abs(kx - hx))
            weg.cubicTo(hx, min(self.boden, hy + durch), (hx + kx) / 2, self.boden + 2 * s, kx, ky)
            p.setPen(stift(KABEL_FARBE, 2.2 * s))
            p.setBrush(KEIN_PINSEL)
            p.drawPath(weg)
            p.setPen(KEIN_STIFT)

    def zeichne_davor(self, p):
        s, r = self.s, self.richtung
        if self.rakete_da:
            x, y, w = self.rakete_lage()
            p.save()
            p.translate(x, y)
            p.scale(s * RG, s * RG)
            zeichne_rakete(p, 0, 0, w, self.flamme, self.t, 0.0, False)
            p.restore()
            if self.hut_rakete:
                nx, ny = self.nase()
                p.save()
                p.translate(nx, ny)
                p.rotate(w)
                p.scale(1.25 * s * r, 1.25 * s)
                zeichne_muetze_prof(p, 0, 22, -6)
                p.restore()
        if self.hut_t is not None or self.tief:
            p.save()
            p.setTransform(self.hut_trafo() if self.hut_t is not None else self.hut_kopf(), True)
            zeichne_muetze_prof(p, 0, 0, 3 * math.sin(self.t * 4))
            p.restore()
        if self.schirm > 0:
            x, y = self.schirm_punkt()
            p.save()
            p.translate(x, y)
            p.scale(s * SG, s * SG)
            zeichne_fallschirm(p, 0, 0, self.schirm, self.t)
            p.restore()

    def requisiten_kasten(self):
        s = self.s
        k = QRectF(self.rampe_x - 40 * s, self.boden - 40 * s, 80 * s, 42 * s)
        if self.halt_h and self.zeige_figur:
            hx, hy = self.hand(vorn=False)
            k = k.united(QRectF(min(hx, self.rampe_x) - 25 * s, hy - 25 * s,
                                abs(hx - self.rampe_x) + 50 * s, self.boden - hy + 30 * s))
        if self.rakete_da:
            x, y, _ = self.rakete_lage()
            nx, ny = self.nase()
            rand = 45 * s if not self.hut_rakete else 70 * s
            k = k.united(QRectF(min(x, nx) - rand, min(y, ny) - rand, abs(x - nx) + 2 * rand,
                                abs(y - ny) + 2 * rand))
            if self.flamme:
                a = math.radians(self.rakete_lage()[2])
                fx, fy = x - math.sin(a) * 80 * s, y + math.cos(a) * 80 * s
                k = k.united(QRectF(fx - 30 * s, fy - 30 * s, 60 * s, 60 * s))
        if self.hut_t is not None or self.tief:
            tr = self.hut_trafo() if self.hut_t is not None else self.hut_kopf()
            k = k.united(tr.mapRect(QRectF(-40, -60, 80, 72)))
        if self.schirm > 0:
            x, y = self.schirm_punkt()
            k = k.united(QRectF(x - 36 * SG * s, y - 62 * SG * s, 72 * SG * s, 66 * SG * s))
        return k

    def weiter(self, dt):
        super().weiter(dt)
        if self.schleift and self.halt_h and not self.erschreckt:
            hx, _ = self.hand(vorn=False)
            kx, _ = self.kabel_ende()
            if abs(kx - hx) > KABEL * self.s:
                ziel = hx + math.copysign(KABEL * self.s, kx - hx)
                self.rampe_x += ziel - kx
                self.rampe_dreh = 7 * math.sin(self.t * 23)
                self.rampe_hopp = 3 * abs(math.sin(self.t * 17))
                if random.random() < 0.25:
                    self.streue(self.rampe_x, self.boden - 2 * self.s, 1, STAUB, tempo=40, dauer=0.5, r=(4, 7),
                                richtung=-math.pi / 2, streuung=1.0)

    # -- Ablauf

    def ablauf(self):
        r, s = self.richtung, self.s
        self.x = self.aussen(-r)

        def zielen(sz, u):
            f = glatt(u / 0.22)
            return Pose(arm_h=-40 - 55 * f, arm_v=-20, blick_y=0.3, auge_zu=blinzeln(sz.t), bein_v=-8 * f,
                        bein_h=8 * f)

        def druecken(sz, u):
            sz.druck = 1.0
            return Pose(arm_h=-98, arm_v=-20, blick_y=0.3, bein_v=-8, bein_h=8, hub=1.5)

        def pff(sz):
            x, y = sz.heck0()
            sz.streue(x, y, 3, RAUCH, tempo=25, dauer=0.6, r=(4, 7))

        def schuetteln(sz, u):
            sz.druck = 1.0 if (u * 8) % 1 < 0.5 else 0.0
            return Pose(arm_h=-60 + 10 * math.sin(u * 40), arm_v=-20, kopf_vorn=u > 0.25, sorge=0.6,
                        blick_y=0.5, hub=-1.5 * abs(math.sin(u * 20)))

        def ausholen(sz, u):
            sz.druck = 0.0
            f = glatt(u / 0.22)
            return Pose(arm_v=-20 - 150 * f, arm_h=-30, blick_y=0.2, sorge=0.3, mund_offen=f > 0.5)

        def klaps(sz, u):
            sz.neigung = 15 * min(1.0, u / 0.06)
            x, y = sz.rumpf(0.45)
            sz.winkel = r * 9 * math.sin(min(1.0, u / 0.08) * math.pi / 2)
            return Pose(arm_v=sz.arm_zu(x - r * 14 * s, y), arm_h=-30, blick_y=0.3, auge_zu=True)

        def wackeln(sz, u):
            sz.neigung = 15 * max(0.0, 1 - u / 0.2)
            sz.winkel = r * 9 * math.cos(u * 26) * math.exp(-u * 5)
            return Pose(arm_v=-60, arm_h=-30, blick_y=0.0, sorge=0.7, auge_zu=blinzeln(sz.t))

        def tritt_ausholen(sz, u):
            f = glatt(u / 0.22)
            sz.neigung = -8 * f
            return Pose(bein_v=40 * f, bein_h=-4, arm_v=-60 + 40 * f, arm_h=-30 - 40 * f, sorge=0.5, blick_y=0.6,
                        mund_offen=True)

        def tritt(sz, u):
            sz.neigung = -10
            sz.rampe_dreh = r * 5
            return Pose(bein_v=-72, bein_h=-4, arm_v=-120, arm_h=20, blick_y=0.6, schreck=0.3, hub=-4)

        def rampe_hopst(sz, u):
            f = min(1.0, u / 0.35)
            sz.neigung = -10 * (1 - f)
            sz.rk_hopp = 40 * math.sin(f * math.pi)
            sz.winkel = -r * 12 * glatt(f)
            sz.rampe_hopp = 6 * math.sin(f * math.pi)
            sz.rampe_dreh = r * 5 * (1 - f)
            if f >= 1 and sz.rk_hopp < 1:
                sz.rk_hopp = 0.0
            return Pose(bein_v=-20 * (1 - f), arm_v=-60, arm_h=-30, sorge=0.8, blick_y=-0.3 + 0.6 * f,
                        schreck=0.5 * (1 - f))

        def lauschen(sz, u):
            sz.neigung = 13 * glatt(u / 0.4)
            return Pose(arm_v=-75, arm_h=-30, blick_y=0.2, auge_zu=u > 0.3, sorge=0.2)

        def stille(sz, u):
            return Pose(arm_v=-75, arm_h=-30, blick_y=0.2, auge_zu=u < 0.2 or u > 0.32, mund_offen=False)

        def start(sz):
            sz.flug_start = sz.heck0()
            sz.flug, sz.flamme = sz.t, 1.0
            sz.hut_rakete, sz.muetze = True, False
            sz.druck = 0.0

        def weggepustet(sz, u):
            f = min(1.0, u / 0.55)
            sz.x = sz.px - r * 55 * s * glatt(f)
            sz.hopp = 46 * s * math.sin(f * math.pi)
            sz.neigung = 13 - 30 * math.sin(f * math.pi * 0.9) if f < 1 else 0.0
            sz.pose = explodiert(sz, u)

        def fliegen(sz, u):
            if sz.rakete_da:
                x, y, _ = sz.rakete_lage()
                sz.streue(x, y, 2, RAUCH, tempo=30, dauer=0.8, r=(7, 13))
                nx, _ = sz.nase()
                if (nx < sz.geo.left() - 120 * s) or (nx > sz.geo.right() + 120 * s):
                    sz.rakete_da = sz.hut_rakete = False

        def landung(sz):
            sz.hopp, sz.neigung = 0.0, 0.0
            sz.streue(sz.x, sz.boden - 4 * s, 6, STAUB, tempo=80, dauer=0.5, r=(5, 9), richtung=-math.pi / 2,
                      streuung=1.4)

        def glatze(sz, u):
            pat = abs(math.sin(u * 14))
            kx, ky = sz.kopf_oben()
            return Pose(arm_v=sz.arm_zu(kx + r * 4 * s, ky + (14 + 6 * pat) * s), arm_h=-30, sorge=0.9,
                        blick_y=-0.9, blick_x=0.0, mund_offen=True)

        def hut_kommt(sz):
            sz.hut_t = sz.t
            sz.rakete_da = sz.hut_rakete = False

        def hochschauen(sz, u):
            v = min(1.0, u / SINKEN)
            return Pose(kopf_vorn=False, blick_y=-0.9 + 0.8 * v, arm_h=-30, arm_v=-20, mund_offen=True,
                        auge_zu=blinzeln(sz.t))

        def aufsetzen(sz):
            sz.hut_t, sz.tief = None, True
            sz.haare = 0.3
            x, y = sz.schirm_punkt()
            sz.streue(x, y + 30 * s, 6, STAUB, tempo=60, dauer=0.4, r=(4, 8))

        def blind(sz, u):
            return Pose(arm_v=-50, arm_h=-40, arm_v_x=14, hub=-6 * math.sin(min(1.0, u / 0.2) * math.pi),
                        bein_v=-5, bein_h=5)

        def tasten(pose, sz):
            w = math.sin(sz.t * 5)
            return Pose(bein_v=pose.bein_v * 0.6, bein_h=pose.bein_h * 0.6, hub=pose.hub,
                        arm_v=-95 + 18 * w, arm_h=-85 - 18 * w, arm_v_x=16, sorge=0.6)

        rueck = self.aussen(-r) - r * (KABEL + 40) * s

        return [
            Setze(halt_h=lambda sz: sz.ausloeser),
            Gehe(bis=self.px, tempo=1.8),
            Setze(richtung=r),
            # 1. Versuch: Knopf
            Stehe(0.22, zielen),
            Stehe(0.14, druecken),
            Tu(pff),
            Stehe(0.5, schuetteln),
            # 2. Versuch: Klaps
            Stehe(0.22, ausholen),
            Stehe(0.1, klaps),
            Stehe(0.45, wackeln),
            # 3. Versuch: Tritt gegen die Rampe
            Stehe(0.22, tritt_ausholen),
            Stehe(0.1, tritt),
            Stehe(0.4, rampe_hopst),
            # Ohr an die Rakete, Stille
            Stehe(0.4, lauschen),
            Stehe(0.4, stille),
            Knall(lambda sz: (sz.rampe_x, sz.boden - 30 * s), groesse=0.8),
            Tu(start),
            Jeweils(0.55, lambda sz, u: (weggepustet(sz, u), fliegen(sz, u))),
            Tu(landung),
            Jeweils(0.35, lambda sz, u: (setattr(sz, 'pose', explodiert(sz, 0.6)), fliegen(sz, u))),
            Ducke(0.3),
            Tu(lambda sz: setattr(sz, 'flamme', 0.0)),
            Stehe(0.5, glatze),
            Publikumsblick(0.8),
            Setze(richtung=-r),
            Tu(hut_kommt),
            Wandel(0.3, schirm=1.0),
            Stehe(SINKEN - 0.3, hochschauen),
            Tu(aufsetzen),
            Wandel(0.3, schirm=0.0),
            Stehe(0.35, blind),
            Stehe(0.6, wuerde_pose),
            Setze(schleift=True),
            Gehe(bis=rueck, tempo=1.1, haltung=tasten),
            Setze(zeige_figur=False, qualm=0.0, schleift=False, halt_h=None, tief=False),
            WarteBis(lambda sz: not sz.wolke and not sz.splitter),
        ]

    def schreck_ablauf(self):
        if self.rakete_da and self.flug is not None:
            nx, ny = self.nase()
            self.streue(nx, ny, 12, RAUCH, tempo=90, dauer=0.6, r=(6, 12))
            self.rakete_da = self.hut_rakete = False
        if self.hut_t is not None or self.schirm > 0:
            x, y = self.schirm_punkt()
            self.streue(x, y, 12, RAUCH, tempo=90, dauer=0.6, r=(6, 12))
            self.hut_t, self.schirm = None, 0.0
        self.hopp, self.neigung, self.flamme = 0.0, 0.0, 0.0
        return self.schreck_puff()
