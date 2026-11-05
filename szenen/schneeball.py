import math
import random

from PyQt6.QtCore import QPointF, QRectF

from zeichnen.figur import Pose
from zeichnen.figuren import Wichtel
from zeichnen.grundlagen import WEISS, blinzeln, flausch
from zeichnen.requisiten import zeichne_schneeball

from .basis import Erschrecke, Gehe, Mit, Nebenbei, Renne, Schaue, Schritt, Setze, Stehe, Szene, Tu, Warte


class Wurf(Schritt):
    """Der Schneeball fliegt im Bogen von start(szene) nach ziel(szene)."""

    def __init__(self, dauer, hoehe):
        self.dauer, self.hoehe = dauer, hoehe

    def beginn(self, sz):
        self.a = sz.elf_hand()
        sz.ball = self.a

    def weiter(self, sz, u, dt):
        bx, by = sz.kopf_punkt()
        f = min(1.0, u / self.dauer)
        sz.ball = (self.a[0] + (bx - self.a[0]) * f,
                   self.a[1] + (by - self.a[1]) * f - self.hoehe * sz.s * 4 * f * (1 - f))


def ausholen(d, u):
    return Pose(arm_v=50 - 210 * max(0.0, (u - 0.45) / 0.15) if u > 0.45 else 50 * min(1.0, u / 0.3),
                arm_v_x=8, mund_offen=True, blick_x=1)


class Schneeball(Szene):
    """Er steht nichtsahnend da, als ein Wichtel vom Rand her einen Schneeball an seine
    Mütze wirft. Er dreht sich empört zu den Zuschauern: Wart ihr das? Der Wichtel lugt
    kichernd wieder hervor, wird erwischt und flitzt davon, er hinterher."""
    name, titel, reihenfolge = 'schneeball', 'Schneeballwurf', 18

    def vorbereiten(self):
        self.w = self.dazu('w', Wichtel, groesse=0.62)
        self.ball = None
        self.schnee = False

    def elf_hand(self):
        q = self.w.trafo().map(QPointF(16, -150))
        return q.x(), q.y()

    def kopf_punkt(self):
        return self.x - self.richtung * 6 * self.s, self.y - self.hopp - 205 * self.s

    def ablauf(self):
        r, s = self.richtung, self.s
        rand = self.aussen(-r)
        self.x = rand
        versteck = self.geo.left() if r > 0 else self.geo.right()
        return [
            Gehe(bis=self.vom_rand(random.uniform(0.22, 0.27))),
            Stehe(1.0),
            Schaue(1.0),
            Stehe(0.6),
            Mit('w', Setze(x=rand, richtung=r)),
            Mit('w', Gehe(bis=versteck + r * 40 * s, tempo=0.8)),
            Mit('w', Stehe(0.62, ausholen)),
            Nebenbei(Mit('w', Stehe(0.3, Pose(arm_v=-150, arm_v_x=8, mund_offen=True))),
                     Mit('w', Gehe(bis=rand, tempo=1.6))),
            Wurf(0.55, 70),
            # Treffer!
            Tu(lambda sz: sz.treffer()),
            Erschrecke(0.3, 26),
            Stehe(0.5, lambda sz, u: Pose(auge_zu=True, sorge=1.0)),
            Stehe(2.2, lambda sz, u: Pose(kopf_vorn=True, sorge=1.0, blick_x=math.sin(u * 2.4) * 0.8,
                                         auge_zu=1.3 < u < 1.45)),
            Mit('w', Gehe(bis=versteck + r * 30 * s, tempo=0.7)),
            Mit('w', Stehe(1.1, lambda d, u: Pose(kopf_vorn=True, mund_offen=(u * 7) % 2 < 1,
                                                  auge_zu=True, arm_v=-80, arm_v_x=10))),
            Setze(richtung=-r),
            Stehe(0.3, Pose(schreck=0.0, sorge=0.0, mund_offen=True)),
            Nebenbei(Mit('w', Erschrecke(0.3, 40)), Mit('w', Renne(zum='rand', tempo=3.4))),
            Warte(0.2),
            Renne(zum='rand', tempo=3.2, haltung=lambda p, sz: Pose(**{**p.__dict__, 'arm_v': -150,
                                                                       'arm_v_x': 22})),
        ]

    def schreck_ablauf(self):
        self.ball = None
        return self.schreck_alle()

    def treffer(self):
        x, y = self.kopf_punkt()
        self.ball = None
        self.schnee = True
        self.streue(x, y, 18, WEISS, tempo=170, dauer=0.8, r=(3, 7))

    def zeichne_vorn(self, p):
        if self.ball:
            zeichne_schneeball(p, *self.ball, 9 * self.s)
        if self.schnee and self.zeige_figur:
            # Schneehaube auf der Mütze
            x, y = self.x + self.richtung * 2 * self.s, self.y - self.hopp - 214 * self.s
            s = self.s
            p.save()
            p.translate(x, y)
            p.scale(s, s)
            flausch(p, [(-18, 6), (-8, 0), (4, -2), (14, 3), (-12, -6), (6, -9)], 9)
            p.restore()

    def grenzen_extra(self):
        if not self.ball:
            return QRectF()
        r = 14 * self.s
        return QRectF(self.ball[0] - r, self.ball[1] - r, 2 * r, 2 * r)
