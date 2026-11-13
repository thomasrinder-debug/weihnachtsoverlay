"""Gemeinsame Bausteine der Wichtelwerkstatt (Szenen werk_*)."""
import math
import random

from PyQt6.QtCore import QPointF
from PyQt6.QtGui import QColor, QTransform

from zeichnen.figur import Pose
from zeichnen.grundlagen import WEISS

from .basis import Stehe

STAUB = (QColor(235, 225, 205, 210), QColor(200, 190, 170, 200), WEISS)
SPAENE = (QColor('#E3B47E'), QColor('#C98F55'), QColor('#F2D3A2'))


def blick_pose(sz, u):
    """Trockener Blick ins Publikum mit zweimal Blinzeln."""
    return Pose(kopf_vorn=True, auge_zu=0.25 < u < 0.4 or 0.75 < u < 0.9, sorge=0.2)


class Blick(Stehe):
    def __init__(self, dauer=1.1, pose=None):
        super().__init__(dauer, pose or blick_pose)


def figur_trafo(sz):
    """Transformation der Weihnachtsmann-Zeichnung (Einheiten -> Bildschirm)."""
    tr = QTransform()
    tr.translate(sz.x, sz.y - sz.hopp)
    tr.rotate(sz.neigung * sz.richtung)
    tr.scale(sz.s * sz.richtung * (2 - sz.stauchen), sz.s * sz.stauchen)
    return tr


def welt(sz, lx, ly):
    q = figur_trafo(sz).map(QPointF(lx, ly))
    return q.x(), q.y()


def hand_trafo(sz, darsteller=False, hinten=False):
    """Transformation in die vordere Hand: Ursprung in der Hand, +y zeigt den Arm entlang weiter.
    darsteller=True für einen Wichtel (Darsteller), sonst der Weihnachtsmann."""
    pose = sz.pose
    if darsteller:
        tr = sz.trafo()
        x, y, lg = (-8 if hinten else 8), -96 + pose.hub, 35
    else:
        tr = figur_trafo(sz)
        x, y, lg = (-10 if hinten else pose.arm_v_x), -140 + pose.hub, 56
    a = QTransform()
    a.translate(x, y)
    a.rotate(pose.arm_h if hinten else pose.arm_v)
    a.translate(0, lg)
    return a * tr


def hand(sz, darsteller=False, hinten=False):
    q = hand_trafo(sz, darsteller, hinten).map(QPointF(0, 0))
    return q.x(), q.y()


def verpuffen(sz, x, y, breite, hoehe, anzahl=18):
    """Requisit verschwindet in einer Staubwolke."""
    for _ in range(anzahl):
        sz.streue(x + random.uniform(-0.5, 0.5) * breite, y - random.uniform(0, 1) * hoehe, 1, STAUB,
                  tempo=90, dauer=0.6, r=(8, 16))


def schweiss(sz, x, y):
    sz.streue(x, y, 1, QColor(160, 210, 255, 220), tempo=60, dauer=0.5, r=(2, 3.5), schwer=True,
              richtung=-math.pi / 2, streuung=1.0)


def greife(sz, zx, zy, neigung=None):
    """Der Weihnachtsmann greift mit der vorderen Hand nach (zx, zy): sucht den Armwinkel für
    die Höhe und rückt ihn waagerecht zurecht. Die übrige Pose bleibt."""
    if neigung is not None:
        sz.neigung = neigung
    lo, hi = -180.0, 0.0
    for _ in range(18):
        mitte = (lo + hi) / 2
        sz.pose.arm_v = mitte
        if hand(sz)[1] < zy:
            lo = mitte
        else:
            hi = mitte
    hx, _ = hand(sz)
    sz.x += zx - hx


def haenge_an(sz, zx, zy, darsteller=False):
    """Verschiebt die Figur (x und hopp), bis ihre vordere Hand bei (zx, zy) ist."""
    hx, hy = hand(sz, darsteller)
    sz.x += zx - hx
    sz.hopp -= zy - hy
