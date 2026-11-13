import math
import random
from dataclasses import replace

from PyQt6.QtCore import QRectF
from PyQt6.QtGui import QColor

from zeichnen.figur import Pose, hand_punkt
from zeichnen.figuren import Katze
from zeichnen.grundlagen import blinzeln, glatt
from zeichnen.hoersaal import zeichne_laserpointer, zeichne_laserpunkt, zeichne_laserstrahl, zeichne_staubwolke

from .basis import Gehe, Jeweils, Mit, Nebenbei, Renne, Setze, Springe, Stehe, Szene, Tu, Wandel, Warte
from .hs_basis import Plumps, Publikumsblick, auf_figur, rueckenlage

STAUB = [QColor(225, 220, 210, 200), QColor(200, 195, 185, 180)]
ZEIGE = dict(arm_v=-72, arm_v_x=14)
HOCH = dict(arm_v=-162, arm_v_x=14)


class HsLaser(Szene):
    """Der Weihnachtsmann neckt eine Katze mit dem Laserpointer. Zweimal springt sie daneben,
    er lacht sich kaputt, und dabei wandert der Punkt auf seinen Bauch. Die Katze wackelt mit
    dem Hintern, er merkt es zu spät: Sprung ins Gesicht, er kippt steif um. Die Katze sitzt
    stolz auf ihm und jagt danach mit dem Pointer im Maul den eigenen Punkt hinaus."""
    name, titel, reihenfolge = 'hs_laser', 'Laserpunkt', 1000

    def vorbereiten(self):
        r, s = self.richtung, self.s
        self.x0 = self.vom_rand(random.uniform(0.09, 0.12))
        self.xk = self.x0 + r * 230 * s
        self.laser = False          # Pointer in seiner Hand an
        self.pointer_weg = False    # Pointer liegt am Boden / ist bei der Katze
        self.katze_traegt = False
        self.px, self.py = self.xk + r * 160 * s, self.boden - 3 * s
        self.auf_bauch = False
        self.lacht = 0.0
        self.staub = 0.0
        self.k = self.dazu('k', Katze, groesse=0.72)
        self.k.x = self.aussen(-r) - r * 60 * s

    # Wohin der Punkt gerade will
    def punkt_auf_bauch(self, sz=None):
        return auf_figur(self, 22, -98)

    def ablauf(self):
        r, s = self.richtung, self.s
        k = self.k
        boden = self.boden
        self.x = self.aussen(-r)

        def guckt(d, u):
            return Pose(blick_y=0.7, schreck=0.45, auge_zu=blinzeln(d.t))

        def lauert(d, u):
            d.neigung = -4 + math.sin(u * 26) * 5
            return Pose(blick_y=0.8, schreck=0.6, bein_v=-20, bein_h=20)

        def lachen(sz, u):
            sz.hopp = abs(math.sin(u * 14)) * 5 * s
            return Pose(kopf_vorn=True, mund_offen=True, auge_zu=True, arm_h=-40 + 20 * math.sin(u * 14),
                        wipp=4 * math.sin(u * 14), arm_v=-72 - 90 * min(1.0, u / 0.5), arm_v_x=14)

        return [
            Nebenbei(Mit('k', Gehe(bis=self.xk, tempo=1.35))),
            Gehe(bis=self.x0),
            Mit('k', Setze(sitzt=True, richtung=r, pose=Pose(auge_zu=False))),
            Stehe(0.35, Pose(arm_v=-40, arm_v_x=14, auge_zu=blinzeln(self.t))),
            Setze(laser=True),
            # Der Punkt tanzt, die Katze erstarrt
            Nebenbei(Mit('k', Stehe(1.0, guckt))),
            Jeweils(0.6, lambda sz, u: sz.tanz(u, 30)),
            # Versuch 1: Satz zum Punkt, der Punkt hüpft weg
            Mit('k', Setze(sitzt=False)),
            Mit('k', Stehe(0.4, lauert)),
            Mit('k', Setze(neigung=0.0)),
            Nebenbei(Warte(0.22), Wandel(0.18, px=lambda sz: sz.px + r * 190 * s)),
            Mit('k', Springe(lambda d: (d.sz.px, boden), 0.45, 80)),
            Mit('k', Stehe(0.35, lambda d, u: Pose(kopf_vorn=True, schreck=0.3, blick_x=math.sin(u * 12)))),
            # Versuch 2: der Punkt saust zurück, die Katze überschlägt sich
            Wandel(0.25, px=lambda sz: sz.xk - r * 30 * s),
            Mit('k', Setze(richtung=-r)),
            Mit('k', Stehe(0.25, lauert)),
            Mit('k', Setze(neigung=0.0)),
            Nebenbei(Warte(0.15), Wandel(0.2, px=lambda sz: sz.x0 + r * 150 * s)),
            Nebenbei(Mit('k', Wandel(0.5, neigung=-360))),
            Mit('k', Springe(lambda d: (d.sz.xk - r * 30 * s, boden), 0.5, 120)),
            Mit('k', Setze(neigung=0.0, sitzt=True, richtung=-r)),
            Nebenbei(Mit('k', Stehe(0.4, lambda d, u: Pose(schreck=0.2, blick_x=math.sin(u * 30))))),
            # Er lacht sich kaputt, der Punkt wandert dabei auf seinen Bauch
            Nebenbei(Wandel(0.8, px=lambda sz: sz.punkt_auf_bauch()[0], py=lambda sz: sz.punkt_auf_bauch()[1])),
            Stehe(1.0, lachen),
            Setze(hopp=0.0, auf_bauch=True),
            # Die Katze lauert, Erwartungspause, er merkt es zu spät
            Mit('k', Setze(sitzt=False, richtung=-r)),
            Nebenbei(Mit('k', Stehe(1.35, lauert))),
            Stehe(0.6, Pose(blick_y=1.0, auge_zu=False, **HOCH)),
            Stehe(0.75, lambda sz, u: Pose(kopf_vorn=True, sorge=1.0, schreck=0.3, blick_x=-0.6 * r,
                                           blick_y=0.6, **HOCH)),
            Mit('k', Setze(neigung=0.0)),
            # Knall: Sprung ins Gesicht, er kippt um
            Mit('k', Springe(lambda d: auf_figur(d.sz, 20, -150), 0.3, 40)),
            Setze(laser=False, pointer_weg=True, auf_bauch=False),
            Tu(lambda sz: setattr(sz, 'katze_oben', True)),
            Plumps(-90, 0.32, 44, rueckenlage),
            Tu(lambda sz: sz.landung()),
            # Reaktion: die Katze thront auf ihm
            Stehe(0.7, rueckenlage),
            # Er hebt vorsichtig den Pointer, ihr Hintern wackelt schon wieder
            Setze(halten=True),
            Stehe(0.6, lambda sz, u: replace(rueckenlage(sz, 1.0), arm_v=-60 - 70 * glatt(u / 0.6), schreck=0.0,
                                                 sorge=0.8, mund_offen=False)),
            Setze(lauer=True),
            Stehe(0.7, lambda sz, u: replace(rueckenlage(sz, 1.0), arm_v=-130, schreck=0.8, sorge=1.0)),
            # Weg damit! Pointer fliegt, Katze hinterher
            Tu(lambda sz: sz.werfen()),
            Stehe(0.25, lambda sz, u: replace(rueckenlage(sz, 1.0), arm_v=-130 - 60 * glatt(u / 0.15), schreck=0.6)),
            Tu(lambda sz: sz.katze_runter()),
            Mit('k', Springe(lambda d: (d.sz.x - r * 200 * s, boden), 0.35, 60)),
            Nebenbei(Mit('k', Renne(zum='rand', tempo=3.4))),
            Wandel(0.4, neigung=0.0, hopp=0.0),
            Publikumsblick(0.7, sack=False, sorge=0.6),
            Renne(zum='rand', tempo=3.0),
            Tu(lambda sz: sz.nebenbei.clear()),
        ]

    def tanz(self, u, weite):
        s = self.s
        self.px = self.xk + self.richtung * (160 + math.sin(u * 9) * weite) * s
        self.py = self.boden - (3 + abs(math.sin(u * 7)) * 8) * s

    def landung(self):
        self.staub = 1.0
        x, y = auf_figur(self, -40, -110)
        self.streue(x, self.boden - 10 * self.s, 14, STAUB, tempo=160, dauer=0.7,
                    r=(8, 16))

    def katze_runter(self):
        self.katze_oben = self.lauer = False
        k = self.k
        k.sitzt, k.neigung = False, 0.0
        k.richtung = -self.richtung

    def werfen(self):
        self.halten = False
        hx, hy = self.hand()
        self.wurf = (hx, hy, self.t)

    katze_oben = lauer = halten = False
    wurf = None

    def weiter(self, dt):
        k, s = self.k, self.s
        self.staub = max(0.0, self.staub - dt * 2)
        if self.katze_oben and not self.erschreckt:
            if abs(self.neigung) > 5:
                bx, by = auf_figur(self, 30, -150 + 40 * min(1.0, abs(self.neigung) / 90))
            else:
                bx, by = auf_figur(self, 20, -150)
            k.x, k.y = bx, by + 10 * s
            k.sitzt, k.richtung = True, -self.richtung
            k.pose = Pose(kopf_vorn=True, auge_zu=blinzeln(self.t, 0.5) or 0.3 < (self.t % 1.6) < 0.4,
                          blick_y=0.2)
            if self.lauer:
                k.sitzt = False
                k.neigung = -6 + math.sin(self.t * 26) * 6
                k.pose = Pose(blick_y=-0.6, schreck=0.7, bein_v=-20, bein_h=20)
        if self.auf_bauch:
            self.px, self.py = self.punkt_auf_bauch()
        if self.katze_traegt and k.zeige_figur:
            self.px = k.x + k.richtung * 150 * k.s / self.s * s
            self.py = self.boden - 3 * s

    def wurf_punkt(self):
        x0, y0, t0 = self.wurf
        u = self.t - t0
        return x0 - self.richtung * 900 * self.s * u, y0 - 700 * self.s * u + 900 * self.s * u * u

    def hand(self):
        return hand_punkt(self.x, self.y - self.hopp, self.s, self.richtung, self.pose, self.stauchen, self.neigung)

    def zeichne_vorn(self, p):
        s, r = self.s, self.richtung
        k = self.k
        if self.laser and self.zeige_figur:
            hx, hy = self.hand()
            w = math.atan2(self.py - hy, (self.px - hx) * r)
            zeichne_laserstrahl(p, hx + r * math.cos(w) * 33 * s, hy + math.sin(w) * 33 * s, self.px, self.py, 1.6 * s)
            p.save()
            p.translate(hx, hy)
            p.scale(s * r, s)
            p.rotate(math.degrees(w))
            zeichne_laserpointer(p, True)
            p.restore()
        elif self.katze_traegt and k.zeige_figur:
            kx, ky = k.x + k.richtung * 48 * k.s, k.y - 76 * k.s
            p.save()
            p.translate(kx, ky)
            p.scale(k.s * k.richtung, k.s)
            p.rotate(12)
            zeichne_laserpointer(p, True)
            p.restore()
            zeichne_laserstrahl(p, kx + k.richtung * 30 * k.s, ky, self.px, self.py, 1.4 * s)
        elif self.halten and self.zeige_figur:
            hx, hy = self.hand()
            p.save()
            p.translate(hx, hy)
            p.scale(s * r, s)
            p.rotate(-80)
            zeichne_laserpointer(p, False)
            p.restore()
        if self.wurf:
            fx, fy = self.wurf_punkt()
            p.save()
            p.translate(fx, fy)
            p.scale(s, s)
            p.rotate((self.t - self.wurf[2]) * 900)
            zeichne_laserpointer(p, True)
            p.restore()
        if self.laser or (self.katze_traegt and k.zeige_figur):
            zeichne_laserpunkt(p, self.px, self.py, 8 * s, self.t)
        if self.staub > 0:
            x, _ = auf_figur(self, -40, -110)
            zeichne_staubwolke(p, x, self.boden - 6 * s, 40 * s * (1.6 - self.staub), int(200 * self.staub))

    def grenzen_extra(self):
        s = self.s
        k = QRectF()
        if self.laser or self.katze_traegt:
            k = QRectF(self.px - 20 * s, self.py - 20 * s, 40 * s, 40 * s)
        if self.staub > 0:
            x, _ = auf_figur(self, -40, -110)
            k = k.united(QRectF(x - 110 * s, self.boden - 70 * s, 220 * s, 70 * s))
        if self.wurf:
            fx, fy = self.wurf_punkt()
            if self.geo.contains(fx, fy):
                k = k.united(QRectF(fx - 30 * s, fy - 30 * s, 60 * s, 60 * s))
        if abs(self.neigung) > 1:
            k = k.united(QRectF(self.x - 330 * s, self.boden - 160 * s, 660 * s, 160 * s))
        return k

    def schreck_ablauf(self):
        k = self.k
        self.laser = self.auf_bauch = self.katze_oben = self.katze_traegt = False
        self.pointer_weg = self.halten = self.lauer = False
        self.wurf = None
        self.staub = 0.0
        self.neigung, self.hopp = 0.0, 0.0
        self.pose_fest = {}
        k.neigung, k.y, k.sitzt, k.stauchen = 0.0, self.boden, False, 1.0
        return self.schreck_alle()

