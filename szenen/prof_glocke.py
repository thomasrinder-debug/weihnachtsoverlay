import math
import random
from dataclasses import replace

from PyQt6.QtCore import QPointF, QRectF
from PyQt6.QtGui import QColor

from zeichnen.figur import Pose
from zeichnen.grundlagen import WEISS, blinzeln, glatt
from zeichnen.labor import zeichne_labortisch
from zeichnen.labor_b import glitzer, zeichne_flocke, zeichne_glocke
from zeichnen.labor_f import zeichne_platthand, zeichne_plattgesicht

from .basis import Erschrecke, Gehe, Jeweils, Kurz, Nebenbei, Rutsche, Setze, Springe, Stehe, Tu, Wandel, Warte, WarteBis
from .professor import FUNKEN, RAUCH, STAUB, HaareHoch, ProfSzene, Publikumsblick, explodiert, triumph_pose

KB, KH = 92, 96          # kleine Glocke
GB, GH = 220, 292        # Riesenglocke
TISCH = 64
TISCH_B = 110
FR = 38                  # Schneeflocke (0,3 H)
KNAUF_K = KH * 0.78 + 4
KNAUF_G = GH * 0.78 + 4
SCHILLER = [QColor(255, 140, 210, 220), QColor(140, 230, 255, 220), QColor(190, 255, 170, 220), WEISS]
KLONK = [QColor(230, 240, 255, 200), WEISS]


class Glocke(ProfSzene):
    """Eine große Schneeflocke entwischt zweimal seiner Glasglocke und setzt sich frech
    obendrauf. Er springt ihr nach, sie kommt mit einer Riesenglocke zurück und stülpt
    sie über ihn. Er klebt mit plattgedrückter Nase am Glas, die Flocke mustert ihn,
    dann kippt er die Glocke an und rutscht bäuchlings darunter hinaus."""
    name, titel, reihenfolge = 'glocke', 'Unter der Glocke', 71

    def vorbereiten(self):
        r, s = self.richtung, self.s
        self.px = self.vom_rand(0.15)
        self.tx = self.px + r * 78 * s
        self.tisch_y = self.boden - (TISCH + 8) * s
        self.klein = 'hand'
        self.k_hopp = 0.0
        self.k_arm = 0.0          # 0: Arm waagerecht, 1: hoch erhoben
        self.g_da = False
        self.gx = self.px - r * 105 * s
        self.gy = self.boden - 300 * s
        self.g_kipp = 0.0
        self.g_platz = 0.0
        self.fx, self.fy = self.tx, self.tisch_y - (FR + 14) * s
        self.f_da = True
        self.f_auf = None         # None, 'klein', 'gross': sitzt auf dem Knauf
        self.fdreh = 0.0
        self.f_froh = 0.0
        self.f_staunen = 0.0
        self.f_zu = False
        self.f_blick = (0.0, 0.3)
        self.platt = 0.0
        self.nebel = 0.0
        self.rutsch = 0.0
        self.halt = self.kleine_in_hand

    # -- Orte

    def unter_klein(self):
        return self.tx, self.tisch_y - (FR + 6) * self.s

    def auf_klein(self):
        return self.tx, self.tisch_y - (KNAUF_K + 8 + FR * 0.8) * self.s - self.k_hopp

    def auf_gross(self):
        return self.gx, self.gy - (KNAUF_G + 10 + FR * 0.8) * self.s

    def flocke_ort(self):
        if self.f_auf == 'klein':
            return self.auf_klein()
        if self.f_auf == 'gross':
            return self.auf_gross()
        return self.fx + math.sin(self.t * 2.3) * 5 * self.s, self.fy + math.sin(self.t * 3.1) * 6 * self.s

    def kopf_mitte(self):
        q = self.trafo().map(QPointF(6, -180))
        return q.x(), q.y()

    def kleine_in_hand(self, p, hx, hy):
        if self.klein != 'hand':
            return
        p.save()
        p.translate(hx + 4, hy + 5)
        zeichne_glocke(p, KB, KH, self.t)
        p.restore()

    # -- Ablauf

    def ablauf(self):
        r, s = self.richtung, self.s
        self.x = self.aussen(-r)
        ux, uy = self.unter_klein()
        sprung_x = self.px - r * 105 * s

        def tragen(p, sz):
            return replace(p, arm_v=-105, arm_v_x=10)

        def lauern(sz, u):
            return Pose(arm_v=-105, blick_y=0.6, auge_zu=blinzeln(sz.t), sorge=0.2)

        def heben(winkel, beide=False, lehne=0.0):
            def pose(sz, u):
                f = glatt(u / 0.3)
                w = -105 + (winkel + 105) * f
                sz.neigung = lehne * f
                return Pose(arm_v=w, arm_h=w if beide else 0, arm_v_x=10, blick_y=0.2, bein_v=-10 * f,
                            bein_h=10 * f, sorge=0.3)
            return pose

        def haue(winkel, beide=False):
            def pose(sz, u):
                f = min(1.0, u / 0.08)
                w = winkel + (-55 - winkel) * f
                sz.neigung = sz.neigung + (28 - sz.neigung) * f
                return Pose(arm_v=w, arm_h=w if beide else 20, blick_y=0.6, bein_v=-24, bein_h=18, mund_offen=True)
            return pose

        def klonk(sz):
            sz.klein = 'tisch'
            sz.streue(sz.tx, sz.tisch_y, 8, KLONK, tempo=110, dauer=0.4, r=(2, 4), art='stern')

        def verdutzt(sz, u):
            sz.neigung = 28 * (1 - glatt(u / 0.3))
            return Pose(arm_v=-40, blick_y=-0.1 + 0.2 * math.sin(u * 6), sorge=0.8, auge_zu=0.2 < u < 0.32)

        def weg_zur_seite(sz):
            sz.f_froh = 1.0

        def guckt_hinein(sz, u):
            sz.neigung = 16 * glatt(u / 0.25)
            return Pose(arm_v=-75, arm_h=-60, blick_y=0.8, sorge=0.6 * glatt(u / 0.4))

        def schaut_hoch(sz, u):
            sz.neigung = 16 * (1 - glatt(u / 0.2))
            sz.f_zu = 0.3 < u < 0.45
            return Pose(arm_v=-40, blick_y=-1.0, sorge=0.9, auge_zu=False)

        def flocke_entwischt_hoch(sz):
            sz.f_auf = None
            sz.fx, sz.fy = sz.auf_klein()

        def umschauen(sz, u):
            return Pose(arm_v=-30, arm_h=-20, blick_x=math.sin(u * 9), sorge=0.7, kopf_vorn=0.25 < u < 0.5)

        def nach_oben(sz, u):
            return Pose(blick_y=-1.0, sorge=1.0, schreck=0.4 * glatt(u / 0.3), arm_v=-20, arm_h=20,
                        auge_zu=False)

        def fallen(sz, u):
            f = min(1.0, u / 0.14) ** 2
            sz.gy = sz.g_von + (sz.boden - sz.g_von) * f

        def aufprall(sz):
            sz.gy = sz.boden
            for k in range(14):
                sz.streue(sz.gx + (k - 6.5) * GB / 13 * s, sz.boden - 4 * s, 1, STAUB, tempo=120, dauer=0.5,
                          r=(5, 10), richtung=-math.pi / 2, streuung=1.3)
            sz.streue(sz.gx, sz.gy - GH * 0.6 * s, 10, KLONK, tempo=200, dauer=0.5, r=(3, 6), art='stern')
            sz.haare = 0.7

        def plattdruecken(sz, u):
            sz.platt = glatt(u / 0.15)
            sz.nebel = max(0.0, math.sin(u * 3.2)) ** 2
            sz.rutsch = 14 * glatt((u - 0.6) / 1.4)
            kx, ky = sz.kopf_mitte()
            sz.fx = kx + r * (96 - 14 * glatt((u - 0.3) / 0.8)) * s
            sz.fy = ky - 30 * s + 6 * math.sin(u * 2) * s
            sz.fdreh = 22 * math.sin(u * 2.6)
            sz.f_staunen = 1.0 if u < 1.2 else 0.0
            sz.f_froh = 0.0 if u < 1.2 else 1.0
            sz.f_blick = (-r * 0.9, 0.0)
            return Pose(kopf_vorn=True, arm_v=-150, arm_h=150, arm_v_x=12)

        def ab_vom_glas(sz):
            sz.platt, sz.nebel, sz.rutsch = 0.0, 0.0, 0.0
            sz.brille = 1.0

        def stemmen(sz, u):
            sz.g_kipp = 26 * glatt(u / 0.6) + 1.5 * math.sin(u * 40)
            sz.stauchen = 1 - 0.08 * glatt(u / 0.3)
            return Pose(arm_v=-172, arm_h=-165, arm_v_x=16, kopf_vorn=False, sorge=1.0, mund_offen=True,
                        bein_v=-16, bein_h=16)

        def zuklappen(sz):
            sz.g_kipp = 0.0
            aufprall(sz)

        def bauch(sz, u):
            return Pose(arm_v=-175, arm_h=-170, bein_v=10, bein_h=25, mund_offen=True, sorge=1.0)

        def zaubern(sz):
            sz.weg(SCHILLER)
            fx, fy = sz.flocke_ort()
            sz.streue(fx, fy, 16, SCHILLER, tempo=180, dauer=0.6, r=(3, 6), art='stern')
            sz.f_da = False

        return [
            Gehe(bis=self.px, tempo=1.8, haltung=tragen),
            Setze(richtung=r),
            Stehe(0.15, lauern),
            # 1. Versuch: eine Hand
            Stehe(0.3, heben(-172)),
            Nebenbei(Wandel(0.12, fx=self.tx + r * 98 * s, fy=self.tisch_y - 80 * s, f_froh=1.0)),
            Stehe(0.08, haue(-172)),
            Tu(klonk),
            Stehe(0.45, verdutzt),
            Setze(klein='hand'),
            Nebenbei(Wandel(0.4, fx=ux, fy=uy - 8 * s)),
            Stehe(0.35, lauern),
            # 2. Versuch: beide Hände, mit Schwung
            Stehe(0.35, heben(-168, beide=True, lehne=-8)),
            Stehe(0.08, haue(-178, beide=True)),
            Nebenbei(Wandel(0.14, fx=lambda sz: sz.auf_klein()[0], fy=lambda sz: sz.auf_klein()[1]),
                     Setze(f_auf='klein')),
            Tu(klonk),
            Kurz(0.1, k_hopp=4 * s),
            Wandel(0.15, neigung=0.0),
            Stehe(0.55, triumph_pose),
            Stehe(0.5, guckt_hinein),
            Stehe(0.6, schaut_hoch),
            # 3. Versuch: der ganze Körper
            Tu(flocke_entwischt_hoch),
            Nebenbei(Wandel(0.35, fx=sprung_x - r * 80 * s, fy=self.boden - 330 * s),
                     Wandel(0.3, fx=self.aussen(-r) - r * 40 * s, fy=self.boden - 420 * s)),
            Setze(richtung=-r),
            Springe(nach=lambda sz: (sprung_x, sz.boden), dauer=0.5, hoehe=70),
            Stehe(0.3, umschauen),
            # die Riesenglocke
            Setze(g_da=True, f_auf='gross', gx=self.aussen(-r) - r * 60 * s),
            Nebenbei(Wandel(0.45, gx=sprung_x)),
            Stehe(0.35, umschauen),
            Stehe(0.4, nach_oben),
            Tu(lambda sz: setattr(sz, 'g_von', sz.gy)),
            Tu(lambda sz: (setattr(sz, 'f_auf', None), setattr(sz, 'fx', sz.auf_gross()[0]),
                           setattr(sz, 'fy', sz.auf_gross()[1]))),
            Jeweils(0.14, fallen),
            Tu(aufprall),
            Kurz(0.08, gy=self.boden - 8 * s),
            Stehe(0.3, lambda sz, u: Pose(kopf_vorn=True, schreck=1.0, arm_v=-35, arm_h=35, bein_v=-6, bein_h=6)),
            # plattgedrückt am Glas, die Flocke mustert ihn
            Stehe(1.75, plattdruecken),
            Tu(ab_vom_glas),
            Publikumsblick(0.8, husten=False),
            Setze(f_froh=1.0, f_staunen=0.0),
            Nebenbei(Wandel(0.4, fx=lambda sz: sz.auf_gross()[0], fy=lambda sz: sz.auf_gross()[1] - 70 * s)),
            Stehe(0.65, stemmen),
            Setze(stauchen=1.0),
            Nebenbei(Warte(0.42), Tu(zuklappen), Kurz(0.08, gy=self.boden - 6 * s),
                     Wandel(0.25, fx=lambda sz: sz.auf_gross()[0], fy=lambda sz: sz.auf_gross()[1]),
                     Setze(f_auf='gross'), Wandel(0.35, fdreh=360.0), Tu(zaubern)),
            Rutsche(zum='rand', tempo=3.2, neigung=82, hoehe=22, pose=bauch),
            Setze(zeige_figur=False),
            WarteBis(lambda sz: not sz.nebenbei and not sz.wolke and not sz.splitter),
        ]

    # -- Zeichnen

    def zeichne_requisiten(self, p):
        s = self.s
        p.save()
        p.translate(self.tx, self.boden)
        p.scale(s, s)
        zeichne_labortisch(p, b=TISCH_B, h=TISCH)
        p.restore()

    def zeichne_davor(self, p):
        s, r = self.s, self.richtung
        if self.klein == 'tisch':
            p.save()
            p.translate(self.tx, self.tisch_y - self.k_hopp)
            p.scale(s, s)
            zeichne_glocke(p, KB, KH, self.t)
            p.restore()
        if self.g_da:
            p.save()
            if self.g_kipp:
                # kippt um die Randecke auf der Tischseite, die Randseite hebt sich
                seite = 1 if self.tx > self.gx else -1
                ex = self.gx + seite * GB / 2 * s
                p.translate(ex, self.gy)
                p.rotate(seite * self.g_kipp)
                p.translate(-ex, -self.gy)
            p.translate(self.gx, self.gy)
            p.scale(s, s)
            zeichne_glocke(p, GB, GH, self.t, self.g_platz)
            p.restore()
        if self.platt > 0 and self.zeige_figur:
            kx, ky = self.kopf_mitte()
            p.save()
            p.translate(kx, ky + self.rutsch * s)
            p.scale(s * 1.12, s * 1.12)
            p.setOpacity(min(1.0, self.platt * 1.5))
            zeichne_plattgesicht(p, self.nebel, self.platt, auge_zu=blinzeln(self.t))
            for seite, dreh in ((-1, -18), (1, 18)):
                p.save()
                p.translate(seite * 40, 6 + self.rutsch * 0.3)
                zeichne_platthand(p, dreh)
                p.restore()
            p.restore()
        if self.f_da:
            fx, fy = self.flocke_ort()
            p.save()
            p.translate(fx, fy)
            p.scale(s, s)
            dreh = self.fdreh + (0 if self.f_auf else self.t * 25)
            zeichne_flocke(p, FR, dreh, self.f_zu or blinzeln(self.t, 0.5), self.f_blick, self.f_froh,
                           self.f_staunen, self.t)
            p.restore()
            if self.f_froh > 0.5:
                glitzer(p, fx + 34 * s * math.cos(self.t * 4), fy + 34 * s * math.sin(self.t * 4), 5 * s, self.t)

    def requisiten_kasten(self):
        s = self.s
        k = QRectF(self.tx - (TISCH_B / 2 + 4) * s, self.tisch_y - (KH + 14) * s, (TISCH_B + 8) * s,
                   self.boden - self.tisch_y + (KH + 16) * s)
        if self.g_da:
            rand = (GB / 2 + 10) * s
            hoch = (GH + 20) * s
            if self.g_kipp:
                hoch += GB * math.sin(math.radians(self.g_kipp)) * s
                rand += 20 * s
            k = k.united(QRectF(self.gx - rand, self.gy - hoch, 2 * rand, hoch + 4 * s))
        if self.f_da:
            fx, fy = self.flocke_ort()
            k = k.united(QRectF(fx - 64 * s, fy - 64 * s, 128 * s, 128 * s))
        return k

    # -- Schreck

    def schreck_ablauf(self):
        s = self.s
        self.nebenbei.clear()
        self.platt = self.nebel = 0.0
        self.g_kipp = 0.0
        self.stauchen = 1.0
        if self.f_da:
            fx, fy = self.flocke_ort()
            self.streue(fx, fy, 12, [WEISS, QColor('#CFEFFF')], tempo=180, dauer=0.5, r=(3, 6), art='stern')
            self.f_da = False
        unter = self.g_da and self.zeige_figur and abs(self.x - self.gx) < GB / 2 * s
        if not unter:
            if self.g_da:
                self.g_da = False
                self.streue(self.gx, self.gy - GH / 2 * s, 24, SCHILLER, tempo=220, dauer=0.5, r=(2, 5),
                            art='stern')
            self.neigung = 0.0
            self.hopp = 0.0
            return self.schreck_puff()
        self.halt = None
        self.neigung = 0.0

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
