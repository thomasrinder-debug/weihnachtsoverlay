import math
import random

from PyQt6.QtCore import QPointF, QRectF

from zeichnen.figur import Pose
from zeichnen.grundlagen import blinzeln
from zeichnen.requisiten import zeichne_zuckerstange

from .basis import Schritt, Setze, Stehe, Szene, Tu, Wandel, Warte, WarteBis

ARM = 195            # von den Füßen bis zu den Händen über dem Kopf
LANG = 200           # Länge der Zuckerstangen


class Abflug(Schritt):
    """Er lässt los und fliegt in hohem Bogen über den oberen Rand hinaus."""

    def beginn(self, sz):
        sz.fliegt = True
        sz.vx = (1 if sz.phi >= 0 else -1) * 260 * sz.s
        sz.vy = -1500 * sz.s

    def weiter(self, sz, u, dt):
        sz.vy += 900 * sz.s * dt
        sz.x += sz.vx * dt
        sz.y += sz.vy * dt
        sz.neigung += 400 * dt
        sz.pose = Pose(arm_v=-150, arm_h=-140, bein_v=-30, bein_h=20, kopf_vorn=True, mund_offen=True,
                       schreck=0.4 if sz.erschreckt else 0.0)

    def fertig(self, sz, u):
        return not sz.figur_sichtbar()

    def ende(self, sz):
        sz.zeige_figur = False


class Trapez(Szene):
    """Ein Trapez aus drei Zuckerstangen senkt sich vom oberen Rand, er hängt daran und
    schaukelt immer höher, hängt sich kopfüber an die Füße und winkt, schwingt zurück
    und lässt sich in hohem Bogen über den Rand hinausschleudern."""
    name, titel, reihenfolge = 'trapez', 'Zuckerstangen-Trapez', 43

    def vorbereiten(self):
        self.px = self.vom_rand(random.uniform(0.11, 0.14))
        self.lang = 0.0
        self.a = 0.0             # Ausschlag in Grad
        self.phi = 0.0
        self.k = 0.0             # 0 an den Händen, 1 kopfüber an den Füßen
        self.fliegt = False
        self.vx = self.vy = 0.0
        self.y = self.oben - 400 * self.s

    def stange(self):
        r = math.radians(self.phi)
        return (self.px + math.sin(r) * self.lang * self.s,
                self.oben - 8 * self.s + math.cos(r) * self.lang * self.s)

    def ablauf(self):
        return [
            Setze(pose=Pose(arm_v=-176, arm_h=-176, arm_v_x=12, kopf_vorn=True)),
            Wandel(1.2, lang=LANG),
            Stehe(0.6, lambda sz, u: Pose(arm_v=-176, arm_h=-176, arm_v_x=12, kopf_vorn=True,
                                         auge_zu=blinzeln(sz.t))),
            Wandel(2.6, a=32),
            Wandel(0.6, k=1.0),
            Stehe(2.2, lambda sz, u: Pose(arm_v=-150 + 25 * math.sin(u * 10), arm_h=-20, arm_v_x=16,
                                         kopf_vorn=True, mund_offen=(u * 4) % 2 < 1, bein_v=-10, bein_h=10)),
            Wandel(0.6, k=0.0),
            Wandel(0.8, a=44),
            WarteBis(lambda sz: abs(sz.phi) > sz.a * 0.9),
            Abflug(),
            Wandel(0.8, a=0.0),
            Wandel(0.8, lang=0.0),
        ]

    def schreck_ablauf(self):
        if self.fliegt:
            if not self.zeige_figur:
                return [Wandel(0.4, a=0.0), Wandel(0.4, lang=0.0)]
            return [Abflug(), Wandel(0.4, lang=0.0)]
        if self.lang < 20:
            return [Wandel(0.2, lang=0.0)]
        return [Setze(striche=True), Wandel(0.15, k=0.0), Setze(striche=False), Abflug(), Wandel(0.4, lang=0.0)]

    def weiter(self, dt):
        self.phi = self.a * math.sin(self.t * 2.3)
        if self.fliegt or not self.zeige_figur:
            return
        bx, by = self.stange()
        n = -self.phi + 180 * self.k
        rad = math.radians(n)
        hoch = (math.sin(rad), -math.cos(rad))
        self.x = bx - (1 - self.k) * ARM * self.s * hoch[0]
        self.y = by - (1 - self.k) * ARM * self.s * hoch[1]
        self.neigung = n * self.richtung
        if not isinstance(self.aktuell, Stehe) and self.k < 0.5:
            sw = math.sin(self.t * 2.3 + 1)
            self.pose = Pose(arm_v=-176, arm_h=-176, arm_v_x=12, bein_v=-25 * sw, bein_h=-10 * sw,
                             kopf_vorn=True, mund_offen=self.a > 25, auge_zu=blinzeln(self.t))

    def striche_punkt(self):
        return self.x, self.y - 40 * self.s

    def zeichne_hinten(self, p):
        if self.lang <= 0:
            return
        s = self.s
        p.save()
        p.translate(self.px, self.oben - 8 * s)
        p.rotate(-self.phi)
        p.scale(s, s)
        for dx in (-34, 34):
            p.save()
            p.translate(dx, 0)
            zeichne_zuckerstange(p, self.lang)
            p.restore()
        p.save()
        p.translate(-44, self.lang)
        p.rotate(-90)
        zeichne_zuckerstange(p, 88, haken=False)
        p.restore()
        p.restore()

    def grenzen_extra(self):
        s = self.s
        r = (self.lang + ARM + 60) * s
        return QRectF(self.px - r, self.oben, 2 * r, r + 20 * s)
