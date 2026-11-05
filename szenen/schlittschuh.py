import math
import random

from PyQt6.QtCore import QRectF
from PyQt6.QtGui import QColor

from zeichnen.figur import Pose
from zeichnen.figuren import Wichtel
from zeichnen.grundlagen import GOLD_HELL, WEISS, blinzeln
from zeichnen.requisiten import zeichne_eisflaeche

from .basis import Gehe, Gleite, Jeweils, Mit, Nebenbei, Setze, Stehe, Szene, Tu, Wandel, Warte, WarteNebenbei

LIEGEN = Pose(arm_v=-160, arm_h=-150, bein_v=-70, bein_h=-50, kopf_vorn=True, mund_offen=True)


def gleiten(pose, d):
    w = d.phase * 0.5
    return Pose(bein_v=-30 * math.sin(w), bein_h=30 * math.sin(w), arm_v=40 + 20 * math.sin(w), arm_h=30,
                hub=pose.hub, auge_zu=pose.auge_zu, wipp=math.sin(w) * 4)


def wackeln(pose, d):
    u = d.t * 14
    return Pose(bein_v=-40 * math.sin(u), bein_h=40 * math.sin(u + 1), arm_v=-120 + 50 * math.sin(u * 0.8),
                arm_h=-100 + 50 * math.cos(u * 0.8), kopf_vorn=True, sorge=1.0, mund_offen=True)


class Schlittschuh(Szene):
    """Zwei Wichtelschwestern auf dem Eis: Die eine gleitet elegant herein und dreht eine
    Pirouette, die andere rudert wackelig hinterher, rauscht in sie hinein und beide rutschen
    auf dem Rücken mit den Beinen in der Luft aus dem Bild."""
    name, titel, reihenfolge = 'schlittschuh', 'Schlittschuh-Schwestern', 50

    def vorbereiten(self):
        self.zeige_figur = False
        r = self.richtung
        a, b = self.vom_rand(0.03), self.vom_rand(0.42)
        self.eis = (min(a, b), max(a, b))
        self.eis_da = 0.0
        self.a = self.dazu('a', Wichtel, groesse=0.55, maedchen=True, kittel=QColor('#2A6FD6'))
        self.b = self.dazu('b', Wichtel, groesse=0.52, maedchen=True, kittel=QColor('#C2185B'), vorn=True)
        for d in (self.a, self.b):
            d.richtung, d.x = r, self.aussen(-r)

    def ablauf(self):
        r, s = self.richtung, self.s
        mitte = self.vom_rand(0.27)

        def pirouette(d, u):
            d.richtung = r if (u * 8) % 2 < 1 else -r
            d.pose = Pose(arm_v=-170, arm_h=-170, bein_v=-60, kopf_vorn=(u * 8) % 2 < 0.5, auge_zu=True)
            if random.random() < 0.3:
                d.streue(d.x, d.boden - 4 * d.sz.s, 1, [WEISS, GOLD_HELL], tempo=80, dauer=0.5, r=(2, 4), art='stern')

        hin = lambda d: Wandel(0.25, neigung=-80, hopp=lambda dd: 44 * dd.s)  # noqa: E731
        return [
            Wandel(0.6, eis_da=1.0),
            Mit('a', Gehe(bis=mitte, tempo=1.1, haltung=gleiten, neigung=-8)),
            Mit('a', Jeweils(1.6, pirouette)),
            Mit('a', Setze(richtung=r, pose=Pose(arm_v=-160, arm_h=-160, kopf_vorn=True, mund_offen=True))),
            Mit('a', Stehe(0.6, Pose(arm_v=-160, arm_h=-160, kopf_vorn=True, auge_zu=True))),
            Mit('b', Gehe(bis=mitte - r * 60 * s, tempo=0.7, haltung=wackeln)),
            Mit('a', Setze(pose=Pose(kopf_vorn=True, schreck=1.0), striche=True)),
            Mit('b', Wandel(0.2, x=lambda d: d.sz.a.x - r * 20 * d.sz.s)),
            Mit('a', Setze(striche=False)),
            Nebenbei(Mit('a', hin('a')), Mit('a', Setze(pose=LIEGEN))),
            Mit('b', hin('b')), Mit('b', Setze(pose=LIEGEN)),
            Warte(0.6),
            Nebenbei(Mit('a', Gleite(self.aussen(-r) - r * 150 * s, 2.2, LIEGEN))),
            Mit('b', Gleite(self.aussen(-r) - r * 200 * s, 2.2, LIEGEN)),
            WarteNebenbei(),
            Wandel(0.5, eis_da=0.0),
        ]

    def schreck_ablauf(self):
        self.nebenbei.clear()
        neu = []
        for n, d in (('a', self.a), ('b', self.b)):
            if d.figur_sichtbar():
                seite = d.naechster_rand()
                neu.append(Nebenbei(Mit(n, Setze(striche=True, pose=Pose(kopf_vorn=True, schreck=1.0))),
                                    Warte(0.2), Mit(n, Setze(striche=False)),
                                    Mit(n, Wandel(0.15, neigung=-80, hopp=lambda dd: 44 * dd.s)),
                                    Mit(n, Gleite(self.aussen(seite) + seite * 150 * self.s, 1.0, LIEGEN))))
            else:
                d.zeige_figur = False
        return neu + [WarteNebenbei(), Wandel(0.3, eis_da=0.0)]

    def zeichne_hinten(self, p):
        if self.eis_da > 0:
            p.save()
            p.setOpacity(self.eis_da)
            zeichne_eisflaeche(p, *self.eis, self.boden, self.s)
            p.restore()

    def grenzen_extra(self):
        s = self.s
        k = QRectF(self.eis[0], self.boden - 14 * s, self.eis[1] - self.eis[0], 14 * s)
        for d in (self.a, self.b):
            if d.zeige_figur and d.neigung < -40:
                k = k.united(QRectF(d.x - 140 * s, d.y - 120 * s, 280 * s, 120 * s))
        return k
