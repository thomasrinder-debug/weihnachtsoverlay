import math
import random

from PyQt6.QtCore import QPointF, QRectF
from PyQt6.QtGui import QColor

from zeichnen.figur import Pose
from zeichnen.figuren import WichtelSteif
from zeichnen.grundlagen import WEISS, blinzeln
from zeichnen.requisiten import zeichne_eisstueck, zeichne_eiszapfen

from .basis import (Erschrecke, Falle, Gehe, Jeweils, Mit, Nebenbei, Renne, Schritt, Setze, Stehe, Szene, Tu,
                    Wandel, Warte, muetze_richten)

LANG = 150          # Länge des großen Zapfens in Einheiten
GLANZ = [WEISS, QColor('#CFEFFF')]


def umklammern(d, u):
    return Pose(arm_v=-70 + 22 * math.sin(u * 16), arm_h=-55, bein_v=-55, bein_h=25, kopf_vorn=False,
                auge_zu=blinzeln(d.t), wipp=math.sin(u * 16) * 2)


def sitzen(d, u):
    return Pose(arm_v=-70 + 22 * math.sin(u * 14), arm_h=-60, bein_v=-80, bein_h=-70, auge_zu=True)


class SeitwaertsWeg(Schritt):
    """Wichtel und Zapfen rutschen gemeinsam waagerecht zum nächsten Rand hinaus."""

    def beginn(self, sz):
        self.seite = -1 if sz.zx - sz.geo.left() < sz.geo.right() - sz.zx else 1

    def weiter(self, sz, u, dt):
        v = self.seite * 1600 * sz.s * min(1.0, u * 4 + 0.2) * dt
        sz.zx += v
        sz.w.x += v

    def fertig(self, sz, u):
        return not sz.grenzen().intersects(sz.geo)


class Eiszapfen(Szene):
    """Ein Wichtel poliert kopfüber umklammert einen Eiszapfen am oberen Rand, rutscht hinunter,
    der Zapfen bricht und er saust mit der Spitze nach unten in die Ecke. Dort poliert er das
    Bruchstück ungerührt weiter und richtet würdevoll seine abgeknickte Mützenspitze."""
    name, titel, reihenfolge = 'eiszapfen', 'Eiszapfen', 30

    def vorbereiten(self):
        self.zeige_figur = False
        r = self.richtung
        self.zx = self.vom_rand(random.uniform(0.04, 0.06))
        self.zy = -LANG * self.s          # Zapfen fährt von oben herein
        self.ab = 0.0
        self.haengt = True
        self.stueck = False
        self.w = self.dazu('w', WichtelSteif, groesse=0.55, knick=1.0)
        self.w.richtung = -r
        self.w.x = self.zx + r * 13 * self.s
        self.w.y = self.oben - 40 * self.s

    def fuss_y(self, anteil):
        return self.oben + self.zy + LANG * self.s * anteil

    def ablauf(self):
        s = self.s
        return [
            Wandel(0.8, zy=0.0),
            Mit('w', Setze(pose=Pose(arm_v=-70, arm_h=-55, bein_v=-55, bein_h=25))),
            Mit('w', Wandel(0.9, y=lambda d: d.sz.fuss_y(0.75))),
            Mit('w', Stehe(2.2, umklammern)),
            Tu(lambda sz: sz.glitzern()),
            Mit('w', Stehe(0.6, lambda d, u: Pose(arm_v=-70, arm_h=-55, bein_v=-55, bein_h=25, kopf_vorn=True,
                                                  blick_y=0.8, sorge=0.6))),
            Mit('w', Wandel(0.5, y=lambda d: d.sz.fuss_y(1.25))),
            Tu(lambda sz: sz.brechen()),
            Mit('w', Stehe(0.25, Pose(arm_v=-70, arm_h=-55, bein_v=-55, bein_h=25, kopf_vorn=True, schreck=1.0))),
            Mit('w', Setze(striche=False)),
            Mit('w', Falle(lambda d: d.y >= d.boden)),
            Tu(lambda sz: sz.landen()),
            Mit('w', Stehe(2.0, sitzen)),
            Tu(lambda sz: sz.glitzern()),
            Mit('w', Setze(hopp=0.0)),
            *muetze_richten('w'),
            Nebenbei(Wandel(0.8, zy=-LANG * s * 0.6)),
            Mit('w', Gehe(bis=self.aussen(-self.richtung), tempo=0.8,
                          haltung=lambda p, d: Pose(bein_v=p.bein_v, bein_h=p.bein_h, hub=p.hub, arm_v=-70,
                                                    arm_h=-60, auge_zu=p.auge_zu))),
            Warte(0.3),
        ]

    def schreck_ablauf(self):
        self.nebenbei.clear()
        w = self.w
        if self.haengt and w.y < self.boden - 60 * self.s:
            return [Mit('w', Setze(striche=True, pose=Pose(arm_v=-70, arm_h=-55, bein_v=-55, bein_h=25,
                                                           kopf_vorn=True, schreck=1.0))),
                    Warte(0.2), SeitwaertsWeg()]
        self.haengt = False
        return [Mit('w', Setze(hopp=0.0)), Nebenbei(Wandel(0.5, zy=-LANG * self.s * 1.1)),
                Mit('w', Erschrecke(0.3, 40)), Mit('w', Setze(knick=1.0)), Mit('w', Renne(zum='rand')),
                Mit('w', Setze(zeige_figur=False)), Warte(0.1)]

    def glitzern(self):
        x, y = self.zx, self.oben + self.zy + LANG * self.s * 0.5
        if self.stueck:
            q = self.w.trafo().map(QPointF(18, -80))
            x, y = q.x(), q.y()
        self.streue(x, y, 8, GLANZ, tempo=60, dauer=0.8, r=(3, 5), art='stern')

    def brechen(self):
        self.ab, self.stueck = 0.45, True
        self.w.striche = True
        self.streue(self.zx, self.oben + LANG * self.s * 0.55, 10, GLANZ, tempo=140, dauer=0.5, r=(2, 4))

    def landen(self):
        w = self.w
        w.y = self.boden
        w.hopp = -38 * w.s
        self.haengt = False
        self.streue(w.x, self.boden - 6 * self.s, 16, WEISS, tempo=150, dauer=0.7, r=(3, 7))

    def zeichne_hinten(self, p):
        s = self.s
        for dx, laenge, b in ((-22, 60, 12), (26, 85, 14), (48, 40, 9)):
            p.save()
            p.translate(self.zx + dx * s * self.richtung, self.oben + self.zy)
            p.scale(s, s)
            zeichne_eiszapfen(p, laenge, b)
            p.restore()
        p.save()
        p.translate(self.zx, self.oben + self.zy)
        p.scale(s, s)
        zeichne_eiszapfen(p, LANG, 22, self.ab)
        p.restore()

    def zeichne_vorn(self, p):
        w = self.w
        if self.stueck and w.zeige_figur:
            faellt = not self.haengt and w.hopp == 0 and w.y < self.boden - 1
            p.save()
            p.setTransform(w.trafo(), True)
            p.translate(*((10, -150) if faellt else (26, -72)))
            p.rotate(0 if faellt else 70)
            zeichne_eisstueck(p, 64, 11)
            p.restore()

    def grenzen_extra(self):
        s = self.s
        k = QRectF(self.zx - 70 * s, self.oben, 140 * s, max(1.0, LANG * s + self.zy + 4 * s))
        if self.stueck:
            k = k.united(self.w.kasten().adjusted(-40 * s, -60 * s, 40 * s, 0))
        return k
