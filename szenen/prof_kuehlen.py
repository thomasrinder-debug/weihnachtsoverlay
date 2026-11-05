import math
import random

from PyQt6.QtCore import QRectF
from PyQt6.QtGui import QColor

from zeichnen.figur import Pose
from zeichnen.figuren import Pinguin
from zeichnen.grundlagen import WEISS, blinzeln, glatt
from zeichnen.labor import zeichne_monitor
from zeichnen.labor_e import rampen_punkt, zeichne_eisblock

from .basis import (Erschrecke, Falle, Gehe, Jeweils, Mit, Nebenbei, Rutsche, Schaue, Setze, Springe,
                    Stehe, Tu, Wandel, Warte, WarteNebenbei)
from .professor import RAUCH, HaareHoch, triumph_pose
from .prof_laptop import GeraetSzene, Hieb, qualm

G = 1.6
EIS_B, EIS_H = 118, 140
EIS = [QColor('#CFEFFF'), QColor('#9FD6F5'), WEISS]


class Kuehlen(GeraetSzene):
    """Der Monitor hängt, ein Hieb, und er qualmt. Der Professor wedelt hilflos, der Pinguin
    setzt sich kühlend obendrauf: der Qualm zischt weg. Triumph-Pose, dann friert der Monitor
    zu einem Eisblock, den der Pinguin auf dem Bauch hinunterrutscht."""
    name, titel, reihenfolge = 'kuehlen', 'Eiskalt gekühlt', 90

    def vorbereiten(self):
        r = self.seite = self.richtung
        s = self.s
        self.mon_x = self.vom_rand(0.12)
        self.stand = self.mon_x + r * 108 * s
        self.bild = 1.0
        self.kringel = True
        self.flackern = False
        self.kaputt = 0.0
        self.raucht = 0.0
        self.eis = 0.0
        pg = self.pg = self.dazu('pingu', Pinguin, groesse=0.62)
        pg.x = self.aussen(-r) - r * 40 * s
        pg.tempo = self.tempo * 0.75

    def weiter(self, dt):
        super().weiter(dt)
        if self.raucht and not self.erschreckt:
            qualm(self, self.mon_x, self.boden - 128 * self.s, self.raucht)
            if random.random() < 0.08 * self.raucht:
                self.streue(self.mon_x + random.uniform(-30, 30) * self.s, self.boden - 90 * self.s, 2,
                            [QColor('#FFE38F'), QColor('#FFB43C')], tempo=160, dauer=0.4, r=(2, 4), art='stern')

    def oben(self):
        return self.boden - (EIS_H if self.eis > 0.5 else 78 * G) * self.s

    def rampe(self, u):
        px, py = rampen_punkt(0, 0, EIS_B, EIS_H, u, -self.seite)
        return self.mon_x + px * self.s, self.boden + py * self.s

    # -- Zeichnen

    def zeichne_requisiten(self, p):
        s = self.s
        p.save()
        p.translate(self.mon_x + self.zitter(), self.boden)
        p.scale(G * s, G * s)
        zeichne_monitor(p, 0, 0, self.bild, self.t, self.kaputt, kringel=self.kringel, flackern=self.flackern)
        p.restore()
        if self.eis > 0:
            p.save()
            p.translate(self.mon_x, self.boden)
            p.scale(s, s)
            zeichne_eisblock(p, 0, 0, EIS_B, EIS_H, self.eis, -self.seite, self.t)
            p.restore()

    def requisiten_kasten(self):
        s = self.s
        b = (EIS_B / 2 + EIS_H) * s
        return QRectF(self.mon_x - b, self.boden - (EIS_H + 10) * s, 2 * b, (EIS_H + 10) * s)

    # -- Ablauf

    def ablauf(self):
        r, s = self.richtung, self.s
        self.x = self.aussen(-r)
        pg = self.pg

        def ungeduldig(sz, u):
            sz.pose = Pose(arm_v=-40, arm_h=30, bein_v=-6 * abs(math.sin(u * 9)), blick_y=0.3,
                           auge_zu=blinzeln(sz.t), sorge=min(1.0, u / 1.5) * 0.7)

        def getroffen(sz):
            sz.kringel, sz.flackern, sz.kaputt, sz.raucht = False, True, 0.8, 0.7

        def wedeln(sz, u):
            w = math.sin(u * 18)
            sz.pose = Pose(arm_v=-110 + 40 * w, arm_h=-100 - 40 * w, arm_v_x=16, schreck=0.6, sorge=1.0,
                           mund_offen=True, kopf_vorn=u > 1.0)

        def zisch(sz):
            sz.raucht = 0.0
            sz.flackern = False
            sz.bild = 0.6
            sz.streue(sz.mon_x, sz.boden - 120 * s, 16, RAUCH, tempo=110, dauer=0.8, r=(6, 14),
                      richtung=-math.pi / 2, streuung=1.2)
            sz.streue(sz.mon_x, sz.boden - 90 * s, 10, EIS, tempo=150, dauer=0.7, r=(3, 6), art='stern')

        def frieren(sz, u):
            sz.eis = min(1.0, u / 1.3)
            pg.y = sz.boden - max(78 * G, EIS_H * glatt(sz.eis)) * s
            if random.random() < 0.3:
                sz.streue(sz.mon_x + random.uniform(-60, 60) * s, sz.boden - random.uniform(10, 130) * s, 1, EIS,
                          tempo=40, dauer=0.6, r=(3, 6), art='stern')
            sz.pose = Pose(schreck=0.8, sorge=0.5, arm_v=-60, arm_h=-40, kopf_vorn=True)

        def rutschen(sz, u):
            f = min(1.0, u / 0.8)
            pg.x, pg.y = sz.rampe(f * f)
            pg.neigung = 80 * min(1.0, u / 0.2)
            pg.hopp = 14 * s
            pg.pose = Pose(arm_v=-170, arm_h=-170, bein_v=10, bein_h=20, mund_offen=True)
            if random.random() < 0.4:
                sz.streue(pg.x, pg.y, 1, EIS, tempo=60, dauer=0.5, r=(3, 5), art='stern')

        def schubsen(sz, u):
            sz.pose = Pose(arm_v=-85 if u > 0.25 else -40, arm_h=-80 if u > 0.25 else -30, arm_v_x=18,
                           bein_v=-20, bein_h=16, wipp=-4)

        start = {}

        def gleiten(sz, u):
            if 'x' not in start:
                start['x'] = sz.mon_x
            f = min(1.0, u / 2.2)
            ziel = sz.aussen(-r) - r * 90 * s
            sz.mon_x = start['x'] + (ziel - start['x']) * (1 - (1 - f) ** 2)
            if random.random() < 0.3:
                sz.streue(sz.mon_x + r * EIS_B / 2 * s, sz.boden, 1, EIS, tempo=50, dauer=0.5, r=(3, 5), art='stern')

        return [
            Nebenbei(Warte(6.5), Mit('pingu', Gehe(bis=self.mon_x - r * 90 * s))),
            Gehe(bis=self.stand),
            Setze(richtung=-r),
            Jeweils(2.0, ungeduldig),
            Hieb(lambda sz: (sz.mon_x, sz.boden - 125 * s), getroffen),
            Jeweils(2.4, wedeln),
            WarteNebenbei(),
            Mit('pingu', Stehe(0.6, lambda d, u: Pose(blick_x=0.2, auge_zu=blinzeln(d.t)))),
            Mit('pingu', Springe(nach=(self.mon_x, self.boden - 78 * G * s), dauer=0.6, hoehe=60)),
            Mit('pingu', Wandel(0.15, stauchen=0.85)),
            Tu(zisch),
            Mit('pingu', Wandel(0.2, stauchen=1.0)),
            Mit('pingu', Stehe(0.5, lambda d, u: Pose(kopf_vorn=True, auge_zu=True))),
            Setze(richtung=r),
            Stehe(1.6, lambda sz, u: triumph_pose(sz, u)),
            Setze(richtung=-r),
            Jeweils(1.4, frieren),
            Stehe(0.6, lambda sz, u: Pose(sorge=1.0, blick_y=-0.4, auge_zu=blinzeln(sz.t))),
            Mit('pingu', Setze(richtung=-r)),
            Mit('pingu', Stehe(0.4, lambda d, u: Pose(kopf_vorn=True, mund_offen=True))),
            Nebenbei(Jeweils(0.8, rutschen), Mit('pingu', Rutsche(zum='rand', tempo=3.0, hoehe=14))),
            Warte(0.8),
            Schaue(1.0),
            Gehe(bis=self.mon_x + r * (EIS_B / 2 + 26) * s, tempo=0.5),
            Jeweils(0.5, schubsen),
            Nebenbei(Jeweils(2.2, gleiten)),
            Stehe(1.4, lambda sz, u: Pose(arm_v=-125 + 20 * math.sin(u * 9), arm_v_x=26, kopf_vorn=u > 0.5,
                                          auge_zu=blinzeln(sz.t))),
            WarteNebenbei(),
            Gehe(bis=self.aussen(-r)),
        ]

    def schreck_ablauf(self):
        self._vorher()
        s = self.s
        neu = []
        pg = self.pg
        if pg.zeige_figur:
            neu.append(Nebenbei(Mit('pingu', Erschrecke(0.25, 26)),
                                Mit('pingu', Falle(lambda d: d.y >= d.sz.boden)),
                                Mit('pingu', Setze(y=self.boden, neigung=0)),
                                Mit('pingu', Rutsche(zum='rand', tempo=4.0, hoehe=14))))
        if not self.figur_sichtbar():
            self.zeige_figur = False
            return neu + self._ende()
        self.streue(self.mon_x, self.boden - 70 * s, 18, EIS, tempo=160, dauer=0.7, r=(3, 7), art='stern')
        return neu + [HaareHoch(1.0), Erschrecke(0.3, 46),
                      Rutsche(zum='rand', tempo=4.5, neigung=80, hoehe=26,
                              pose=Pose(arm_v=-170, arm_h=-170, bein_v=10, bein_h=20, schreck=1.0))] + self._ende()
