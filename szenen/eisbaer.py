import math
import random

from PyQt6.QtCore import QPointF
from PyQt6.QtGui import QColor

from zeichnen.figur import Pose
from zeichnen.figuren import Eisbaer
from zeichnen.grundlagen import blinzeln

from .basis import (Erschrecke, Gehe, Jeweils, Mit, Nebenbei, Renne, Setze, Stehe, Szene, Tu, Wandel, Warte,
                    WarteNebenbei)

BLASE = QColor(200, 230, 255, 220)


def schleichen(pose, sz):
    return Pose(bein_v=pose.bein_v * 1.5, bein_h=pose.bein_h * 1.5, arm_v=-70 + pose.arm_v * 0.3,
                arm_h=-60, hub=pose.hub * 2, kopf_vorn=True, sorge=0.8, blick_x=0.6, wipp=pose.wipp)


class EisbaerSzene(Szene):
    """Ein Eisbär tapst herein, gähnt und schläft mit einer Schlafblase an der Nase ein.
    Der Weihnachtsmann schleicht auf Zehenspitzen heran, die Blase wird größer und
    größer und platzt: Beide fahren hoch, er flieht, der Bär hinterher."""
    name, titel, reihenfolge = 'eisbaer', 'Schlafender Eisbär', 19

    def vorbereiten(self):
        self.b = self.dazu('b', Eisbaer, groesse=1.25, liegt=0.0, schlaeft=False, blase=0.0)
        self.b.tempo = self.tempo * 0.8
        self.atmen = False

    def ablauf(self):
        r, s = self.richtung, self.s
        self.x = self.aussen(-r)
        ziel = self.vom_rand(random.uniform(0.17, 0.22))
        return [
            Mit('b', Gehe(bis=ziel)),
            Mit('b', Stehe(1.1, lambda d, u: Pose(mund_offen=0.2 < u < 0.9, auge_zu=0.2 < u < 1.0))),
            Mit('b', Wandel(0.7, liegt=1.0)),
            Mit('b', Setze(schlaeft=True)),
            Setze(atmen=True),
            Warte(0.6),
            Gehe(bis=lambda sz: sz.b.x - r * 125 * s, tempo=0.45, haltung=schleichen),
            Stehe(1.5, lambda sz, u: Pose(kopf_vorn=True, sorge=0.9, blick_x=-0.5, arm_v=-60, arm_h=-60,
                                         auge_zu=blinzeln(sz.t))),
            Setze(atmen=False),
            Mit('b', Wandel(1.3, blase=22)),
            Mit('b', Stehe(0.1)),
            Tu(lambda sz: sz.platzen()),
            Nebenbei(Mit('b', Erschrecke(0.4, 50)), Mit('b', Setze(liegt=0.0)), Warte(0.3),
                     Mit('b', Renne(zum='zurueck', tempo=3.2))),
            Erschrecke(0.4, 55),
            Renne(zum='zurueck', tempo=3.6),
            WarteNebenbei(),
        ]

    def schreck_ablauf(self):
        b = self.b
        if b.blase > 0:
            self.platzen()
        b.liegt, b.schlaeft, self.atmen = 0.0, False, False
        return self.schreck_alle()

    def platzen(self):
        b = self.b
        b.schlaeft = False
        if b.blase > 0:
            q = b.trafo().map(QPointF(118 + b.blase * 0.7, -24))
            self.streue(q.x(), q.y(), 14, BLASE, tempo=150, dauer=0.5, r=(1.5, 3.5))
        b.blase = 0.0

    def weiter(self, dt):
        if self.atmen:
            self.b.blase = 5 + 5 * (0.5 + 0.5 * math.sin(self.t * 2.2))
