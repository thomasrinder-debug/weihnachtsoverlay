import math
import random

from PyQt6.QtCore import QPointF, QRectF
from PyQt6.QtGui import QPainterPath

from zeichnen.figur import Pose
from zeichnen.figuren import Wichtel
from zeichnen.grundlagen import GOLD, GOLD_HELL, HAUT, HAUT_DUNKEL, KEIN_PINSEL, KEIN_STIFT, blinzeln, kreis, linear, radial, stift

from .basis import Erschrecke, Gehe, Jeweils, Mit, Schritt, Setze, Stehe, Szene, Tu, Wandel, Warte

GEBUNDEN = Pose(arm_v=-8, arm_h=8, bein_v=0, bein_h=0)


class Hopsen(Schritt):
    """Das verschnürte Paket hüpft mit geschlossenen Beinen bis aus dem Bild."""

    def __init__(self, seite, tempo=1.2):
        self.seite, self.tempo = seite, tempo

    def weiter(self, sz, u, dt):
        w = sz.w
        w.x += self.seite * sz.tempo * self.tempo * dt
        f = (u / 0.38) % 1.0
        w.hopp = math.sin(math.pi * f) * 26 * sz.s
        w.stauchen = 1 - 0.1 * max(0.0, 1 - f / 0.15)

    def fertig(self, sz, u):
        return not sz.w.figur_sichtbar()


class Geschenkband(Szene):
    """Ein Wichtel will mit einem langen Goldband eine Schleife binden, dreht sich dabei
    immer weiter hinein und ist am Ende selbst ein verschnürtes Paket mit Schleife auf dem
    Kopf. Mit dem letzten freien Finger rückt er die Schleife pedantisch gerade und hopst davon."""
    name, titel, reihenfolge = 'geschenkband', 'Zu viel Geschenkband', 38

    def vorbereiten(self):
        self.zeige_figur = False
        self.w = self.dazu('w', Wichtel, groesse=0.6)
        self.w.richtung = self.richtung
        self.baender = 0.0          # wie viele Bänder um ihn liegen
        self.schleife = 0.0         # 0..1 sichtbar
        self.schleife_w = 28.0      # schief
        self.finger = False
        self.schlaufe = 0.0         # Band, das er in der Luft schwingt
        self.zug = 0.0              # Bandende zieht ihn nach unten (Schreck)

    def ablauf(self):
        r = self.richtung

        def binden(sz, u):
            sz.schlaufe = 1.0
            sz.w.pose = Pose(arm_v=-110 + 50 * math.sin(u * 7), arm_h=-80 - 40 * math.sin(u * 7 + 1),
                             kopf_vorn=True, sorge=min(1.0, u / 2), blick_y=-0.5, mund_offen=u > 1.5)

        def drehen(sz, u):
            sz.w.richtung = r if (u * 6) % 2 < 1 else -r
            sz.baender = min(7.0, u / 1.6 * 7)
            sz.schlaufe = max(0.0, 1 - u / 1.6)
            sz.w.pose = GEBUNDEN

        return [
            Mit('w', Gehe(bis=self.vom_rand(random.uniform(0.13, 0.17)))),
            Mit('w', Stehe(0.4)),
            Jeweils(2.2, binden),
            Jeweils(1.6, drehen),
            Mit('w', Setze(richtung=r, pose=GEBUNDEN)),
            Wandel(0.3, schleife=1.0),
            Mit('w', Stehe(1.2, lambda d, u: Pose(arm_v=-8, arm_h=8, kopf_vorn=True, sorge=0.6,
                                                  auge_zu=0.5 < u < 0.65))),
            Setze(finger=True), Warte(0.4),
            Wandel(0.5, schleife_w=0.0), Warte(0.3), Setze(finger=False),
            Mit('w', Stehe(0.8, Pose(arm_v=-8, arm_h=8, kopf_vorn=True, auge_zu=True))),
            Hopsen(-r),
        ]

    def schreck_ablauf(self):
        self.nebenbei.clear()
        w = self.w
        if not w.figur_sichtbar():
            return []
        if self.baender < 3:
            self.schlaufe = 0.0
            return [Mit('w', Erschrecke(0.3, 40)), Hopsen(w.naechster_rand(), 4.0)]
        return [Mit('w', Erschrecke(0.3, 45)), Setze(zug=1.0),
                Mit('w', Wandel(0.45, y=lambda d: d.boden + 260 * d.sz.s)), Mit('w', Setze(zeige_figur=False))]

    def zeichne_vorn(self, p):
        w = self.w
        if not w.zeige_figur:
            return
        p.save()
        p.setTransform(w.trafo(), True)
        if self.schlaufe > 0:
            t = self.t
            band = QPainterPath()
            band.moveTo(14, -70)
            for k in range(1, 5):
                band.quadTo(26 + k * 6, -110 - 14 * math.sin(t * 6 + k), 10 + k * 8, -60 - 30 * self.schlaufe * k / 4)
            p.setBrush(KEIN_PINSEL)
            p.setPen(stift(GOLD_HELL, 3))
            p.drawPath(band)
            p.setPen(KEIN_STIFT)
        n = int(self.baender)
        if n:
            koerper = QPainterPath()
            koerper.addRoundedRect(QRectF(-30, -150, 60, 148), 22, 22)
            p.setClipPath(koerper)
            for k in range(n):
                y = -140 + k * 20
                p.save()
                p.translate(0, y)
                p.rotate(28 if k % 2 else -28)
                p.setBrush(linear(0, -4, 0, 4, GOLD_HELL, GOLD))
                p.drawRect(QRectF(-50, -4, 100, 8))
                p.restore()
            p.setClipping(False)
        if self.schleife > 0:
            p.save()
            p.translate(4, -150)
            p.rotate(self.schleife_w)
            p.scale(self.schleife, self.schleife)
            for seite in (-1, 1):
                schl = QPainterPath()
                schl.moveTo(0, 0)
                schl.cubicTo(seite * 10, -26, seite * 30, -22, seite * 24, -8)
                schl.cubicTo(seite * 20, 0, seite * 8, 0, 0, 0)
                p.setBrush(linear(0, -26, 0, 0, GOLD_HELL, GOLD.darker(115)))
                p.drawPath(schl)
            p.setBrush(radial(-1, -2, 6, GOLD_HELL, GOLD))
            kreis(p, 0, -1, 5)
            p.restore()
        if self.finger:
            p.setBrush(radial(18, -150, 7, HAUT, HAUT_DUNKEL))
            kreis(p, 20 - 6 * (1 - self.schleife_w / 28), -152, 4)
        p.restore()
        if self.zug:
            q = w.trafo().map(QPointF(0, -10))
            p.setPen(stift(GOLD_HELL, 3 * self.s))
            p.drawLine(q, QPointF(q.x() - w.richtung * 30 * self.s, self.boden + 40))
            p.setPen(KEIN_STIFT)

    def grenzen_extra(self):
        w = self.w
        if not w.zeige_figur:
            return QRectF()
        return w.kasten().adjusted(-30 * self.s, -30 * self.s, 30 * self.s, 0)

