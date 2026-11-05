import math
import random

from PyQt6.QtCore import QPointF, QRectF
from PyQt6.QtGui import QColor

from zeichnen.figur import Pose
from zeichnen.figuren import Nussknacker
from zeichnen.grundlagen import blinzeln
from zeichnen.requisiten import zeichne_walnuss

from .basis import Erschrecke, Gehe, Jeweils, Mit, Renne, Schritt, Setze, Stehe, Szene, Tu, Wandel, Warte

SCHALE = [QColor('#9A6A36'), QColor('#7A5228'), QColor('#C9965A'), QColor('#E8D2A8')]


class NussHuepft(Schritt):
    """Die Walnuss springt im Bogen zum Punkt ziel(szene)."""

    def __init__(self, ziel, dauer, hoehe):
        self.ziel, self.dauer, self.hoehe = ziel, dauer, hoehe

    def beginn(self, sz):
        self.x0, self.y0 = sz.nuss

    def weiter(self, sz, u, dt):
        x1, y1 = self.ziel(sz)
        f = min(1.0, u / self.dauer)
        sz.nuss = (self.x0 + (x1 - self.x0) * f,
                   self.y0 + (y1 - self.y0) * f - self.hoehe * sz.s * 4 * f * (1 - f))
        sz.nuss_dreh += 720 * dt * sz.nk.richtung * -1


class NussknackerSzene(Szene):
    """Ein Nussknacker marschiert steif herein und salutiert. Eine Walnuss hüpft heran
    und springt ihm in den aufgerissenen Mund: Knack! Die Schalen fliegen, er kaut
    zufrieden, der Kiefer klappt ihm herunter, er drückt ihn wieder zu und marschiert ab."""
    name, titel, reihenfolge = 'nussknacker', 'Nussknacker', 16

    def vorbereiten(self):
        self.zeige_figur = False
        self.nk = self.dazu('nk', Nussknacker, groesse=0.72, kiefer=0.0)
        self.nuss = None
        self.nuss_dreh = 0.0

    def mund(self, sz=None):
        q = self.nk.trafo().map(QPointF(12, -196))
        return q.x(), q.y()

    def ablauf(self):
        r = self.richtung
        marsch = lambda p, d: Pose(bein_v=p.bein_v, bein_h=p.bein_h, arm_v=p.arm_v * 1.3,  # noqa: E731
                                   arm_h=p.arm_h * 1.3, hub=p.hub * 0.5, auge_zu=p.auge_zu)
        s = self.s
        boden = self.boden - 8 * s
        return [
            Mit('nk', Gehe(bis=self.vom_rand(random.uniform(0.15, 0.2)), tempo=0.85, haltung=marsch)),
            Mit('nk', Stehe(0.4)),
            Mit('nk', Stehe(1.3, lambda d, u: Pose(arm_v=-148 if 0.2 < u < 1.1 else 0, arm_v_x=16,
                                                   kopf_vorn=True, auge_zu=blinzeln(d.t)))),
            # die Nuss kommt von hinten angehüpft
            Setze(nuss=(self.aussen(-r), boden)),
            NussHuepft(lambda sz: (sz.nk.x - r * 260 * s, boden), 0.5, 60),
            Mit('nk', Setze(pose=Pose(kopf_vorn=True, blick_x=-1, sorge=0.4))),
            NussHuepft(lambda sz: (sz.nk.x - r * 150 * s, boden), 0.45, 50),
            Mit('nk', Setze(richtung=-r, pose=Pose(blick_x=1, sorge=0.2))),
            Mit('nk', Wandel(0.3, kiefer=1.0)),
            Mit('nk', Setze(pose=Pose(mund_offen=True, blick_x=1))),
            NussHuepft(lambda sz: sz.mund(), 0.55, 120),
            # Knack!
            Setze(nuss=None),
            Mit('nk', Wandel(0.07, kiefer=0.0)),
            Tu(lambda sz: sz.knack()),
            Mit('nk', Stehe(0.35, Pose(kopf_vorn=True, schreck=0.6))),
            Mit('nk', Setze(striche=False)),
            Mit('nk', Jeweils(1.3, lambda d, u: setattr(d, 'kiefer', 0.25 + 0.25 * math.sin(u * 18)))),
            Mit('nk', Setze(pose=Pose(auge_zu=True))),
            Mit('nk', Wandel(0.12, kiefer=1.3)),
            Mit('nk', Stehe(0.9, lambda d, u: Pose(kopf_vorn=True, sorge=0.8, auge_zu=0.5 < u < 0.6))),
            Mit('nk', Stehe(0.4, lambda d, u: Pose(arm_v=-100 * min(1.0, u / 0.3), arm_v_x=12))),
            Mit('nk', Wandel(0.15, kiefer=0.0)),
            Mit('nk', Stehe(0.6, Pose(arm_v=-100, arm_v_x=12, auge_zu=True))),
            Warte(0.2),
            Mit('nk', Gehe(tempo=0.95, haltung=marsch)),
        ]

    def schreck_ablauf(self):
        self.nebenbei.clear()
        self.nuss = None
        if not self.nk.figur_sichtbar():
            return []
        return [Mit('nk', Setze(kiefer=1.0)), Mit('nk', Erschrecke(0.35, 50)),
                Mit('nk', Renne(zum='rand', tempo=3.6))]

    def knack(self):
        x, y = self.mund()
        self.nk.striche = True
        self.streue(x, y, 24, SCHALE, tempo=300, dauer=1.1, r=(3, 6), schwer=True,
                    richtung=-math.pi / 2, streuung=1.4)

    def weiter(self, dt):
        if self.erschreckt:
            self.nk.kiefer = max(self.nk.kiefer, self.nk.pose.schreck)

    def zeichne_vorn(self, p):
        if self.nuss:
            p.save()
            p.translate(*self.nuss)
            p.rotate(self.nuss_dreh)
            zeichne_walnuss(p, 0, 0, 9 * self.s)
            p.restore()

    def grenzen_extra(self):
        if not self.nuss:
            return QRectF()
        r = 14 * self.s
        return QRectF(self.nuss[0] - r, self.nuss[1] - r, 2 * r, 2 * r)
