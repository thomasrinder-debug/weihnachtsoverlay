import math
import random

from PyQt6.QtCore import QPointF, QRectF
from PyQt6.QtGui import QColor

import zeichnen.professor as prof_zeichnung
from zeichnen.figur import Pose
from zeichnen.figuren import Lebkuchenmann
from zeichnen.grundlagen import blinzeln
from zeichnen.labor import zeichne_blitz, zeichne_kolben, zeichne_labortisch
from zeichnen.labor_a import zeichne_brille, zeichne_sternchen_kreis, zeichne_zauberstab

from .basis import Erschrecke, Gehe, Mit, Nebenbei, Renne, Setze, Springe, Stehe, Tu, Wandel, WarteNebenbei
from .professor import FUNKEN, ProfSzene, ziehen

TISCH_H = 72
KEKS = 0.5
TISCH_B = 176
BRILLE_GROESSE = 2.0          # Brille in Keks-Einheiten (sie ist ihm viel zu groß)
DURCHSICHTIG = QColor(0, 0, 0, 0)


def keks_hand(pose):
    """Vordere Hand des Lebkuchenmanns in seinen Einheiten."""
    a = math.radians(-30 + 0.9 * pose.arm_v)
    return 22 - math.sin(a) * 40, -88 + pose.hub + math.cos(a) * 40


class Brillendieb(ProfSzene):
    """Ein Blitz aus seinem Elektrostab erweckt einen Lebkuchenmann zum Leben. Der
    springt hoch, klaut die Brille und flieht, der Professor tastet blind umher. Der
    Dieb setzt die Brille auf und läuft prompt gegen den großen Kolben."""
    name, titel, reihenfolge = 'brillendieb', 'Brillendieb', 65

    def vorbereiten(self):
        r, s = self.richtung, self.s
        self.tisch_x = self.vom_rand(0.2) + r * 50 * s
        self.px = self.tisch_x - r * 126 * s
        self.kolben_x = self.tisch_x + r * 62 * s
        self.kolben_wackel = 0.0
        self.ohne_brille = False
        self.keks_brille = None       # None, 'hand' oder 'auf'
        self.keks_sterne = False
        self.zap = 0.0
        k = self.dazu('keks', Lebkuchenmann, groesse=KEKS, vorn=True)
        k.x, k.y = self.tisch_x - r * 56 * s, self.boden - TISCH_H * s
        k.richtung = -r
        k.pose = Pose(auge_zu=True)

    # -- Professor ohne Brille

    def zeichne_figur(self, p, zwischen=None):
        if not self.ohne_brille:
            return super().zeichne_figur(p, zwischen)
        glas, farbe = prof_zeichnung._glas, prof_zeichnung.BRILLE
        prof_zeichnung._glas = lambda *a: None
        prof_zeichnung.BRILLE = DURCHSICHTIG
        try:
            super().zeichne_figur(p, zwischen)
        finally:
            prof_zeichnung._glas, prof_zeichnung.BRILLE = glas, farbe

    def gesicht(self):
        q = self.trafo().map(QPointF(22, -185))
        return q.x(), q.y()

    def stab(self, p, hx, hy):
        zeichne_zauberstab(p, hx, hy, 60, self.zap, self.t)

    def stab_spitze(self):
        hx, hy = self.hand()
        w = math.radians(60)
        return hx + self.richtung * math.sin(w) * 33 * self.s, hy - math.cos(w) * 33 * self.s

    # -- Zeichnen

    def zeichne_requisiten(self, p):
        s = self.s
        p.save()
        p.translate(self.tisch_x, self.boden)
        p.scale(s, s)
        zeichne_labortisch(p, TISCH_B)
        p.restore()
        p.save()
        p.translate(self.kolben_x, self.boden - TISCH_H * s)
        p.scale(s, s)
        p.rotate(self.kolben_wackel * 9 * math.sin(self.t * 24))
        zeichne_kolben(p, 0, 0, QColor('#3FB8A8'), 0.55, 'rund', groesse=1.45, blasen=0.3, t=self.t)
        p.restore()

    def zeichne_davor(self, p):
        if self.zap > 0 and self.zeige_figur:
            k = self.darsteller['keks']
            q = k.trafo().map(QPointF(0, -100))
            x0, y0 = self.stab_spitze()
            for i in range(2):
                p.save()
                p.translate(x0, y0)
                p.scale(self.s, self.s)
                zeichne_blitz(p, 0, 0, (q.x() - x0) / self.s, (q.y() - y0) / self.s + i * 14,
                              int(self.t * 18) + i, 2.4 - i)
                p.restore()

    def zeichne_vorn(self, p):
        super().zeichne_vorn(p)
        k = self.darsteller['keks']
        if not k.zeige_figur:
            return
        if self.keks_brille:
            p.save()
            p.setTransform(k.trafo(), True)
            if self.keks_brille == 'auf':
                zeichne_brille(p, 0, -128 + k.pose.hub, -4 if self.keks_sterne else 0, 9.5 * BRILLE_GROESSE)
            else:
                hx, hy = keks_hand(k.pose)
                p.translate(hx, hy)
                p.scale(BRILLE_GROESSE, BRILLE_GROESSE)
                zeichne_brille(p, 0, -4, 30)
            p.restore()
        if self.keks_sterne:
            q = k.trafo().map(QPointF(0, -125))
            p.save()
            p.translate(q.x(), q.y())
            p.scale(self.s, self.s)
            zeichne_sternchen_kreis(p, 0, -30, 22, self.t)
            p.restore()

    def requisiten_kasten(self):
        s = self.s
        k = QRectF(self.tisch_x - 92 * s, self.boden - 150 * s, 184 * s, 150 * s)
        keks = self.darsteller['keks']
        if keks.zeige_figur and (self.keks_brille or self.keks_sterne):
            k = k.united(keks.kasten().adjusted(-40 * s, -50 * s, 40 * s, 0))
        if self.zap > 0:
            x0, y0 = self.stab_spitze()
            k = k.united(QRectF(x0 - 30 * s, y0 - 30 * s, 60 * s, 60 * s))
        return k

    # -- Ablauf

    def ablauf(self):
        r, s = self.richtung, self.s
        self.x = self.aussen(-r)
        keks = self.darsteller['keks']
        tisch_y = self.boden - TISCH_H * s

        def zielen(sz, u):
            q = keks.trafo().map(QPointF(0, -100))
            return Pose(arm_v=sz.arm_zu(q.x(), q.y()) - 15, blick_y=0.5, auge_zu=blinzeln(sz.t), mund_offen=u > 0.3)

        def zappen(sz, u):
            sz.zap = 1.0
            if random.random() < 0.3:
                q = keks.trafo().map(QPointF(0, -100))
                sz.streue(q.x(), q.y(), 2, FUNKEN, tempo=140, dauer=0.4, r=(2, 4), art='stern')
            keks.pose = Pose(schreck=1.0, arm_v=-60 + 40 * math.sin(u * 50), arm_h=-60 - 40 * math.sin(u * 50))
            keks.hopp = abs(math.sin(u * 30)) * 4 * s
            return zielen(sz, 1.0)

        def erwacht(d, u):
            return Pose(auge_zu=0.2 < u < 0.35, blick_x=math.sin(u * 4), arm_v=-30, arm_h=-30)

        def tasten(sz, u):
            w = math.sin(u * 3.2)
            return Pose(arm_v=-95 + 22 * w, arm_h=-80 - 22 * w, arm_v_x=16, auge_zu=(u % 0.8) < 0.5,
                        sorge=1.0, blick_y=0.2, bein_v=-6 * w, bein_h=6 * w, hub=-1.5 * abs(w))

        def greif(sz):
            sz.ohne_brille, sz.keks_brille = True, 'hand'
            gx, gy = sz.gesicht()
            sz.streue(gx, gy, 5, FUNKEN, tempo=100, dauer=0.3, r=(2, 3), art='stern')

        def bonk(sz):
            sz.kolben_wackel = 1.0
            sz.keks_sterne = True
            q = keks.trafo().map(QPointF(0, -120))
            sz.streue(q.x() + r * 14 * s, q.y(), 8, FUNKEN, tempo=150, dauer=0.5, r=(3, 5), art='stern')

        def finden(sz, u):
            q = keks.trafo().map(QPointF(0, -100))
            klopf = 8 * s * abs(math.sin(u * 9))
            return Pose(arm_v=sz.arm_zu(q.x(), q.y() - klopf), arm_h=-70, auge_zu=(u % 0.8) < 0.5, sorge=0.7,
                        blick_y=0.4)

        def aufsetzen(sz, u):
            gx, gy = sz.gesicht()
            return Pose(arm_v=sz.arm_zu(gx, gy), auge_zu=True)

        return [
            Gehe(bis=self.px),
            Setze(richtung=r),
            Stehe(0.6, lambda sz, u: Pose(blick_y=0.5, auge_zu=blinzeln(sz.t))),
            Setze(halt=lambda sz: sz.stab),
            Stehe(0.6, zielen),
            Stehe(0.8, zappen),
            Setze(zap=0.0, halt=None),
            Tu(lambda sz: setattr(keks, 'hopp', 0.0)),
            Mit('keks', Stehe(1.1, erwacht)),
            Wandel(0.5, neigung=12.0, x=lambda sz: sz.x + r * 8 * s),
            Stehe(0.5, lambda sz, u: Pose(blick_y=0.6, mund_offen=True, arm_v=-20, auge_zu=blinzeln(sz.t))),
            Mit('keks', Springe(nach=lambda d: (self.gesicht()[0] + r * 10 * s, self.gesicht()[1] + 48 * s),
                                dauer=0.35, hoehe=40)),
            Tu(greif),
            Setze(neigung=0.0),
            Nebenbei(Mit('keks', Springe(nach=(self.tisch_x - r * 50 * s, tisch_y), dauer=0.45, hoehe=60)),
                     Mit('keks', Stehe(0.3, Pose(arm_v=-110, kopf_vorn=True))),
                     Mit('keks', Stehe(0.5, lambda d, u: Pose(arm_v=-110 - 60 * min(1, u / 0.4), mund_offen=True))),
                     Tu(lambda sz: setattr(sz, 'keks_brille', 'auf')),
                     Mit('keks', Stehe(0.6, Pose(arm_v=-20, arm_h=-20))),
                     Mit('keks', Gehe(bis=self.kolben_x - r * 26 * s, tempo=1.5)),
                     Tu(bonk),
                     Mit('keks', Springe(nach=(self.kolben_x - r * 34 * s, tisch_y), dauer=0.3, hoehe=14)),
                     Mit('keks', Wandel(0.25, neigung=-90.0))),
            Stehe(1.0, lambda sz, u: Pose(schreck=0.6, sorge=1.0, auge_zu=(u % 0.4) < 0.25, arm_v=-60,
                                          arm_h=-50, arm_v_x=16)),
            Stehe(2.3, tasten),
            WarteNebenbei(),
            Wandel(0.4, kolben_wackel=0.0),
            Gehe(bis=self.px + r * 34 * s, tempo=0.3, haltung=lambda p, sz: Pose(
                **{**p.__dict__, 'arm_v': -95, 'arm_h': -80, 'arm_v_x': 16, 'sorge': 1.0, 'auge_zu': True})),
            Stehe(0.9, finden),
            Setze(keks_brille=None),
            Stehe(0.4, aufsetzen),
            Setze(ohne_brille=False),
            Stehe(0.7, lambda sz, u: Pose(blick_y=0.5, auge_zu=0.15 < u < 0.28, sorge=0.5)),
            Setze(keks_sterne=False),
            Mit('keks', Wandel(0.2, neigung=0.0)),
            Nebenbei(Mit('keks', Erschrecke(0.3, 30)),
                     Mit('keks', Springe(nach=lambda d: (self.x + r * 40 * s, self.boden), dauer=0.5, hoehe=50)),
                     Mit('keks', Renne(zum='rand', tempo=2.6))),
            Stehe(1.2, lambda sz, u: Pose(blick_y=0.3, sorge=0.6, mund_offen=True, auge_zu=blinzeln(sz.t))),
            Stehe(1.0, lambda sz, u: Pose(kopf_vorn=True, arm_v=-75, arm_h=-75, arm_v_x=20, sorge=0.8,
                                          hub=-3 * math.sin(min(1, u / 0.3) * math.pi))),
            Setze(mitnehmen=('tisch_x', 'kolben_x')),
            Gehe(bis=self.aussen(-r) - r * 260 * s, haltung=ziehen),
            WarteNebenbei(),
        ]

    def schreck_ablauf(self):
        self.zap = 0.0
        self.mitnehmen = ()
        return self.schreck_versinken()
