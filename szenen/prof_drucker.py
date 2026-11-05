import math
import random
from dataclasses import replace

from PyQt6.QtCore import QPointF, QRectF
from PyQt6.QtGui import QColor, QPainterPath

from zeichnen.figur import Pose
from zeichnen.grundlagen import KEIN_STIFT, WEISS, blinzeln, glatt, linear, stift
from zeichnen.labor import zeichne_labortisch
from zeichnen.labor_e import PAPIER, PAPIER_SCHATTEN, drucker_schlitz, zeichne_blatt, zeichne_drucker, \
    zeichne_papierberg, zeichne_schuhe, zeichne_winkehand

from .basis import Gehe, Jeweils, Schritt, Setze, Stehe, Tu, Wandel, WarteBis
from .geraet import GeraetSzene

G = 1.5
TISCH_H = 80
TISCH_B = 136
BERG_B = 400
BERG_MAX = 330
PAPIERFETZEN = [PAPIER, WEISS, QColor('#E6E8EE')]


class Drucker(GeraetSzene):
    """Der Drucker liefert ein Blatt, der Professor nimmt es zufrieden. Dann drei Blätter,
    dann ein Papierstrom. Er hält den Schlitz zu, ein dicker Papierfächer quillt heraus
    und drückt seine Arme auseinander. Stille, dann begräbt ihn eine Papierlawine.
    Eine Hand winkt heraus, ein letztes Blatt deckt sie zu, sie sinkt. Unter dem Berg
    erscheinen Schuhe, und der Berg schlurft hinaus."""
    name, titel, reihenfolge = 'drucker', 'Papierlawine', 88

    def vorbereiten(self):
        r = self.richtung
        self.seite = r
        self.tisch_x = self.vom_rand(0.07)
        self.berg_x = self.tisch_x + r * 95 * self.s
        self.drucker_da = True
        self.berg = 0.0
        self.heben = 0.0          # 0..1: der Berg hebt sich auf zwei Beine
        self.geh_phase = 0.0
        self.laeuft = 1.0
        self.wut = 0.0
        self.spuck = 0.0          # Blätter je Sekunde
        self._spuck_rest = 0.0
        self.blaetter = []        # fliegende Blätter: [t0, dauer, x0, y0, x1, y1, dreh, bogen]
        self.erstes = 0.0
        self.packen = 0.0         # 0..1: Papierfächer zwischen seinen Händen
        self.packen_hand = None   # (vorn, hinten) Weltpunkte der Hände
        self.winkhand = 0.0
        self.wedeln = 1.0
        self.letztes = None       # (x, y, dreh)
        self.begraben = False

    # -- Orte

    def schlitz(self):
        return drucker_schlitz(self.tisch_x, self.boden - TISCH_H * self.s, self.s * G, self.seite)

    def berg_oben(self, x):
        """y der Bergoberfläche über x (wie zeichne_papierberg)."""
        halb = BERG_B / 2 * min(1.0, 0.45 + self.berg / 140) * self.s
        u = (x - self.berg_x) / halb
        if abs(u) >= 1:
            return self.berg_boden()
        return self.berg_boden() - self.berg * (1 - u * u) ** 0.7 * self.s

    def berg_boden(self):
        return self.boden - 40 * glatt(self.heben) * self.s - 3 * self.s * abs(math.sin(self.geh_phase))

    def hand_ort(self):
        x = self.berg_x + self.seite * 60 * self.s
        return x, self.berg_oben(x) + (24 - 44 * self.winkhand) * self.s

    # -- Ablauf im Hintergrund

    def weiter(self, dt):
        super().weiter(dt)
        if self.erschreckt:
            return
        s = self.s
        if self.spuck > 0:
            self._spuck_rest += self.spuck * dt
            while self._spuck_rest >= 1:
                self._spuck_rest -= 1
                x0, y0 = self.schlitz()
                ziel_x = self.x + self.seite * random.uniform(30, 150) * s
                self.blaetter.append([self.t, random.uniform(0.4, 0.6), x0, y0, ziel_x,
                                      self.boden - random.uniform(5, 30) * s, random.uniform(-300, 300),
                                      random.uniform(90, 170)])
        self.blaetter = [b for b in self.blaetter if self.t - b[0] < b[1]]

    # -- Zeichnen

    def zeichne_requisiten(self, p):
        s = self.s
        if self.drucker_da:
            p.save()
            p.translate(self.tisch_x, self.boden)
            p.scale(s, s)
            zeichne_labortisch(p, TISCH_B, TISCH_H)
            p.restore()
            p.save()
            p.translate(self.tisch_x + self.zitter(), self.boden - TISCH_H * s)
            p.scale(G * s, G * s)
            zeichne_drucker(p, 0, 0, self.t, self.laeuft, self.wut, 0.0, self.seite)
            p.restore()
        if 0 < self.erstes < 1:
            x, y = self.schlitz()
            p.save()
            p.translate(x + self.seite * 20 * self.erstes * s, y)
            p.scale(s * 1.3, s * 1.3)
            zeichne_blatt(p, 0, 0, 90 * self.seite, 1.0)
            p.restore()
        if self.packen_hand:
            self.zeichne_faecher(p)

    def zeichne_faecher(self, p):
        """Dicker Papierfächer, der aus dem Schlitz zwischen seine Hände quillt."""
        s = self.s
        sx, sy = self.schlitz()
        (vx, vy), (hx, hy) = self.packen_hand
        zit = math.sin(self.t * 47) * 2 * s * self.packen

        def oben(f):
            return sx + (vx - sx) * f, sy - 4 * s + (vy - sy) * glatt(f) + zit * f

        def unten(f):
            return sx + (hx - sx) * f, sy + 4 * s + (hy - sy) * glatt(f) - zit * f

        pfad = QPainterPath()
        pfad.moveTo(*oben(0))
        for k in range(1, 11):
            pfad.lineTo(*oben(k / 10))
        mx = (vx + hx) / 2 - self.seite * 14 * s * self.packen
        pfad.quadTo(QPointF(mx, (vy + hy) / 2), QPointF(hx, hy))
        for k in range(9, -1, -1):
            pfad.lineTo(*unten(k / 10))
        pfad.closeSubpath()
        p.setPen(KEIN_STIFT)
        p.setBrush(linear(sx, sy, vx, vy, PAPIER, PAPIER_SCHATTEN))
        p.drawPath(pfad)
        p.setPen(stift(QColor(160, 165, 175, 150), 0.8 * s))
        for k in range(1, 7):
            a = k / 7
            punkte = []
            for j in range(11):
                f = j / 10
                (ox, oy), (ux, uy) = oben(f), unten(f)
                punkte.append(QPointF(ox + (ux - ox) * a, oy + (uy - oy) * a))
            for j in range(10):
                p.drawLine(punkte[j], punkte[j + 1])
        p.setPen(KEIN_STIFT)

    def zeichne_davor(self, p):
        s = self.s
        if self.winkhand > 0:
            hx, hy = self.hand_ort()
            p.save()
            p.translate(hx, hy)
            p.scale(s * 1.5, s * 1.5)
            w = 26 * math.sin(self.t * 10) * self.wedeln
            zeichne_winkehand(p, 0, 0, w * self.seite, 30)
            p.restore()
        if self.heben > 0:
            p.save()
            p.translate(self.berg_x, self.boden)
            p.scale(s * 1.5, s * 1.5)
            zeichne_schuhe(p, 0, 0, 26 * glatt(self.heben), self.geh_phase, -self.seite)
            p.restore()
        if self.berg > 0:
            p.save()
            p.translate(self.berg_x, self.berg_boden())
            p.rotate(2.5 * math.sin(self.geh_phase) * glatt(self.heben))
            p.scale(s, s)
            zeichne_papierberg(p, 0, 0, self.berg, BERG_B, saat=7)
            p.restore()
        if self.letztes:
            x, y, dreh = self.letztes
            p.save()
            p.translate(x, y)
            p.scale(s * 1.7, s * 1.7)
            zeichne_blatt(p, 0, 0, dreh, 1.0)
            p.restore()
        for t0, dauer, x0, y0, x1, y1, dreh, bogen in self.blaetter:
            f = (self.t - t0) / dauer
            x = x0 + (x1 - x0) * f
            y = y0 + (y1 - y0) * f - bogen * s * math.sin(f * math.pi)
            p.save()
            p.translate(x, y)
            p.scale(s * 1.2, s * 1.2)
            zeichne_blatt(p, 0, 0, dreh * f, abs(math.cos(f * 5)), bild=False)
            p.restore()

    def requisiten_kasten(self):
        s = self.s
        k = QRectF(self.tisch_x - (TISCH_B / 2 + 10) * s, self.boden - (TISCH_H + 82 * G) * s,
                   (TISCH_B + 20) * s, (TISCH_H + 82 * G) * s)
        if self.berg > 0:
            hoch = self.berg + 40
            b = BERG_B / 2 + 30
            k = k.united(QRectF(self.berg_x - b * s, self.boden - hoch * s, 2 * b * s, hoch * s))
        if self.winkhand > 0:
            x, y = self.hand_ort()
            k = k.united(QRectF(x - 50 * s, y - 100 * s, 100 * s, 100 * s))
        if self.packen_hand:
            for x, y in self.packen_hand:
                k = k.united(QRectF(x - 20 * s, y - 20 * s, 40 * s, 40 * s))
        for t0, dauer, x0, y0, x1, y1, dreh, bogen in self.blaetter:
            k = k.united(QRectF(min(x0, x1) - 30 * s, min(y0, y1) - (bogen + 30) * s,
                                abs(x1 - x0) + 60 * s, abs(y1 - y0) + (bogen + 60) * s))
        if self.letztes:
            x, y = self.letztes[:2]
            k = k.united(QRectF(x - 40 * s, y - 40 * s, 80 * s, 80 * s))
        return k

    # -- Ablauf

    def ablauf(self):
        r, s = self.richtung, self.s
        self.x = self.aussen(-r)
        sx, sy = self.schlitz()
        stand = sx + r * 62 * s

        def erstes_raus(sz, u):
            sz.erstes = min(0.99, u / 0.45)
            sz.pose = Pose(arm_v=sz.arm_zu(sx + r * 20 * s, sy) if u > 0.25 else -40, blick_y=0.3,
                           auge_zu=blinzeln(sz.t))

        def nehmen(sz):
            sz.erstes = 0.0
            sz.halt = lambda p, hx, hy: zeichne_blatt(p, hx + 4, hy - 16, -8, 1.0)

        def zufrieden(sz, u):
            return Pose(arm_v=-118, arm_v_x=16, kopf_vorn=u > 0.25, blick_y=-0.2, auge_zu=0.45 < u < 0.7,
                        hub=-3 * abs(math.sin(u * 9)), wipp=3 * math.sin(u * 9))

        def drei_blaetter(sz, u):
            sz.pose = Pose(arm_v=-118, arm_v_x=16, schreck=0.6, blick_y=-0.5 * min(1.0, u / 0.3),
                           blick_x=0.3, sorge=0.5)

        def hechten(sz, u):
            sz.halt = None
            f = glatt(min(1.0, u / 0.3))
            sz.packen = 0.0
            sz.x = stand + (sz.halte_x(0.0) - stand) * f
            sz.neigung = 12 * f
            sz.spuck = 0.0 if f >= 1 else 20.0
            zupacken(sz, 0.0, f)

        def zupacken(sz, packen, f=1.0, ruck=0.0):
            spreiz = 8 + 46 * packen + 6 * ruck
            sz.pose = Pose(arm_v=-90 - spreiz, arm_h=-90 + spreiz, arm_v_x=12, bein_v=-22 - 10 * packen,
                           bein_h=18 + 8 * packen, sorge=packen, schreck=0.6 * ruck, mund_offen=ruck > 0.3,
                           auge_zu=ruck > 0.7)
            sz.packen_hand = (sz.hand(True), sz.hand(False)) if f >= 1 else None

        def stolz(sz, u):
            zupacken(sz, 0.0)
            sz.pose = replace(sz.pose, kopf_vorn=u > 0.2, sorge=0.0, auge_zu=0.5 < u < 0.65)
            sz.wut = min(1.0, u * 2)

        def druck(sz, u):
            # drei Stöße, jeder schiebt den Fächer weiter auf
            stufe = min(2, int(u / 0.42))
            v = (u - stufe * 0.42) / 0.42
            ruck = max(0.0, 1 - v * 3)
            ziel = (0.35, 0.68, 1.0)[stufe]
            vor = (0.0, 0.35, 0.68)[stufe]
            sz.packen = vor + (ziel - vor) * glatt(min(1.0, v * 3))
            sz.x = sz.halte_x(sz.packen)
            sz.neigung = 12 - 22 * sz.packen
            zupacken(sz, sz.packen, 1.0, ruck)
            sz.wackel = max(sz.wackel, 0.6 * ruck)

        def lauern(sz, u):
            zupacken(sz, 1.0)
            sz.pose = replace(sz.pose, kopf_vorn=True, sorge=1.0)
            sz.laeuft = 0.0

        def lawine(sz):
            x0, y0 = sz.schlitz()
            sz.packen_hand, sz.packen = None, 0.0
            sz.laeuft, sz.wut, sz.wackel = 1.0, 1.0, 1.0
            for _ in range(26):
                ziel_x = sz.berg_x + random.uniform(-0.45, 0.5) * BERG_B * s
                sz.blaetter.append([sz.t, random.uniform(0.3, 0.6), x0, y0, ziel_x,
                                    sz.boden - random.uniform(80, 300) * s, random.uniform(-400, 400),
                                    random.uniform(60, 200)])
            sz.streue(x0, y0, 30, PAPIERFETZEN, tempo=380, dauer=0.9, r=(4, 8), schwer=True,
                      richtung=-math.pi / 2, streuung=1.4)

        def begraben(sz, u):
            f = min(1.0, u / 0.35)
            sz.berg = BERG_MAX * (1 - (1 - f) ** 2)
            sz.neigung = -10 - 18 * f
            sz.hopp = 20 * s * math.sin(f * math.pi)
            sz.pose = Pose(arm_v=-175, arm_h=-160, arm_v_x=16, schreck=1.0, sorge=1.0, bein_v=-30, bein_h=20,
                           kopf_vorn=True)
            if f >= 1 and not sz.begraben:
                sz.begraben, sz.zeige_figur, sz.hopp, sz.neigung = True, False, 0.0, 0.0
                sz.x = sz.berg_x + r * 60 * s

        def setzen(sz, u):
            sz.berg = BERG_MAX + 10 * math.sin(u * 14) * (1 - u / 0.4)

        def winken(sz, u):
            sz.winkhand = min(1.0, u / 0.15)
            if u > 0.6:
                sz.wedeln = 0.0

        start = {}

        def segeln(sz, u):
            f = min(1.0, u / 0.65)
            if 'p' not in start:
                start['p'] = (sz.tisch_x, sz.berg_oben(sz.tisch_x))
                sz.wut, sz.laeuft = 0.0, 0.0
            x0, y0 = start['p']
            hx, hy = sz.hand_ort()
            x1, y1 = hx, hy - 72 * s
            sz.letztes = (x0 + (x1 - x0) * f, y0 + (y1 - y0) * f - 110 * s * math.sin(f * math.pi),
                          -r * 340 * f + 8 * r)

        def versinken(sz, u):
            f = glatt(min(1.0, u / 0.5))
            sz.winkhand = 1 - f
            hx, hy = sz.hand_ort()
            sz.letztes = (hx, hy - 72 * s + 30 * s * f, 8 * r - 70 * r * f)

        def heben(sz, u):
            sz.heben = min(1.0, u / 0.25)
            sz.drucker_da = False
            hx, _ = sz.hand_ort()
            sz.letztes = (hx, sz.berg_oben(hx) - 4 * s, -62 * r)

        return [
            Gehe(bis=stand, tempo=2.2),
            Setze(richtung=-r),
            Jeweils(0.5, erstes_raus),
            Tu(nehmen),
            Stehe(0.7, zufrieden),
            Setze(spuck=6.0),
            Jeweils(0.5, drei_blaetter),
            Jeweils(0.35, hechten),
            Jeweils(0.55, stolz),
            Jeweils(1.26, druck),
            Jeweils(0.35, lauern),
            Tu(lawine),
            Jeweils(0.4, begraben),
            Jeweils(0.4, setzen),
            Wandel(0.25, wackel=0.0),
            Jeweils(0.8, winken),
            Jeweils(0.65, segeln),
            Stehe(0.25),
            Jeweils(0.5, versinken),
            Stehe(0.35),
            Jeweils(0.45, heben),
            _Schlurfen(self.aussen(-r)),
            WarteBis(lambda sz: not sz.wolke and not sz.splitter),
        ]

    def halte_x(self, packen):
        """x des Professors, wenn er den Fächer in dieser Stärke zwischen den Händen hält."""
        sx, _ = self.schlitz()
        spreiz = math.radians(8 + 46 * packen)
        return sx + self.seite * (14 + 80 * packen + 52 * math.cos(spreiz) + 10) * self.s

    def schreck_ablauf(self):
        s = self.s
        if self.berg > 0:
            for _ in range(int(14 + self.berg / 6)):
                self.streue(self.berg_x + random.uniform(-0.45, 0.45) * BERG_B * s,
                            self.boden - random.uniform(0, self.berg) * s, 1, PAPIERFETZEN, tempo=420, dauer=0.9,
                            r=(4, 8), schwer=True, richtung=-math.pi / 2, streuung=1.3)
        self.blaetter, self.letztes, self.packen_hand = [], None, None
        if self.begraben:
            self.zeige_figur, self.neigung, self.hopp = True, 0.0, 0.0
            self.x = self.berg_x
        return self.schreck_rennen()


class _Schlurfen(Schritt):
    """Der Papierberg schlurft auf zwei Schuhen zum Rand hinaus."""

    def __init__(self, rand_x):
        self.rand_x = rand_x

    def weiter(self, sz, u, dt):
        v = sz.tempo * 1.1 * min(1.0, u / 0.3)
        sz.berg_x -= sz.seite * v * dt
        sz.x = sz.berg_x
        sz.geh_phase += v * dt / (sz.s * 22)
        if sz.letztes:
            hx = sz.berg_x + sz.seite * 60 * sz.s
            sz.letztes = (hx, sz.berg_oben(hx) - 4 * sz.s, -62 * sz.seite)

    def fertig(self, sz, u):
        return (sz.berg_x - self.rand_x) * -sz.seite >= BERG_B * 0.3 * sz.s
