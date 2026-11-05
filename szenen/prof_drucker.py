import math
import random

from PyQt6.QtCore import QRectF
from PyQt6.QtGui import QColor

from zeichnen.figur import Pose
from zeichnen.grundlagen import WEISS, blinzeln, glatt
from zeichnen.labor_e import PAPIER, drucker_schlitz, zeichne_blatt, zeichne_drucker, zeichne_papierberg, \
    zeichne_winkehand

from .basis import Gehe, Jeweils, Nebenbei, Setze, Stehe, Tu, Wandel, Warte
from .professor import RAUCH
from .prof_laptop import GeraetSzene, Hieb, qualm

G = 1.3
BERG_B = 175
BERG_MAX = 250
PAPIERFETZEN = [PAPIER, WEISS, QColor('#E6E8EE')]


class Drucker(GeraetSzene):
    """Der Drucker liefert brav ein Blatt, dann spuckt er endlos Papier. Ein Hieb macht es
    nur schlimmer, der Papierberg begräbt den Professor, eine Hand winkt heraus. Ein letztes
    Blatt segelt herab und legt sich genau über die Hand. Dann schlurft der Berg davon."""
    name, titel, reihenfolge = 'drucker', 'Papierlawine', 88

    def vorbereiten(self):
        r = self.richtung
        self.seite = r
        self.drucker_x = self.vom_rand(0.06)
        self.stand = self.drucker_x + r * 118 * self.s
        self.berg_x = self.stand
        self.berg = 0.0
        self.laeuft = 0.0
        self.wut = 0.0
        self.kaputt = 0.0
        self.spuck = 0.0          # Blätter je Sekunde
        self._spuck_rest = 0.0
        self.blaetter = []        # fliegende Blätter: [t0, dauer, x0, y0, x1, y1, dreh]
        self.erstes = 0.0         # erstes Blatt schiebt sich aus dem Schlitz
        self.hand = 0.0           # 0: keine Hand, 1: Hand ragt heraus
        self.letztes = None       # (x, y, dreh) des letzten Blattes
        self.wedeln = True

    # -- Orte

    def schlitz(self):
        return drucker_schlitz(self.drucker_x, self.boden, self.s * G, self.seite)

    def drucker_punkt(self, lx, ly):
        return self.drucker_x + self.seite * lx * G * self.s, self.boden + ly * G * self.s

    def hand_ort(self):
        return self.berg_x + self.seite * 6 * self.s, self.boden - (self.berg - 8 - 70 * (1 - self.hand)) * self.s

    # -- Ablauf im Hintergrund

    def weiter(self, dt):
        super().weiter(dt)
        if self.erschreckt:
            return
        if self.spuck > 0:
            self._spuck_rest += self.spuck * dt
            while self._spuck_rest >= 1:
                self._spuck_rest -= 1
                x0, y0 = self.schlitz()
                ziel_x = self.berg_x + random.uniform(-0.45, 0.45) * BERG_B * self.s
                ziel_y = self.boden - (max(self.berg, 120) * random.uniform(0.5, 1.0)) * self.s
                self.blaetter.append([self.t, random.uniform(0.35, 0.55), x0, y0, ziel_x, ziel_y,
                                      random.uniform(-200, 200)])
        self.blaetter = [b for b in self.blaetter if self.t - b[0] < b[1]]

    # -- Zeichnen

    def zeichne_requisiten(self, p):
        p.save()
        p.translate(self.drucker_x, self.boden)
        p.scale(G * self.s, G * self.s)
        zeichne_drucker(p, 0, 0, self.t, self.laeuft, self.wut, self.kaputt, self.seite)
        p.restore()
        if 0 < self.erstes < 1:
            x, y = self.schlitz()
            p.save()
            p.translate(x + self.seite * 16 * self.erstes * self.s, y)
            p.scale(self.s, self.s)
            zeichne_blatt(p, 0, 0, 90 * self.seite, 1.0)
            p.restore()

    def zeichne_davor(self, p):
        s = self.s
        if self.hand > 0:
            hx, hy = self.hand_ort()
            p.save()
            p.translate(hx, hy)
            p.scale(s * 1.4, s * 1.4)
            w = 22 * math.sin(self.t * 9) if self.wedeln else 4
            zeichne_winkehand(p, 0, 0, w * self.seite, 34)
            p.restore()
        if self.berg > 0:
            p.save()
            p.translate(self.berg_x, self.boden)
            p.scale(s, s)
            zeichne_papierberg(p, 0, 0, self.berg, BERG_B)
            p.restore()
        if self.letztes:
            x, y, dreh, flach = self.letztes
            p.save()
            p.translate(x, y)
            p.scale(s * 1.5, s * 1.5)
            zeichne_blatt(p, 0, 0, dreh, flach)
            p.restore()
        for t0, dauer, x0, y0, x1, y1, dreh in self.blaetter:
            f = (self.t - t0) / dauer
            x = x0 + (x1 - x0) * f
            y = y0 + (y1 - y0) * f - 90 * s * math.sin(f * math.pi)
            p.save()
            p.translate(x, y)
            p.scale(s, s)
            zeichne_blatt(p, 0, 0, dreh * f, abs(math.cos(f * 5)), bild=False)
            p.restore()

    def requisiten_kasten(self):
        s = self.s
        k = QRectF(self.drucker_x - 75 * G * s, self.boden - 90 * G * s, 150 * G * s, 90 * G * s)
        hoch = max(self.berg, 0) + (60 if self.hand else 0) + 25
        k = k.united(QRectF(self.berg_x - (BERG_B * 0.6 + 20) * s, self.boden - hoch * s,
                            (BERG_B * 1.2 + 40) * s, hoch * s))
        if self.blaetter:
            x0, y0 = self.schlitz()
            k = k.united(QRectF(min(x0, self.berg_x) - 120 * s, self.boden - (self.berg + 180) * s,
                                abs(self.berg_x - x0) + 240 * s, (self.berg + 180) * s))
        if self.letztes:
            x, y = self.letztes[:2]
            k = k.united(QRectF(x - 40 * s, y - 40 * s, 80 * s, 80 * s))
        return k

    # -- Ablauf

    def ablauf(self):
        r, s = self.richtung, self.s
        self.x = self.aussen(-r)
        knopf = lambda sz: sz.drucker_punkt(15, -36)

        def druecken(sz, u):
            sz.pose = Pose(arm_v=sz.arm_zu(*knopf(sz)) + (6 if 0.3 < u < 0.5 else 0), blick_y=0.4,
                           auge_zu=blinzeln(sz.t))

        def blatt_kommt(sz, u):
            sz.erstes = min(1.0, u / 1.2)
            sz.pose = Pose(arm_v=-40, blick_y=0.4, auge_zu=blinzeln(sz.t), hub=-2 * abs(math.sin(u * 4)))

        def nehmen(sz):
            sz.erstes = 0.0
            sz.halt = lambda p, hx, hy: zeichne_blatt(p, hx + 4, hy - 14, -6, 1.0)
            sz.laeuft = 0.0

        def anschauen(sz, u):
            sz.pose = Pose(arm_v=-100 + 4 * math.sin(u * 3), arm_v_x=14, blick_y=-0.1, auge_zu=blinzeln(sz.t),
                           mund_offen=u > 0.9)

        def wehren(sz, u):
            sz.pose = Pose(arm_v=-120 + 30 * math.sin(u * 16), arm_h=-110 - 30 * math.sin(u * 16), arm_v_x=16,
                           schreck=0.7, sorge=1.0, bein_v=-10, bein_h=10)
            if random.random() < 0.15:
                sz.streue(sz.x + random.uniform(-30, 30) * s, sz.y - random.uniform(80, 200) * s, 1, PAPIERFETZEN,
                          tempo=90, dauer=0.5, r=(3, 6), schwer=True)

        def wut(sz):
            sz.wut, sz.kaputt, sz.spuck = 1.0, 0.6, 16.0

        def begraben(sz, u):
            sz.pose = Pose(arm_v=-150 + 25 * math.sin(u * 14), arm_h=-150 - 25 * math.sin(u * 14), arm_v_x=16,
                           schreck=1.0, sorge=1.0, kopf_vorn=True)
            sz.berg = 70 + (BERG_MAX - 70) * glatt(u / 2.6)
            if sz.berg > 236:
                sz.zeige_figur = False
                sz.hand = min(1.0, sz.hand + 0.08)

        def segeln(sz, u):
            f = min(1.0, u / 2.6)
            hx, hy = sz.hand_ort()
            ziel_y = hy - 50 * s
            y = sz.boden - 430 * s + (ziel_y - (sz.boden - 430 * s)) * f
            x = hx + 46 * s * math.sin(u * 3.2) * (1 - f)
            sz.letztes = (x, y, 24 * math.sin(u * 3.2) * (1 - f), 1.0)

        def zudecken(sz, u):
            f = min(1.0, u / 0.3)
            hx, hy = sz.hand_ort()
            sz.wedeln = False
            sz.letztes = (hx, hy - (60 - 6 * f) * s, -10 * r, 1.0)

        def versinken(sz, u):
            f = glatt(u / 1.2)
            sz.hand = 1 - f
            x, y = sz.berg_x + r * 6 * s, sz.boden - sz.berg * s
            sz.letztes = (x, y - (54 - 46 * f) * s, -10 * r - 60 * r * f, 1.0 - 0.2 * f)

        def schlurfen(sz, u):
            sz.x = sz.berg_x
            if (sz.berg_x - sz.drucker_x) * -r >= 0:
                sz.drucker_x = sz.berg_x
            sz.berg = BERG_MAX + 6 * math.sin(u * 9)
            sz.letztes = (sz.berg_x + r * 6 * s, sz.boden - (sz.berg + 8) * s, -70 * r + 4 * math.sin(u * 9), 0.8)

        return [
            Gehe(bis=self.stand),
            Setze(richtung=-r),
            Stehe(0.4),
            Jeweils(0.6, druecken),
            Setze(laeuft=1.0),
            Jeweils(1.4, blatt_kommt),
            Tu(nehmen),
            Jeweils(1.6, anschauen),
            Stehe(0.6, lambda sz, u: Pose(kopf_vorn=True, arm_v=-60, auge_zu=True, hub=-3 * abs(math.sin(u * 8)))),
            # jetzt legt er los
            Setze(laeuft=1.0, wut=0.4, spuck=4.0),
            Stehe(0.8, lambda sz, u: Pose(kopf_vorn=True, arm_v=-60, schreck=0.8, sorge=0.6)),
            Setze(halt=None, berg=1.0),
            Nebenbei(Wandel(1.6, berg=60)),
            Jeweils(1.4, wehren),
            Hieb(lambda sz: sz.drucker_punkt(-6, -50), wut, aushol=0.4, nach=0.3),
            Nebenbei(Jeweils(7.0, lambda sz, u: qualm(sz, *sz.drucker_punkt(0, -52), 0.3))),
            Wandel(0.2, berg=70),
            Jeweils(3.0, begraben),
            Setze(zeige_figur=False, hand=1.0),
            Jeweils(1.0, lambda sz, u: None),
            Setze(spuck=0.0, wut=0.0, laeuft=0.0),
            Tu(lambda sz: sz.streue(*sz.drucker_punkt(0, -55), 10, RAUCH, tempo=70, dauer=1.0, r=(6, 14))),
            Warte(0.8),
            Jeweils(2.6, segeln),
            Jeweils(0.3, zudecken),
            Warte(0.8),
            Jeweils(1.2, versinken),
            Warte(1.0),
            _Schlurfen(self.aussen(-r), schlurfen),
        ]

    def schreck_ablauf(self):
        s = self.s
        if self.berg > 0:
            for _ in range(int(14 + self.berg / 6)):
                self.streue(self.berg_x + random.uniform(-0.5, 0.5) * BERG_B * s,
                            self.boden - random.uniform(0, self.berg) * s, 1, PAPIERFETZEN, tempo=420, dauer=0.9,
                            r=(4, 8), schwer=True, richtung=-math.pi / 2, streuung=1.3)
        self.blaetter = []
        self.letztes = None
        if not self.zeige_figur and abs(self.x - self.stand) < 1:
            self.zeige_figur = True
        return self.schreck_rennen()


class _Schlurfen(Jeweils):
    """Der Papierberg schlurft zum Rand hinaus."""

    def __init__(self, rand_x, funktion):
        super().__init__(60.0, funktion)
        self.rand_x = rand_x

    def weiter(self, sz, u, dt):
        sz.berg_x += sz.richtung * sz.tempo * 0.55 * dt
        self.funktion(sz, u)

    def fertig(self, sz, u):
        return (sz.berg_x - self.rand_x) * sz.richtung >= 0
