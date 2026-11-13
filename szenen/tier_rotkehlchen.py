import math

from PyQt6.QtGui import QColor

from zeichnen.figur import Pose
from zeichnen.tiere import KEHLCHEN_BRAUN, KEHLCHEN_ROT, Rotkehlchen

from .basis import Hoppel, Jeweils, Mit, Schritt, Setze, Stehe, Szene, Tu, Wandel, Warte
from .tier_gemeinsam import SCHNEE, publikumsblick, sterne

VOGEL_G = 1.6
FLAUM = [KEHLCHEN_BRAUN.lighter(120), KEHLCHEN_BRAUN, KEHLCHEN_ROT, QColor('#F4ECE0')]


def radius(d):
    return 17 * d.plustern * d.s


class Rollen(Schritt):
    """Die Federkugel rollt in Richtung 'seite' (-1/1). bis=None: aus dem Bild; sonst bremst sie
    in 'dauer' Sekunden bis x=bis ab."""

    def __init__(self, seite, tempo=2.5, bis=None, dauer=1.0):
        self.seite_v, self.tempo, self.bis_v, self.dauer = seite, tempo, bis, dauer

    def beginn(self, sz):
        self.seite = self.seite_v(sz) if callable(self.seite_v) else self.seite_v
        self.x0 = sz.x
        self.bis = self.bis_v(sz) if callable(self.bis_v) else self.bis_v

    def weiter(self, sz, u, dt):
        alt = sz.x
        if self.bis is None:
            v = sz.tempo * self.tempo * min(1.0, 0.3 + u * 1.5)
            sz.x += self.seite * v * dt
        else:
            f = min(1.0, u / self.dauer)
            sz.x = self.x0 + (self.bis - self.x0) * (1 - (1 - f) ** 2)
        weg = (sz.x - alt) * sz.richtung
        sz.roll += math.degrees(weg / radius(sz))
        sz.pose = Pose(bein_v=40 * math.sin(sz.t * 25), schreck=1.0)

    def fertig(self, sz, u):
        if self.bis is None:
            return u > 0.1 and not sz.figur_sichtbar()
        return u >= self.dauer


class Plusterkugel(Szene):
    """Ein frierendes Rotkehlchen plustert sich bei jeder kalten Bö weiter auf: rund, kugelrund,
    riesengroß auf dünnen Beinchen. Zufrieden blinzelt es ins Publikum – da kippt die nächste Bö
    die Federkugel um, sie rollt aus dem Bild, prallt draußen irgendwo an und rollt rückwärts
    wieder herein. Kopfüber bleibt sie liegen; dann zieht das Rotkehlchen alle Federn an und
    steht spindeldürr und schlotternd da."""
    name, titel, reihenfolge = 'tier_rotkehlchen', 'Plusterkugel', 760

    def vorbereiten(self):
        self.zeige_figur = False
        self.v = self.dazu('v', Rotkehlchen, groesse=VOGEL_G, plustern=1.0, fluegel=0.0, zittern=0.0, roll=0.0, duenn=1.0)

    def boe(self, n=14, tempo=420):
        r = self.richtung
        w = 0.0 if -r > 0 else math.pi
        for _ in range(n):
            y = self.boden - __import__('random').uniform(10, 180) * self.s
            x = self.v.x + r * __import__('random').uniform(120, 260) * self.s
            self.streue(x, y, 1, SCHNEE, tempo=tempo, dauer=0.9, r=(2, 4), richtung=w, streuung=0.08)

    def aufplustern(self, k):
        def f(sz):
            v = sz.v
            sz.streue(v.x, v.y - radius(v) - 14 * v.s, 6, FLAUM, tempo=70, dauer=0.6, r=(2, 4))
        return [Tu(f), Mit('v', Wandel(0.14, plustern=k * 1.08)), Mit('v', Wandel(0.12, plustern=k))]

    def frieren(self, dauer):
        return [Tu(lambda sz: sz.boe()), Mit('v', Setze(zittern=1.0)),
                Mit('v', Stehe(dauer, Pose(sorge=1.0, auge_zu=False))), Mit('v', Setze(zittern=0.0))]

    def ablauf(self):
        r = self.richtung
        froh = lambda d, u: Pose(auge_zu=u > 0.1)  # noqa: E731
        return [
            Mit('v', Hoppel(bis=self.vom_rand(0.1), tempo=0.8, hoehe=16)),
            Mit('v', Setze(richtung=r)),
            # drei Böen, drei Mal aufplustern
            *self.frieren(0.45),
            *self.aufplustern(1.9),
            Mit('v', Stehe(0.35, froh)),
            *self.frieren(0.4),
            *self.aufplustern(2.9),
            Mit('v', Stehe(0.3, froh)),
            *self.frieren(0.35),
            *self.aufplustern(4.2),
            Mit('v', Jeweils(0.6, lambda d, u: setattr(d, 'neigung', 7 * math.sin(u * 14) * (1 - u / 0.6)))),
            Mit('v', Setze(neigung=0.0)),
            publikumsblick('v', 0.75),
            # die große Bö
            Tu(lambda sz: sz.boe(30, 600)),
            Mit('v', Stehe(0.25, Pose(schreck=1.0))),
            Mit('v', Rollen(-r, 2.6)),
            Warte(0.35),
            Tu(lambda sz: sterne(sz, sz.geo.left() + 30 * sz.s if r > 0 else sz.geo.right() - 30 * sz.s,
                                 sz.boden - 120 * sz.s, 7)),
            Warte(0.25),
            Mit('v', Rollen(r, bis=lambda d: self.vom_rand(0.12) + r * 0.0, dauer=1.3)),
            Mit('v', Setze(roll=lambda d: d.roll % 360.0)),
            Mit('v', Wandel(0.25, roll=180.0)),
            Mit('v', Stehe(0.8, lambda d, u: Pose(bein_v=10 * math.sin(u * 12), auge_zu=0.3 < u < 0.42))),
            # Luft raus
            Tu(lambda sz: sz.federwolke()),
            Mit('v', Wandel(0.1, plustern=0.95, duenn=0.6)),
            Mit('v', Setze(roll=0.0, zittern=2.0)),
            Mit('v', Stehe(0.9, lambda d, u: Pose(sorge=1.0, kopf_vorn=True, auge_zu=0.4 < u < 0.5))),
            Mit('v', Setze(richtung=-r)),
            Mit('v', Hoppel(tempo=1.6, hoehe=18)),
        ]

    def federwolke(self):
        v = self.v
        self.streue(v.x, v.y - radius(v) - 14 * v.s, 26, FLAUM, tempo=200, dauer=1.0, r=(3, 6))

    def schreck_ablauf(self):
        self.nebenbei.clear()
        v = self.v
        if not v.figur_sichtbar():
            v.zeige_figur = False
            return [Warte(0.01)]
        if v.plustern > 1.5:
            return [Mit('v', Setze(pose=Pose(schreck=1.0))), Mit('v', Rollen(v.naechster_rand(), 4.0))]
        v.roll, v.zittern = 0.0, 0.0
        return [Mit('v', Setze(pose=Pose(schreck=1.0), richtung=v.naechster_rand())),
                Mit('v', Hoppel(tempo=3.4, hoehe=24))]
