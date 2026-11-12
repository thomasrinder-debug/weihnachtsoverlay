import math

from PyQt6.QtCore import QRectF

from zeichnen.figur import Pose, zeichne_sack
from zeichnen.figuren import Osterhase
from zeichnen.grundlagen import GOLD_HELL, WEISS, blinzeln
from zeichnen.requisiten import zeichne_hasenohren

from .basis import (Erschrecke, Gehe, Hoppel, Kurz, Mit, Nebenbei, Setze, Springe, Stehe, Szene, Tu,
                    Wandel, Warte, WarteNebenbei)


class Rollentausch(Szene):
    """Weihnachtsmann und Osterhase laufen sich über den Weg und erschrecken voreinander. Puff:
    Sie haben getauscht. Der Weihnachtsmann trägt Hasenohren und versucht zu hoppeln, die
    Hopser werden immer höher, bis er auf dem Hosenboden landet. Der Hase trägt Mütze und Sack
    und wird vom Sack plattgedrückt. Puff, alles zurück, beide machen sich schnell davon."""
    name, titel, reihenfolge = 'rollentausch', 'Rollentausch', 95

    def vorbereiten(self):
        r = self.richtung
        self.hase = self.dazu('hase', Osterhase, groesse=0.6, korb=3, vorn=True)
        self.hase.x = self.aussen(-r)
        self.x = self.aussen(-r)
        self.ohren = False
        self.hase_sack = False

    def tausch(self, hin):
        s = self.s
        mitte = (self.x + self.hase.x) / 2
        for k in range(3):
            self.streue(mitte + (k - 1) * 70 * s, self.boden - 90 * s, 12, WEISS, tempo=120, dauer=1.0,
                        r=(14, 28))
        h = self.hase
        self.ohren = hin
        self.hase_sack = hin
        h.muetze = hin
        h.korb = 0 if hin else 3
        self.pose_fest = {'muetze': False, 'sack': False} if hin else {}

    def ablauf(self):
        r, s = self.richtung, self.s
        hz = self.vom_rand(0.1)
        hoch = lambda hoehe, dauer: Springe(lambda sz: (sz.x, sz.boden), dauer, hoehe)  # noqa: E731
        return [
            Nebenbei(Warte(0.9), Mit('hase', Hoppel(bis=hz, tempo=0.7, hoehe=22))),
            Gehe(bis=self.vom_rand(0.24)),
            WarteNebenbei(),
            Setze(richtung=-r),
            Nebenbei(Mit('hase', Erschrecke(0.35, 40))),
            Erschrecke(0.35, 40),
            Nebenbei(Mit('hase', Stehe(1.0, lambda d, u: Pose(blick_x=1, sorge=0.5, auge_zu=0.6 < u < 0.72)))),
            Stehe(1.0, lambda sz, u: Pose(sorge=0.5, auge_zu=0.3 < u < 0.42)),
            Nebenbei(Mit('hase', Stehe(0.8, Pose(kopf_vorn=True, sorge=0.3)))),
            Stehe(0.8, lambda sz, u: Pose(kopf_vorn=True, blick_y=0.2, sorge=0.3, auge_zu=0.5 < u < 0.62)),
            Tu(lambda sz: sz.tausch(True)),
            Mit('hase', Setze(stauchen=0.86)),
            Warte(0.5),
            Stehe(0.7, lambda sz, u: Pose(kopf_vorn=True, blick_y=-0.8, sorge=0.6, auge_zu=blinzeln(sz.t))),
            Setze(richtung=r),
            hoch(40, 0.4), Kurz(0.1, stauchen=0.9),
            hoch(90, 0.55), Kurz(0.1, stauchen=0.88),
            Nebenbei(Mit('hase', Gehe(dauer=0.9, tempo=0.12, haltung=self.wackel)),
                     Mit('hase', Wandel(0.15, stauchen=0.3)),
                     Mit('hase', Setze(pose=Pose(auge_zu=True, sorge=1.0)))),
            hoch(230, 0.95),
            Tu(lambda sz: sz.plumps()),
            Kurz(0.16, stauchen=0.72),
            Stehe(1.2, lambda sz, u: Pose(kopf_vorn=True, auge_zu=True, sorge=1.0, bein_v=-70, bein_h=-60,
                                          arm_v=-60, arm_h=-50, hub=10)),
            Stehe(0.6, lambda sz, u: Pose(kopf_vorn=True, sorge=0.8, auge_zu=0.3 < u < 0.42)),
            Tu(lambda sz: sz.tausch(False)),
            Mit('hase', Setze(stauchen=1.0, pose=Pose(kopf_vorn=True, schreck=0.6))),
            Warte(0.5),
            Nebenbei(Mit('hase', Setze(richtung=-r)), Mit('hase', Hoppel(tempo=2.0, hoehe=28))),
            Stehe(0.3, Pose(kopf_vorn=True, schreck=0.6)),
            Setze(richtung=-r),
            Gehe(tempo=1.6),
            WarteNebenbei(),
        ]

    @staticmethod
    def wackel(pose, d):
        pose.bein_v = 12 * math.sin(d.t * 30)
        pose.bein_h = -pose.bein_v
        pose.sorge, pose.auge_zu = 1.0, False
        return pose

    def plumps(self):
        s = self.s
        self.streue(self.x, self.boden - 4 * s, 14, WEISS, tempo=150, dauer=0.6, r=(4, 10))
        self.streue(self.x, self.y - 250 * s, 6, GOLD_HELL, tempo=50, dauer=1.6, r=(5, 8), art='stern')

    def zeichne_figur(self, p, zwischen=None):
        if not self.ohren:
            return super().zeichne_figur(p, zwischen)

        def ohren(q):
            if zwischen:
                zwischen(q)
            x = 6 if self.pose.kopf_vorn else 2
            zeichne_hasenohren(q, x, -212 + self.pose.hub, math.sin(self.t * 5) * 6)
        super().zeichne_figur(p, ohren)

    def zeichne_vorn(self, p):
        if not self.hase_sack:
            return
        h = self.hase
        p.save()
        p.translate(h.x - h.richtung * 26 * h.s, h.y - h.hopp - (100 * h.stauchen + 8) * h.s)
        p.scale(self.s * h.richtung, self.s)
        zeichne_sack(p, 0, 0, -14, 0.62)
        p.restore()

    def grenzen_extra(self):
        if not self.hase_sack:
            return QRectF()
        h, s = self.hase, self.s
        return QRectF(h.x - 70 * s, h.y - 160 * s, 140 * s, 160 * s)

    def schreck_ablauf(self):
        self.ohren = self.hase_sack = False
        self.pose_fest = {}
        h = self.hase
        h.muetze, h.stauchen, h.korb = False, 1.0, 3
        return self.schreck_alle(hoehe=45)

