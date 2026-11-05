import math
import random

from PyQt6.QtCore import QPointF
from PyQt6.QtGui import QColor

from zeichnen.figur import Pose
from zeichnen.figuren import Pinguin
from zeichnen.grundlagen import GOLD_HELL, WEISS, blinzeln

from .basis import Erschrecke, Gehe, Gleite, Mit, Rutsche, Setze, Stehe, Szene, Wandel

GLEITEN = Pose(arm_v=12, arm_h=-12, bein_v=20, bein_h=30, mund_offen=True)


class PinguinSzene(Szene):
    """Ein Pinguin rauscht auf dem Bauch herein, watschelt stolz weiter, rutscht aus,
    landet auf dem Rücken und sieht Sterne. Danach saust er bäuchlings davon."""
    name, titel, reihenfolge = 'pinguin', 'Pinguin', 14

    def vorbereiten(self):
        self.zeige_figur = False
        self.pg = self.dazu('pg', Pinguin, groesse=0.85)
        self.sterne = False

    def ablauf(self):
        pg = self.pg
        hoch = lambda d: 28 * d.s  # noqa: E731
        pg.x, pg.richtung = self.aussen(-self.richtung), self.richtung
        return [
            Mit('pg', Setze(neigung=80, hopp=hoch, pose=GLEITEN)),
            Mit('pg', Gleite(self.vom_rand(random.uniform(0.12, 0.16)), 1.6)),
            Mit('pg', Wandel(0.35, neigung=0, hopp=0)),
            Mit('pg', Stehe(0.5, lambda d, u: Pose(arm_v=-60 + 50 * math.sin(u * 30), arm_h=-60,
                                                   auge_zu=True))),
            Mit('pg', Stehe(0.9, lambda d, u: Pose(kopf_vorn=True, auge_zu=blinzeln(d.t, 2)))),
            Mit('pg', Gehe(bis=self.vom_rand(0.24), tempo=0.45,
                           haltung=lambda p, d: Pose(bein_v=p.bein_v * 1.4, bein_h=p.bein_h * 1.4, arm_v=-30,
                                                     arm_h=-30, auge_zu=True, hub=p.hub))),
            # ausgerutscht!
            Mit('pg', Wandel(0.22, neigung=-85, hopp=lambda d: 36 * d.s)),
            Mit('pg', Setze(pose=Pose(arm_v=-150, arm_h=-150, bein_v=-40, bein_h=-20, schreck=1.0))),
            Setze(sterne=True),
            Mit('pg', Stehe(1.6, lambda d, u: Pose(arm_v=-150 + 20 * math.sin(u * 8), arm_h=-140, bein_v=-40,
                                                   bein_h=-25 + 15 * math.sin(u * 6), auge_zu=True,
                                                   mund_offen=True))),
            Setze(sterne=False),
            Mit('pg', Wandel(0.4, neigung=0, hopp=0)),
            Mit('pg', Stehe(1.2, lambda d, u: Pose(kopf_vorn=True, sorge=0.8, blick_y=0.2,
                                                   auge_zu=0.5 < u < 0.62))),
            Mit('pg', Stehe(0.8, lambda d, u: Pose(kopf_vorn=True, arm_v=-120 + 40 * math.sin(u * 20),
                                                   arm_h=-120 - 40 * math.sin(u * 20), mund_offen=True))),
            Mit('pg', Wandel(0.25, neigung=80, hopp=hoch)),
            Mit('pg', Rutsche(zum='zurueck', tempo=3.5, hoehe=28, pose=GLEITEN)),
        ]

    def schreck_ablauf(self):
        if not self.pg.figur_sichtbar():
            return []
        self.sterne = False
        return [Mit('pg', Setze(neigung=0, hopp=0)), Mit('pg', Erschrecke(0.35, 55)),
                Mit('pg', Rutsche(zum='rand', tempo=5.0, hoehe=28, pose=GLEITEN))]

    def weiter(self, dt):
        pg, s = self.pg, self.s
        if pg.neigung > 60 and random.random() < 0.7:
            self.streue(pg.x + pg.richtung * 70 * pg.s, self.boden - 3 * s, 1, WEISS, tempo=70, dauer=0.5,
                        r=(2, 5), richtung=-math.pi / 2, streuung=1.0)
        if self.sterne and random.random() < 0.5:
            q = pg.trafo().map(QPointF(0, -110))
            w = self.t * 6
            self.streue(q.x() + math.cos(w) * 30 * s, q.y() - 30 * s + math.sin(w) * 8 * s, 1,
                        [GOLD_HELL, QColor('#FFFFFF')], tempo=10, dauer=0.7, r=(4, 6), art='stern')
