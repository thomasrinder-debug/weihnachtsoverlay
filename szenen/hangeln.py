import math
import random

from PyQt6.QtCore import QPointF, QRectF
from PyQt6.QtGui import QColor, QPainterPath

from zeichnen.figur import Pose
from zeichnen.figuren import Wichtel
from zeichnen.grundlagen import GOLD_HELL, WEISS, blinzeln, kreis, stift
from zeichnen.requisiten import zeichne_lichterkette

from .basis import Gehe, Mit, Renne, Setze, Stehe, Szene, Tu, Wandel, Warte

ARM = 128          # von den Füßen bis zu den Händen (Einheiten des Wichtels)
FUNKEN = [GOLD_HELL, WEISS]


def hangeln(pose, d):
    w = d.phase * 0.9
    return Pose(arm_v=-150 + 14 * math.sin(w), arm_h=155 - 14 * math.sin(w), arm_v_x=14,
                bein_v=-20 + 18 * math.sin(w + 1), bein_h=10 - 18 * math.sin(w + 1), auge_zu=pose.auge_zu,
                mund_offen=pose.mund_offen)


class Hangeln(Szene):
    """Unter dem oberen Rand rollt sich eine Lichterkette aus. Ein Wichtel hangelt sich
    daran entlang, baumelt, winkt mit einer Hand und bekommt von einem Birnchen einen
    kleinen Schlag. Dann hangelt er zurück und die Kette rollt sich wieder ein."""
    name, titel, reihenfolge = 'hangeln', 'Hangeln oben', 23

    def vorbereiten(self):
        self.zeige_figur = False
        r = self.richtung
        self.w = self.dazu('w', Wichtel, groesse=0.62)
        self.w.richtung = r
        self.w.x = self.aussen(-r)
        self.w.tempo = self.tempo * 0.45
        self.start = self.aussen(-r)
        self.ende_x = self.vom_rand(random.uniform(0.38, 0.45))
        self.laenge = 0.0
        self.an = 1.0
        self.haken = 220 * self.s

    def kette_y(self, x):
        """Höhe der durchhängenden Kette an der Stelle x."""
        s = self.s
        u = ((x - self.geo.left()) / self.haken) % 1.0
        return self.oben + 8 * s + 46 * s * math.sin(math.pi * u)

    def ablauf(self):
        r = self.richtung
        winken = lambda d, u: Pose(arm_v=-100 + 25 * math.sin(u * 10), arm_v_x=14, arm_h=155,  # noqa: E731
                                   bein_v=-10 * math.sin(u * 3), bein_h=10 * math.sin(u * 3), kopf_vorn=True,
                                   mund_offen=(u * 4) % 2 < 1, auge_zu=blinzeln(d.t))
        baumeln = lambda d, u: Pose(arm_v=-150, arm_h=155, arm_v_x=14, bein_v=-30 * math.sin(u * 4),  # noqa: E731
                                    bein_h=30 * math.sin(u * 4), kopf_vorn=True, blick_x=math.sin(u * 2),
                                    auge_zu=blinzeln(d.t))
        return [
            Wandel(1.2, laenge=1.0),
            Mit('w', Gehe(bis=self.vom_rand(random.uniform(0.2, 0.26)), haltung=hangeln)),
            Mit('w', Stehe(1.6, baumeln)),
            Mit('w', Stehe(1.5, winken)),
            Mit('w', Stehe(0.6, lambda d, u: Pose(arm_v=-150, arm_h=155, arm_v_x=14, kopf_vorn=True,
                                                  blick_y=-1, auge_zu=blinzeln(d.t)))),
            Tu(lambda sz: sz.zack()),
            Mit('w', Stehe(0.5, lambda d, u: Pose(arm_v=-150, arm_h=155, arm_v_x=14, kopf_vorn=True, schreck=1.0,
                                                  bein_v=-40, bein_h=40))),
            Mit('w', Setze(striche=False)),
            Setze(an=1.0),
            Mit('w', Stehe(0.9, lambda d, u: Pose(arm_v=-150, arm_h=155, arm_v_x=14, kopf_vorn=True, sorge=1.0,
                                                  auge_zu=0.4 < u < 0.5))),
            Mit('w', Renne(zum='zurueck', tempo=1.6, haltung=hangeln, neigung=0)),
            Wandel(0.9, laenge=0.0),
        ]

    def schreck_ablauf(self):
        self.nebenbei.clear()
        neu = []
        if self.w.figur_sichtbar():
            neu = [Mit('w', Setze(striche=True, pose=Pose(arm_v=-150, arm_h=155, arm_v_x=14, kopf_vorn=True,
                                                          schreck=1.0, bein_v=-40, bein_h=40))),
                   Warte(0.25), Mit('w', Setze(striche=False)),
                   Mit('w', Renne(zum='rand', tempo=4.5, haltung=hangeln, neigung=0))]
        else:
            self.w.zeige_figur = False
        return neu + [Wandel(0.35, laenge=0.0)]

    def zack(self):
        w = self.w
        q = w.trafo().map(QPointF(0, -ARM))
        self.an = 0.0
        w.striche = True
        self.streue(q.x(), q.y(), 12, FUNKEN, tempo=200, dauer=0.5, r=(3, 6), art='stern')

    def weiter(self, dt):
        w = self.w
        w.neigung = math.sin(self.t * 2.6) * 7
        rad = math.radians(w.neigung * w.richtung)
        hx = w.x + ARM * w.s * math.sin(rad)
        w.y = self.kette_y(hx) + ARM * w.s * math.cos(rad)

    def kette(self):
        bis = self.start + (self.ende_x - self.start) * self.laenge
        a, b = sorted((self.start, bis))
        pfad = QPainterPath()
        n = max(2, int((b - a) / (6 * self.s)))
        for i in range(n + 1):
            x = a + (b - a) * i / n
            if i == 0:
                pfad.moveTo(x, self.kette_y(x))
            else:
                pfad.lineTo(x, self.kette_y(x))
        return pfad, a, b

    def zeichne_hinten(self, p):
        if self.laenge <= 0:
            return
        pfad, a, b = self.kette()
        zeichne_lichterkette(p, pfad, self.s, self.an, self.t, abstand=30, groesse=1.3)
        s = self.s
        p.setPen(stift(QColor('#8A8F98'), 2.2 * s))
        x = self.geo.left()
        while x < b:
            if x > a:
                p.drawLine(QPointF(x, self.oben), QPointF(x, self.oben + 9 * s))
            x += self.haken
        p.setPen(stift(QColor(0, 0, 0, 0), 0))
        p.setBrush(QColor('#1E4A2A'))
        ende = b if self.richtung > 0 else a
        kreis(p, ende, self.kette_y(ende), 4 * s)

    def grenzen_extra(self):
        if self.laenge <= 0:
            return QRectF()
        _, a, b = self.kette()
        return QRectF(a - 20 * self.s, self.oben, b - a + 40 * self.s, 80 * self.s)
