import math
import random

from PyQt6.QtCore import QPointF, QRectF
from PyQt6.QtGui import QColor

from zeichnen.figur import Pose, segment, zeichne_schreckstriche
from zeichnen.figuren import Wichtel
from zeichnen.grundlagen import (GRUEN, GRUEN_DUNKEL, ROT_DUNKEL, ROT_HELL, WEISS, blinzeln, flausch, kreis, linear,
                                 radial, stift)
from zeichnen.requisiten import zeichne_keks

from .basis import Gehe, Jeweils, Mit, Renne, Setze, Stehe, Szene, Tu, Wandel, Warte

KEKSE = [(-16, -8), (0, -8), (16, -8), (-8, -16), (8, -16)]
LOEFFEL = QColor('#B07A42')


class Plaetzchen(Szene):
    """Auf einem Teller am unteren Rand liegen Plätzchen. Eine Hand im roten Ärmel greift
    vom Seitenrand herein und stibitzt einen Keks, dann noch einen. Beim dritten Mal haut
    ihr der Wichtel, der Wache hält, mit dem Kochlöffel auf die Finger. Die Hand legt kleinlaut
    einen Keks zurück, der Wichtel nimmt den Teller und trägt ihn davon."""
    name, titel, reihenfolge = 'plaetzchen', 'Plätzchenteller', 42

    def vorbereiten(self):
        self.zeige_figur = False
        self.seite = -self.richtung                         # die Hand kommt von hier
        self.kante = self.geo.left() if self.seite < 0 else self.geo.right()
        self.tx = self.kante - self.seite * 150 * self.s    # Teller
        self.kekse = len(KEKSE)
        self.hand = 0.0          # 0 draußen, 1 am Teller
        self.greift = False      # hält einen Keks
        self.aua = False
        self.w = self.dazu('w', Wichtel, groesse=0.55, vorn=True)
        self.w.richtung = self.seite
        self.w.x = self.aussen(self.seite)
        self.loeffel = False

    def ablauf(self):
        s, r = self.s, self.richtung
        hauen = lambda d, u: Pose(arm_v=-170 + 150 * min(1.0, u / 0.12), arm_v_x=10, kopf_vorn=False,  # noqa: E731
                                  sorge=0.0, mund_offen=True)
        return [
            Mit('w', Gehe(bis=self.tx - self.seite * 60 * s)),
            Mit('w', Setze(richtung=self.seite)),
            Mit('w', Stehe(1.0, lambda d, u: Pose(kopf_vorn=True, auge_zu=blinzeln(d.t), blick_x=-0.6))),
            Mit('w', Setze(pose=Pose(auge_zu=True))),
            *self.stibitzen(),
            Mit('w', Stehe(0.8, lambda d, u: Pose(kopf_vorn=True, sorge=0.8, blick_y=0.6))),
            *self.stibitzen(),
            Mit('w', Stehe(1.0, lambda d, u: Pose(kopf_vorn=True, sorge=1.0, blick_x=-0.8))),
            Setze(loeffel=True),
            Mit('w', Stehe(0.6, Pose(arm_v=-170, arm_v_x=10, kopf_vorn=True, sorge=1.0))),
            Wandel(0.6, hand=1.0),
            Mit('w', Stehe(0.15, hauen)),
            Setze(aua=True),
            Wandel(0.15, hand=0.0),
            Mit('w', Stehe(0.8, Pose(arm_v=-30, arm_v_x=10, kopf_vorn=True))),
            Setze(aua=False),
            Warte(0.6),
            Setze(greift=True), Wandel(0.9, hand=1.0), Setze(greift=False, kekse=lambda sz: sz.kekse + 1),
            Wandel(0.5, hand=0.0),
            Mit('w', Stehe(1.0, lambda d, u: Pose(kopf_vorn=True, auge_zu=u > 0.3, mund_offen=False))),
            Setze(loeffel=False),
            Mit('w', Wandel(0.2, x=lambda d: d.sz.tx + d.sz.richtung * 10 * s)),
            Setze(traegt=True),
            Mit('w', Gehe(bis=self.aussen(self.seite), tempo=0.8,
                          haltung=lambda p, d: Pose(bein_v=p.bein_v, bein_h=p.bein_h, hub=p.hub, arm_v=-70,
                                                    arm_h=-60))),
        ]

    traegt = False

    def stibitzen(self):
        return [Wandel(0.9, hand=1.0), Setze(greift=True, kekse=lambda sz: sz.kekse - 1), Warte(0.2),
                Wandel(0.5, hand=0.0), Setze(greift=False), Warte(0.4)]

    def schreck_ablauf(self):
        self.nebenbei.clear()
        neu = [Wandel(0.15, hand=0.0), Setze(loeffel=False)]
        if self.w.figur_sichtbar():
            self.traegt = True
            neu = [Setze(aua=True)] + neu + [Setze(aua=False),
                                             Mit('w', Setze(striche=True, pose=Pose(kopf_vorn=True, schreck=1.0))),
                                             Warte(0.2), Mit('w', Setze(striche=False)),
                                             Mit('w', Renne(zum='rand'))]
        return neu

    def teller(self):
        if self.traegt:
            q = self.w.trafo().map(QPointF(26, -64))
            return q.x(), q.y() + 8 * self.s
        return self.tx, self.boden - 3 * self.s

    def zeichne_hinten(self, p):
        if self.traegt and not self.w.zeige_figur:
            return
        s = self.s
        x, y = self.teller()
        p.save()
        p.translate(x, y)
        p.scale(s, s)
        p.setBrush(linear(0, -6, 0, 4, WEISS, QColor('#C9D2DE')))
        p.drawEllipse(QRectF(-34, -6, 68, 10))
        p.setBrush(QColor('#E8EDF4'))
        p.drawEllipse(QRectF(-24, -5, 48, 6))
        for i, (kx, ky) in enumerate(KEKSE[:self.kekse]):
            p.save()
            p.translate(kx, ky)
            p.scale(1, 0.75)
            zeichne_keks(p, 9)
            p.restore()
        p.restore()

    def zeichne_vorn(self, p):
        s = self.s
        if self.hand > 0:
            reich = 175 * s * self.hand
            hx = self.kante - self.seite * reich + self.seite * 25 * s
            hy = self.boden - 26 * s + (math.sin(self.t * 40) * 4 * s if self.aua else 0)
            p.save()
            p.translate(0, 0)
            ax = self.kante + self.seite * 40 * s
            p.setBrush(linear(0, hy - 10 * s, 0, hy + 10 * s, ROT_HELL, ROT_DUNKEL))
            a, b = sorted((ax, hx))
            p.drawRoundedRect(QRectF(a, hy - 10 * s, b - a, 20 * s), 9 * s, 9 * s)
            flausch(p, [(hx + self.seite * 6 * s, hy + dy * s) for dy in (-9, -3, 3, 9)], 5 * s)
            p.setBrush(radial(hx - self.seite * 6 * s, hy - 3 * s, 14 * s, GRUEN.lighter(135), GRUEN_DUNKEL))
            p.drawEllipse(QPointF(hx - self.seite * 10 * s, hy), 11 * s, 10 * s)
            if self.greift:
                p.save()
                p.translate(hx - self.seite * 20 * s, hy - 4 * s)
                p.scale(s, s)
                zeichne_keks(p, 9)
                p.restore()
            if self.aua:
                zeichne_schreckstriche(p, hx - self.seite * 10 * s, hy - 14 * s, s * 0.8)
            p.restore()
        if self.loeffel and self.w.zeige_figur:
            w = self.w
            p.save()
            p.setTransform(w.trafo(), True)
            p.translate(8, -96)
            p.rotate(w.pose.arm_v)
            p.setPen(stift(LOEFFEL, 4))
            p.drawLine(QPointF(0, 30), QPointF(0, 70))
            p.setPen(stift(QColor(0, 0, 0, 0), 0))
            p.setBrush(radial(0, 74, 9, LOEFFEL.lighter(130), LOEFFEL.darker(120)))
            p.drawEllipse(QPointF(0, 76), 7, 10)
            p.restore()

    def grenzen_extra(self):
        s = self.s
        a, b = sorted((self.kante, self.tx))
        k = QRectF(a - 60 * s, self.boden - 60 * s, b - a + 120 * s, 60 * s)
        if self.traegt:
            x, y = self.teller()
            k = k.united(QRectF(x - 50 * s, y - 40 * s, 100 * s, 60 * s))
        return k
