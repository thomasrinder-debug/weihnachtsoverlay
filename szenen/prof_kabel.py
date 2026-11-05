import math
from dataclasses import replace

from PyQt6.QtCore import QPointF, QRectF

from zeichnen.figur import Pose
from zeichnen.grundlagen import blinzeln, glatt
from zeichnen.labor_d import (kabel_linie, wicklung_punkt, zeichne_kabelschleife, zeichne_knaeuel, zeichne_stecker,
                               zeichne_wicklung)

from .basis import Erschrecke, Gehe, Jeweils, Schaue, Schritt, Setze, Stehe, Tu, Wandel
from .professor import FUNKEN, HaareHoch, ProfSzene, Zurueck
from .prof_klopfen import STAUB

SCHLEIFE = (16, -118)     # Knoten der Schleife in Figur-Einheiten
KN = 1.6                  # Kabelknäuel, vergrößert


class Drehe(Schritt):
    """Dreht sich ratlos um sich selbst (Seite, vorn, andere Seite, vorn ...) und wickelt sich dabei ein."""

    def __init__(self, dauer, runden, wickel_bis, menge_bis):
        self.dauer, self.runden, self.wickel_bis, self.menge_bis = dauer, runden, wickel_bis, menge_bis

    def beginn(self, sz):
        self.r0, self.w0, self.m0 = sz.richtung, sz.wickel, sz.menge

    def weiter(self, sz, u, dt):
        f = min(1.0, u / self.dauer)
        viertel = int(f * self.runden * 4)
        sz.richtung = self.r0 if viertel % 4 in (0, 1) else -self.r0
        vorn = viertel % 2 == 1
        sz.wickel = self.w0 + (self.wickel_bis - self.w0) * f
        sz.menge = self.m0 + (self.menge_bis - self.m0) * f
        sz.pose = Pose(kopf_vorn=vorn, arm_v=-105 + 10 * math.sin(u * 9), arm_h=-80, arm_v_x=16,
                       bein_v=-10 * math.sin(u * 14), bein_h=10 * math.sin(u * 14), sorge=0.6,
                       blick_y=0.4, auge_zu=blinzeln(sz.t))


class Huepfe(Schritt):
    """Hüpft mit zusammengebundenen Beinen zum nächsten Rand hinaus."""

    def __init__(self, tempo=1.0, hoehe=28, takt=0.42):
        self.tempo, self.hoehe, self.takt = tempo, hoehe, takt

    def beginn(self, sz):
        sz.richtung = sz.naechster_rand()

    def weiter(self, sz, u, dt):
        ph = (u / self.takt) % 1
        luft = 0.15 < ph
        if luft:
            sz.x += sz.richtung * self.tempo * sz.tempo * dt / 0.85
            sz.hopp = math.sin(math.pi * (ph - 0.15) / 0.85) * self.hoehe * sz.s
            sz.stauchen = 1.0
        else:
            sz.hopp = 0.0
            sz.stauchen = 1 - 0.12 * math.sin(math.pi * ph / 0.15)
        sz.pose = Pose(kopf_vorn=False, sorge=0.5, mund_offen=luft, auge_zu=blinzeln(sz.t), wipp=4 * math.sin(u * 12))

    def fertig(self, sz, u):
        return u > 0.1 and not sz.figur_sichtbar()

    def ende(self, sz):
        sz.hopp, sz.stauchen = 0.0, 1.0


class Kabel(ProfSzene):
    """Beim Entwirren wickelt er sich selbst ein, zieht am letzten freien Ende und
    schnürt sich zum Paket mit Schleife. Dann hüpft er hinaus."""
    name, titel, reihenfolge = 'kabel', 'Kabelsalat', 86

    def vorbereiten(self):
        self.rand = -self.richtung
        self.kx = self.vom_rand(0.2)
        self.menge = 1.0
        self.wickel = 0.0
        self.eng = 0.0
        self.schleife = 0.0
        self.haelt = False        # hält das Kabelende in der Hand

    def weiter(self, dt):
        super().weiter(dt)
        if self.eng > 0.4:
            self.pose = replace(self.pose, arm_v=-3, arm_h=4, arm_v_x=10, bein_v=0, bein_h=0)

    # -- Punkte

    def knaeuel_punkt(self):
        return self.kx, self.boden - 14 * KN * self.s * (0.35 + 0.65 * self.menge)

    def koerper_punkt(self):
        rx, y = wicklung_punkt(self.wickel)
        q = self.trafo().map(QPointF(-rx * 0.6, y))
        return q.x(), q.y()

    # -- Zeichnen

    def zeichne_requisiten(self, p):
        p.save()
        p.translate(self.kx, self.boden)
        p.scale(self.s * KN, self.s * KN)
        zeichne_knaeuel(p, 0, 0, self.menge, self.t)
        if self.menge > 0.05 and not self.haelt and self.wickel == 0:
            kabel_linie(p, [(20, -6), (34, -3), (44, -2)])
            zeichne_stecker(p, 44, -2, 0)
        p.restore()

    def zeichne_davor(self, p):
        if not self.zeige_figur:
            return
        kx, ky = self.knaeuel_punkt()
        if self.haelt and self.menge > 0.03:
            hx, hy = self.hand()
            if self.wickel > 0:
                bx, by = self.koerper_punkt()
                kabel_linie(p, [(kx, ky), ((kx + bx) / 2, max(ky, by) + 10 * self.s), (bx, by)], 3.2 * self.s)
            else:
                kabel_linie(p, [(kx, ky), ((kx + hx) / 2, max(ky, hy) + 14 * self.s), (hx, hy)], 3.2 * self.s)
                p.save()
                p.translate(hx, hy)
                p.scale(self.s, self.s)
                zeichne_stecker(p, 0, 0, -90)
                p.restore()

    def zeichne_hinten(self, p):
        super().zeichne_hinten(p)
        if self.zeige_figur and self.wickel > 0:
            p.save()
            p.setTransform(self.trafo(), True)
            zeichne_wicklung(p, self.wickel, self.eng, vorn=False)
            p.restore()

    def zeichne_vorn(self, p):
        if self.zeige_figur and self.wickel > 0:
            p.save()
            p.setTransform(self.trafo(), True)
            zeichne_wicklung(p, self.wickel, self.eng, vorn=True)
            zeichne_kabelschleife(p, *SCHLEIFE, 1.6 * self.schleife)
            p.restore()
        super().zeichne_vorn(p)

    def requisiten_kasten(self):
        s = self.s
        k = QRectF(self.kx - 40 * KN * s, self.boden - 50 * KN * s, 95 * KN * s, 50 * KN * s)
        if self.haelt and self.zeige_figur:
            hx, hy = self.hand()
            k = k.united(QRectF(hx - 12 * s, hy - 12 * s, 24 * s, 24 * s))
        return k

    # -- Ablauf

    def zuziehen(self, sz):
        self.haelt = False
        x, y = self.knaeuel_punkt()
        self.streue(x, y, 8, STAUB, tempo=100, dauer=0.6, r=(4, 9))
        q = self.trafo().map(QPointF(*SCHLEIFE))
        self.streue(q.x(), q.y(), 7, FUNKEN, tempo=180, dauer=0.5, r=(3, 6), art='stern')

    def ablauf(self):
        self.x = self.aussen(self.rand)
        r = self.rand
        boden_hand = lambda sz: (sz.kx + r * 10 * sz.s, sz.boden - 12 * sz.s)
        ziehen = lambda sz, u: Pose(arm_v=sz.arm_zu(*sz.knaeuel_punkt()) - 40, arm_h=30, sorge=0.2,
                                    blick_y=0.5, auge_zu=blinzeln(sz.t))
        return [
            Gehe(bis=self.kx + r * 110 * self.s),
            Setze(richtung=-r),
            Stehe(0.9, lambda sz, u: Pose(blick_y=0.8, sorge=0.6, auge_zu=blinzeln(sz.t))),
            Stehe(0.8, lambda sz, u: Pose(arm_v=-170, arm_v_x=8, blick_y=0.5, sorge=0.8,
                                          wipp=3 * math.sin(u * 20))),
            Stehe(0.5, lambda sz, u: Pose(arm_v=sz.arm_zu(*boden_hand(sz)), hub=6 * min(1, u * 3), blick_y=0.9)),
            Setze(haelt=True),
            Zurueck(45, 0.8),
            Stehe(0.6, ziehen),
            Drehe(3.2, 3, 0.72, 0.25),
            Stehe(0.9, lambda sz, u: Pose(kopf_vorn=True, blick_y=0.9, sorge=0.8, arm_v=-60, arm_h=-50,
                                          auge_zu=blinzeln(sz.t))),
            Schaue(1.0),
            Setze(richtung=-r),
            Stehe(0.6, lambda sz, u: Pose(blick_y=0.7, mund_offen=u > 0.3, arm_v=-60)),
            Stehe(0.4, lambda sz, u: Pose(arm_v=-60 + 50 * glatt(u / 0.4), arm_h=30, blick_y=0.5, sorge=0.0)),
            Stehe(0.25, lambda sz, u: Pose(arm_v=10 + 60 * min(1, u / 0.12), arm_h=40,
                                           mund_offen=True)),
            Tu(self.zuziehen),
            Wandel(0.22, wickel=1.0, eng=1.0, menge=0.0, stauchen=0.9, schleife=1.25),
            Wandel(0.15, stauchen=1.0, schleife=1.0),
            Stehe(0.8, lambda sz, u: Pose(kopf_vorn=True, schreck=0.6 * (1 - u), sorge=1.0)),
            Jeweils(1.0, lambda sz, u: (setattr(sz, 'neigung', 6 * math.sin(u * 14)),
                                        setattr(sz, 'pose', Pose(sorge=0.8, blick_y=0.5, wipp=4)))),
            Setze(neigung=0.0),
            Stehe(1.0, lambda sz, u: Pose(kopf_vorn=True, auge_zu=0.5 < u < 0.62, sorge=0.3)),
            Huepfe(tempo=0.9),
        ]

    def schreck_ablauf(self):
        self._vorher()
        self.haelt = False
        if not self.zeige_figur or not self.figur_sichtbar():
            self.zeige_figur = False
            return self._ende()
        return [Wandel(0.15, wickel=1.0, eng=1.0, schleife=1.0, neigung=0.0),
                HaareHoch(1.0), Erschrecke(0.3, 50),
                Huepfe(tempo=3.6, hoehe=40, takt=0.3)] + self._ende()
