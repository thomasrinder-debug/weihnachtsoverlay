import math

from zeichnen.figur import Pose
from zeichnen.grundlagen import blinzeln

from .basis import Schaue, Setze, Stehe, Warte
from .professor import Schreibe, Streiche, TafelSzene, Zurueck


class Einsplus(TafelSzene):
    """Der Professor schreibt 1+1=3 an die Tafel, stutzt, streicht die 3 durch und
    schreibt ... wieder eine 3. Stolzes Nicken."""
    name, titel, reihenfolge = 'einsplus', 'Stur gerechnet', 72

    def vorbereiten(self):
        self.tafel_vorbereiten(0.2)
        self.a = self.schreib('1+1=', -62, -180, 26)
        self.b = self.schreib('3', 14, -180, 26)
        self.c = self.schreib('3', 38, -154, 34)

    def ablauf(self):
        self.x = self.aussen(-self.richtung)
        return [
            *self.an_tafel(),
            Stehe(0.4),
            Setze(kreide_da=False),
            Schreibe(self.a, 2.0),
            Schreibe(self.b, 0.6),
            Stehe(0.5, lambda sz, u: Pose(arm_v=-40, auge_zu=blinzeln(sz.t))),
            Schaue(0.9),
            Setze(richtung=-1),
            Stehe(0.9, lambda sz, u: Pose(arm_v=-150, arm_v_x=12, blick_y=-0.6, sorge=0.6 * min(1, u))),
            Streiche(self.b, 0.4),
            Warte(0.3),
            Schreibe(self.c, 0.7),
            Setze(kreide_ort=None),
            Zurueck(55),
            Stehe(1.6, lambda sz, u: Pose(kopf_vorn=True, auge_zu=True, hub=-4 * abs(math.sin(u * 7)),
                                          arm_v=-20, arm_h=20)),
            *self.tafel_abgang(),
        ]

    def schreck_ablauf(self):
        self.kreide_ort = None
        return self.schreck_versinken()
