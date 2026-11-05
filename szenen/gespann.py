import math
import random

from PyQt6.QtCore import QPointF, QRectF
from PyQt6.QtGui import QColor

from zeichnen.figur import Pose, renn_pose, zeichne_sack, zeichne_weihnachtsmann
from zeichnen.figuren import Rentier
from zeichnen.grundlagen import KEIN_PINSEL, KEIN_STIFT, WEISS, blinzeln, stift
from zeichnen.requisiten import zeichne_schlitten

from .basis import Ducke, Gehe, Mit, Nebenbei, Setze, Springe, Stehe, Szene, Warte, WarteNebenbei

SCHWEISS = QColor(170, 215, 250, 230)
ABSTAND = 175          # von den Hufen des Rentiers zur Schlittenmitte, Einheiten des Weihnachtsmanns


def hinterher(pose, sz):
    p = renn_pose(sz.phase)
    p.arm_v, p.arm_v_x, p.kopf_vorn, p.sorge = -95 + 10 * math.sin(sz.t * 9), 18, True, 1.0
    return p


class Gespann(Szene):
    """Das Rentier galoppiert mit dem leeren Schlitten davon, er rennt hinterher und
    bleibt japsend stehen. Das Rentier kommt gemütlich zurück, hält neben ihm, er
    klettert hinein und braust winkend davon."""
    name, titel, reihenfolge = 'gespann', 'Gespann ohne Fahrer', 26

    def vorbereiten(self):
        r = self.richtung
        self.rt = self.dazu('rt', Rentier, groesse=0.8)
        self.rt.richtung = r
        self.rt.x = self.aussen(-r) + r * 40 * self.s
        self.im_schlitten = False

    def schlitten_x(self):
        return self.rt.x - self.rt.richtung * ABSTAND * self.s

    def ablauf(self):
        r, s = self.richtung, self.s
        self.x = self.aussen(-r) - r * 120 * s
        halt = self.vom_rand(random.uniform(0.2, 0.26))
        weit = self.aussen(r) + r * (ABSTAND + 150) * s
        return [
            Nebenbei(Mit('rt', Gehe(bis=weit, tempo=3.0))),
            Gehe(bis=halt, tempo=2.2, haltung=hinterher, neigung=10),
            Stehe(2.0, lambda sz, u: Pose(kopf_vorn=True, mund_offen=(u * 5) % 2 < 1, sorge=0.8, arm_v=30,
                                         arm_h=25, hub=3 * math.sin(u * 10), auge_zu=0.8 < u < 1.0)),
            WarteNebenbei(),
            Stehe(0.6, lambda sz, u: Pose(kopf_vorn=True, sorge=0.6, auge_zu=blinzeln(sz.t))),
            # gemütlich zurück
            Mit('rt', Setze(richtung=-r)),
            Nebenbei(Mit('rt', Gehe(bis=lambda d: halt - r * (ABSTAND - 10) * d.sz.s, tempo=1.0))),
            Stehe(0.6, lambda sz, u: Pose(kopf_vorn=True, schreck=0.4, blick_x=1)),
            Setze(richtung=-r),
            WarteNebenbei(),
            Ducke(0.3),
            Springe(lambda sz: (sz.schlitten_x(), sz.boden - 40 * s), 0.5, 90),
            Setze(zeige_figur=False, im_schlitten=True),
            Warte(0.5),
            Mit('rt', Gehe(tempo=3.2)),
            Warte(0.4),
        ]

    def schreck_ablauf(self):
        self.nebenbei.clear()
        neu = self.schreck_alle(weihnachtsmann=not self.im_schlitten)
        return neu

    def weiter(self, dt):
        if self.im_schlitten and random.random() < 0.6 or (not self.im_schlitten and self.rt.figur_sichtbar()
                                                          and random.random() < 0.4):
            self.streue(self.schlitten_x() - self.rt.richtung * 60 * self.s, self.boden - 4 * self.s, 1, WEISS,
                        tempo=60, dauer=0.5, r=(2, 5))
        if not self.im_schlitten and self.zeige_figur and isinstance(self.aktuell, Stehe) and self.pose.mund_offen \
                and random.random() < 0.04:
            self.streue(self.x + self.richtung * 30 * self.s, self.y - 215 * self.s, 1, SCHWEISS, tempo=60,
                        dauer=0.6, r=(3, 4), schwer=True)

    def zeichne_hinten(self, p):
        rt, s = self.rt, self.s
        if not rt.zeige_figur:
            return
        sx, f = self.schlitten_x(), s * 0.62
        p.save()
        p.translate(sx, self.boden)
        p.scale(f * rt.richtung, f)
        if self.im_schlitten:
            t = self.t
            zeichne_sack(p, -64, -96, -10, 1.35)
            sitz = Pose(sitzt=True, sack=False, arm_v=-125 + 20 * math.sin(t * 9), arm_v_x=26,
                        arm_h=-50, wipp=math.sin(t * 4) * 4, auge_zu=blinzeln(t), mund_offen=(t * 3) % 2 < 1)
            if self.erschreckt:
                sitz.kopf_vorn, sitz.schreck, sitz.auge_zu, sitz.arm_v = True, 1.0, False, -60
            p.save()
            p.translate(-14, 0)
            zeichne_weihnachtsmann(p, sitz)
            p.restore()
        zeichne_schlitten(p)
        p.restore()
        # Zugleine vom Schlitten zum Geschirr
        a = QPointF(sx + rt.richtung * 60 * s, self.boden - 30 * s)
        b = rt.trafo().map(QPointF(46, -86))
        p.setPen(stift(QColor('#5A3A1E'), 2.2 * s))
        p.setBrush(KEIN_PINSEL)
        p.drawLine(a, b)
        p.setPen(KEIN_STIFT)

    def grenzen_extra(self):
        if not self.rt.zeige_figur:
            return QRectF()
        sx, s = self.schlitten_x(), self.s
        return QRectF(sx - 90 * s, self.boden - 230 * s, 180 * s, 230 * s)
