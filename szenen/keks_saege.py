import math
import random

from PyQt6.QtCore import QPointF, QRectF
from PyQt6.QtGui import QColor

from zeichnen.figur import Pose
from zeichnen.figuren import Wichtel
from zeichnen.grundlagen import GRUEN, GRUEN_DUNKEL, blinzeln
from zeichnen.requisiten import zeichne_keks, zeichne_taennchen

from .basis import Gehe, Jeweils, Mit, Setze, Stehe, Szene, Tu, Wandel, Warte

KEKS_R = 14
SPAENE = [QColor('#E8C890'), QColor('#C9A06A'), GRUEN, GRUEN_DUNKEL]


class KeksSaege(Szene):
    """Ein Wichtel kann einen steinharten Keks nicht durchbrechen und rollt ihn wütend
    weg. Der Keks sägt wie ein Kreissägeblatt ein Tännchen um, dessen Spitze in hohem
    Bogen zurückfliegt und ihm passgenau als stachelige Mütze auf dem Kopf landet."""
    name, titel, reihenfolge = 'keks', 'Keks als Sägeblatt', 39

    def vorbereiten(self):
        self.zeige_figur = False
        r = self.richtung
        self.w = self.dazu('w', Wichtel, groesse=0.6, muetze=True)
        self.w.richtung = r
        self.tx = self.vom_rand(random.uniform(0.3, 0.34))
        self.gesaegt = False
        self.keks = None            # [x, y, drehung] in der Hand oder rollend
        self.spitze = None          # [x, y, drehung] fliegende Tannenspitze, oder 'auf'
        self.versinken = 0.0        # beim Schreck geht es nach unten weg (Pixel)

    def hand(self):
        q = self.w.trafo().map(QPointF(20, -64))
        return q.x(), q.y()

    def ablauf(self):
        r, s = self.richtung, self.s
        ziel = self.vom_rand(random.uniform(0.12, 0.15))

        def brechen(sz, u):
            sz.w.pose = Pose(arm_v=-80 + 6 * math.sin(u * 40), arm_h=-75, kopf_vorn=True, sorge=1.0,
                             schreck=0.3 if u > 1.2 else 0, auge_zu=u < 1.2, wipp=math.sin(u * 40) * 2)
            sz.w.stauchen = 1 - 0.04 * abs(math.sin(u * 20))
            x, y = sz.hand()
            sz.keks = [x, y, math.sin(u * 40) * 4]

        def flug(sz, u):
            f = min(1.0, u / 1.0)
            kx, ky = sz.w.trafo().map(QPointF(4, -146)).x(), sz.w.trafo().map(QPointF(4, -146)).y()
            sx, sy = sz.tx, sz.boden - 30 * s
            sz.spitze = [sx + (kx - sx) * f, sy + (ky - sy) * f - 260 * s * 4 * f * (1 - f), -720 * f]

        return [
            Mit('w', Gehe(bis=ziel)),
            Mit('w', Stehe(0.4)),
            Jeweils(2.2, brechen),
            Mit('w', Setze(stauchen=1.0)),
            Mit('w', Stehe(0.5, Pose(kopf_vorn=True, sorge=1.0, mund_offen=True))),
            Mit('w', Stehe(0.3, Pose(arm_v=-20, arm_h=-75))),
            Rolle(),
            Tu(lambda sz: sz.saegen_start()),
            Jeweils(1.0, lambda sz, u: sz.saegen(u)),
            Setze(gesaegt=True),
            Jeweils(1.0, flug),
            Setze(spitze='auf'),
            Mit('w', Setze(muetze=False)),
            Tu(lambda sz: sz.nadeln()),
            Mit('w', Stehe(0.4, Pose(kopf_vorn=True, schreck=0.6))),
            Mit('w', Stehe(1.8, lambda d, u: Pose(kopf_vorn=True, blick_y=-0.9, blick_x=math.sin(u * 3) * 0.5,
                                                  auge_zu=0.8 < u < 0.95))),
            Mit('w', Gehe(bis=self.aussen(-r), tempo=0.9)),
            Wandel(0.5, versinken=40 * s),
        ]

    def schreck_ablauf(self):
        self.nebenbei.clear()
        if not self.w.figur_sichtbar() and not self.keks:
            return [Wandel(0.3, versinken=40 * self.s)]
        if self.keks and self.keks[1] < self.boden - KEKS_R * self.s - 2:
            self.keks = None
        return [Mit('w', Setze(striche=True, pose=Pose(kopf_vorn=True, schreck=1.0, arm_v=-120, arm_h=-110))),
                Warte(0.25), Mit('w', Setze(striche=False)),
                Wandel(0.5, versinken=300 * self.s)]

    def nadeln(self):
        q = self.w.trafo().map(QPointF(4, -150))
        self.streue(q.x(), q.y(), 10, SPAENE, tempo=120, dauer=0.5, r=(2, 4), schwer=True)

    def saegen_start(self):
        self.keks[0] = self.tx - self.richtung * 4 * self.s

    def saegen(self, u):
        k, s = self.keks, self.s
        k[2] += 25
        if random.random() < 0.8:
            self.streue(self.tx, self.boden - 10 * s, 2, SPAENE, tempo=180, dauer=0.6, r=(1.5, 3), schwer=True,
                        richtung=-math.pi / 2, streuung=1.2)

    def weiter(self, dt):
        w = self.w
        w.y = self.boden + self.versinken
        if self.spitze == 'auf' and self.keks and not self.erschreckt:
            k = self.keks
            k[0] += self.richtung * self.tempo * 2.4 * dt
            k[2] += self.richtung * self.tempo * 2.4 / (KEKS_R * self.s) * 57.3 * dt
            if not self.geo.adjusted(-40, -40, 40, 40).contains(QPointF(k[0], k[1])):
                self.keks = None

    def zeichne_vorn(self, p):
        s, w = self.s, self.w
        p.save()
        p.setClipRect(QRectF(self.geo.left(), self.geo.top(), self.geo.width(), self.boden - self.geo.top()))
        p.save()
        p.translate(self.tx, self.boden + self.versinken)
        p.scale(s * 1.1, s * 1.1)
        zeichne_taennchen(p, abgesaegt=self.gesaegt)
        p.restore()
        if self.keks:
            p.save()
            p.translate(self.keks[0], self.keks[1] + (self.versinken if self.keks[1] > self.boden - 30 * s else 0))
            p.rotate(self.keks[2])
            p.scale(s, s)
            zeichne_keks(p, KEKS_R)
            p.restore()
        if self.spitze == 'auf' and w.zeige_figur:
            p.save()
            p.setTransform(w.trafo(), True)
            p.translate(4, -134)
            p.scale(1.1 / 0.6, 1.1 / 0.6)
            zeichne_taennchen(p, nur_spitze=True)
            p.restore()
        elif isinstance(self.spitze, list):
            p.save()
            p.translate(self.spitze[0], self.spitze[1])
            p.rotate(self.spitze[2])
            p.scale(s * 1.1, s * 1.1)
            zeichne_taennchen(p, nur_spitze=True)
            p.restore()
        p.restore()

    def grenzen_extra(self):
        s = self.s
        k = QRectF(self.tx - 40 * s, self.boden - 80 * s, 80 * s, 80 * s)
        if self.keks:
            k = k.united(QRectF(self.keks[0] - 20 * s, self.keks[1] - 20 * s, 40 * s, 40 * s))
        if isinstance(self.spitze, list):
            k = k.united(QRectF(self.spitze[0] - 40 * s, self.spitze[1] - 70 * s, 80 * s, 90 * s))
        if self.versinken >= 39 * s and not self.w.zeige_figur:
            return QRectF()
        return k


class Rolle(Jeweils):
    """Der Keks rollt vom Wichtel zum Tännchen."""

    def __init__(self):
        super().__init__(0, None)

    def beginn(self, sz):
        sz.keks[1] = sz.boden - KEKS_R * sz.s
        self.ziel = sz.tx - sz.richtung * 4 * sz.s

    def weiter(self, sz, u, dt):
        k = sz.keks
        v = sz.richtung * sz.tempo * 2.4
        k[0] += v * dt
        k[2] += v / (KEKS_R * sz.s) * 57.3 * dt

    def fertig(self, sz, u):
        return (sz.keks[0] - self.ziel) * sz.richtung >= 0
