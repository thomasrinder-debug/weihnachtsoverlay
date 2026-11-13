import math
import random

from PyQt6.QtCore import QPointF, QRectF
from PyQt6.QtGui import QColor

from zeichnen.figur import Pose
from zeichnen.figuren import WichtelSteif
from zeichnen.grundlagen import GOLD_HELL, WEISS
from zeichnen.werkstatt import zeichne_hammer, zeichne_nagel, zeichne_werkblock

from .basis import Erschrecke, Gehe, Jeweils, Mit, Nebenbei, Renne, Schritt, Setze, Stehe, Szene, Tu, Warte, WarteBis
from .werk_basis import STAUB, Blick, greife, hand, hand_trafo, schweiss, verpuffen, welt

WG = 0.65          # Größe des Wichtels
BLOCK_B, BLOCK_H, NAGEL = 50, 66, 30
STERNE = (QColor('#FFE38F'), QColor('#FFF4C2'))


def arm_winkel(d, zx, zy):
    """Armwinkel des Wichtels, mit dem der verlängerte Arm auf (zx, zy) zeigt."""
    q = d.trafo().map(QPointF(8, -96 + d.pose.hub))
    vx, vy = zx - q.x(), zy - q.y()
    return math.degrees(math.atan2(-d.richtung * vx, vy))


class Hammerszene(Szene):
    """Der Weihnachtsmann hält vorsichtig einen Nagel auf den Klotz, der Wichtel klopft zweimal
    daneben, jedes Mal zuckt der Weihnachtsmann. Der Wichtel wirft den kleinen Hammer weg, zieht
    einen Riesenhammer hinter dem Rücken hervor, wankt damit, hält oben inne, der Weihnachtsmann
    kneift die Augen zu. Rums: der Hammer trifft den Weihnachtsmann, der bis zum Bauch im Boden
    steckt, den Nagel noch zwischen den Fingern. Blick ins Publikum, dann versinkt er ganz."""
    name, titel, reihenfolge = 'werk_hammer', 'Hammer und Nagel', 903

    def vorbereiten(self):
        r, s = self.richtung, self.s
        self.xb = self.vom_rand(0.13)
        self.nx = self.xb - r * 6 * s
        self.x = self.aussen(-r)
        self.pose_fest = {'sack': False}
        self.halten = False           # Hand am Nagel
        self.nagel_lose = False       # Nagel hängt in der Hand
        self.versenkt = 0.0
        self.stiel, self.kopf, self.hammer_da, self.wachsen = 30.0, 1.0, True, 1.0
        self.lose = []
        self.weg = False
        self.w = self.dazu('w', WichtelSteif, groesse=WG, knick=1.0)
        self.w.richtung = r
        self.w.x = self.aussen(-r) - r * 60 * s
        self.w.tempo = self.tempo * 1.1
        self.xw = self.nx + r * 58 * s

    def nagelkopf(self):
        return self.nx, self.boden - (BLOCK_H + NAGEL - 2) * self.s

    def ablauf(self):
        r, s = self.richtung, self.s

        def halten(sz, u, angst=0.0, zu=False):
            sz.halten = True
            sz.pose = Pose(sack=False, arm_h=-20, bein_v=-6, bein_h=10, kopf_vorn=angst > 0.5 or zu,
                           sorge=angst, auge_zu=zu or (sz.t % 3.4) < 0.14, blick_y=0.6 if not zu else 0.0,
                           schreck=0.0)
            greife(sz, *sz.nagelkopf(), neigung=20)

        def klopf(ziel_x, zucken):
            def f(sz, u):
                w = sz.w
                tx, ty = ziel_x(sz), sz.boden - BLOCK_H * s
                treff = arm_winkel(w, tx, ty)
                if u < 0.25:
                    a = -60 + (-175 + 60) * u / 0.25
                elif u < 0.33:
                    a = -175 + (treff + 175) * (u - 0.25) / 0.08
                else:
                    a = treff - 8 * math.sin(min(1.0, (u - 0.33) / 0.15) * math.pi)
                w.pose = Pose(arm_v=a, arm_h=-30, bein_v=-10, bein_h=10, blick_y=0.6, kopf_vorn=u > 0.6,
                              sorge=0.3 if u > 0.6 else 0.0)
                if 0.33 <= u < 0.35 and not getattr(sz, '_geklopft', False):
                    sz._geklopft = True
                    sz.streue(tx, ty, 6, STAUB, tempo=70, dauer=0.4, r=(3, 6))
                if u > 0.4:
                    sz._geklopft = False
                if 0.33 <= u < 0.75:
                    k = math.sin(min(1.0, (u - 0.33) / 0.4) * math.pi)
                    sz.halten = False
                    sz.pose = Pose(sack=False, arm_v=-150 * k, arm_h=-60 * k, kopf_vorn=True, schreck=k,
                                   sorge=1.0, mund_offen=True, bein_v=-14 * k, bein_h=14 * k)
                    sz.hopp = zucken * k * s
                    sz.striche = k > 0.3
                    if zucken > 20 and random.random() < 0.2:
                        schweiss(sz, *welt(sz, 10, -230))
                else:
                    sz.hopp, sz.striche = 0.0, False
                    halten(sz, u, angst=1.0 if zucken > 20 else 0.4)
            return f

        def wegwerfen(sz, u):
            w = sz.w
            w.pose = Pose(arm_v=-60 - 140 * min(1.0, u / 0.25), arm_h=-30, kopf_vorn=u < 0.15,
                          blick_y=0.0, sorge=0.0)
            if u >= 0.25 and sz.hammer_da:
                sz.hammer_da = False
                gx, gy = hand(w, True)
                sz.lose.append({'x': gx, 'y': gy, 'w': 0.0, 'stiel': sz.stiel, 'kopf': 1.0,
                                'vx': r * 160 * s, 'vy': -380 * s, 'vw': r * 720, 'liegt': False})
            halten(sz, u, angst=0.6)

        def riesenhammer(sz):
            w = sz.w
            w.pose = Pose(arm_v=-190, arm_h=-170)
            tx, ty = welt(sz, 6, -222)
            q = w.trafo().map(QPointF(8, -96))
            lg = math.hypot(tx - q.x(), ty - q.y()) / (WG * s)
            sz.stiel, sz.kopf, sz.hammer_da, sz.wachsen = lg - 35, 3.4, True, 0.0

        def hervorziehen(sz, u):
            f = min(1.0, u / 0.4)
            sz.wachsen = f
            sz.w.pose = Pose(arm_v=-300 + 110 * f, arm_h=-160, kopf_vorn=f > 0.8, blick_y=-0.4,
                             mund_offen=f > 0.8)
            halten(sz, u, angst=1.0)

        def wanken(sz, u):
            w = sz.w
            z = math.sin(u * 7)
            w.pose = Pose(arm_v=-190 + 28 * z, arm_h=-180 + 28 * z, bein_v=-20 * z, bein_h=20 * z,
                          sorge=0.8, mund_offen=True, kopf_vorn=True, hub=-2)
            w.neigung = -10 * z
            w.x = sz.xw + r * 8 * z * s
            halten(sz, u, angst=1.0)
            if random.random() < 0.1:
                schweiss(sz, w.x, w.y - 140 * WG * s)

        def innehalten(sz, u):
            w = sz.w
            w.neigung = 0.0
            w.x = sz.xw
            w.pose = Pose(arm_v=-200, arm_h=-195, bein_v=-14, bein_h=14, kopf_vorn=True, auge_zu=u > 0.4,
                          sorge=0.0)
            halten(sz, u, angst=1.0, zu=u > 0.15)
            sz.pose.kopf_vorn = True

        def schlag(sz, u):
            w = sz.w
            treff = arm_winkel(w, *welt(sz, 6, -222))
            f = min(1.0, u / 0.1)
            w.pose = Pose(arm_v=-200 + (treff + 200) * f * f, arm_h=-195 + (treff + 195) * f * f,
                          bein_v=-24, bein_h=24, mund_offen=True)

        def einschlag(sz):
            hx, hy = welt(sz, 6, -222)
            sz.halten, sz.nagel_lose = False, True
            sz.versenkt = 1.0
            sz.y = sz.boden + 118 * s
            sz.stauchen = 0.78
            sz.neigung = 0.0
            sz.streue(hx, hy, 9, STERNE, tempo=160, dauer=0.9, r=(5, 9), art='stern')
            sz.streue(sz.x, sz.boden, 18, STAUB, tempo=160, dauer=0.7, r=(8, 15))
            sz.pose = Pose(sack=False, arm_v=-100, arm_h=-40, kopf_vorn=True, schreck=1.0, mund_offen=True)

        def loslassen(sz):
            w = sz.w
            gx, gy = hand(w, True)
            hx, hy = hand_trafo(w, True).map(QPointF(0, sz.stiel)).x(), hand_trafo(w, True).map(QPointF(0, sz.stiel)).y()
            sz.hammer_da = False
            sz.lose.append({'x': gx, 'y': gy, 'w': math.degrees(math.atan2(-(hx - gx), hy - gy)),
                            'stiel': sz.stiel, 'kopf': sz.kopf, 'vx': -r * 40 * s, 'vy': 0.0,
                            'vw': r * 200, 'liegt': False})

        def benommen(sz, u):
            sz.stauchen = 1.0 - 0.22 * math.exp(-u * 9) * math.cos(u * 30)
            sz.pose = Pose(sack=False, arm_v=-100, arm_h=-30, kopf_vorn=True, schreck=max(0.0, 1 - u * 2),
                           auge_zu=0.6 < u < 0.75 or 1.05 < u < 1.2, sorge=0.2)
            if random.random() < 0.3:
                hx, hy = welt(sz, 6, -230)
                sz.streue(hx + math.cos(sz.t * 9) * 30 * s, hy, 1, STERNE, tempo=10, dauer=0.5, r=(4, 7),
                          art='stern')

        def versinken(sz, u):
            sz.y = sz.boden + (118 + 200 * min(1.0, u / 1.0) ** 2) * s
            sz.pose = Pose(sack=False, arm_v=-178, arm_h=-30, kopf_vorn=True, auge_zu=True, sorge=0.3)

        return [
            Nebenbei(Mit('w', Gehe(bis=self.xw)), Mit('w', Setze(richtung=-r)),
                     Mit('w', Stehe(9, Pose(arm_v=-60, arm_h=-30, blick_y=0.5)))),
            Gehe(bis=self.nx - r * 70 * s, tempo=1.3),
            Jeweils(0.35, lambda sz, u: halten(sz, u)),
            WarteBis(lambda sz: abs(sz.w.x - sz.xw) < 1 and sz.w.richtung == -r),
            Tu(lambda sz: sz.nebenbei.clear()),
            Jeweils(0.85, klopf(lambda sz: sz.nx + r * 14 * s, 14)),
            Jeweils(0.9, klopf(lambda sz: sz.nx - r * 13 * s, 30)),
            Mit('w', Stehe(0.35, lambda d, u: Pose(arm_v=-110, arm_h=-30, kopf_vorn=False, blick_y=-0.2))),
            Jeweils(0.4, wegwerfen),
            Tu(riesenhammer),
            Jeweils(0.45, hervorziehen),
            Jeweils(1.3, wanken),
            Jeweils(0.7, innehalten),
            Jeweils(0.1, schlag),
            Tu(einschlag),
            Warte(0.12),
            Tu(loslassen),
            Mit('w', Stehe(0.3, Pose(arm_v=-150, arm_h=-140, kopf_vorn=True, schreck=1.0, mund_offen=True))),
            Nebenbei(Mit('w', Gehe(bis=lambda d: d.sz.xb - r * 130 * s, tempo=0.5,
                                   haltung=lambda p, d: _schleichen(p))), Mit('w', Renne(zum='rand'))),
            Jeweils(1.4, benommen),
            Setze(stauchen=1.0),
            Jeweils(1.1, versinken),
            Setze(zeige_figur=False),
            Tu(lambda sz: sz.aufraeumen()),
            WarteNebenbeiUndTeilchen(),
        ]

    def aufraeumen(self):
        s = self.s
        verpuffen(self, self.xb, self.boden, BLOCK_B * s, BLOCK_H * s, 10)
        for h in self.lose:
            verpuffen(self, h['x'], h['y'], 40 * s, 20 * s, 6)
        self.lose.clear()
        self.weg = True

    def schreck_ablauf(self):
        self.nebenbei.clear()
        self.halten = False
        w = self.w
        if self.hammer_da and self.stiel > 40:
            self.hammer_da = False
        w.neigung = 0.0
        self.aufraeumen()
        if self.versenkt:
            neu = []
            if w.zeige_figur and w.figur_sichtbar():
                neu.append(Nebenbei(Mit('w', Erschrecke(0.3, 40)), Mit('w', Renne(zum='rand'))))
            else:
                w.zeige_figur = False
            self.pose = Pose(sack=False, arm_v=-178, arm_h=-170, kopf_vorn=True, schreck=1.0)
            self.striche = True
            return neu + [Jeweils(0.4, lambda sz, u: setattr(sz, 'y', sz.y + 1400 * sz.s / 60)),
                          Setze(zeige_figur=False, striche=False), WarteNebenbeiUndTeilchen()]
        self.neigung, self.hopp, self.stauchen = 0.0, 0.0, 1.0
        return self.schreck_alle()

    def weiter(self, dt):
        s = self.s
        for h in self.lose:
            if h['liegt']:
                continue
            h['vy'] += 1500 * s * dt
            h['x'] += h['vx'] * dt
            h['y'] += h['vy'] * dt
            h['w'] += h['vw'] * dt
            boden = self.boden - 7 * h['kopf'] * WG * s
            if h['y'] >= boden and h['vy'] > 0:
                ziel = 90 if (h['w'] % 360) < 180 else 270
                h.update(y=boden, liegt=True, w=ziel)
                hx = h['x'] + (-math.sin(math.radians(ziel))) * h['stiel'] * WG * s
                self.streue(hx, self.boden, 8, STAUB, tempo=90, dauer=0.5, r=(5, 10))

    def zeichne_werkstueck(self, p):
        p.save()
        p.translate(self.xb, self.boden)
        p.scale(self.s, self.s)
        zeichne_werkblock(p, BLOCK_B, BLOCK_H)
        p.restore()
        if not self.nagel_lose:
            p.save()
            p.translate(self.nx, self.boden - BLOCK_H * self.s)
            p.scale(self.s, self.s)
            zeichne_nagel(p, NAGEL)
            p.restore()

    def zeichne_vorn(self, p):
        s = self.s
        if not self.weg:
            self.zeichne_werkstueck(p)
        if self.nagel_lose and self.zeige_figur:
            hx, hy = hand(self)
            p.save()
            p.translate(hx, hy - 6 * s)
            p.scale(s, s)
            zeichne_nagel(p, NAGEL)
            p.restore()
        if self.hammer_da and self.w.zeige_figur:
            p.save()
            p.setTransform(hand_trafo(self.w, True), True)
            p.scale(self.wachsen, self.wachsen)
            zeichne_hammer(p, self.stiel, self.kopf)
            p.restore()
        for h in self.lose:
            p.save()
            p.translate(h['x'], h['y'])
            p.rotate(h['w'])
            p.scale(WG * s, WG * s)
            zeichne_hammer(p, h['stiel'], h['kopf'])
            p.restore()

    def grenzen_extra(self):
        s = self.s
        k = QRectF()
        if not self.weg:
            k = QRectF(self.xb - 40 * s, self.boden - (BLOCK_H + NAGEL + 10) * s, 80 * s, (BLOCK_H + NAGEL + 12) * s)
        if self.hammer_da and self.w.zeige_figur:
            gx, gy = hand(self.w, True)
            lg = (self.stiel + 20 * self.kopf) * WG * s
            k = k.united(QRectF(gx - lg, gy - lg, 2 * lg, 2 * lg))
        for h in self.lose:
            lg = (h['stiel'] + 20 * h['kopf']) * WG * s
            k = k.united(QRectF(h['x'] - lg, h['y'] - lg, 2 * lg, 2 * lg))
        if self.nagel_lose and self.zeige_figur:
            hx, hy = hand(self)
            k = k.united(QRectF(hx - 10 * s, hy - 50 * s, 20 * s, 60 * s))
        return k


def _schleichen(p):
    p.kopf_vorn = True
    p.sorge = 1.0
    p.arm_v, p.arm_h = -100, -90
    return p


class WarteNebenbeiUndTeilchen(Schritt):
    def fertig(self, sz, u):
        return not sz.nebenbei and not sz.wolke and not sz.splitter
