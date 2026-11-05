import math
import random
from dataclasses import replace

from PyQt6.QtCore import QRectF

from zeichnen.figur import Pose, hand_punkt
from zeichnen.grundlagen import WEISS, blinzeln
from zeichnen.requisiten import zeichne_schaufel, zeichne_schneehaufen, zeichne_schneewuerfel

from .basis import Erschrecke, Gehe, Jeweils, Renne, Setze, Stehe, Szene, Tu, Wandel, Warte

WUERFEL = 30         # Kantenlänge in Einheiten


def tragen(pose, sz):
    return replace(pose, arm_v=-60, arm_v_x=14)


class Schaufel(Szene):
    """Er schippt einen Schneehaufen über die Schulter. Der Schnee kommt als sauberer Würfel
    zurückgeflogen und landet genau an derselben Stelle. Er schaufelt ihn empört weg, der
    Würfel ist sofort wieder da, beim dritten Mal schon, bevor er überhaupt ausholt.
    Schließlich lädt er den Würfel auf die Schaufel und trägt ihn beleidigt davon."""
    name, titel, reihenfolge = 'schaufel', 'Schneeschaufel', 40

    def vorbereiten(self):
        self.haufen = 1.0
        self.wuerfel = None          # [x, y, drehung]
        self.geladen = False
        self.schaufel_w = 20.0       # Winkel der Schaufel in seinem Blickfeld

    def stelle(self):
        return self.x + self.richtung * 95 * self.s

    def ablauf(self):
        r, s = self.richtung, self.s
        self.x = self.aussen(-r)
        return [
            Gehe(bis=self.vom_rand(random.uniform(0.1, 0.13)), haltung=tragen),
            Stehe(0.5, Pose(arm_v=-60, arm_v_x=14)),
            *self.schippen(1.0, erst=True),
            *self.zurueck(1.0),
            Stehe(1.0, lambda sz, u: Pose(kopf_vorn=True, sorge=0.8, blick_y=0.6, arm_v=-60, arm_v_x=14,
                                         auge_zu=0.5 < u < 0.62)),
            *self.schippen(0.6),
            *self.zurueck(0.6),
            Stehe(0.5, Pose(kopf_vorn=True, schreck=0.6, arm_v=-60, arm_v_x=14)),
            Stehe(0.4, Pose(arm_v=-90, arm_v_x=14, sorge=1.0)),
            Setze(wuerfel=None, schaufel_w=20.0),
            *self.zurueck(0.5),
            Stehe(1.4, lambda sz, u: Pose(kopf_vorn=True, sorge=1.0, arm_v=-60, arm_v_x=14,
                                         auge_zu=0.4 < u < 0.55 or 0.9 < u < 1.05)),
            Setze(stauchen=0.9), Warte(0.3), Setze(geladen=True, wuerfel=None, stauchen=1.0),
            Renne(zum='zurueck', tempo=1.2, haltung=tragen),
        ]

    def schippen(self, dauer, erst=False):
        def f(sz, u):
            g = u / dauer
            sz.pose = Pose(arm_v=-40 - 120 * max(0.0, g - 0.4) / 0.6, arm_v_x=14, mund_offen=g > 0.5)
            sz.stauchen = 1 - 0.1 * math.sin(math.pi * min(1.0, g / 0.5))
            sz.schaufel_w = 30 - 240 * max(0.0, g - 0.4) / 0.6
        return [Jeweils(dauer, f), Tu(lambda sz: sz.wegwerfen(erst)), Setze(stauchen=1.0, schaufel_w=20.0)]

    def zurueck(self, dauer):
        def flug(sz, u):
            f = min(1.0, u / dauer)
            x0 = sz.aussen(-sz.richtung)
            x1, y1 = sz.stelle(), sz.boden - WUERFEL / 2 * sz.s
            sz.wuerfel = [x0 + (x1 - x0) * f, sz.boden - 200 * sz.s + (y1 - sz.boden + 200 * sz.s) * f
                          - 220 * sz.s * 4 * f * (1 - f), 360 * (1 - f)]
        return [Jeweils(dauer, flug), Tu(lambda sz: sz.aufsetzen())]

    def wegwerfen(self, erst):
        s, r = self.s, self.richtung
        if erst:
            self.haufen = 0.0
        self.wuerfel = None
        x, y = self.x - r * 40 * s, self.y - 230 * s
        self.streue(x, y, 14, WEISS, tempo=260, dauer=0.7, r=(4, 8), schwer=True,
                    richtung=math.atan2(-1, -r * 1.2), streuung=0.4)

    def aufsetzen(self):
        x, y, _ = self.wuerfel
        self.wuerfel = [x, y, 0.0]
        self.streue(x, self.boden - 4 * self.s, 8, WEISS, tempo=90, dauer=0.5, r=(2, 5))

    def schreck_ablauf(self):
        self.nebenbei.clear()
        if not self.figur_sichtbar():
            return []
        if self.wuerfel and abs(self.wuerfel[2]) < 1:
            self.geladen, self.wuerfel = True, None
        self.haufen = 0.0
        return [Setze(stauchen=1.0, schaufel_w=20.0), Erschrecke(0.3, 45),
                Renne(zum='rand', haltung=tragen)]

    def zeichne_hinten(self, p):
        if self.haufen > 0:
            zeichne_schneehaufen(p, self.stelle(), self.boden, 90 * self.s, 34 * self.s * self.haufen)

    def zeichne_vorn(self, p):
        s = self.s
        if self.wuerfel:
            zeichne_schneewuerfel(p, self.wuerfel[0], self.wuerfel[1], WUERFEL * s, self.wuerfel[2])
        if self.zeige_figur:
            hx, hy = hand_punkt(self.x, self.y - self.hopp, s, self.richtung, self.pose, self.stauchen,
                                self.neigung)
            p.save()
            p.translate(hx, hy)
            p.scale(s * self.richtung, s)
            zeichne_schaufel(p, self.schaufel_w, self.geladen)
            p.restore()

    def grenzen_extra(self):
        s = self.s
        k = QRectF(self.x - 200 * s, self.y - 300 * s, 400 * s, 300 * s)
        if self.wuerfel:
            k = k.united(QRectF(self.wuerfel[0] - 40 * s, self.wuerfel[1] - 40 * s, 80 * s, 80 * s))
        return k
