import math
import random

from PyQt6.QtCore import QPointF, QRectF
from PyQt6.QtGui import QColor

from zeichnen.figur import Pose, zeichne_schreckstriche
from zeichnen.figuren import Wichtel
from zeichnen.grundlagen import ROT_DUNKEL, ROT_HELL, blinzeln, kreis, radial, stift
from zeichnen.requisiten import zeichne_strumpf

from .basis import Jeweils, Setze, Szene, Wandel, Warte

LAENGE = 150       # Band vom Rand bis zur Schlaufe, Einheiten


class Strumpf(Szene):
    """Ein Weihnachtsstrumpf schwebt an einem Band vom oberen Rand herab, zappelt und
    beult sich aus. Ein Wichtel steckt den Kopf heraus, schaut sich um, winkt und
    taucht wieder ab; dann wird der Strumpf nach oben gezogen."""
    name, titel, reihenfolge = 'strumpf', 'Strumpf oben', 24

    def vorbereiten(self):
        self.zeige_figur = False
        self.f = self.s * 0.95
        self.xs = self.vom_rand(random.uniform(0.15, 0.3))
        self.ab = 0.0           # 0 = oben über dem Rand, 1 = ganz herabgelassen
        self.dreh = 0.0
        self.zappeln = 0.0
        self.voll = 0.0
        self.raus = 0.0         # Wichtelkopf schaut heraus
        self.pose = Pose()
        self.winken = 0.0
        self.huch = False

    def ablauf(self):
        def umschauen(sz, u):
            sz.pose = Pose(blick_x=math.sin(u * 4), kopf_vorn=True, auge_zu=blinzeln(sz.t))

        return [
            Wandel(1.2, ab=1.0),
            Warte(0.6),
            Wandel(0.3, zappeln=1.0, voll=1.0), Warte(0.9), Wandel(0.3, zappeln=0.0),
            Warte(0.4),
            Wandel(0.2, zappeln=1.0), Warte(0.4), Wandel(0.2, zappeln=0.0),
            Wandel(0.3, raus=1.0),
            Jeweils(1.6, umschauen),
            Setze(pose=Pose(kopf_vorn=True, sorge=0.8, blick_y=0.3)),
            Warte(0.7),
            Setze(pose=Pose(kopf_vorn=True, mund_offen=True)),
            Wandel(0.25, winken=1.0), Warte(1.2), Wandel(0.2, winken=0.0),
            Setze(pose=Pose(kopf_vorn=True, auge_zu=True)), Warte(0.4),
            Wandel(0.2, raus=0.0), Setze(voll=0.6),
            Wandel(0.25, zappeln=1.0), Warte(0.3),
            Wandel(0.7, ab=0.0),
        ]

    def schreck_ablauf(self):
        if self.ab <= 0:
            return []
        neu = []
        if self.raus > 0.1:
            neu = [Setze(pose=Pose(kopf_vorn=True, schreck=1.0), huch=True, winken=0.0),
                   Wandel(0.1, raus=1.15), Warte(0.15), Setze(huch=False), Wandel(0.12, raus=0.0)]
        return neu + [Setze(zappeln=1.0), Wandel(0.35, ab=0.0)]

    def lage(self):
        """Schlaufe des Strumpfs in Pixeln."""
        return self.xs, self.oben - 170 * self.f + (LAENGE + 170) * self.f * self.ab

    def weiter(self, dt):
        self.dreh = math.sin(self.t * 2.1) * 6 * (1 - self.zappeln) + math.sin(self.t * 31) * 9 * self.zappeln

    def zeichne_vorn(self, p):
        if self.ab <= 0:
            return
        x, y = self.lage()
        f = self.f
        p.setPen(stift(ROT_DUNKEL, 3 * f))
        p.drawLine(QPointF(x, self.oben - 5), QPointF(x, y))
        p.setPen(stift(QColor(0, 0, 0, 0), 0))
        p.save()
        p.translate(x, y)
        p.rotate(self.dreh)
        p.scale(f * (1 - 0.06 * self.zappeln * math.sin(self.t * 23)), f)
        if self.raus > 0:
            p.save()
            p.setClipRect(QRectF(-80, -200, 160, 228))
            Wichtel.kopf(p, self.pose, self.t, 0, 50 - 52 * self.raus)
            p.restore()
        zeichne_strumpf(p, self.voll)
        if self.raus > 0.5:
            for seite in (-1, 1):
                wx, wy = seite * 27, 26
                if seite > 0 and self.winken:
                    wx += 10 * self.winken
                    wy -= 30 * self.winken + math.sin(self.t * 12) * 5 * self.winken
                p.setBrush(radial(wx - 2, wy - 2, 9, ROT_HELL, ROT_DUNKEL))
                kreis(p, wx, wy, 6.5)
        if self.huch:
            zeichne_schreckstriche(p, 0, 50 - 52 * self.raus - 50, 1.0)
        p.restore()

    def grenzen_extra(self):
        if self.ab <= 0:
            return QRectF()
        x, y = self.lage()
        f = self.f
        return QRectF(x - 110 * f, self.oben, 220 * f, y - self.oben + 190 * f)
