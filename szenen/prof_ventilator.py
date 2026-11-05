import math
import random

from PyQt6.QtCore import QPointF, QRectF
from PyQt6.QtGui import QColor, QTransform

from zeichnen.figur import Pose
from zeichnen.grundlagen import KEIN_PINSEL, KEIN_STIFT, blinzeln, glatt, stift
from zeichnen.labor_a import muetze_trafo
from zeichnen.labor_d import (VENT_KNOPF, VENT_MITTE, VENT_R, ballon_kopf_y, ballon_mass, zeichne_ballonprof,
                              zeichne_ventilator)
from zeichnen.professor import KOPF_Y, zeichne_muetze_prof

from .basis import Gehe, Jeweils, Schritt, Setze, Stehe, Tu, Wandel, WarteBis
from .professor import FUNKEN, QUALM, RAUCH, HaareHoch, ProfSzene, Publikumsblick

TROPFEN = [QColor(150, 200, 255, 220), QColor(200, 230, 255, 200)]
FLUEGEL = (0, 380, 900, 1700, 3200)     # Grad je Sekunde je Stufe
WIND_WEITE = 330                         # wie weit die Windlinien reichen (Einheiten)
G = 1.35                                 # Ventilator, vergrößert


class Schwebe(Schritt):
    """Treibt im Wind mit dem Ballonkittel: wippt auf und ab, paddelt mit Armen und Beinen.
    zug: Einheiten je Sekunde Richtung Ventilator (negativ: der Wind schiebt ihn weg)."""

    def __init__(self, dauer, zug=-30.0, pose=None):
        self.dauer, self.zug, self.pose_fn = dauer, zug, pose

    def weiter(self, sz, u, dt):
        sz.x -= sz.rand * self.zug * sz.s * dt
        if self.pose_fn:
            sz.pose = self.pose_fn(sz, u)
        else:
            sz.pose = Pose(arm_v=-90 + 70 * math.sin(u * 14), arm_h=-90 - 70 * math.sin(u * 14),
                           bein_v=-30 * math.sin(u * 12), bein_h=30 * math.sin(u * 12), sorge=0.8,
                           mund_offen=True, blick_y=0.3, auge_zu=blinzeln(sz.t))


class Wegblasen(Schritt):
    """Schießt quer über den Rand hinaus und überschlägt sich dabei."""

    def beginn(self, sz):
        self.x0, self.h0 = sz.x, sz.hopp

    def weiter(self, sz, u, dt):
        v = 300 + 2400 * min(1.0, u / 0.35) ** 2
        sz.x += sz.rand * v * sz.s * dt
        sz.hopp = self.h0 + 60 * sz.s * math.sin(min(1.0, u / 0.5) * math.pi / 2)
        sz.neigung = -sz.rand * sz.richtung * 900 * u
        sz.pose = Pose(kopf_vorn=True, schreck=1.0, arm_v=-150, arm_h=-30, bein_v=-40, bein_h=30, mund_offen=True)

    def fertig(self, sz, u):
        return u > 0.05 and not sz.figur_sichtbar()

    def ende(self, sz):
        sz.zeige_figur = False
        sz.neigung = 0.0


class Ventilator(ProfSzene):
    """Ihm ist heiß. Fußtipp auf den Schalter: kühle Brise. Stampfen: der Kittel bläht sich.
    Sprung mit beiden Füßen: der Kittel wird zum runden Ballon, er hebt ab und treibt hilflos
    paddelnd im Wind, Blick ins Publikum. Mit der Fußspitze erwischt er den Schalter noch
    einmal, doch der dreht nicht ab, sondern hoch: er wird quer über den Rand geweht, die
    Mütze bleibt kurz in der Luft hängen und saust hinterher, der Ventilator raucht ab."""
    name, titel, reihenfolge = 'ventilator', 'Kittel im Wind', 87

    def vorbereiten(self):
        self.rand = -self.richtung
        self.vx = self.vom_rand(0.17)
        self.stufe = 0
        self.fan_v = 0.0
        self.dreh = 0.0
        self.druck = 0.0
        self.bal = 0.0
        self.wackel = 0.0
        self.hut = None          # (Welt-Trafo der Mütze beim Wegfliegen, Startzeit)
        self.hut_los = None

    # -- Zustand

    def weiter(self, dt):
        super().weiter(dt)
        self.dreh += self.fan_v * dt
        if self.bal > 0.05 and self.zeige_figur:
            _, _, _, bein = ballon_mass(self.bal)
            self.hopp = max(self.hopp, (bein + 62) * self.s)

    def wind(self):
        return min(1.0, self.fan_v / FLUEGEL[3])

    def korb(self):
        cx, cy = VENT_MITTE
        return self.vx + self.rand * cx * G * self.s, self.boden + cy * G * self.s

    def knopf(self):
        kx, ky = VENT_KNOPF
        return self.vx + self.rand * kx * G * self.s, self.boden + ky * G * self.s

    # -- Figur mit Ballonkittel

    def zeichne_figur(self, p, zwischen=None):
        if self.bal <= 0.02:
            return super().zeichne_figur(p, zwischen)
        p.save()
        p.setTransform(self.trafo(), True)
        p.setPen(KEIN_STIFT)
        zeichne_ballonprof(p, self, self.bal)
        p.restore()

    def figur_kasten(self):
        k = super().figur_kasten()
        if self.bal > 0.02:
            _, rx, _, bein = ballon_mass(self.bal)
            k = k.united(self.trafo().mapRect(QRectF(-rx - 12, ballon_kopf_y(self.bal) - 80, 2 * rx + 24,
                                                     bein + 70 - ballon_kopf_y(self.bal) + 80)))
        return k

    def kopf_oben(self):
        if self.bal <= 0.02:
            return super().kopf_oben()
        q = self.trafo().map(QPointF(4, ballon_kopf_y(self.bal) - 52 - 26 * self.haare))
        return q.x(), q.y()

    def mund(self):
        if self.bal <= 0.02:
            return super().mund()
        q = self.trafo().map(QPointF(6 if self.pose.kopf_vorn else 22, ballon_kopf_y(self.bal) + 20))
        return q.x(), q.y()

    # -- Mütze im Flug

    def hut_trafo(self):
        tr0, t0 = self.hut
        u = self.t - t0
        q = tr0.map(QPointF(0, -20))
        if self.hut_los is None:
            dx, dy, w = self.rand * 10 * math.sin(u * 9) * self.s, -6 * u * self.s, 25 * math.sin(u * 13)
        else:
            v = self.t - self.hut_los
            dx = self.rand * (1400 * v * v + 300 * v) * self.s
            dy, w = -40 * v * self.s, 900 * v * self.rand
        f = QTransform()
        f.translate(q.x() + dx, q.y() + dy)
        f.rotate(w)
        f.translate(-q.x(), -q.y())
        return tr0 * f

    # -- Zeichnen

    def zeichne_requisiten(self, p):
        s, r = self.s, self.rand
        p.save()
        p.translate(self.vx, self.boden)
        p.rotate(self.wackel * 3 * math.sin(self.t * 47))
        p.scale(s * r * G, s * G)
        blinkt = self.stufe >= 4 and (self.t * 8) % 1 < 0.5
        zeichne_ventilator(p, self.dreh, min(1.0, self.fan_v / 1200), 0 if blinkt else min(3, self.stufe),
                           self.druck)
        p.restore()

    def zeichne_davor(self, p):
        s, r = self.s, self.rand
        w = self.fan_v / FLUEGEL[3]
        if w > 0.05:
            kx, ky = self.korb()
            n = int(3 + 9 * min(w, 1.6))
            laenge = (14 + 26 * min(w, 1.6)) * s
            alpha = int(min(230, 110 + 90 * w))
            p.setBrush(KEIN_PINSEL)
            for k in range(n):
                ph = (self.t * (0.7 + 1.6 * w) + k * 0.618) % 1
                hy = ((k * 37) % 9 - 4) / 4 * (VENT_R * G + 6) * s
                x0 = kx + r * (20 * s + ph * WIND_WEITE * s)
                a = int(alpha * math.sin(ph * math.pi))
                p.setPen(stift(QColor(255, 255, 255, a), (1.8 + 1.4 * min(w, 1.5)) * s))
                y = ky + hy + 4 * s * math.sin(self.t * 9 + k)
                p.drawLine(QPointF(x0, y), QPointF(x0 + r * laenge, y + 2 * s * math.sin(k)))
            p.setPen(KEIN_STIFT)
        if self.hut is not None:
            p.save()
            p.setTransform(self.hut_trafo(), True)
            zeichne_muetze_prof(p, 0, 0, 6 * math.sin(self.t * 20))
            p.restore()

    def requisiten_kasten(self):
        s, r = self.s, self.rand
        xa, xb = self.vx - r * 66 * s, self.vx + r * 128 * s
        k = QRectF(min(xa, xb), self.boden - 205 * s, abs(xb - xa), 205 * s)
        kx, ky = self.korb()
        x1 = kx + r * (WIND_WEITE + 80) * s
        k = k.united(QRectF(min(kx, x1), ky - (VENT_R * G + 16) * s, abs(x1 - kx), 2 * (VENT_R * G + 16) * s))
        if self.hut is not None:
            k = k.united(self.hut_trafo().mapRect(QRectF(-40, -60, 80, 72)))
        return k

    # -- Ablauf

    def stelle(self, stufe):
        def tu(sz):
            sz.stufe = stufe
            x, y = sz.knopf()
            sz.streue(x, y - 6 * sz.s, 3 + 2 * stufe, FUNKEN, tempo=90 + 40 * stufe, dauer=0.35, r=(2, 4),
                      art='stern')
        return Tu(tu)

    def wegblasen(self, sz):
        tr = muetze_trafo(self.pose, self.haare) * QTransform.fromTranslate(0, ballon_kopf_y(self.bal) - KOPF_Y)
        self.hut = (tr * self.trafo(), self.t)
        self.muetze = False
        x, y = self.korb()
        self.streue(x + self.rand * 60 * self.s, y, 10, RAUCH, tempo=260, dauer=0.5, r=(6, 12),
                    richtung=0 if self.rand > 0 else math.pi, streuung=0.4)

    def abrauchen(self, sz):
        x, y = self.korb()
        self.streue(x - self.rand * 20 * self.s, y - 10 * self.s, 3, QUALM, tempo=60, dauer=0.9, r=(6, 12),
                    richtung=-math.pi / 2, streuung=0.6)

    def puff(self, sz):
        self.weg(QUALM)
        x, y = self.korb()
        self.streue(x, y + 40 * self.s, 8, FUNKEN, tempo=220, dauer=0.5, r=(3, 6), art='stern')

    def ablauf(self):
        r, s = self.rand, self.s
        self.x = self.aussen(r)
        px = self.vx + r * 150 * s

        def schwitzen(sz, u):
            if 0.2 < u < 0.3 and random.random() < 0.5:
                x, y = sz.kopf_oben()
                sz.streue(x, y + 30 * s, 2, TROPFEN, tempo=80, dauer=0.5, r=(2, 4), schwer=True)
            return Pose(arm_v=-170 + 20 * math.sin(u * 16), arm_v_x=14, sorge=0.5, mund_offen=True,
                        auge_zu=blinzeln(sz.t))

        def fuss(winkel, dauer=0.25, hoch=0):
            def pose(sz, u):
                f = glatt(u / dauer)
                return Pose(bein_v=winkel * f, hub=-hoch * f, arm_v=-40, arm_h=30, blick_y=0.8)
            return pose

        def geniessen(sz, u):
            return Pose(kopf_vorn=True, auge_zu=True, arm_v=-50, arm_h=-50, arm_v_x=16, blick_y=-0.4,
                        wipp=-8 - 3 * math.sin(sz.t * 14))

        def bauch_gucken(sz, u):
            return Pose(kopf_vorn=False, blick_y=1.0, sorge=0.4, arm_v=-55, arm_h=-40, arm_v_x=18,
                        wipp=-10 - 4 * math.sin(sz.t * 18), auge_zu=blinzeln(sz.t))

        def sprung(sz, u):
            f = min(1.0, u / 0.35)
            sz.hopp = math.sin(f * math.pi) * 34 * s
            sz.pose = Pose(arm_v=-150, arm_h=-150, arm_v_x=16, bein_v=-20, bein_h=10, mund_offen=True,
                           kopf_vorn=False, blick_y=0.6)

        def abheben(sz, u):
            return Pose(kopf_vorn=True, schreck=1.0, arm_v=-120, arm_h=-120, arm_v_x=16, bein_v=-20, bein_h=20)

        def zum_knopf(sz, u):
            kx, ky = sz.knopf()
            return Pose(arm_v=-100 + 60 * math.sin(u * 16), arm_h=-100 - 60 * math.sin(u * 16),
                        bein_v=-50 - 8 * math.sin(u * 20), bein_h=10, blick_y=1.0, sorge=0.6,
                        mund_offen=False)

        def erwartung(sz, u):
            return Pose(arm_v=-110, arm_h=-110, bein_v=-55, bein_h=10, kopf_vorn=u > 0.15, sorge=0.2,
                        auge_zu=False)

        return [
            Gehe(bis=px, tempo=1.8),
            Setze(richtung=-r),
            Stehe(0.4, schwitzen),
            Stehe(0.22, fuss(-40)),
            Setze(druck=1.0), self.stelle(1), Wandel(0.15, fan_v=FLUEGEL[1], druck=0.0),
            Wandel(0.25, bal=0.12, haare=0.3),
            Stehe(0.6, geniessen),
            Stehe(0.2, fuss(-45, 0.2, 6)),
            Setze(druck=1.0), self.stelle(2), Wandel(0.15, fan_v=FLUEGEL[2], druck=0.0),
            Wandel(0.35, bal=0.45, haare=0.6),
            Stehe(0.3, geniessen),
            Stehe(0.45, bauch_gucken),
            Stehe(0.25, lambda sz, u: Pose(kopf_vorn=True, auge_zu=False, blick_y=-0.2, hub=6, arm_v=-20, arm_h=20)),
            Jeweils(0.35, sprung),
            Setze(druck=1.0, wackel=0.5), self.stelle(3),
            Wandel(0.5, fan_v=FLUEGEL[3], bal=1.0, haare=1.0, druck=0.0),
            Stehe(0.1, abheben),
            Wandel(0.5, hopp=lambda sz: sz.hopp + 70 * s),
            Schwebe(0.7, zug=-40),
            Schwebe(0.9, zug=-10, pose=lambda sz, u: Publikumsblick.blick(sz, u / 0.9)),
            Wandel(0.3, hopp=lambda sz: sz.hopp - 50 * s),
            Schwebe(0.9, zug=55, pose=zum_knopf),
            Stehe(0.35, erwartung),
            Setze(druck=1.0, wackel=1.0), self.stelle(4),
            Wandel(0.1, fan_v=FLUEGEL[4]),
            Wandel(0.12, stauchen=0.86),
            Setze(stauchen=1.0),
            Tu(self.wegblasen),
            Wegblasen(),
            Stehe(0.7),
            Setze(hut_los=lambda sz: sz.t),
            Jeweils(0.6, lambda sz, u: sz.abrauchen(sz) if random.random() < 0.4 else None),
            Setze(hut=None, stufe=0),
            Wandel(0.3, fan_v=0.0, wackel=0.0),
            Tu(self.puff),
            WarteBis(lambda sz: not sz.wolke and not sz.splitter),
        ]

    def schreck_ablauf(self):
        self.hut = None
        self.muetze = True
        if self.bal > 0.3 and self.zeige_figur and self.figur_sichtbar():
            self.wackel = 0.0
            self._vorher()
            return [HaareHoch(1.0), Setze(stufe=0), Wegblasen()] + self._ende()
        self.bal = 0.0
        self.hopp = 0.0
        if not self.zeige_figur:
            self._vorher()
            return self._ende()
        return self.schreck_kittel()
