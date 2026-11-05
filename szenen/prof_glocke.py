import math
import random
from dataclasses import replace

from PyQt6.QtCore import QRectF
from PyQt6.QtGui import QColor

from zeichnen.figur import Pose
from zeichnen.grundlagen import WEISS, blinzeln, glatt
from zeichnen.labor import zeichne_labortisch
from zeichnen.labor_b import glitzer, zeichne_flocke, zeichne_glocke

from .basis import Erschrecke, Gehe, Jeweils, Kurz, Nebenbei, Setze, Stehe, Tu, Wandel, Warte, WarteNebenbei
from .professor import FUNKEN, RAUCH, HaareHoch, ProfSzene, ziehen

KB, KH = 44, 46          # kleine Glocke
GB, GH = 214, 282        # große Glocke
TISCH = 64
FR = 16                  # Flöckchen
KNAUF_K = KH * 0.78 + 4
KNAUF_G = GH * 0.78 + 4
SCHILLER = [QColor(255, 140, 210, 220), QColor(140, 230, 255, 220), QColor(190, 255, 170, 220), WEISS]


class Glocke(ProfSzene):
    """Ein Schneeflöckchen mit Äuglein entwischt zweimal unter seiner Glasglocke: einmal
    unter dem Rand hindurch, einmal lässt es die Glocke hüpfen. Dann holt es eine riesige
    Glocke, stülpt sie über ihn und betrachtet ihn neugierig von außen."""
    name, titel, reihenfolge = 'glocke', 'Unter der Glocke', 71

    def vorbereiten(self):
        r, s = self.richtung, self.s
        self.px = self.vom_rand(random.uniform(0.13, 0.15))
        self.tx = self.px + r * 62 * s
        self.tisch_y = self.boden - (TISCH + 8) * s
        # kleine Glocke: 'hand', 'tisch'
        self.klein = 'hand'
        self.kx, self.ky = 0.0, 0.0
        self.kipp = 0.0
        self.k_hopp = 0.0
        # große Glocke
        self.g_da = False
        self.traegt = False
        self.gx, self.gy = self.aussen(-r) - r * 200 * s, self.boden - 520 * s
        self.g_platz = 0.0
        # Flöckchen
        self.f_da = True
        self.fx, self.fy = self.aussen(-r) - r * 20 * s, self.boden - 150 * s
        self.fdreh = 0.0
        self.f_froh = 0.0
        self.f_staunen = 0.0
        self.f_ruhe = False          # sitzt still (nicht schweben)
        self.halt = self.kleine_in_hand

    # -- Orte

    def auf_tisch(self):
        return self.tx, self.tisch_y - FR * self.s

    def kleine_in_hand(self, p, hx, hy):
        if self.klein != 'hand':
            return
        p.save()
        p.translate(hx, hy + KNAUF_K)
        zeichne_glocke(p, KB, KH, self.t)
        p.restore()

    def flocke_ort(self):
        if self.f_ruhe:
            return self.fx, self.fy
        return self.fx + math.sin(self.t * 2.3) * 4 * self.s, self.fy + math.sin(self.t * 3.1) * 5 * self.s

    # -- Ablauf

    def ablauf(self):
        r, s = self.richtung, self.s
        self.x = self.aussen(-r)
        tx, ty = self.auf_tisch()
        aussen_f = self.px - r * 98 * s

        def tragen(p, sz):
            return replace(p, arm_v=-95, arm_v_x=16)

        def gucken(sz, u):
            return Pose(arm_v=-95, arm_v_x=16, blick_y=0.5, auge_zu=blinzeln(sz.t))

        def ausholen(sz, u):
            return Pose(arm_v=-95 - 60 * glatt(u / 0.4), arm_v_x=16, blick_y=0.6, sorge=0.3, bein_v=-10, bein_h=10)

        def staunen(sz, u):
            return Pose(kopf_vorn=u > 0.5, sorge=0.8, arm_v=-150 if u > 1.0 else -30, arm_v_x=12,
                        blick_x=math.sin(u * 4) * 0.7, auge_zu=blinzeln(sz.t))

        def anheben(sz, u):
            sz.pose = Pose(arm_v=sz.arm_zu(sz.kx, sz.ky - KNAUF_K * sz.s), arm_v_x=16, blick_y=0.5)
            if u > 0.25:
                sz.klein = 'hand'

        def an_scheibe(sz, u):
            k = 6 * math.sin(u * 12) if 0.8 < u < 1.6 else 0
            return Pose(arm_v=-92 + k, arm_h=-88, arm_v_x=18, sorge=1.0, kopf_vorn=u > 1.6,
                        mund_offen=0.8 < u < 1.6, auge_zu=blinzeln(sz.t), blick_x=-0.5)

        def mustern(sz, u):
            sz.fdreh = 18 * math.sin(u * 2.5)
            sz.f_froh = 1.0
            sz.fy = sz.boden - (178 + 50 * math.sin(u * 1.3)) * sz.s

        return [
            Nebenbei(Warte(1.0), Wandel(1.6, fx=tx, fy=ty - 60 * s), Wandel(0.5, fy=ty),
                     Setze(f_ruhe=True), Kurz(0.15, f_staunen=0.0)),
            Gehe(bis=self.px, haltung=tragen),
            Setze(richtung=r),
            WarteNebenbei(),
            Stehe(1.0, gucken),
            Stehe(0.5, ausholen),
            Tu(lambda sz: sz.stuelpen()),
            Stehe(0.6, lambda sz, u: Pose(arm_v=sz.arm_zu(sz.kx, sz.ky - KNAUF_K * sz.s), arm_v_x=16,
                                          kopf_vorn=u > 0.2, auge_zu=0.3 < u < 0.45)),
            # erstes Entwischen: unter dem Rand hindurch
            Wandel(0.35, kipp=-16.0),
            Setze(f_ruhe=False),
            Wandel(0.35, fx=tx + r * 44 * s, fy=ty - 6 * s),
            Wandel(0.2, kipp=0.0),
            Wandel(0.5, fy=ty - 70 * s, f_froh=1.0),
            Stehe(1.6, staunen),
            Wandel(0.6, fx=tx, fy=ty),
            Setze(f_ruhe=True),
            Jeweils(0.35, anheben),
            Stehe(0.4, ausholen),
            Tu(lambda sz: sz.stuelpen()),
            Stehe(0.4, lambda sz, u: Pose(arm_v=-40, arm_v_x=16, kopf_vorn=True, auge_zu=True, mund_offen=False)),
            # zweites Entwischen: die Glocke hüpft
            Jeweils(1.0, lambda sz, u: setattr(sz, 'k_hopp', abs(math.sin(u * math.pi * 3)) * (6 + 16 * u) * sz.s)),
            Setze(f_ruhe=False, f_froh=1.0),
            Nebenbei(Wandel(0.45, fx=tx - r * 40 * s, fy=ty - 90 * s)),
            Wandel(0.3, k_hopp=0.0),
            Stehe(1.2, lambda sz, u: Pose(kopf_vorn=True, sorge=1.0, arm_v=-20, arm_h=-20, arm_v_x=26, schreck=0.4,
                                          blick_y=-0.5)),
            # die große Glocke
            Wandel(0.9, fx=self.aussen(-r) - r * 10 * s, fy=self.boden - 240 * s),
            Setze(traegt=True, g_da=True, fy=self.boden - (KNAUF_G + 300) * s),
            Stehe(0.7, lambda sz, u: Pose(kopf_vorn=True, sorge=0.6, arm_v=-150, arm_v_x=12, auge_zu=blinzeln(sz.t))),
            Wandel(1.3, fx=self.px + r * 38 * s),
            Setze(richtung=-r),
            Stehe(0.3, lambda sz, u: Pose(blick_y=-1.0, schreck=0.6, sorge=0.6)),
            Setze(traegt=False),
            Nebenbei(Wandel(0.5, fx=aussen_f, fy=self.boden - 170 * s)),
            Wandel(0.28, gy=self.boden),
            Tu(lambda sz: sz.aufsetzen()),
            Kurz(0.12, gy=self.boden - 6 * s),
            Stehe(0.4, lambda sz, u: Pose(schreck=1.0, arm_v=-120, arm_h=-110, arm_v_x=20)),
            Nebenbei(Jeweils(3.2, mustern)),
            Stehe(3.2, an_scheibe),
            Setze(f_froh=1.0),
            Wandel(0.6, fdreh=360.0),
            Nebenbei(Wandel(1.2, fx=self.aussen(-r) - r * 30 * s, fy=self.boden - 120 * s)),
            Stehe(0.8, lambda sz, u: Pose(kopf_vorn=True, auge_zu=True, arm_v=-30, arm_h=-20, sorge=0.5)),
            Setze(mitnehmen=('tx', 'gx', 'kx'), richtung=-r),
            Gehe(bis=self.aussen(-r) - r * 240 * s, haltung=ziehen, tempo=0.8),
        ]

    # -- Handlung

    def stuelpen(self):
        self.klein = 'tisch'
        self.kx, self.ky = self.tx, self.tisch_y
        self.kipp = 0.0
        self.streue(self.kx, self.ky, 6, [WEISS], tempo=60, dauer=0.4, r=(2, 4), art='stern')

    def aufsetzen(self):
        s = self.s
        for k in range(10):
            self.streue(self.gx + (k - 4.5) * GB / 10 * s, self.boden, 1, [QColor(230, 240, 255, 180)], tempo=60,
                        dauer=0.5, r=(4, 8))

    def weiter(self, dt):
        super().weiter(dt)
        s = self.s
        if self.traegt:
            self.gx = self.fx
            self.gy = self.fy + (KNAUF_G + FR) * s + math.sin(self.t * 3.1) * 5 * s
        if self.klein == 'tisch' and not self.erschreckt and 'kx' not in self.mitnehmen:
            self.kx = self.tx

    # -- Zeichnen

    def zeichne_requisiten(self, p):
        s = self.s
        p.save()
        p.translate(self.tx, self.boden)
        p.scale(s, s)
        zeichne_labortisch(p, b=78, h=TISCH)
        p.restore()

    def zeichne_davor(self, p):
        s, r = self.s, self._r()
        if self.f_da:
            fx, fy = self.flocke_ort()
            p.save()
            p.translate(fx, fy)
            p.scale(s, s)
            zeichne_flocke(p, FR, self.fdreh + self.t * 20 * (0 if self.f_ruhe else 1), blinzeln(self.t, 0.5),
                           (r * 0.7 if self.g_da else 0.0, 0.3), self.f_froh, self.f_staunen, self.t)
            p.restore()
            if self.f_froh > 0.5 and not self.f_ruhe:
                glitzer(p, fx + 14 * s * math.cos(self.t * 4), fy + 14 * s * math.sin(self.t * 4), 3 * s, self.t)
        if self.klein == 'tisch':
            p.save()
            p.translate(self.kx - r * KB / 2 * s, self.ky - self.k_hopp)
            p.rotate(-r * abs(self.kipp))
            p.translate(r * KB / 2 * s, 0)
            p.scale(s, s)
            zeichne_glocke(p, KB, KH, self.t)
            p.restore()
        if self.g_da:
            p.save()
            p.translate(self.gx, self.gy)
            p.scale(s, s)
            zeichne_glocke(p, GB, GH, self.t, self.g_platz)
            p.restore()

    def _r(self):
        return 1 if self.tx > self.px else -1

    def requisiten_kasten(self):
        s = self.s
        k = QRectF(self.tx - 44 * s, self.tisch_y - 60 * s, 88 * s, (TISCH + 70) * s)
        if self.g_da:
            k = k.united(QRectF(self.gx - (GB / 2 + 6) * s, self.gy - (GH + 20) * s, (GB + 12) * s, (GH + 26) * s))
        if self.f_da:
            fx, fy = self.flocke_ort()
            k = k.united(QRectF(fx - 26 * s, fy - 26 * s, 52 * s, 52 * s))
        return k

    # -- Schreck

    def schreck_ablauf(self):
        s = self.s
        self.nebenbei.clear()
        self.traegt = False
        if self.f_da:
            fx, fy = self.flocke_ort()
            self.streue(fx, fy, 10, [WEISS, QColor('#CFEFFF')], tempo=160, dauer=0.5, r=(3, 6), art='stern')
            self.f_da = False
        if not self.g_da or not self.zeige_figur:
            if self.g_da:
                self.g_da = False
                self.streue(self.gx, self.gy - GH / 2 * s, 24, SCHILLER, tempo=220, dauer=0.5, r=(2, 5),
                            art='stern')
            return self.schreck_puff()
        self.halt = None

        def platzen(sz):
            sz.g_da = False
            for k in range(30):
                a = math.pi * k / 29
                x = sz.gx - math.cos(a) * GB / 2 * s
                y = sz.gy - math.sin(a) * GH * s * 0.9
                sz.streue(x, y, 1, SCHILLER, tempo=140, dauer=0.5, r=(2, 5), art='stern')
            sz.weg()

        def puff(sz):
            k = sz.figur_kasten()
            for _ in range(24):
                sz.streue(random.uniform(k.left(), k.right()), random.uniform(k.top(), k.bottom()), 1, RAUCH,
                          tempo=120, dauer=0.7, r=(8, 18))
            sz.streue(k.center().x(), k.center().y(), 8, FUNKEN, tempo=260, dauer=0.6, r=(3, 6), art='stern')
            sz.zeige_figur = False

        return [HaareHoch(1.0), Erschrecke(0.3, 50), Wandel(0.12, g_platz=0.7), Tu(platzen), Tu(puff)] + self._ende()
