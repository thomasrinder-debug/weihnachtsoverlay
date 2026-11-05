import math
import random

from PyQt6.QtCore import QRectF
from PyQt6.QtGui import QColor

from zeichnen.figur import Pose, geh_pose, renn_pose
from zeichnen.grundlagen import GOLD_HELL, ROT, WEISS, GRUEN
from zeichnen.requisiten import zeichne_geschenk

from .basis import Erschrecke, Gehe, Renne, Schritt, Setze, Stehe, Szene

PAKETE = [(70, 46, QColor('#2A6FD6')), (60, 40, ROT), (64, 34, GRUEN), (48, 36, QColor('#7B3FB8')),
          (40, 30, QColor('#E3A928')), (30, 26, ROT)]


def hoch(pose, sz):
    p = Pose(**{**pose.__dict__})
    p.arm_v, p.arm_h, p.arm_v_x, p.sack = -172, -168, 8, False
    return p


class Balancieren(Schritt):
    """Der Turm neigt sich immer stärker, er rennt unter ihm hin und her, um ihn zu halten."""

    def __init__(self, dauer):
        self.dauer = dauer

    def weiter(self, sz, u, dt):
        a = 6 + 20 * (u / self.dauer)
        sz.kipp = a * math.sin(u * 3.2)
        v = sz.kipp / 26 * sz.tempo * 1.7
        if abs(v) > 1:
            sz.richtung = 1 if v > 0 else -1
        sz.x += v * dt
        sz.phase += abs(v) * dt / (sz.s * 34)
        sz.pose = hoch(renn_pose(sz.phase) if abs(v) > sz.tempo * 0.5 else geh_pose(sz.phase, sz.t), sz)
        sz.pose.kopf_vorn, sz.pose.sorge, sz.pose.blick_y = True, 1.0, -1.0


class Geschenketurm(Szene):
    """Er balanciert einen hohen Stapel Geschenke über dem Kopf. Der Turm schwankt immer
    stärker, er rennt unter ihm hin und her, bis der Turm endgültig kippt und er ihm
    hinterher aus dem Bild stolpert."""
    name, titel, reihenfolge = 'turm', 'Geschenketurm', 41

    def vorbereiten(self):
        self.kipp = 0.0          # Neigung des Turms in Grad (Weltrichtung, + nach rechts)

    def ablauf(self):
        r = self.richtung
        self.x = self.aussen(-r)
        return [
            Gehe(bis=self.vom_rand(random.uniform(0.16, 0.2)), tempo=0.8, haltung=hoch),
            Stehe(0.6, lambda sz, u: hoch(Pose(kopf_vorn=True, blick_y=-1), sz)),
            Balancieren(5.0),
            Setze(kipp=lambda sz: sz.naechster_rand() * 30),
            Renne(zum='rand', tempo=2.4, haltung=lambda p, sz: hoch(p, sz)),
        ]

    def schreck_ablauf(self):
        if not self.figur_sichtbar():
            return []
        return [Erschrecke(0.3, 40), Setze(kipp=lambda sz: sz.naechster_rand() * 25),
                Renne(zum='rand', haltung=lambda p, sz: hoch(p, sz))]

    def weiter(self, dt):
        if self.erschreckt:
            self.kipp += math.sin(self.t * 30) * 2

    def zeichne_vorn(self, p):
        if not self.zeige_figur:
            return
        s = self.s
        p.save()
        p.translate(self.x + self.richtung * 12 * s, self.y - self.hopp - 248 * s)
        p.scale(s, s)
        y = 0.0
        for i, (b, h, farbe) in enumerate(PAKETE):
            p.save()
            p.rotate(self.kipp * (0.25 + 0.15 * i))
            p.translate(math.sin(math.radians(self.kipp)) * -y * 0.4, -y)
            zeichne_geschenk(p, b, h, farbe, GOLD_HELL if i % 2 else WEISS, muster=False)
            p.restore()
            y += h + 14
        p.restore()

    def grenzen_extra(self):
        s = self.s
        return QRectF(self.x - 280 * s, self.y - 600 * s, 560 * s, 400 * s)
