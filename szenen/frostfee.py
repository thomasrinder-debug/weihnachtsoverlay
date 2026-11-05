import math
import random

from PyQt6.QtCore import QPointF, QRectF
from PyQt6.QtGui import QColor

from zeichnen.figur import Pose
from zeichnen.figuren import Frostfee
from zeichnen.grundlagen import KEIN_PINSEL, KEIN_STIFT, WEISS, blinzeln, linear, stift

from .basis import (Erschrecke, Gehe, Jeweils, Mit, Nebenbei, Renne, Schaue, Setze, Stehe, Szene, Tu, Wandel,
                    Warte, WarteNebenbei)

EIS = [QColor('#CFEFFF'), QColor('#9FD6F5'), WEISS]
GLANZ = [WEISS, QColor('#BDE7FF')]


class FrostfeeSzene(Szene):
    """Eine kleine Frostfee schwebt heran und tippt dem Weihnachtsmann freundlich auf die
    Schulter, und schon steckt er in einem Eisblock. Erschrocken reibt sie das Eis, bis es
    zerspringt. Er bibbert, niest, sie winkt verlegen und beide machen sich davon."""
    name, titel, reihenfolge = 'frostfee', 'Frostfee', 49

    def vorbereiten(self):
        r = self.richtung
        self.eis = 0.0
        self.riss = 0.0
        self.bibbern = False
        self.f = self.dazu('f', Frostfee, groesse=0.62, vorn=True)
        self.f.richtung = r
        self.f.x = self.aussen(-r)
        self.f.tempo = self.tempo * 0.8

    def ablauf(self):
        r, s = self.richtung, self.s
        ziel = self.vom_rand(random.uniform(0.2, 0.24))
        self.x = self.aussen(-r)

        def reiben(sz, u):
            sz.f.pose = Pose(arm_v=-90 + 30 * math.sin(u * 22), arm_h=-80 - 30 * math.sin(u * 22), kopf_vorn=True,
                             sorge=1.0)
            sz.riss = min(1.0, u / 1.4)
            if random.random() < 0.3:
                sz.streue(sz.x + random.uniform(-60, 60) * s, sz.y - random.uniform(30, 230) * s, 1, GLANZ,
                          tempo=40, dauer=0.6, r=(3, 5), art='stern')

        return [
            Gehe(bis=ziel),
            Schaue(1.2),
            Setze(richtung=r),
            Stehe(0.4),
            Mit('f', Gehe(bis=ziel - r * 95 * s)),
            Mit('f', Stehe(0.6, lambda d, u: Pose(kopf_vorn=True, auge_zu=blinzeln(d.t)))),
            Mit('f', Stehe(0.4, Pose(arm_v=-95, arm_v_x=12, mund_offen=True))),
            Setze(pose=Pose(kopf_vorn=True, schreck=0.7, sorge=0.5, arm_v=-60, arm_h=-50)),
            Tu(lambda sz: sz.streue(sz.x, sz.y - 140 * s, 20, GLANZ, tempo=160, dauer=0.6, r=(3, 6), art='stern')),
            Wandel(0.25, eis=1.0),
            Mit('f', Stehe(1.2, lambda d, u: Pose(arm_v=-160, arm_h=-160, kopf_vorn=True, schreck=0.5, sorge=1.0))),
            Mit('f', Stehe(1.0, lambda d, u: Pose(kopf_vorn=True, sorge=1.0, blick_x=math.sin(u * 4)))),
            Mit('f', Wandel(0.3, x=lambda d: d.sz.x - r * 70 * d.sz.s)),
            Jeweils(1.6, reiben),
            Tu(lambda sz: sz.zerspringen()),
            Setze(bibbern=True),
            Stehe(1.4, lambda sz, u: Pose(kopf_vorn=True, sorge=1.0, arm_v=-40, arm_h=-35, mund_offen=(u * 12) % 2 < 1)),
            Stehe(0.5, lambda sz, u: Pose(kopf_vorn=True, auge_zu=True, mund_offen=True, sorge=u)),
            Tu(lambda sz: sz.streue(sz.x + r * 30 * s, sz.y - 175 * s, 10, WEISS, tempo=140, dauer=0.5, r=(2, 5))),
            Erschrecke(0.25, 20),
            Mit('f', Stehe(1.0, lambda d, u: Pose(kopf_vorn=True, arm_v=-120 + 25 * math.sin(u * 10), arm_v_x=12,
                                                  sorge=0.6, mund_offen=True))),
            Nebenbei(Mit('f', Gehe(bis=self.aussen(-r), tempo=1.2))),
            Warte(0.4),
            Gehe(bis=self.aussen(-r), tempo=1.0,
                 haltung=lambda p, sz: Pose(**{**p.__dict__, 'arm_v': -40, 'arm_h': -35, 'sorge': 1.0})),
            WarteNebenbei(),
        ]

    def schreck_ablauf(self):
        self.nebenbei.clear()
        f = self.f
        if f.zeige_figur and f.figur_sichtbar():
            q = f.trafo().map(QPointF(0, -80))
            self.streue(q.x(), q.y(), 30, GLANZ, tempo=220, dauer=0.8, r=(3, 6), art='stern')
        f.zeige_figur = False
        if self.eis > 0:
            self.zerspringen()
        return self.schreck_alle()

    def zerspringen(self):
        s = self.s
        for _ in range(26):
            self.streue(self.x + random.uniform(-70, 70) * s, self.y - random.uniform(10, 260) * s, 1, EIS,
                        tempo=260, dauer=0.9, r=(4, 9), schwer=True)
        self.eis, self.riss = 0.0, 0.0

    def weiter(self, dt):
        if self.bibbern and self.zeige_figur:
            self.neigung = math.sin(self.t * 60) * 1.5

    def zeichne_vorn(self, p):
        if self.eis <= 0 or not self.zeige_figur:
            return
        s = self.s
        k = QRectF(self.x - 82 * s, self.y - 275 * s, 164 * s, 275 * s)
        a = int(140 * self.eis)
        p.setBrush(linear(k.left(), k.top(), k.right(), k.bottom(), QColor(220, 245, 255, a),
                          QColor(120, 190, 235, a)))
        p.setPen(stift(QColor(255, 255, 255, int(200 * self.eis)), 2 * s))
        p.drawRoundedRect(k, 14 * s, 14 * s)
        p.setPen(stift(QColor(255, 255, 255, int(150 * self.eis)), 4 * s))
        p.drawLine(QPointF(k.left() + 20 * s, k.top() + 30 * s), QPointF(k.left() + 40 * s, k.top() + 120 * s))
        if self.riss > 0:
            p.setPen(stift(QColor(255, 255, 255, 230), 1.6 * s))
            p.setBrush(KEIN_PINSEL)
            n = int(self.riss * 6)
            zufall = random.Random(7)
            for i in range(n):
                x0 = k.left() + zufall.uniform(0.2, 0.8) * k.width()
                y0 = k.top() + zufall.uniform(0.1, 0.9) * k.height()
                pt = QPointF(x0, y0)
                for _ in range(3):
                    nx = pt + QPointF(zufall.uniform(-20, 20) * s, zufall.uniform(-25, 25) * s)
                    p.drawLine(pt, nx)
                    pt = nx
        p.setPen(KEIN_STIFT)

    def grenzen_extra(self):
        if self.eis <= 0:
            return QRectF()
        s = self.s
        return QRectF(self.x - 90 * s, self.y - 285 * s, 180 * s, 290 * s)
