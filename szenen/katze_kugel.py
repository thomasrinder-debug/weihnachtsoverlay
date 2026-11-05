import math
import random

from PyQt6.QtCore import QPointF, QRectF
from PyQt6.QtGui import QColor

from zeichnen.figur import Pose
from zeichnen.figuren import GRAU, Katze
from zeichnen.grundlagen import GOLD, GOLD_HELL, KEIN_STIFT, ROT, blinzeln, kreis, radial, stift

from .basis import Gehe, Jeweils, Mit, Renne, Setze, Stehe, Szene, Tu, Wandel, Warte

LANG = 120          # Band der Kugel, Einheiten
KUGEL = 13


class KatzeKugel(Szene):
    """Unter dem oberen Rand hängt eine Christbaumkugel. Eine graue Katze spaziert kopfüber
    an der Kante entlang, tippt die Kugel an, schlägt immer übermütiger zu, bis sich das Band
    um ihre Pfote wickelt, und schleift die Kugel stolz mit davon."""
    name, titel, reihenfolge = 'katzekugel', 'Katze und Kugel', 46

    def vorbereiten(self):
        self.zeige_figur = False
        r = self.richtung
        self.kx = self.vom_rand(random.uniform(0.18, 0.24))
        self.band = 0.0                 # Länge, die Kugel senkt sich herab
        self.w, self.vw = 0.0, 0.0      # Pendel in Grad, Winkelgeschwindigkeit
        self.an_pfote = False
        self.k = self.dazu('k', Katze, groesse=0.62, fell=GRAU)
        self.k.neigung = 180
        self.k.richtung = r
        self.k.y = self.oben
        self.k.x = self.aussen(-r)
        self.k.tempo = self.tempo * 0.6

    def kugel(self):
        if self.an_pfote:
            q = self.k.trafo().map(QPointF(36, -26))
            return q.x(), q.y()
        a = math.radians(self.w)
        return (self.kx + math.sin(a) * self.band * self.s,
                self.oben + math.cos(a) * self.band * self.s)

    def schubs(self, staerke):
        def f(sz):
            sz.vw += staerke
        return Tu(f)

    def ablauf(self):
        r, s = self.richtung, self.s
        tatze = lambda st: [Mit('k', Stehe(0.25, Pose(arm_v=-70, kopf_vorn=True))), self.schubs(r * st),  # noqa: E731
                            Mit('k', Stehe(0.4, Pose(arm_v=0, kopf_vorn=True, blick_x=0.6, blick_y=1)))]
        return [
            Wandel(1.0, band=LANG),
            Mit('k', Gehe(bis=self.kx - r * 95 * s, neigung=180)),
            Mit('k', Stehe(1.0, lambda d, u: Pose(kopf_vorn=True, blick_y=1, blick_x=math.sin(self.w / 20),
                                                  auge_zu=blinzeln(d.t)))),
            *tatze(80), Warte(0.6),
            *tatze(120), Warte(0.5),
            Mit('k', Stehe(0.6, Pose(kopf_vorn=True, blick_y=1, mund_offen=True))),
            *tatze(260), *tatze(200),
            Warte(0.4),
            Setze(an_pfote=True, band=0.0),
            Mit('k', Stehe(0.9, lambda d, u: Pose(kopf_vorn=True, sorge=0.6, arm_v=-30, auge_zu=0.4 < u < 0.55))),
            Mit('k', Stehe(0.6, Pose(kopf_vorn=True, auge_zu=True, arm_v=-30))),
            Mit('k', Gehe(bis=self.aussen(-r), tempo=1.2, neigung=180,
                          haltung=lambda p, d: Pose(bein_v=p.bein_v, bein_h=p.bein_h, arm_v=-30, hub=p.hub))),
        ]

    def schreck_ablauf(self):
        self.nebenbei.clear()
        k = self.k
        neu = []
        if k.figur_sichtbar():
            neu = [Mit('k', Setze(buckel=1.0, striche=True, pose=Pose(kopf_vorn=True, schreck=1.0))), Warte(0.25),
                   Mit('k', Setze(striche=False)), Mit('k', Renne(zum='rand', tempo=4.0, neigung=180))]
        return neu + ([] if self.an_pfote else [Wandel(0.3, band=0.0)])

    def weiter(self, dt):
        self.k.neigung = 180            # läuft kopfüber an der Kante
        self.vw += -self.w * 9 * dt - self.vw * 0.6 * dt
        self.w += self.vw * dt
        self.w = max(-80.0, min(80.0, self.w))

    def zeichne_vorn(self, p):
        s = self.s
        if self.band <= 0 and not self.an_pfote:
            return
        if not self.k.zeige_figur and self.an_pfote:
            return
        x, y = self.kugel()
        p.setPen(stift(GOLD, 1.8 * s))
        p.drawLine(QPointF(self.kx if not self.an_pfote else x, self.oben if not self.an_pfote else y - 8 * s),
                   QPointF(x, y - KUGEL * s))
        p.setPen(KEIN_STIFT)
        p.setBrush(GOLD_HELL)
        p.drawRect(QRectF(x - 3 * s, y - (KUGEL + 4) * s, 6 * s, 5 * s))
        p.setBrush(radial(x - 4 * s, y - 4 * s, KUGEL * 1.6 * s, QColor('#FF8090'), ROT.darker(140)))
        kreis(p, x, y, KUGEL * s)
        p.setBrush(QColor(255, 255, 255, 190))
        kreis(p, x - 4 * s, y - 5 * s, 3 * s)

    def grenzen_extra(self):
        s = self.s
        if self.band <= 0 and not self.an_pfote:
            return QRectF()
        x, y = self.kugel()
        return QRectF(min(x, self.kx) - 30 * s, self.oben, abs(x - self.kx) + 60 * s, y - self.oben + 30 * s)
