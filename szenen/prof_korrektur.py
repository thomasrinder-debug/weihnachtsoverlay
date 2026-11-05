import math

from PyQt6.QtCore import QPointF

from zeichnen.figur import Pose
from zeichnen.grundlagen import blinzeln
from zeichnen.labor import zeichne_kreide
from zeichnen.labor_c import WeihnachtsmannOhneSack

from .basis import Gehe, Mit, Nebenbei, Setze, Stehe, WarteNebenbei
from .professor import Schreibe, TafelSzene, Wische, Zurueck

WM_SCHULTER = (10, -140)
WM_ARM = 56


def wm_arm_zu(d, x, y):
    """Armwinkel des Weihnachtsmanns zum Weltpunkt (x, y)."""
    q = d.trafo().map(QPointF(d.pose.arm_v_x, WM_SCHULTER[1] + d.pose.hub))
    dx = (x - q.x()) * d.richtung / d.s
    dy = (y - q.y()) / d.s
    return math.degrees(math.atan2(-dx, dy))


def nicken(sz, u):
    return Pose(kopf_vorn=True, auge_zu=True, hub=-4 * abs(math.sin(u * 7)), arm_v=-20, arm_h=20, sack=False)


class Korrektur(TafelSzene):
    """2+2=5: der Weihnachtsmann macht eine 4 daraus, der Professor wischt und schreibt wieder 5.
    Da ändert der Weihnachtsmann die erste 2 in eine 3, und beide nicken zufrieden."""
    name, titel, reihenfolge = 'korrektur', 'Korrigiert!', 77

    def vorbereiten(self):
        self.tafel_vorbereiten(0.22)
        h, x0, y = 30, -62, -182
        w = 0.72 * h
        self.z2 = self.schreib('2', x0, y, h)
        self.rest = self.schreib('+2=', x0 + w, y, h)
        self.f5 = self.schreib('5', x0 + 4 * w, y, h)
        self.f4 = self.schreib('4', x0 + 4 * w, y, h)
        self.f5b = self.schreib('5', x0 + 4 * w + 1, y + 1, h)
        self.z3 = self.schreib('3', x0, y, h)
        wm = self.dazu('wm', WeihnachtsmannOhneSack, groesse=0.88)
        wm.kreide_ort = None
        wm.schwamm_ort = None
        wm.arm_zu = lambda x, y, vorn=True: wm_arm_zu(wm, x, y)
        wm.pose = Pose(sack=False)

    def zeichne_davor(self, p):
        super().zeichne_davor(p)
        wm = self.darsteller['wm']
        if wm.kreide_ort and wm.zeige_figur:
            p.save()
            p.translate(*wm.kreide_ort)
            p.scale(self.s, self.s)
            zeichne_kreide(p, 0, 0, -50, 10)
            p.restore()

    def ablauf(self):
        r = self.richtung
        s = self.s
        self.x = self.aussen(-r)
        wm = self.darsteller['wm']
        wm.x = self.aussen(-r) - r * 60 * s
        links = lambda d: d.sz.tafel_x - 128 * d.sz.s  # noqa: E731
        return [
            *self.an_tafel(),
            Stehe(0.3),
            Setze(kreide_da=False),
            Schreibe(self.z2, 0.5),
            Schreibe(self.rest, 1.5),
            Schreibe(self.f5, 0.6),
            Setze(kreide_ort=None),
            Zurueck(50),
            Stehe(1.0, lambda sz, u: Pose(kopf_vorn=True, auge_zu=True, hub=-4 * abs(math.sin(u * 7)),
                                          arm_v=-20, arm_h=20)),
            # der Weihnachtsmann kommt und verbessert
            Mit('wm', Gehe(bis=links, tempo=1.1)),
            Mit('wm', Setze(richtung=1)),
            Mit('wm', Stehe(0.9, lambda d, u: Pose(sack=False, blick_y=-0.3, sorge=0.5,
                                                   arm_v=-150, arm_v_x=12, auge_zu=blinzeln(d.t)))),
            Mit('wm', Wische([self.f5], 0.6)),
            Mit('wm', Schreibe(self.f4, 0.6, abstand=46)),
            Mit('wm', Setze(kreide_ort=None)),
            Mit('wm', Gehe(bis=links, tempo=0.8)),
            Mit('wm', Setze(richtung=1)),
            Nebenbei(Mit('wm', Stehe(1.0, lambda d, u: Pose(sack=False, kopf_vorn=True, auge_zu=0.3 < u < 0.45)))),
            Stehe(0.9, lambda sz, u: Pose(schreck=0.6, sorge=1.0, blick_y=-0.2, arm_v=-60)),
            WarteNebenbei(),
            # der Professor stellt sein Ergebnis wieder her
            Gehe(bis=lambda sz: sz.tafel_x + 105 * sz.s, tempo=1.2),
            Setze(richtung=-1),
            Wische([self.f4], 0.9),
            Schreibe(self.f5b, 0.6),
            Setze(kreide_ort=None),
            Zurueck(45),
            Stehe(0.8, lambda sz, u: Pose(kopf_vorn=True, arm_v=-20, arm_h=20, auge_zu=blinzeln(sz.t))),
            # der Weihnachtsmann passt die Aufgabe an
            Mit('wm', Stehe(1.0, lambda d, u: Pose(sack=False, arm_v=-150 + 6 * math.sin(u * 5), arm_v_x=12,
                                                   blick_y=-0.8, auge_zu=blinzeln(d.t)))),
            Mit('wm', Stehe(0.3, Pose(sack=False, kopf_vorn=True, mund_offen=True, arm_v=-130, arm_v_x=20))),
            Mit('wm', Wische([self.z2], 0.6)),
            Mit('wm', Schreibe(self.z3, 0.6, abstand=46)),
            Mit('wm', Setze(kreide_ort=None)),
            Mit('wm', Gehe(bis=links, tempo=0.8)),
            Mit('wm', Setze(richtung=1)),
            Stehe(0.5, lambda sz, u: Pose(blick_y=-0.3, sorge=0.4, auge_zu=blinzeln(sz.t))),
            Nebenbei(Mit('wm', Stehe(1.6, nicken))),
            Stehe(1.6, lambda sz, u: Pose(kopf_vorn=True, auge_zu=True, hub=-4 * abs(math.sin(u * 7)),
                                          arm_v=-20, arm_h=20)),
            WarteNebenbei(),
            Nebenbei(Mit('wm', Gehe(bis=lambda d: d.sz.aussen(d.naechster_rand()), tempo=1.0))),
            *self.tafel_abgang(),
            WarteNebenbei(),
        ]

    def schreck_ablauf(self):
        self.kreide_ort = self.schwamm_ort = None
        wm = self.darsteller['wm']
        wm.kreide_ort = None
        return self.schreck_rennen()
