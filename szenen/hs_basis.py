"""Gemeinsames für die Hörsaal-Szenen (hs_*.py): Publikumsblick des Weihnachtsmanns,
Hinfallen und Aufrappeln, Punkte auf seiner Figur."""
import math

from PyQt6.QtCore import QPointF

from zeichnen.figur import Pose
from zeichnen.grundlagen import blinzeln
from zeichnen.hoersaal import figur_trafo

from .basis import Schritt, Stehe


def auf_figur(sz, x, y):
    """Weltpunkt eines Punkts der Weihnachtsmann-Zeichnung (Einheiten, Blick nach rechts)."""
    q = figur_trafo(sz).map(QPointF(x, y))
    return q.x(), q.y()


class Publikumsblick(Stehe):
    """Trockener Blick ins Publikum: zweimal blinzeln, kein Wort."""

    def __init__(self, dauer=1.0, **extra):
        self.extra = extra
        super().__init__(dauer, self.blick)

    def blick(self, sz, u):
        zu = 0.25 < u < 0.37 or 0.5 < u < 0.62
        return Pose(kopf_vorn=True, auge_zu=zu, blick_y=0.1, **self.extra)


class Plumps(Schritt):
    """Fällt in 'dauer' Sekunden um: neigung -90 auf den Rücken, +80 aufs Gesicht.
    Beschleunigt wie ein umfallendes Brett, prallt kurz nach."""

    def __init__(self, neigung=-90, dauer=0.35, hoehe=46, pose=None):
        self.ziel, self.dauer_f, self.hoehe, self.pose = neigung, dauer, hoehe, pose
        self.dauer = dauer + 0.18

    def beginn(self, sz):
        self.n0, self.h0 = sz.neigung, sz.hopp
        sz.striche = False

    def weiter(self, sz, u, dt):
        f = min(1.0, u / self.dauer_f)
        f = f * f
        nach = 0.0
        if u > self.dauer_f:
            nach = math.sin(min(1.0, (u - self.dauer_f) / 0.18) * math.pi) * 0.06
        sz.neigung = self.n0 + (self.ziel - self.n0) * (f - nach)
        sz.hopp = self.h0 + (self.hoehe * sz.s - self.h0) * f
        if self.pose is not None:
            sz.pose = self.pose(sz, u) if callable(self.pose) else self.pose

    def ende(self, sz):
        sz.neigung = self.ziel


def rueckenlage(sz, u):
    """Liegt steif auf dem Rücken, die Beine zucken."""
    z = math.sin(u * 22) * 6 if u < 0.8 else 0
    return Pose(sack=False, arm_v=-60, arm_h=-40, bein_v=-20 + z, bein_h=10 - z, schreck=0.5, kopf_vorn=False,
                auge_zu=blinzeln(sz.t), mund_offen=True)
