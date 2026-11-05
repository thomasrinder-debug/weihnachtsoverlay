import math
import random

from PyQt6.QtCore import QPointF, QRectF
from PyQt6.QtGui import QColor

from zeichnen.figur import Pose
from zeichnen.figuren import Katze
from zeichnen.grundlagen import GOLD, KEIN_STIFT, ROT, kreis, radial
from zeichnen.requisiten import zeichne_taennchen

from .basis import Gehe, Jeweils, Mit, Renne, Schritt, Setze, Stehe, Szene, Tu, Wandel, Warte

GROESSE = 2.4        # Tännchen-Maßstab
KUGELN = [(-14, -24, ROT), (12, -30, QColor('#2A6FD6')), (-6, -44, GOLD), (8, -56, QColor('#B04AC8'))]


class Schieben(Schritt):
    """Der Kater schiebt das Bäumchen mit dem Kopf aus dem Bild."""

    def weiter(self, sz, u, dt):
        k = sz.k
        v = -sz.richtung * sz.tempo * 0.7
        k.x += v * dt
        k.phase += abs(v) * dt / (k.s * 30)
        k.richtung = -sz.richtung
        k.pose = Pose(bein_v=-25 * math.sin(k.phase), bein_h=25 * math.sin(k.phase), auge_zu=True)
        sz.tx = k.x - sz.richtung * 30 * sz.s

    def fertig(self, sz, u):
        return not sz.grenzen().intersects(sz.geo)


class Grummelkater(Szene):
    """Ein mürrischer Kater setzt sich neben ein geschmücktes Bäumchen, schaut die Zuschauer
    an und schubst ganz langsam eine Kugel nach der anderen herunter. Zum Schluss schiebt er
    das ganze Bäumchen mit dem Kopf aus dem Bild."""
    name, titel, reihenfolge = 'grummelkater', 'Grummelkater', 48

    def vorbereiten(self):
        self.zeige_figur = False
        r = self.richtung
        self.tx = self.vom_rand(random.uniform(0.1, 0.13))
        self.baum = 0.0
        self.kugeln = [list(k) for k in KUGELN]
        self.unten = []          # [x, y, vx, vy, farbe]
        self.k = self.dazu('k', Katze, groesse=0.6, grummelig=True)
        self.k.richtung = -r
        self.k.x = self.aussen(-r)
        self.k.tempo = self.tempo * 0.5

    def ablauf(self):
        r, s = self.richtung, self.s
        tatze = lambda i: [  # noqa: E731
            Mit('k', Stehe(0.5, Pose(arm_v=-70 * 0.6, kopf_vorn=False))),
            Mit('k', Stehe(0.5, Pose(arm_v=-90))),
            Tu(lambda sz: sz.runter(i)),
            Mit('k', Stehe(1.3, lambda d, u: Pose(kopf_vorn=True, auge_zu=0.8 < u < 0.95)))]
        return [
            Wandel(0.8, baum=1.0),
            Mit('k', Setze(x=self.aussen(-r))),
            Mit('k', Gehe(bis=self.tx + r * 70 * s)),
            Mit('k', Setze(sitzt=True, richtung=-r)),
            Mit('k', Stehe(1.5, lambda d, u: Pose(kopf_vorn=True))),
            *tatze(3), *tatze(1),
            Mit('k', Stehe(0.8, Pose(kopf_vorn=True))),
            *tatze(0), *tatze(0),
            Mit('k', Setze(sitzt=False)),
            Mit('k', Stehe(0.5, Pose(kopf_vorn=True))),
            Mit('k', Wandel(0.3, x=lambda d: d.sz.tx + r * 34 * d.sz.s)),
            Schieben(),
        ]

    def schreck_ablauf(self):
        self.nebenbei.clear()
        k = self.k
        neu = []
        if k.figur_sichtbar():
            neu = [Mit('k', Setze(sitzt=False, buckel=1.0, grummelig=False, striche=True,
                                  pose=Pose(kopf_vorn=True, schreck=1.0))),
                   Warte(0.25), Mit('k', Setze(striche=False)), Mit('k', Renne(zum='rand', tempo=4.0))]
        return neu + [Wandel(0.3, baum=0.0), Setze(unten=[])]

    def runter(self, i):
        if not self.kugeln:
            return
        i = min(i, len(self.kugeln) - 1)
        x, y, farbe = self.kugeln.pop(i)
        q = self.ort(x, y)
        self.unten.append([q[0], q[1], -self.richtung * 40 * self.s, -150 * self.s, farbe])

    def ort(self, x, y):
        f = self.s * GROESSE
        return self.tx + x * f, self.boden + (1 - self.baum) * 150 * self.s - 16 * f + y * f

    def weiter(self, dt):
        s = self.s
        boden = self.boden - 6 * s
        for k in self.unten:
            k[3] += 1300 * s * dt
            k[0] += k[2] * dt
            k[1] += k[3] * dt
            if k[1] > boden:
                k[1] = boden
                k[3] = -k[3] * 0.4 if abs(k[3]) > 120 * s else 0.0
                k[2] = -self.richtung * max(abs(k[2]), 200 * s)
        self.unten = [k for k in self.unten if self.geo.adjusted(-30, -30, 30, 30).contains(QPointF(k[0], k[1]))]

    def zeichne_hinten(self, p):
        if self.baum <= 0:
            return
        s = self.s
        p.setPen(KEIN_STIFT)
        p.save()
        p.translate(self.tx, self.boden + (1 - self.baum) * 150 * s)
        p.scale(s * GROESSE, s * GROESSE)
        zeichne_taennchen(p)
        p.restore()
        for x, y, farbe in self.kugeln:
            self.kugel(p, *self.ort(x, y), farbe)

    def kugel(self, p, x, y, farbe):
        r = 6 * self.s
        p.setBrush(radial(x - r * 0.4, y - r * 0.4, r * 1.5, farbe.lighter(160), farbe.darker(130)))
        kreis(p, x, y, r)
        p.setBrush(QColor(255, 255, 255, 180))
        kreis(p, x - r * 0.35, y - r * 0.35, r * 0.25)

    def zeichne_vorn(self, p):
        for x, y, _, _, farbe in self.unten:
            self.kugel(p, x, y, farbe)

    def grenzen_extra(self):
        s = self.s
        k = QRectF()
        if self.baum > 0:
            k = QRectF(self.tx - 70 * s, self.boden - 170 * s, 140 * s, 170 * s)
        for x, y, *_ in self.unten:
            k = k.united(QRectF(x - 10 * s, y - 10 * s, 20 * s, 20 * s))
        return k
