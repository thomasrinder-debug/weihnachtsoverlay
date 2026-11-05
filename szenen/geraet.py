"""Gemeinsames der Computer-Szenen des Professors (drucker, kuehlen, mauszeiger).
GeraetSzene hat keinen name und erscheint deshalb nicht im Menü."""
import math
import random

from PyQt6.QtCore import QPointF, QRectF
from PyQt6.QtGui import QColor

from zeichnen.grundlagen import KEIN_STIFT, kreis, radial
from zeichnen.professor import ARM_LAENGE, HANDSCHUH, HANDSCHUH_DUNKEL, SCHULTER_Y

from .basis import Schritt
from .professor import ProfSzene

QUALM_GRAU = [QColor(150, 150, 160, 210), QColor(115, 112, 118, 200), QColor(190, 190, 198, 200)]
HAUT = QColor('#F2C4A8')
HAUT_DUNKEL = QColor('#D4957A')


def qualm(sz, x, y, dichte=0.25, groesse=1.0):
    """Für Jeweils: steigender Qualm aus einem Gerät."""
    if random.random() < dichte:
        sz.streue(x + random.uniform(-6, 6) * sz.s, y, 1, QUALM_GRAU, tempo=85, dauer=1.5,
                  r=(7 * groesse, 17 * groesse), richtung=-math.pi / 2, streuung=0.4)


def zeichne_wolke(p, x, y, r, t=0.0, farbe=QColor(120, 118, 124, 225), saat=0):
    """Dichte, runde Qualmwolke aus Kugeln, Mitte (x, y), Radius r (Weltkoordinaten)."""
    if r <= 0:
        return
    p.setPen(KEIN_STIFT)
    z = random.Random(saat)
    kugeln = []
    for k in range(9):
        w = k / 9 * 2 * math.pi + z.uniform(-0.3, 0.3)
        d = r * z.uniform(0.35, 0.6)
        kr = r * z.uniform(0.42, 0.6) * (1 + 0.06 * math.sin(t * 5 + k))
        kugeln.append((x + math.cos(w) * d * 1.25, y + math.sin(w) * d * 0.8, kr))
    kugeln.append((x, y, r * 0.65))
    for kx, ky, kr in kugeln:
        p.setBrush(radial(kx - kr * 0.3, ky - kr * 0.4, kr * 1.3, farbe.lighter(135), farbe.darker(115)))
        kreis(p, kx, ky, kr)


def nackte_hand(p, sz):
    """Malt über den vorderen Gummihandschuh des Professors eine bloße Hand mit Fingern."""
    pose = sz.pose
    p.save()
    p.setTransform(sz.trafo(), True)
    p.translate(pose.arm_v_x, SCHULTER_Y + pose.hub)
    p.rotate(pose.arm_v)
    p.setPen(KEIN_STIFT)
    p.setBrush(radial(-2, ARM_LAENGE - 4, 12, HAUT.lighter(110), HAUT_DUNKEL))
    p.drawRoundedRect(QRectF(-7, 37.5, 14, 9), 3, 3)
    for k in range(4):
        p.drawRoundedRect(QRectF(-6 + k * 3.4, ARM_LAENGE - 2, 3, 10 + 2 * math.sin(sz.t * 20 + k)), 1.5, 1.5)
    kreis(p, 0, ARM_LAENGE - 3, 8)
    p.drawEllipse(QPointF(7, ARM_LAENGE - 8), 3.4, 5)
    p.restore()


def zeichne_handschuh_leer(p, x, y, s, winkel=0.0):
    """Leerer gelber Gummihandschuh mit gespreizten Fingern, Mitte bei (x, y)."""
    p.save()
    p.translate(x, y)
    p.rotate(winkel)
    p.scale(s, s)
    p.setPen(KEIN_STIFT)
    p.setBrush(radial(-2, -2, 12, HANDSCHUH.lighter(125), HANDSCHUH_DUNKEL))
    for k in range(4):
        p.save()
        p.rotate(-50 + k * 30)
        p.drawRoundedRect(QRectF(-2, -17, 4.4, 11), 2, 2)
        p.restore()
    kreis(p, 0, 0, 8)
    p.drawEllipse(QPointF(8, 1), 3.4, 5)
    p.drawRoundedRect(QRectF(-7, 5, 14, 9), 3, 3)
    p.setBrush(QColor(255, 255, 255, 80))
    kreis(p, -3, -3, 2)
    p.restore()


class GeraetSzene(ProfSzene):
    """Gemeinsames der Computer-Szenen: wackel klingt nach einem Stoß ab."""
    wackel = 0.0

    def weiter(self, dt):
        super().weiter(dt)
        self.wackel = max(0.0, self.wackel - dt * 2.2)

    def zitter(self):
        return math.sin(self.t * 60) * 3 * self.wackel * self.s


class Solange(Schritt):
    """Wie Jeweils, aber ohne feste Dauer: ruft funktion(sz, u), bis bis(sz) wahr ist."""

    def __init__(self, funktion, bis):
        self.funktion, self.bis = funktion, bis

    def weiter(self, sz, u, dt):
        self.funktion(sz, u)

    def fertig(self, sz, u):
        return self.bis(sz)
