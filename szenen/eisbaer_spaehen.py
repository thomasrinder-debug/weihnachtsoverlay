import math
import random

from PyQt6.QtCore import QPointF, QRectF
from PyQt6.QtGui import QColor, QTransform

from zeichnen.figur import Pose, zeichne_schreckstriche
from zeichnen.figuren import EISBAER, EISBAER_SCHATTEN, zeichne_baerenkopf_vorn
from zeichnen.grundlagen import KEIN_STIFT, WEISS, blinzeln, kreis, radial, stern

from .basis import Jeweils, Setze, Szene, Tu, Wandel, Warte


class EisbaerSpaehen(Szene):
    """Ein Eisbär lugt seitlich um den Rand, fängt mit der Zunge eine Schneeflocke und
    genießt sie. Die nächste landet auf seiner Nase: Er niest, erschrickt vor sich
    selbst und verschwindet verlegen."""
    name, titel, reihenfolge = 'baerspaeht', 'Eisbär späht', 25

    def vorbereiten(self):
        self.zeige_figur = False
        self.sc = self.s * 1.25
        self.links = random.random() < 0.5
        self.ey = self.oben + self.geo.height() * random.uniform(0.3, 0.6)
        self.h = self.hand = 0.0
        self.pose = Pose()
        self.zunge = 0.0
        self.zittern = 0.0
        self.huch = False
        self.flocke = None          # (x, y) in Einheiten des Bären

    def trafo(self):
        tr = QTransform()
        tr.translate(self.geo.left() if self.links else self.geo.right(), self.ey)
        tr.scale(self.sc * (-1 if self.links else 1), self.sc)
        return tr

    def kopf(self):
        return 44 - 82 * self.h + math.sin(self.t * 40) * self.zittern, 0.0

    def flug(self, dauer, ziel):
        def f(sz, u):
            g = min(1.0, u / dauer)
            kx, ky = sz.kopf()
            zx, zy = kx + ziel[0], ky + ziel[1]
            sz.flocke = (zx + math.sin(u * 3) * 18 * (1 - g) - 30 * (1 - g), zy - 150 * (1 - g))
        return Jeweils(dauer, f)

    def ablauf(self):
        return [
            Wandel(0.5, hand=1.0), Wandel(1.1, h=0.85),
            Jeweils(1.6, lambda sz, u: setattr(sz, 'pose', Pose(blick_x=-math.sin(u * 4), auge_zu=blinzeln(sz.t)))),
            Setze(pose=Pose(blick_y=-1, blick_x=-0.3)),
            self.flug(1.0, (0, 22)),
            Setze(pose=Pose(blick_y=0.6)),
            Wandel(0.3, zunge=1.0),
            self.flug(0.5, (0, 30)),
            Setze(flocke=None, pose=Pose(auge_zu=True)),
            Wandel(0.2, zunge=0.0),
            Warte(1.0),
            Setze(pose=Pose(sorge=0.3, auge_zu=False)),
            Warte(0.5),
            Setze(pose=Pose(blick_y=-1, blick_x=-0.3)),
            self.flug(1.3, (0, 2)),
            Setze(pose=Pose(auge_zu=True, sorge=0.8, mund_offen=True)),
            Warte(0.5),
            Tu(lambda sz: sz.niesen()),
            Wandel(0.08, h=0.55),
            Setze(pose=Pose(schreck=1.0), huch=True, zittern=1.5),
            Warte(0.4),
            Setze(huch=False, zittern=0.0),
            Wandel(0.5, h=0.8),
            Setze(pose=Pose(sorge=1.0, blick_x=-0.4, auge_zu=False)),
            Warte(0.6),
            Setze(pose=Pose(sorge=1.0, auge_zu=True)),
            Warte(0.2),
            Wandel(0.3, h=0.0), Wandel(0.3, hand=0.0),
        ]

    def schreck_ablauf(self):
        self.flocke = None
        if self.h <= 0 and self.hand <= 0:
            return []
        return [Setze(pose=Pose(schreck=1.0, sorge=0.3), huch=True, zittern=1.8, zunge=0.0),
                Wandel(0.1, h=lambda sz: sz.h + 0.06), Warte(0.15), Setze(zittern=0.0, huch=False),
                Wandel(0.12, h=0.0), Wandel(0.12, hand=0.0), Warte(0.1)]

    def niesen(self):
        self.flocke = None
        kx, ky = self.kopf()
        q = self.trafo().map(QPointF(kx - 30, ky + 8))
        self.streue(q.x(), q.y(), 14, WEISS, tempo=150, dauer=0.6, r=(3, 7))

    def grenzen_extra(self):
        if self.h <= 0 and self.hand <= 0 and not self.flocke:
            return QRectF()
        k = self.trafo().mapRect(QRectF(-100, -240, 112, 320))
        return k

    def zeichne_vorn(self, p):
        if self.h <= 0 and self.hand <= 0:
            return
        p.save()
        p.setTransform(self.trafo(), True)
        p.setPen(KEIN_STIFT)
        p.setClipRect(QRectF(-400, -400, 400, 800))
        kx, ky = self.kopf()
        # Schulter und Kopf
        p.setBrush(radial(kx + 40, ky + 40, 70, EISBAER, EISBAER_SCHATTEN))
        p.drawEllipse(QPointF(kx + 50, ky + 50), 40, 50)
        p.save()
        p.translate(kx, ky)
        p.rotate(-12)
        zeichne_baerenkopf_vorn(p, 0, 0, self.pose, self.t, self.zunge)
        if self.huch:
            zeichne_schreckstriche(p, 0, -52, 1.0)
        p.restore()
        # Tatzen an der Kante
        greif = -4 + 26 * (1 - self.hand)
        for y in (-58, 62):
            p.setBrush(radial(greif - 4, y - 4, 18, EISBAER, EISBAER_SCHATTEN))
            p.drawEllipse(QPointF(greif, y), 14, 16)
            p.setBrush(QColor('#3A3A3A'))
            for dy in (-9, -3, 3, 9):
                kreis(p, greif - 13, y + dy, 1.8)
        p.setClipping(False)
        if self.flocke:
            p.setBrush(QColor(255, 255, 255, 240))
            fx, fy = self.flocke
            stern(p, fx, fy, 6)
            p.rotate(0)
        p.restore()
