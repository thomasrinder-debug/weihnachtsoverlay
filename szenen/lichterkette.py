import math
import random
from dataclasses import replace

from PyQt6.QtCore import QPointF, QRectF
from PyQt6.QtGui import QColor, QPainterPath

from zeichnen.figur import Pose, hand_punkt
from zeichnen.grundlagen import GOLD_HELL, WEISS, blinzeln, kreis, radial
from zeichnen.requisiten import zeichne_lichterkette, zeichne_steckdose, zeichne_stecker

from .basis import (Ducke, Erschrecke, Gehe, Jeweils, Nebenbei, Renne, Schaue, Setze, Stehe, Szene, Tu, Wandel,
                    Warte, Winke)

RAUCH = QColor(90, 90, 95, 200)
FUNKEN = [GOLD_HELL, WEISS, QColor('#8FD3FF')]


def tragen(pose, sz):
    return replace(pose, arm_v=-55, arm_v_x=14)


class Lichterkette(Szene):
    """Er zieht eine Lichterkette herein und steckt sie in eine Bodensteckdose. Die Lichter
    strahlen, er ist stolz, dann flackert es und es gibt einen Schlag: Funken, Rauch und
    ein rußgeschwärztes Gesicht. Er zieht den Stecker und schleicht verkohlt davon."""
    name, titel, reihenfolge = 'lichter', 'Lichterkette', 20

    def vorbereiten(self):
        self.dose_x = self.vom_rand(random.uniform(0.2, 0.26))
        self.steckt = False
        self.an = 0.0
        self.russ = 0.0
        self.blitz = False
        self.dose = 0.0             # Bodensteckdose klappt hoch (0..1)
        self.seite = self.richtung   # von dort kommt das Kabel

    def ablauf(self):
        r, s = self.richtung, self.s
        self.x = self.aussen(-r)

        def flackern(sz, u):
            sz.an = 1.0 if (u * 9) % 2 < 1 else 0.15

        def schlag(sz, u):
            sz.blitz = (u * 14) % 2 < 1
            sz.hopp = abs(math.sin(u * 40)) * 8 * sz.s
            sz.pose = Pose(kopf_vorn=True, schreck=1.0, arm_v=-120, arm_h=-110, arm_v_x=20, bein_v=-20,
                           bein_h=20, wipp=math.sin(u * 50) * 8)
            if random.random() < 0.5:
                sz.streue(sz.x + random.uniform(-40, 40) * s, sz.y - random.uniform(20, 220) * s, 2, FUNKEN,
                          tempo=260, dauer=0.4, r=(3, 6), art='stern')

        return [
            Nebenbei(Warte(1.0), Wandel(0.4, dose=1.0)),
            Gehe(bis=self.dose_x - r * 48 * s, haltung=tragen),
            Stehe(0.4, Pose(arm_v=-55, arm_v_x=14, auge_zu=False)),
            Ducke(0.3), Setze(steckt=True), Stehe(0.3, Pose(arm_v=40, arm_h=35, bein_v=-8, bein_h=8, hub=4)),
            Setze(stauchen=1.0),
            Jeweils(0.6, lambda sz, u: setattr(sz, 'an', min(1.0, u / 0.4))),
            Schaue(1.4),
            Winke(1.3),
            Jeweils(1.0, flackern),
            Setze(an=1.0, striche=True),
            Jeweils(1.0, schlag),
            Setze(blitz=False, hopp=0.0, striche=False, an=0.0, russ=1.0),
            Tu(lambda sz: sz.streue(sz.x, sz.y - 230 * s, 14, RAUCH, tempo=40, dauer=1.6, r=(6, 12),
                                    richtung=-math.pi / 2, streuung=0.6)),
            Stehe(2.0, lambda sz, u: Pose(kopf_vorn=True, sorge=0.2, auge_zu=0.5 < u < 0.7 or 1.4 < u < 1.6,
                                         wipp=-4, mund_offen=1.0 < u < 1.3)),
            Tu(lambda sz: sz.streue(sz.x + r * 14 * s, sz.y - 168 * s, 5, RAUCH, tempo=50, dauer=1.0, r=(3, 6),
                                    richtung=0 if r > 0 else math.pi, streuung=0.4)),
            Stehe(0.6, lambda sz, u: Pose(kopf_vorn=True, auge_zu=True, mund_offen=True)),
            Ducke(0.3), Setze(steckt=False, stauchen=1.0),
            Renne(zum='zurueck', tempo=1.4, haltung=tragen),
            Wandel(0.4, dose=0.0),
        ]

    def schreck_ablauf(self):
        if not self.figur_sichtbar():
            self.nebenbei.clear()
            return [Wandel(0.2, dose=0.0)]
        self.steckt, self.an, self.blitz, self.hopp = False, 0.0, False, 0.0
        self.nebenbei.clear()
        return [Setze(stauchen=1.0), Erschrecke(0.35, 50), Renne(zum='zurueck', tempo=3.4, haltung=tragen),
                Wandel(0.2, dose=0.0)]

    def weiter(self, dt):
        if self.russ:
            self.pose = replace(self.pose, russ=self.russ)

    def stecker_ort(self):
        if self.steckt:
            return self.dose_x, self.dose_y() - 30 * self.s, 0
        x, y = hand_punkt(self.x, self.y - self.hopp, self.s, self.richtung, self.pose, self.stauchen, self.neigung)
        return x, y + 4 * self.s, 0

    def dose_y(self):
        return self.boden + (1 - self.dose) * 30 * self.s

    def kabel(self):
        s, r = self.s, self.seite
        sx, sy, _ = self.stecker_ort()
        start = self.aussen(-r) - r * 200 * s
        pfad = QPainterPath()
        y = self.boden - 24 * s     # die Birnchen liegen auf dem Boden
        # immer von links nach rechts, damit die Birnchen nach unten hängen
        if start < sx:
            pfad.moveTo(start, y)
            pfad.lineTo(sx - r * 30 * s, y)
            pfad.quadTo(sx - r * 6 * s, y, sx, sy + 10 * s)
        else:
            pfad.moveTo(sx, sy + 10 * s)
            pfad.quadTo(sx - r * 6 * s, y, sx - r * 30 * s, y)
            pfad.lineTo(start, y)
        return pfad

    def zeichne_hinten(self, p):
        if self.blitz:
            gelb = QColor(255, 240, 120, 150)
            aus = QColor(255, 240, 120, 0)
            m = QPointF(self.x, self.y - 130 * self.s)
            p.setBrush(radial(m.x(), m.y(), 190 * self.s, gelb, aus))
            kreis(p, m.x(), m.y(), 190 * self.s)
        p.save()
        p.setClipRect(QRectF(self.geo.left(), self.geo.top(), self.geo.width(), self.boden - self.geo.top()))
        zeichne_steckdose(p, self.dose_x, self.dose_y(), self.s)
        p.restore()

    def zeichne_vorn(self, p):
        zeichne_lichterkette(p, self.kabel(), self.s, self.an, self.t, groesse=1.6)
        sx, sy, w = self.stecker_ort()
        zeichne_stecker(p, sx, sy, w, self.s)

    def grenzen_extra(self):
        s = self.s
        k = self.kabel().boundingRect().adjusted(-20 * s, -20 * s, 20 * s, 20 * s)
        k = k.united(QRectF(self.dose_x - 25 * s, self.boden - 40 * s, 50 * s, 40 * s))
        if self.blitz:
            k = k.united(QRectF(self.x - 190 * s, self.y - 320 * s, 380 * s, 380 * s))
        return k
