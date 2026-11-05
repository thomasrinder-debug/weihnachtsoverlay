import math
import random

from PyQt6.QtCore import QRectF

from zeichnen.figur import Pose
from zeichnen.figuren import WichtelSteif
from zeichnen.grundlagen import WEISS, blinzeln
from zeichnen.requisiten import zeichne_rodel

from .basis import Jeweils, Mit, Schritt, Setze, Stehe, Szene, Tu, Wandel, Warte, muetze_richten

SITZ = Pose(bein_v=-82, bein_h=-74, arm_v=-55, arm_h=-50, hub=14, mund_offen=True)


class Kante(Schritt):
    """Bewegt den Wichtel an der Seitenkante senkrecht: tempo < 0 nach oben, Ziel bis(szene)."""

    def __init__(self, tempo, bis, pose=None, beschleunigen=False):
        self.tempo, self.bis, self.pose, self.beschl = tempo, bis, pose, beschleunigen

    def beginn(self, sz):
        self.ziel = self.bis(sz)

    def weiter(self, sz, u, dt):
        w = sz.w
        v = self.tempo * sz.s * (1 + 2.5 * u if self.beschl else 1)
        w.y += v * dt
        w.phase += abs(v) * dt / (w.s * 38)
        if self.pose:
            w.pose = self.pose(w, u)
        if self.beschl and random.random() < 0.6:
            sz.streue(w.x, w.y, 1, WEISS, tempo=50, dauer=0.5, r=(2, 5))

    def fertig(self, sz, u):
        return (sz.w.y - self.ziel) * self.tempo >= 0


class Rodeln(Szene):
    """Ein Wichtel rodelt die Seitenkante senkrecht hinunter. Unten steigt er ab, richtet
    seine abgeknickte Mützenspitze, klappt den Schlitten hoch und marschiert ihn wie eine
    Leiter vor sich herschiebend die Kante wieder hinauf."""
    name, titel, reihenfolge = 'rodeln', 'Senkrecht rodeln', 31

    def vorbereiten(self):
        self.zeige_figur = False
        self.seite = random.choice((-1, 1))          # -1 linker, +1 rechter Rand
        kante = self.geo.left() if self.seite < 0 else self.geo.right()
        self.w = self.dazu('w', WichtelSteif, groesse=0.55, knick=1.0)
        self.w.x = kante
        self.w.richtung = self.seite                 # mit neigung 90: Blick nach unten, Kante ist der Boden
        self.w.neigung = 90 * -self.seite * self.seite
        self.w.y = self.oben - 80 * self.s
        self.rodel_an = True                         # Rodel unter dem Wichtel
        self.leiter = False                          # Rodel vor ihm, Spitze nach oben

    def kante(self):
        return self.geo.left() if self.seite < 0 else self.geo.right()

    def drehung(self, seitlich):
        """seitlich: an der Kante (Kopf ins Bild); sonst aufrecht am Boden."""
        w = self.w
        if seitlich == 'hoch':
            w.richtung, w.neigung = self.seite, -90
        elif seitlich:
            w.richtung, w.neigung = -self.seite, 90
        else:
            w.richtung, w.neigung = self.seite, 0

    def ablauf(self):
        s = self.s
        unten = lambda sz: sz.boden - 70 * s  # noqa: E731
        gehen = lambda d, u: Pose(bein_v=-22 * math.sin(d.phase), bein_h=22 * math.sin(d.phase),  # noqa: E731
                                  arm_v=-95, arm_h=-90, arm_v_x=12, hub=-abs(math.cos(d.phase)) * 3,
                                  auge_zu=blinzeln(d.t))
        return [
            Tu(lambda sz: sz.drehung(True)),
            Mit('w', Setze(pose=SITZ)),
            Kante(420, unten, lambda d, u: SITZ, beschleunigen=True),
            Tu(lambda sz: sz.ankommen()),
            Mit('w', Stehe(0.6, Pose(kopf_vorn=True, auge_zu=True))),
            Mit('w', Stehe(0.7, lambda d, u: Pose(kopf_vorn=True, sorge=0.6, blick_x=math.sin(u * 5)))),
            *muetze_richten('w'),
            Mit('w', Stehe(0.4, Pose(arm_v=-90, arm_h=-90, arm_v_x=12))),
            Tu(lambda sz: sz.hochklappen()),
            Warte(0.4),
            Tu(lambda sz: sz.drehung('hoch')),
            Mit('w', Setze(y=lambda d: d.boden - 60 * d.sz.s, hopp=0.0, x=lambda d: d.sz.kante())),
            Kante(-230, lambda sz: sz.oben - 160 * s, gehen),
        ]

    def schreck_ablauf(self):
        self.nebenbei.clear()
        w = self.w
        if w.y < self.oben - 100 * self.s:
            return []
        hektisch = lambda d, u: Pose(bein_v=-40 * math.sin(u * 30), bein_h=40 * math.sin(u * 30),  # noqa: E731
                                     arm_v=-150, arm_h=-140, kopf_vorn=True, schreck=1.0)
        return [Mit('w', Setze(striche=True, knick=1.0, x=self.kante())), Tu(lambda sz: sz.drehung('hoch')),
                Setze(rodel_an=False),
                Mit('w', Setze(hopp=0.0)), Kante(-1500, lambda sz: sz.oben - 180 * self.s, hektisch)]

    def ankommen(self):
        w = self.w
        self.streue(w.x, w.y, 16, WEISS, tempo=160, dauer=0.7, r=(3, 7))
        self.rodel_an = False
        self.drehung(False)
        w.x = (self.geo.left() if self.seite < 0 else self.geo.right()) - self.seite * 70 * self.s
        w.y = self.boden
        w.richtung = self.seite
        self.leiter = 'liegt'

    def hochklappen(self):
        self.leiter = True

    def zeichne_hinten(self, p):
        w, s = self.w, self.s
        kante = self.geo.left() if self.seite < 0 else self.geo.right()
        if self.rodel_an:
            p.save()
            p.setTransform(w.trafo(), True)
            p.scale(1 / 0.55 * 0.62, 1 / 0.55 * 0.62)
            zeichne_rodel(p)
            p.restore()
        elif self.leiter:
            p.save()
            if self.leiter == 'liegt':
                p.translate(kante - self.seite * 30 * s, self.boden)
                p.scale(s * 0.62 * -self.seite, s * 0.62)
            else:
                # aufgestellt an der Kante, oberhalb des Wichtels
                p.translate(kante, w.y - 30 * s - 52 * 0.62 * s)
                p.rotate(-90)
                p.scale(s * 0.62, s * 0.62 * self.seite)
            zeichne_rodel(p)
            p.restore()

    def grenzen_extra(self):
        w, s = self.w, self.s
        if not w.zeige_figur:
            return QRectF()
        kante = self.geo.left() if self.seite < 0 else self.geo.right()
        return QRectF(kante - 160 * s, w.y - 220 * s, 320 * s, 330 * s)
