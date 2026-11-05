import math
import random

from PyQt6.QtCore import QPointF, QRectF
from PyQt6.QtGui import QTransform

from zeichnen.figur import Pose
from zeichnen.grundlagen import WEISS
from zeichnen.requisiten import zeichne_schneehaufen, zeichne_ski

from .basis import (Erschrecke, Jeweils, Nebenbei, Renne, Schritt, Setze, Springe, Stehe, Szene, Tu, Wandel,
                    Warte)

HOCKE = Pose(bein_v=-14, bein_h=12, arm_v=-35, arm_h=40, hub=8, wipp=-5)
KOPFUEBER = Pose(bein_v=-6, bein_h=6, arm_v=-10, arm_h=10)


class Abfahrt(Schritt):
    """Gleitet in der Hocke bis x=bis und folgt dabei der Höhe des Schanzenhügels."""

    def __init__(self, bis, tempo):
        self.bis, self.tempo = bis, tempo

    def beginn(self, sz):
        self.r = 1 if self.bis > sz.x else -1

    def weiter(self, sz, u, dt):
        sz.x += self.r * sz.tempo * self.tempo * dt
        sz.y = sz.boden - sz.huegel_hoehe(sz.x)
        sz.pose, sz.stauchen = HOCKE, 0.93
        if random.random() < 0.5:
            sz.streue(sz.x - self.r * 40 * sz.s, sz.y - 2 * sz.s, 1, WEISS, tempo=70, dauer=0.4, r=(2, 4))

    def fertig(self, sz, u):
        return (sz.x - self.bis) * self.r >= 0

    def ende(self, sz):
        sz.stauchen = 1.0


class Skisprung(Szene):
    """Er rast auf Skiern heran, springt flach über einen Schneehügel und landet kopfüber in
    einer Schneewehe. Die herausragenden Ski stellen sich brav parallel, als wäre alles
    gelungen; dann versinkt er gemächlich im Schnee."""
    name, titel, reihenfolge = 'skisprung', 'Skisprung', 32

    def vorbereiten(self):
        self.hx = self.vom_rand(random.uniform(0.12, 0.15))
        self.wx = self.vom_rand(random.uniform(0.27, 0.31))
        self.schnee = 0.0           # Hügel und Wehe wachsen am Anfang, schrumpfen am Ende
        self.ski = True
        self.kreuz = 0.0            # gekreuzte Ski nach der Landung

    def huegel_hoehe(self, x):
        b, h = 170 * self.s, 55 * self.s * self.schnee
        d = abs(x - self.hx) / (b / 2)
        return h * max(0.0, 1 - d * d) if d < 1 else 0.0

    def ablauf(self):
        r, s = self.richtung, self.s
        self.x = self.aussen(-r)
        oben = lambda sz: (sz.wx, sz.boden - 172 * s)  # noqa: E731
        return [
            Wandel(0.6, schnee=1.0),
            Abfahrt(self.hx, 2.4),
            Nebenbei(Wandel(0.7, neigung=180)),
            Springe(oben, 0.75, 45),
            Setze(neigung=180, pose=KOPFUEBER, stauchen=1.0, kreuz=1.0),
            Tu(lambda sz: sz.streue(sz.wx, sz.boden - 90 * s, 18, WEISS, tempo=200, dauer=0.8, r=(4, 8))),
            Stehe(0.8, lambda sz, u: Pose(bein_v=-6 + 6 * math.sin(u * 25), bein_h=6, arm_v=-10)),
            Wandel(0.6, kreuz=0.0),
            Stehe(1.6, KOPFUEBER),
            Stehe(0.6, lambda sz, u: Pose(bein_v=-6 + 10 * math.sin(u * 14), bein_h=6 - 10 * math.sin(u * 14))),
            Wandel(1.2, y=lambda sz: sz.boden + 120 * s),
            Setze(zeige_figur=False, ski=False),
            Wandel(0.6, schnee=0.0),
        ]

    def schreck_ablauf(self):
        self.nebenbei.clear()
        s = self.s
        if self.neigung > 90 and self.zeige_figur:
            return [Stehe(0.25, Pose(bein_v=-50, bein_h=50, arm_v=-10)),
                    Wandel(0.35, y=lambda sz: sz.boden + 150 * s),
                    Setze(zeige_figur=False, ski=False), Wandel(0.3, schnee=0.0)]
        neu = [Setze(neigung=0, ski=False, stauchen=1.0, y=self.boden)]
        if self.figur_sichtbar():
            neu += [Erschrecke(0.3, 45), Renne(zum='rand')]
        return neu + [Setze(zeige_figur=False), Wandel(0.3, schnee=0.0)]

    def trafo(self):
        tr = QTransform()
        tr.translate(self.x, self.y - self.hopp)
        tr.rotate(self.neigung * self.richtung)
        tr.scale(self.s * self.richtung * (2 - self.stauchen), self.s * self.stauchen)
        return tr

    def zeichne_hinten(self, p):
        zeichne_schneehaufen(p, self.hx, self.boden, 170 * self.s, 55 * self.s * self.schnee)

    def zeichne_vorn(self, p):
        s = self.s
        zeichne_schneehaufen(p, self.wx, self.boden, 230 * s, 105 * s * self.schnee)
        if self.ski and self.zeige_figur:
            p.save()
            p.setTransform(self.trafo(), True)
            h = self.pose.hub
            for winkel, kreuz in ((self.pose.bein_h, -1), (self.pose.bein_v, 1)):
                a = math.radians(winkel)
                fx, fy = -math.sin(a) * 60 + 6, -68 + h + math.cos(a) * 60 + 6
                zeichne_ski(p, fx, fy, winkel * 0.3 + kreuz * 28 * self.kreuz, 130)
            p.restore()

    def grenzen_extra(self):
        s = self.s
        k = QRectF(self.hx - 90 * s, self.boden - 70 * s, 180 * s, 70 * s)
        k = k.united(QRectF(self.wx - 120 * s, self.boden - 115 * s, 240 * s, 115 * s))
        if self.ski and self.zeige_figur:
            k = k.united(self.trafo().mapRect(QRectF(-110, -40, 220, 50)))
        return k
