import math

from PyQt6.QtCore import QPointF, QRectF
from PyQt6.QtGui import QColor

from zeichnen.figur import Pose
from zeichnen.grundlagen import blinzeln, stift
from zeichnen.labor import zeichne_kolben, zeichne_labortisch
from zeichnen.labor_a import (SCHAUM, SCHAUM_HELL, muetze_trafo, zeichne_schaum, zeichne_schaumflocke,
                              zeichne_seifenblase)
from zeichnen.professor import zeichne_muetze_prof

from .basis import Erschrecke, Gehe, Jeweils, Nebenbei, Setze, Stehe, Tu, Wandel, Warte
from .professor import HaareHoch, ProfSzene, triumph_pose

ROT_SAFT = QColor('#E0405A')
BLAU_SAFT = QColor('#3E6FE0')
VIOLETT = QColor('#9A55D8')
SCHAUMFARBEN = [SCHAUM_HELL, SCHAUM, QColor(255, 255, 255, 220)]
TISCH_H = 72


def mische(a, b, f):
    return QColor(int(a.red() + (b.red() - a.red()) * f), int(a.green() + (b.green() - a.green()) * f),
                  int(a.blue() + (b.blue() - a.blue()) * f))


class Schaum(ProfSzene):
    """Er kippt zwei Kolben zusammen, ein Schaumberg quillt hervor und verschluckt ihn,
    nur die Mütze schwimmt obenauf. Eine große Blase platzt, und die Mütze sackt eine
    Etage tiefer. Dann fällt der Schaum zusammen und setzt ihm die Mütze wieder auf."""
    name, titel, reihenfolge = 'schaum', 'Schaumberg', 60

    def vorbereiten(self):
        r, s = self.richtung, self.s
        self.tisch_x = self.vom_rand(0.2) + r * 40 * s
        self.px = self.tisch_x - r * 96 * s
        self.a_x = self.tisch_x - r * 30 * s
        self.b_x = self.tisch_x + r * 24 * s
        self.a_da, self.a_fuell, self.b_fuell = True, 0.7, 0.35
        self.b_mix, self.b_blasen = 0.0, 0.0
        self.giessen = 0.0
        self.schaum_h = 0.0
        self.blase_r, self.blase_dy = 0.0, 0.0
        self.hut_lose, self.hut_dreh, self.hut_hopp = False, 0.0, 0.0
        self.hut_kopf = None
        self.reste = 0.0

    # -- Zustand

    def schaum_lage(self):
        """Mitte (Welt-x) und Breite des Schaumbergs in Einheiten."""
        h = self.schaum_h
        ziel = self.px + self.richtung * 52 * self.s
        f = min(1.0, h / 140)
        return self.b_x + (ziel - self.b_x) * f, min(280.0, 34 + h * 1.25)

    def hut_kopf_lage(self):
        tr = muetze_trafo(self.pose, self.haare, vorn=False) * self.trafo()
        q = tr.map(QPointF(0, 0))
        return q.x(), q.y() - self.senke

    def weiter(self, dt):
        super().weiter(dt)
        if not self.hut_lose:
            if self.pose.muetze and not self.pose.kopf_vorn and self.zeige_figur:
                self.hut_kopf = self.hut_kopf_lage()
            if self.hut_kopf and self.schaum_h > 0 and self.schaum_oben() < self.hut_kopf[1] - 4 * self.s:
                self.hut_lose, self.muetze = True, False
        elif not self.erschreckt and self.schaum_oben() > self.hut_kopf[1] and self.schaum_h < 200:
            self.hut_lose, self.muetze, self.hut_dreh = False, True, 0.0

    def schaum_oben(self):
        return self.boden - (self.schaum_h - 14) * self.s

    def hut_ort(self):
        hx, hy = self.hut_kopf
        return hx, min(hy, self.schaum_oben()) - self.hut_hopp * self.s

    # -- Zeichnen

    def kolben_halt(self, p, hx, hy):
        p.save()
        p.translate(hx, hy)
        p.rotate(105 * self.giessen)
        p.translate(0, 36)
        zeichne_kolben(p, 0, 0, ROT_SAFT, self.a_fuell, 'rund', t=self.t)
        p.restore()

    def zeichne_requisiten(self, p):
        s = self.s
        p.save()
        p.translate(self.tisch_x, self.boden)
        p.scale(s, s)
        zeichne_labortisch(p)
        p.restore()
        p.save()
        p.translate(0, self.boden - TISCH_H * s)
        p.scale(s, s)
        if self.a_da:
            zeichne_kolben(p, self.a_x / s, 0, ROT_SAFT, self.a_fuell, 'rund', t=self.t)
        zeichne_kolben(p, self.b_x / s, 0, mische(BLAU_SAFT, VIOLETT, self.b_mix), self.b_fuell, 'erlen',
                       blasen=self.b_blasen, t=self.t)
        p.restore()

    def zeichne_davor(self, p):
        s = self.s
        if self.giessen > 0.6 and self.halt and self.zeige_figur:
            hx, hy = self.hand()
            bx, by = self.b_x, self.boden - (TISCH_H + 40) * s
            p.setPen(stift(QColor(224, 64, 90, 220), 3.4 * s))
            p.drawLine(QPointF(hx + self.richtung * 4 * s, hy + 6 * s), QPointF(bx, by))
            p.setPen(stift(QColor(255, 255, 255, 120), 1.0 * s))
            p.drawLine(QPointF(hx + self.richtung * 4 * s, hy + 6 * s), QPointF(bx, by))
        if self.schaum_h > 0:
            cx, b = self.schaum_lage()
            p.save()
            p.translate(cx, self.boden)
            p.scale(s, s)
            zeichne_schaum(p, b, self.schaum_h, self.t)
            p.restore()
        if self.blase_r > 0:
            cx, _ = self.schaum_lage()
            bx = cx + self.richtung * 46 * s
            by = self.schaum_oben() - (self.blase_r - 4 + self.blase_dy) * s
            p.save()
            p.translate(bx, by)
            p.scale(s, s)
            zeichne_seifenblase(p, 0, 0, self.blase_r, self.t)
            p.restore()
        if self.hut_lose:
            hx, hy = self.hut_ort()
            p.save()
            p.translate(hx, hy)
            p.scale(1.12 * s * self.richtung, 1.12 * s)
            p.rotate(self.hut_dreh + 4 * math.sin(self.t * 2.5))
            zeichne_muetze_prof(p, 0, 0, 3 * math.sin(self.t * 3))
            if self.hut_hopp < 5:
                for dx in (-18, -6, 8, 18):
                    zeichne_schaumflocke(p, dx, 2, 5)
            p.restore()
        if self.reste > 0 and self.zeige_figur:
            p.save()
            p.setTransform(self.trafo(), True)
            p.setOpacity(min(1.0, self.reste))
            for x, y, r in ((-20, -156, 9), (24, -150, 7), (-30, -208, 8), (12, -82, 6), (-34, -60, 7)):
                zeichne_schaumflocke(p, x, y + self.pose.hub, r)
            p.restore()

    def requisiten_kasten(self):
        s = self.s
        k = QRectF(self.tisch_x - 70 * s, self.boden - 135 * s, 140 * s, 135 * s)
        if self.schaum_h > 0:
            cx, b = self.schaum_lage()
            k = k.united(QRectF(cx - (b / 2 + 26) * s, self.boden - (self.schaum_h + 28) * s,
                                (b + 52) * s, (self.schaum_h + 28) * s))
        if self.blase_r > 0:
            cx, _ = self.schaum_lage()
            bx = cx + self.richtung * 46 * s
            by = self.schaum_oben() - (self.blase_r - 4 + self.blase_dy) * s
            rr = (self.blase_r + 4) * s
            k = k.united(QRectF(bx - rr, by - rr, 2 * rr, 2 * rr))
        if self.hut_lose:
            hx, hy = self.hut_ort()
            k = k.united(QRectF(hx - 45 * s, hy - 75 * s, 90 * s, 90 * s))
        if self.giessen > 0 and self.halt:
            hx, hy = self.hand()
            k = k.united(QRectF(hx - 50 * s, hy - 50 * s, 100 * s, 100 * s))
        return k

    # -- Ablauf

    def ablauf(self):
        r, s = self.richtung, self.s
        self.x = self.aussen(-r)
        b_hals = lambda sz: (sz.b_x - r * 2 * s, sz.boden - (TISCH_H + 84) * s)

        def greife(sz, u):
            return Pose(arm_v=sz.arm_zu(sz.a_x, sz.boden - (TISCH_H + 38) * s), blick_y=0.5, auge_zu=blinzeln(sz.t))

        def giesse(sz, u):
            sz.giessen = min(1.0, u / 0.5)
            if u > 0.5:
                f = min(1.0, (u - 0.5) / 1.3)
                sz.a_fuell = 0.7 * (1 - f)
                sz.b_fuell = 0.35 + 0.4 * f
                sz.b_mix = f
            sz.pose = Pose(arm_v=sz.arm_zu(*b_hals(sz)) + 2 * math.sin(u * 9), blick_y=0.6, auge_zu=blinzeln(sz.t))

        def zurueck(sz, u):
            sz.giessen = max(0.0, 1 - u / 0.3)
            return Pose(arm_v=sz.arm_zu(sz.a_x, sz.boden - (TISCH_H + 38) * s), blick_y=0.5)

        def brodeln(sz, u):
            sz.b_blasen = min(1.0, u / 0.6)
            return Pose(blick_y=0.6, arm_v=-20, sorge=0.3, auge_zu=blinzeln(sz.t))

        def quellen(sz, u):
            sz.schaum_h = 300 * (1 - (1 - min(1.0, u / 1.7)) ** 2)
            if u % 0.1 < 1 / 60:
                cx, b = sz.schaum_lage()
                sz.streue(cx + (u * 37 % 1 - 0.5) * b * s, sz.boden - sz.schaum_h * s, 1, SCHAUMFARBEN,
                          tempo=50, dauer=0.6, r=(4, 8))
            sz.pose = Pose(arm_v=-160, arm_h=-150, arm_v_x=16, schreck=0.8, sorge=0.8, blick_y=-0.5)

        def platzen(sz):
            cx, _ = sz.schaum_lage()
            bx = cx + r * 46 * s
            by = sz.schaum_oben() - (sz.blase_r - 4 + sz.blase_dy) * s
            sz.streue(bx, by, 14, [QColor(255, 255, 255, 230), QColor(230, 200, 255, 220)], tempo=170, dauer=0.5,
                      r=(2, 4), art='stern')
            sz.streue(bx, by, 8, SCHAUMFARBEN, tempo=90, dauer=0.5, r=(4, 7))
            sz.blase_r = 0.0

        def schuetteln(sz, u):
            if u % 0.15 < 1 / 60 and sz.reste > 0.2:
                sz.streue(sz.x + (u * 53 % 1 - 0.5) * 60 * s, sz.y - (120 + u * 83 % 1 * 90) * s, 2, SCHAUMFARBEN,
                          tempo=120, dauer=0.5, r=(4, 7))
            sz.reste = max(0.0, 1 - u / 0.9)
            return Pose(kopf_vorn=True, auge_zu=True, blick_x=math.sin(u * 30), wipp=6 * math.sin(u * 30),
                        hub=-2 * abs(math.sin(u * 15)), mund_offen=True)

        return [
            Gehe(bis=self.px),
            Setze(richtung=r),
            Stehe(0.6, lambda sz, u: Pose(blick_y=0.5, auge_zu=blinzeln(sz.t))),
            Stehe(0.4, greife),
            Setze(a_da=False, halt=lambda sz: sz.kolben_halt),
            Jeweils(1.9, giesse),
            Stehe(0.35, zurueck),
            Setze(a_da=True, halt=None, giessen=0.0),
            Stehe(0.8, brodeln),
            Stehe(1.3, lambda sz, u: triumph_pose(sz, u)),
            Jeweils(1.7, quellen),
            Setze(pose=Pose(arm_v=-160, arm_h=-150)),
            Stehe(1.2, lambda sz, u: Pose(arm_v=-160, arm_h=-150)),
            Wandel(1.0, blase_r=32.0, blase_dy=6.0),
            Warte(0.35),
            Tu(platzen),
            Wandel(0.25, schaum_h=250.0, hut_dreh=-16.0),
            Warte(1.5),
            Setze(reste=1.0),
            Wandel(1.3, schaum_h=0.0),
            Stehe(0.9, lambda sz, u: Pose(sorge=0.6, blick_y=-0.7, auge_zu=(u % 0.6) < 0.12)),
            Stehe(0.9, schuetteln),
            Stehe(0.8, lambda sz, u: Pose(kopf_vorn=True, auge_zu=True, arm_v=-20, arm_h=20,
                                          hub=-3 * abs(math.sin(u * 7)))),
            Tu(lambda sz: sz.weg(SCHAUMFARBEN)),
            Gehe(bis=self.aussen(-r)),
        ]

    def schreck_ablauf(self):
        if self.schaum_h < 200:
            liste = self.schreck_versinken()
            if self.hut_lose:
                liste.insert(0, Nebenbei(Jeweils(0.5, lambda sz, u: setattr(sz, 'hut_hopp', math.sin(math.pi * min(1, u / 0.5)) * 70))))
            return liste
        self.nebenbei.clear()
        self.halt = None
        tief = 340 * self.s
        return [Nebenbei(Jeweils(0.55, lambda sz, u: setattr(sz, 'hut_hopp',
                                                             math.sin(math.pi * min(1, u / 0.55)) * 80))),
                HaareHoch(1.0), Erschrecke(0.35, 8),
                Wandel(0.45, y=lambda sz: sz.y + tief, senke=tief),
                Tu(lambda sz: setattr(sz, 'zeige_figur', False))] + self._ende()
