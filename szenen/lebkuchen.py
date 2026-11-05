import math
import random
from dataclasses import replace

from PyQt6.QtCore import QPointF
from PyQt6.QtGui import QColor

from zeichnen.figur import Pose, hand_punkt
from zeichnen.figuren import Lebkuchenmann
from zeichnen.grundlagen import blinzeln

from .basis import Gehe, Mit, Nebenbei, Renne, Springe, Stehe, Szene, Tu, WarteNebenbei

KRUEMEL = [QColor('#C98A4B'), QColor('#A8692F'), QColor('#E0B07A')]


def halten(pose, sz):
    return replace(pose, arm_v=-78, arm_v_x=14)


class Lebkuchen(Szene):
    """Er kommt mit einem Lebkuchenmann in der Hand, beißt ihm ein Stück vom Kopf ab,
    worauf der Keks entsetzt herunterspringt und flieht; er schaut verdutzt und rennt hinterher."""
    name, titel, reihenfolge = 'lebkuchen', 'Lebkuchenmann', 12

    def vorbereiten(self):
        self.keks = self.dazu('keks', Lebkuchenmann, groesse=0.3, biss=False)
        self.in_hand = True
        self.arm = -78.0

    def ablauf(self):
        self.x = self.aussen(-self.richtung)
        return [
            Gehe(bis=self.vom_rand(random.uniform(0.16, 0.22)), haltung=halten),
            Stehe(1.0, lambda sz, u: Pose(arm_v=-78, arm_v_x=14, auge_zu=blinzeln(sz.t), blick_x=1)),
            Stehe(0.7, lambda sz, u: Pose(arm_v=-78 - 30 * min(1.0, u / 0.5), arm_v_x=14, mund_offen=u > 0.3)),
            Tu(lambda sz: sz.beissen()),
            Stehe(1.0, lambda sz, u: Pose(arm_v=-108, arm_v_x=14, mund_offen=(u * 6) % 2 < 1,
                                         auge_zu=True)),
            Tu(lambda sz: sz.loslassen()),
            Nebenbei(Mit('keks', Springe(lambda d: (d.x + d.richtung * 50 * d.sz.s, d.boden), 0.45, 110)),
                     Mit('keks', Renne(zum='rand', tempo=3.2))),
            Stehe(1.0, lambda sz, u: Pose(arm_v=-108 + 30 * min(1.0, u / 0.3), arm_v_x=14, mund_offen=True,
                                         schreck=0.0, blick_x=1)),
            Stehe(1.3, lambda sz, u: Pose(kopf_vorn=True, sorge=0.9, arm_v=-78, arm_v_x=14,
                                         auge_zu=0.6 < u < 0.75)),
            Renne(zum='rand', tempo=2.8),
            WarteNebenbei(),
        ]

    def schreck_ablauf(self):
        if self.in_hand:
            self.in_hand = False
            self.keks.y = self.boden
        return self.schreck_alle()

    def beissen(self):
        self.keks.biss = True
        q = self.keks.trafo().map(QPointF(20, -146))
        self.streue(q.x(), q.y(), 10, KRUEMEL, tempo=140, dauer=0.9, r=(1.5, 3), schwer=True)
        self.keks.striche = True

    def loslassen(self):
        self.in_hand = False
        self.keks.striche = False

    def weiter(self, dt):
        k = self.keks
        if self.in_hand:
            hx, hy = hand_punkt(self.x, self.y - self.hopp, self.s, self.richtung, self.pose,
                                self.stauchen, self.neigung)
            k.x, k.y = hx + self.richtung * 3 * self.s, hy + 5 * self.s
            k.richtung = -self.richtung
            if k.biss:
                k.pose = Pose(kopf_vorn=True, schreck=1.0, arm_v=-115, arm_h=-100,
                              bein_v=math.sin(self.t * 30) * 30, bein_h=-math.sin(self.t * 30) * 30)
            elif self.pose.mund_offen:
                k.pose = Pose(kopf_vorn=True, sorge=1.0, schreck=0.3)
            else:
                k.pose = Pose(auge_zu=blinzeln(self.t, 1.1), blick_x=1)
