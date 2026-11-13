import math
import random

from PyQt6.QtCore import QRectF
from PyQt6.QtGui import QColor

from zeichnen.figur import Pose
from zeichnen.figuren import Pinguin, Schneemann
from zeichnen.grundlagen import blinzeln, flausch
from zeichnen.hoersaal import zeichne_wisch

from .basis import Ducke, Gehe, Mit, Nebenbei, Rutsche, Schritt, Setze, Springe, Stehe, Szene, Tu, Warte
from .hs_basis import Publikumsblick

HOEHE = 330          # Höhe der Wischkante in Einheiten
FUNKEN = [QColor('#FFFFFF'), QColor('#CFE8FF'), QColor('#FFE38F')]
STAUB = [QColor(225, 230, 240, 200), QColor(200, 210, 225, 180)]


class Wisch(Schritt):
    """Eine Folienübergangs-Kante fegt von x0 nach x1. Überquert sie den Weihnachtsmann
    (oder seine Verwandlung) am Boden, ruft sie verwandle(szene) auf."""

    def __init__(self, von, nach, dauer, verwandle=None, immer=False):
        self.von, self.nach, self.dauer, self.verwandle, self.immer = von, nach, dauer, verwandle, immer

    def beginn(self, sz):
        self.x0, self.x1 = self.von(sz), self.nach(sz)
        sz.wisch = self.x0
        sz.wisch_r = 1 if self.x1 > self.x0 else -1
        self.getan = False

    def weiter(self, sz, u, dt):
        sz.wisch = self.x0 + (self.x1 - self.x0) * min(1.0, u / self.dauer)
        if not self.getan and (sz.wisch - sz.ziel_x()) * sz.wisch_r >= 0:
            self.getan = True
            if self.verwandle and (self.immer or sz.am_boden()):
                self.verwandle(sz)
                sz.funkeln(sz.ziel_x())

    def ende(self, sz):
        sz.wisch = None


class HsFolie(Szene):
    """Folienwechsel: eine Wischkante fegt über ihn, und er ist ein Schneemann mit Rauschebart.
    Der nächste Wisch macht ihn wieder zum Weihnachtsmann. Den dritten überspringt er und
    jubelt; beim Freudensprung erwischt ihn ein vierter von hinten, als Pinguin landet er
    auf dem Bauch und rutscht bedröppelt hinaus."""
    name, titel, reihenfolge = 'hs_folie', 'Folienwechsel', 1002

    def vorbereiten(self):
        r, s = self.richtung, self.s
        self.x0 = self.vom_rand(random.uniform(0.15, 0.19))
        self.wisch = None
        self.wisch_r = 1
        self.sm = self.dazu('sm', Schneemann, groesse=1.15, zeige_figur=False)
        self.pg = self.dazu('pg', Pinguin, groesse=1.25, zeige_figur=False)
        self.form = 'wm'

    def ziel_x(self):
        return self.x

    def am_boden(self):
        return self.hopp < 30 * self.s and self.y > self.boden - 40 * self.s

    def funkeln(self, x):
        self.streue(x, self.boden - 120 * self.s, 16, FUNKEN,
                    tempo=220, dauer=0.6, r=(3, 7), art='stern')

    def zu(self, form):
        self.form = form
        self.zeige_figur = form == 'wm'
        for name, d in (('sm', self.sm), ('pg', self.pg)):
            d.zeige_figur = form == name
            d.x, d.y, d.richtung, d.hopp = self.x, self.y, self.richtung, self.hopp
            d.pose = Pose(kopf_vorn=True, schreck=1.0)
        self.mitflug = form == 'pg' and not self.am_boden()

    def ablauf(self):
        r, s = self.richtung, self.s
        self.x = self.aussen(-r)
        innen = lambda sz: sz.x0 + r * 620 * s       # noqa: E731
        draussen = lambda sz: sz.aussen(-r)          # noqa: E731

        def schaut_sich_an(d, u):
            return Pose(kopf_vorn=True, schreck=1.0 if u < 0.5 else 0.6, sorge=1.0,
                        blick_y=0.9 if u > 0.4 else 0.0, auge_zu=False)

        def erleichtert(sz, u):
            k = math.sin(u * 12) * 15
            return Pose(kopf_vorn=True, arm_v=-20 + k, arm_h=-20 - k, arm_v_x=16, sorge=0.6, mund_offen=u < 0.3,
                        auge_zu=0.45 < u < 0.7)

        def jubel(sz, u):
            return Pose(kopf_vorn=True, arm_v=-150, arm_h=-150, arm_v_x=14, bein_v=-14, bein_h=14,
                        mund_offen=True, wipp=3 * math.sin(u * 8), auge_zu=0.3 < u < 0.45)

        return [
            Gehe(bis=self.x0),
            Stehe(0.35, Pose(kopf_vorn=True, auge_zu=blinzeln(self.t), arm_v=-120, arm_v_x=24)),
            # Wisch 1: Schneemann
            Wisch(innen, draussen, 0.5, lambda sz: sz.zu('sm')),
            Mit('sm', Stehe(1.1, schaut_sich_an)),
            # Wisch 2: zurück
            Wisch(draussen, innen, 0.45, lambda sz: sz.zu('wm')),
            Stehe(0.9, erleichtert),
            # Wisch 3 kommt langsam, er springt drüber
            Tu(lambda sz: setattr(sz, 'wisch', innen(sz))),
            Stehe(0.3, Pose(kopf_vorn=False, schreck=1.0, sorge=1.0, blick_x=1)),
            Ducke(0.2),
            Tu(lambda sz: sz.nebenbei_wisch(innen, draussen, 0.55)),
            Springe(lambda sz: (sz.x, sz.boden), 0.75, 190),
            # Triumph, Erwartungspause
            Stehe(0.8, jubel),
            Stehe(0.25, Pose(kopf_vorn=True, auge_zu=True, mund_offen=False, arm_v=-150, arm_h=-150, bein_v=-14,
                             bein_h=14)),
            # Freudensprung, Wisch 4 von hinten, als Pinguin landet er auf dem Bauch
            Tu(lambda sz: sz.nebenbei_wisch(draussen, innen, 0.32, verzoegerung=0.22, verwandle=lambda z: z.zu('pg'))),
            Springe(lambda sz: (sz.x, sz.boden), 0.7, 150),
            Tu(lambda sz: sz.zu('pg') if sz.form != 'pg' else None),
            Setze(mitflug=False),
            Mit('pg', Setze(neigung=80, hopp=lambda d: 26 * d.s, y=lambda d: d.sz.boden,
                            pose=Pose(kopf_vorn=True, schreck=0.8, sorge=1.0, arm_v=-170, arm_h=-170))),
            Tu(lambda sz: sz.platsch()),
            Mit('pg', Stehe(0.35, Pose(kopf_vorn=True, schreck=0.8, sorge=1.0, arm_v=-170, arm_h=-170))),
            Mit('pg', Publikumsblick(0.75, sorge=1.0, arm_v=-170, arm_h=-170)),
            Mit('pg', Rutsche(zum='rand', tempo=2.4, neigung=80, hoehe=26,
                              pose=Pose(sorge=1.0, arm_v=-170, arm_h=-170, auge_zu=True))),
        ]

    def nebenbei_wisch(self, von, nach, dauer, verzoegerung=0.0, verwandle=None):
        schritte = ([Warte(verzoegerung)] if verzoegerung else []) + [Wisch(von, nach, dauer, verwandle, True)]
        n = Nebenbei(*schritte)
        n.beginn(self)

    mitflug = False

    def weiter(self, dt):
        if self.mitflug and not self.erschreckt:
            pg = self.pg
            pg.x, pg.y = self.x, self.y
            pg.neigung = min(80.0, pg.neigung + 260 * dt)
            pg.pose = Pose(kopf_vorn=True, schreck=1.0, arm_v=-170, arm_h=-170)

    def platsch(self):
        s = self.s
        self.streue(self.x, self.boden - 10 * s, 12, STAUB, tempo=150, dauer=0.6, r=(6, 12))

    def zeichne_vorn(self, p):
        s = self.s
        if self.wisch is not None:
            zeichne_wisch(p, self.wisch, self.boden - HOEHE * s, self.boden, s, self.wisch_r, self.t)
        # In jeder Verwandlung behält er seinen Rauschebart
        for d, punkte, r, versatz in (
                (self.sm, [(-16, -174), (-10, -164), (-2, -158), (8, -156), (16, -161), (22, -170), (4, -168)], 8, 6),
                (self.pg, [(-6, -84), (0, -78), (7, -75), (14, -79), (17, -86), (5, -83)], 5.5, 8)):
            if d.zeige_figur:
                p.save()
                p.setTransform(d.trafo(), True)
                if not d.pose.kopf_vorn:
                    punkte = [(x + versatz, y) for x, y in punkte]
                flausch(p, punkte, r)
                p.restore()

    def grenzen_extra(self):
        s = self.s
        if self.wisch is None:
            return QRectF()
        return QRectF(self.wisch - 240 * s, self.boden - HOEHE * s - 10 * s, 480 * s, HOEHE * s + 10 * s)

    def schreck_ablauf(self):
        self.nebenbei.clear()
        self.wisch = None
        for d in (self.sm, self.pg):
            d.neigung, d.hopp = 0.0, 0.0
        self.y = self.boden
        return self.schreck_alle()

