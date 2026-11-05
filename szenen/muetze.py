import math
import random
from dataclasses import replace

from PyQt6.QtCore import QRectF
from PyQt6.QtGui import QColor

from zeichnen.figur import Pose
from zeichnen.grundlagen import blinzeln
from zeichnen.requisiten import zeichne_muetze_lose

from .basis import Ducke, Erschrecke, Gehe, Renne, Schaue, Setze, Stehe, Szene, Tu, WarteBis

WIND = QColor(255, 255, 255, 200)


def kopf_halten(pose, sz):
    return replace(pose, arm_v=-165, arm_h=-160, arm_v_x=16)


class Muetze(Szene):
    """Eine Windbö reißt ihm die Mütze vom Kopf. Er hält sich verschämt die Glatze,
    jagt der Mütze hinterher, und als er sie fast hat, weht sie über ihn hinweg
    zurück; er dreht sich um und rennt ihr nach."""
    name, titel, reihenfolge = 'muetze', 'Mütze weg', 22

    def vorbereiten(self):
        self.auf = True
        self.m = None           # lose Mütze: [x, y, vx, vy, drehung, liegt]
        self.schweben = False   # vom Wind getragen, fällt kaum

    def ablauf(self):
        r, s = self.richtung, self.s
        self.x = self.aussen(-r)
        return [
            Gehe(bis=self.vom_rand(random.uniform(0.12, 0.17))),
            Schaue(1.0),
            Tu(lambda sz: sz.boe(r, 260, -520)),
            Stehe(0.5, Pose(kopf_vorn=True, schreck=1.0, muetze=False)),
            Stehe(1.6, lambda sz, u: Pose(kopf_vorn=True, sorge=1.0, arm_v=-165, arm_h=-160, arm_v_x=16,
                                         auge_zu=0.6 < u < 0.75, blick_x=math.sin(u * 3))),
            WarteBis(lambda sz: sz.m[5]),
            Gehe(bis=lambda sz: sz.m[0] - r * 70 * s, tempo=1.6, haltung=kopf_halten),
            Ducke(0.25),
            Setze(stauchen=1.0),
            Tu(lambda sz: sz.boe(-r, 480, -300, schweben=True)),
            Stehe(0.6, lambda sz, u: Pose(kopf_vorn=True, schreck=1.0, blick_y=-1)),
            Renne(zum='zurueck', tempo=2.4, haltung=kopf_halten),
            WarteBis(lambda sz: sz.m is None),
        ]

    def schreck_ablauf(self):
        if self.m and self.m[5]:
            self.m[2], self.m[3], self.m[5] = self.naechster_rand() * 900 * self.s, -300 * self.s, False
            self.schweben = True
        if not self.figur_sichtbar():
            return [WarteBis(lambda sz: sz.m is None)]
        return [Erschrecke(0.35, 50), Renne(zum='rand', tempo=3.6, haltung=None if self.auf else kopf_halten),
                WarteBis(lambda sz: sz.m is None)]

    def boe(self, wohin, vx, vy, schweben=False):
        s = self.s
        self.schweben = schweben
        if self.auf:
            self.auf = False
            self.m = [self.x + self.richtung * 6 * s, self.y - 205 * s, 0, 0, 0.0, False]
        m = self.m
        m[2], m[3], m[5] = wohin * vx * s, vy * s, False
        for _ in range(10):
            y = self.y - random.uniform(20, 260) * s
            self.streue(self.x - wohin * 200 * s, y, 1, WIND, tempo=900, dauer=0.5, r=(1.5, 3),
                        richtung=0 if wohin > 0 else math.pi, streuung=0.05)

    def weiter(self, dt):
        if not self.auf:
            self.pose = replace(self.pose, muetze=False)
        m = self.m
        if m and not m[5]:
            m[3] += (150 if self.schweben else 900) * self.s * dt
            m[0] += m[2] * dt
            m[1] += m[3] * dt
            m[4] += m[2] / self.s * 0.6 * dt
            if m[1] >= self.boden - 2 * self.s and m[3] > 0:
                m[1], m[5] = self.boden - 2 * self.s, True
                m[4] = 0.0
        if m and not self.geo.adjusted(-80, -80, 80, 80).contains(m[0], m[1]):
            self.m = None

    def zeichne_vorn(self, p):
        if self.m:
            p.save()
            p.translate(self.m[0], self.m[1])
            p.rotate(self.m[4])
            p.scale(self.s, self.s)
            zeichne_muetze_lose(p)
            p.restore()

    def grenzen_extra(self):
        if not self.m:
            return QRectF()
        r = 60 * self.s
        return QRectF(self.m[0] - r, self.m[1] - r, 2 * r, 2 * r)
