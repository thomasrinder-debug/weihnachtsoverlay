import math
import random

from PyQt6.QtCore import QRectF

from zeichnen.figur import Pose
from zeichnen.grundlagen import GOLD_HELL, WEISS, blinzeln
from zeichnen.requisiten import zeichne_eisflaeche

from .basis import Gehe, Gleite, Jeweils, Nebenbei, Setze, Stehe, Szene, Wandel

LIEGT = 58         # so weit muss er angehoben werden, wenn er auf dem Rücken liegt (Einheiten)


def rudern(sz, u):
    w = u * 22
    return Pose(bein_v=-50 * math.sin(w), bein_h=50 * math.sin(w + 1.2), arm_v=-120 + 60 * math.sin(w * 0.8),
                arm_h=-110 + 60 * math.cos(w * 0.8), arm_v_x=20, kopf_vorn=True, schreck=0.8, sorge=0.6,
                wipp=math.sin(w) * 8)


def am_boden(sz, u):
    return Pose(bein_v=-70 + 10 * math.sin(u * 7), bein_h=-50 + 10 * math.cos(u * 6), arm_v=-160, arm_h=-150,
                arm_v_x=20, kopf_vorn=True, auge_zu=True, mund_offen=True)


class Glatteis(Szene):
    """Er spaziert auf eine Eisfläche, rudert wild mit Armen und Beinen, landet auf dem
    Rücken, sieht Sterne und schlittert kopfüber aus dem Bild."""
    name, titel, reihenfolge = 'glatteis', 'Glatteis', 21

    def vorbereiten(self):
        a, b = self.vom_rand(0.13), self.vom_rand(0.3)
        self.eis = (min(a, b), max(a, b))
        self.sterne = False
        self.eis_weg = 1.0

    def ablauf(self):
        r, s = self.richtung, self.s
        self.x = self.aussen(-r)
        start = self.eis[0] if r > 0 else self.eis[1]
        return [
            Nebenbei(Wandel(0.6, eis_weg=0.0)),
            Gehe(bis=start + r * 40 * s),
            Setze(phase=0.0),
            *self.ausrutschen(r),
            Stehe(1.6, am_boden),
            Setze(sterne=False),
            Stehe(1.0, lambda sz, u: Pose(bein_v=-60, bein_h=-45, arm_v=-150, arm_h=-150, arm_v_x=20,
                                         kopf_vorn=True, sorge=0.9, auge_zu=blinzeln(sz.t, 0.3))),
            Gleite(self.aussen(-r) - r * 250 * s, 1.8, am_boden),
            Wandel(0.6, eis_weg=1.0),
        ]

    def ausrutschen(self, r):
        s = self.s
        return [Setze(x0=lambda sz: sz.x),
                Jeweils(1.2, lambda sz, u: (setattr(sz, 'pose', rudern(sz, u)),
                                             setattr(sz, 'neigung', math.sin(u * 11) * 16),
                                             setattr(sz, 'x', sz.x0 + r * 70 * s * u))),
                Wandel(0.22, neigung=-82, hopp=LIEGT * s),
                Setze(sterne=True, striche=False)]

    def schreck_ablauf(self):
        self.nebenbei.clear()
        if not self.figur_sichtbar():
            return [Wandel(0.3, eis_weg=1.0)]
        self.sterne = False
        seite = self.naechster_rand()
        return [Setze(striche=True), Jeweils(0.35, lambda sz, u: (setattr(sz, 'pose', rudern(sz, u * 2)),
                                                                   setattr(sz, 'neigung', math.sin(u * 30) * 18))),
                Setze(striche=False), Wandel(0.15, neigung=-82, hopp=LIEGT * self.s),
                Gleite(self.aussen(seite) + seite * 250 * self.s, 1.0, am_boden), Wandel(0.2, eis_weg=1.0)]

    def weiter(self, dt):
        if self.sterne and random.random() < 0.5:
            kx = self.x - self.richtung * 190 * self.s
            w = self.t * 6
            self.streue(kx + math.cos(w) * 30 * self.s, self.y - 40 * self.s + math.sin(w) * 8 * self.s, 1,
                        [GOLD_HELL, WEISS], tempo=10, dauer=0.7, r=(5, 7), art='stern')

    def zeichne_hinten(self, p):
        if self.eis_weg < 1:
            p.save()
            p.setOpacity(1 - self.eis_weg)
            zeichne_eisflaeche(p, *self.eis, self.boden, self.s)
            p.restore()

    def grenzen_extra(self):
        k = QRectF(self.eis[0], self.boden - 14 * self.s, self.eis[1] - self.eis[0], 14 * self.s)
        if self.neigung < -40:
            k = k.united(QRectF(self.x - 300 * self.s, self.y - 160 * self.s, 600 * self.s, 160 * self.s))
        return k
