"""Gemeinsames für die Szenen der Weihnachtsbäckerei (back_*.py)."""
import math

from PyQt6.QtCore import QPointF

from zeichnen.figur import Pose, hand_punkt

from .basis import Schritt, Stehe


def publikum(dauer=1.1, **merkmale):
    """Trockener Blick ins Publikum mit zweimal Blinzeln. merkmale: weitere Pose-Werte."""
    def pose(sz, u):
        zu = 0.35 < u < 0.47 or 0.62 < u < 0.74
        return Pose(kopf_vorn=True, auge_zu=zu, **merkmale)
    return Stehe(dauer, pose)


def zittern(t, frequenz=40.0, staerke=1.0):
    return math.sin(t * frequenz) * staerke


def hand(sz):
    """Weltlage des vorderen Fäustlings des Weihnachtsmanns."""
    return hand_punkt(sz.x, sz.y - sz.hopp, sz.s, sz.richtung, sz.pose, sz.stauchen, sz.neigung)


def darsteller_punkt(d, x, y):
    q = d.trafo().map(QPointF(x, y))
    return q.x(), q.y()


class Flug(Schritt):
    """Fliegt ein Requisit (Liste [x, y, winkel]) im Bogen nach ziel(sz) -> (x, y)."""

    def __init__(self, attr, ziel, dauer=0.5, hoehe=80, drehung=0.0):
        self.attr, self.ziel, self.dauer, self.hoehe, self.drehung = attr, ziel, dauer, hoehe, drehung

    def beginn(self, sz):
        self.x0, self.y0, self.w0 = getattr(sz, self.attr)
        self.x1, self.y1 = self.ziel(sz)

    def weiter(self, sz, u, dt):
        f = min(1.0, u / self.dauer)
        getattr(sz, self.attr)[:] = [self.x0 + (self.x1 - self.x0) * f,
                                     self.y0 + (self.y1 - self.y0) * f - self.hoehe * sz.s * 4 * f * (1 - f),
                                     self.w0 + self.drehung * f]


def figur_trafo(sz):
    """Abbildung der Zeichen-Einheiten des Weihnachtsmanns in die Welt (wie zeichnen.figur.figur)."""
    from PyQt6.QtGui import QTransform
    tr = QTransform()
    tr.translate(sz.x, sz.y - sz.hopp)
    tr.rotate(sz.neigung * sz.richtung)
    tr.scale(sz.s * sz.richtung * (2 - sz.stauchen), sz.s * sz.stauchen)
    return tr


def kopf(sz, dx=6, dy=-188):
    """Weltlage eines Punkts am Kopf des Weihnachtsmanns (Standard: Kopfmitte von vorn)."""
    q = figur_trafo(sz).map(QPointF(dx, dy + sz.pose.hub))
    return q.x(), q.y()
