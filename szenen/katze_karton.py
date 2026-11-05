import math
import random

from PyQt6.QtCore import QRectF
from PyQt6.QtGui import QColor

from zeichnen.figur import Pose
from zeichnen.figuren import Katze
from zeichnen.grundlagen import GOLD_HELL, blinzeln
from zeichnen.requisiten import zeichne_geschenk

from .basis import Erschrecke, Gehe, Jeweils, Mit, Renne, Schaue, Setze, Springe, Stehe, Szene, Tu, Wandel, Warte

B, H = 84, 62        # Karton in Einheiten
GRUEN_KARTON = QColor('#2E9A52')


class KatzeKarton(Szene):
    """Eine Katze entdeckt ein offenes Geschenk und springt hinein, nur Ohren und Augen schauen
    heraus. Der Weihnachtsmann kommt, legt nichtsahnend den Deckel auf, die Kiste zappelt,
    der Deckel fliegt hoch und die Katze landet auf seiner Mütze. Mit ihr zieht er weiter."""
    name, titel, reihenfolge = 'katzekarton', 'Katze im Karton', 47

    def vorbereiten(self):
        r = self.richtung
        self.bx = self.vom_rand(random.uniform(0.2, 0.24))
        self.deckel = None             # None: Deckel trägt er; sonst (dx, dy, dreh) auf der Kiste
        self.wackel = 0.0
        self.karton = 0.0              # Kiste rückt vom Rand herein (0..1)
        self.k = self.dazu('k', Katze, groesse=0.55)
        self.k.richtung = r
        self.k.x = self.aussen(-r)
        self.auf_kopf = False
        self.zeige_figur = False

    def kiste_x(self):
        return self.bx

    def ablauf(self):
        r, s = self.richtung, self.s
        self.x = self.aussen(-r)
        drin = lambda d: self.boden - 24 * s  # noqa: E731
        return [
            Wandel(0.5, karton=1.0),
            Mit('k', Gehe(bis=self.bx - r * 80 * s, tempo=0.7)),
            Mit('k', Stehe(0.9, lambda d, u: Pose(kopf_vorn=True, blick_x=0.8, blick_y=0.5, auge_zu=blinzeln(d.t)))),
            Mit('k', Springe(lambda d: (d.sz.bx - r * 30 * s, d.sz.boden - 24 * s), 0.5, 90)),
            Mit('k', Setze(sitzt=True, pose=Pose(kopf_vorn=True), y=drin)),
            Mit('k', Stehe(1.2, lambda d, u: Pose(kopf_vorn=True, auge_zu=0.5 < u < 0.65))),
            Setze(zeige_figur=True),
            Gehe(bis=self.bx - r * 120 * s),
            Schaue(0.6),
            Stehe(0.6, Pose(arm_v=-90, arm_v_x=14)),
            Setze(deckel=(0.0, 0.0, 0.0)),
            Mit('k', Setze(zeige_figur=False)),
            Stehe(0.6, Pose(kopf_vorn=True, auge_zu=True)),
            Jeweils(1.0, lambda sz, u: setattr(sz, 'wackel', math.sin(u * 45) * 8)),
            Setze(wackel=0.0),
            Stehe(0.4, Pose(kopf_vorn=True, schreck=0.8, blick_x=1)),
            Tu(lambda sz: sz.aufspringen()),
            Mit('k', Springe(lambda d: (d.sz.x + r * 6 * s, d.sz.y - 238 * s), 0.6, 80)),
            Setze(auf_kopf=True),
            Stehe(1.2, lambda sz, u: Pose(kopf_vorn=True, sorge=0.7, blick_y=-1, auge_zu=0.6 < u < 0.75)),
            Stehe(0.8, Pose(kopf_vorn=True, auge_zu=True, mund_offen=True)),
            Gehe(bis=self.aussen(-r), tempo=0.9),
            Wandel(0.4, karton=0.0),
        ]

    def schreck_ablauf(self):
        self.nebenbei.clear()
        neu = []
        k = self.k
        if self.auf_kopf:
            self.auf_kopf = False
            k.y = self.boden
        if self.deckel is not None and not k.zeige_figur:
            self.deckel = None
        if k.figur_sichtbar() or self.auf_kopf:
            k.sitzt, k.y = False, self.boden
            k.zeige_figur = True
            neu.append(Mit('k', Setze(buckel=1.0)))
        return neu + self.schreck_alle(hoehe=45) + [Wandel(0.3, karton=0.0)]

    def aufspringen(self):
        self.deckel = None
        k = self.k
        k.zeige_figur, k.sitzt, k.buckel = True, True, 0.0
        k.y = self.boden - 40 * self.s
        k.pose = Pose(kopf_vorn=True, schreck=0.6)

    def weiter(self, dt):
        k = self.k
        if self.auf_kopf:
            k.x, k.y = self.x + self.richtung * 6 * self.s, self.y - self.hopp - 238 * self.s
            k.richtung = self.richtung
            k.pose = Pose(kopf_vorn=True, auge_zu=blinzeln(self.t, 0.7))

    def zeichne_vorn(self, p):
        if self.karton <= 0:
            return
        s = self.s
        p.save()
        p.translate(self.bx, self.boden + (1 - self.karton) * 80 * s)
        p.rotate(self.wackel)
        p.scale(s, s)
        deckel = self.deckel if self.deckel is not None else (0, -400, 0)
        p.setClipRect(QRectF(-200, -400, 400, 400) if self.deckel is not None else QRectF(-200, -H + 1, 400, 400))
        zeichne_geschenk(p, B, H, GRUEN_KARTON, GOLD_HELL, deckel)
        p.restore()

    def grenzen_extra(self):
        s = self.s
        return QRectF(self.bx - 70 * s, self.boden - 110 * s, 140 * s, 110 * s)
