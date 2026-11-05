import math
import random
from dataclasses import replace

from PyQt6.QtCore import QPointF, QRectF
from PyQt6.QtGui import QColor, QTransform

from zeichnen.figur import Pose, zeichne_schreckstriche
from zeichnen.figuren import Wichtel
from zeichnen.grundlagen import GOLD_HELL, KEIN_STIFT, WEISS, blinzeln, teilchen_kasten
from zeichnen.labor_b import kescher_mitte, zeichne_ball, zeichne_kescher
from zeichnen.professor import hand_lokal

from .basis import Erschrecke, Gehe, Jeweils, Mit, Nebenbei, Setze, Stehe, Tu, Wandel, Warte, WarteBis, WarteNebenbei
from .professor import RAUCH, HaareHoch, ProfSzene

RB = 12                 # Ballradius
STIEL = 70
K_WINKEL = 25
ARM_V, ARM_H = -42, -50
SCHWERE = 1100          # Einheiten/s²


def kopfueber(x, y, s, richtung, stauchen=1.0):
    """Figur steht kopfüber an der Oberkante: nur senkrecht gespiegelt, Blickrichtung bleibt."""
    tr = QTransform()
    tr.translate(x, y)
    tr.scale(s * richtung * (2 - stauchen), -s * stauchen)
    return tr


class Ball:
    def __init__(self, farbe, streifen):
        self.farbe, self.streifen = farbe, streifen
        self.zustand = 'hand'
        self.x = self.y = self.v = 0.0
        self.dreh = 0.0
        self.da = True


class Schwerkraft(ProfSzene):
    """Kopfüber an der Oberkante: sein Ball fällt brav nach unten in seinen Kescher, der Ball
    des Wichtels fällt nach oben an die Decke. Der Professor holt seinen Ball heraus, dreht
    ihn prüfend nach allen Seiten, lässt ihn noch einmal fallen: wieder in den Kescher."""
    name, titel, reihenfolge = 'schwerkraft', 'Verkehrte Schwerkraft', 70

    def vorbereiten(self):
        r, s = self.richtung, self.s
        self.y = self.oben
        self.netz = 0.0
        self.mein = Ball(QColor('#D3172E'), GOLD_HELL)
        self.sein = Ball(QColor('#2B7BD9'), WEISS)
        self.w = self.dazu('w', Wichtel, groesse=0.7)
        w = self.w
        w.y = self.oben
        w.x = self.aussen(-r) - r * 70 * s
        w.tempo = self.tempo * 0.85
        w.trafo = lambda: kopfueber(w.x, w.y + w.hopp, w.s, w.richtung, w.stauchen)
        self.w_da = False
        self.halt_h = self.kescher

    # -- Figur kopfüber

    def trafo(self):
        return kopfueber(self.x, self.y + self.hopp, self.s, self.richtung, self.stauchen)

    def kescher(self, p, hx, hy):
        zeichne_kescher(p, hx, hy, K_WINKEL, STIEL, self.netz)

    def netzort(self):
        hx, hy = hand_lokal(self.pose, False)
        q = self.trafo().map(QPointF(*kescher_mitte(hx, hy, K_WINKEL, STIEL, self.netz)))
        return q.x(), q.y()

    def handort(self):
        hx, hy = hand_lokal(self.pose, True)
        q = self.trafo().map(QPointF(hx + 2, hy - 4))
        return q.x(), q.y()

    def w_hand(self):
        w = self.w
        a = math.radians(w.pose.arm_v)
        q = w.trafo().map(QPointF(8 - math.sin(a) * 40, -96 + math.cos(a) * 40 + w.pose.hub))
        return q.x(), q.y()

    # -- Ablauf

    def ablauf(self):
        r, s = self.richtung, self.s
        self.x = self.aussen(-r)
        px = self.vom_rand(random.uniform(0.13, 0.16))
        wx = px + r * 125 * s

        def halten(sz, u=0.0, **mehr):
            werte = dict(arm_v=ARM_V, arm_h=ARM_H, arm_v_x=14, auge_zu=blinzeln(sz.t))
            werte.update(mehr)
            return Pose(**werte)

        def gang(p, sz):
            return replace(p, arm_v=ARM_V + 0.3 * p.arm_v, arm_h=ARM_H, arm_v_x=14)

        def w_halten(d, u):
            return Pose(arm_v=-155, kopf_vorn=True, auge_zu=blinzeln(d.t, 0.7))

        def pruefen(sz, u):
            sz.mein.dreh = 200 * u + 60 * math.sin(u * 5)
            return Pose(arm_v=-22 + 8 * math.sin(u * 3), arm_h=ARM_H, arm_v_x=14, blick_y=0.8,
                        blick_x=0.3 * math.sin(u * 4), sorge=0.6, kopf_vorn=1.0 < u < 1.6,
                        auge_zu=blinzeln(sz.t))

        def greifen(sz, u):
            nx, ny = sz.netzort()
            sz.pose = Pose(arm_v=ARM_V - 60 * math.sin(math.pi * min(1.0, u / 0.5)), arm_h=ARM_H, arm_v_x=14, blick_y=-0.8)
            if u > 0.35 and sz.mein.zustand == 'netz':
                sz.mein.zustand = 'hand'
                sz.netz = 0.0

        def klatschen(d, u):
            k = 30 * abs(math.sin(u * 10))
            return Pose(arm_v=-80 + k, arm_h=-80 - k, kopf_vorn=True, mund_offen=True, auge_zu=u > 0.5,
                        hub=-3 * abs(math.sin(u * 10)))

        return [
            Nebenbei(Warte(0.6), Mit('w', Gehe(bis=wx)), Mit('w', Setze(richtung=-r)),
                     Mit('w', Stehe(0.4, w_halten)), Setze(w_da=True)),
            Gehe(bis=px, haltung=gang),
            Stehe(0.5, halten),
            WarteBis(lambda sz: sz.w_da),
            Stehe(0.6, lambda sz, u: halten(sz, u, blick_y=0.4)),
            Tu(lambda sz: sz.loslassen(sz.mein)),
            Stehe(1.1, lambda sz, u: halten(sz, u, blick_y=-0.9)),
            Stehe(0.7, lambda sz, u: halten(sz, u, kopf_vorn=True, auge_zu=True, hub=-3 * abs(math.sin(u * 8)))),
            Mit('w', Stehe(0.5, w_halten)),
            Tu(lambda sz: sz.loslassen(sz.sein)),
            Nebenbei(Mit('w', Stehe(0.7, lambda d, u: Pose(arm_v=-30, kopf_vorn=True, blick_y=0.9))),
                     Mit('w', Stehe(1.2, klatschen))),
            Stehe(0.5, lambda sz, u: halten(sz, u, blick_y=0.6)),
            Stehe(1.1, lambda sz, u: halten(sz, u, kopf_vorn=True, schreck=0.5, sorge=0.8, blick_x=0.6)),
            Jeweils(0.5, greifen),
            Setze(brille=0.6),
            Stehe(2.2, pruefen),
            Setze(brille=0.0),
            Stehe(0.4, lambda sz, u: halten(sz, u, blick_y=0.4)),
            Tu(lambda sz: sz.loslassen(sz.mein)),
            Stehe(1.0, lambda sz, u: halten(sz, u, blick_y=-0.9)),
            Stehe(1.2, lambda sz, u: Pose(kopf_vorn=True, arm_v=-40, arm_h=ARM_H, arm_v_x=14, sorge=1.0,
                                          blick_x=0.6 * math.sin(u * 3), hub=-2 * math.sin(u * 6))),
            Nebenbei(Mit('w', Gehe(bis=lambda d: d.sz.sein.x + r * 10 * s)),
                     Mit('w', Stehe(0.3, lambda d, u: Pose(arm_v=-10, kopf_vorn=True))),
                     Tu(lambda sz: setattr(sz.sein, 'zustand', 'hand')),
                     Mit('w', Gehe(bis=self.aussen(-r) - r * 30 * s, tempo=1.1))),
            Warte(0.6),
            Gehe(bis=self.aussen(-r), haltung=gang),
            WarteNebenbei(),
        ]

    # -- Bälle

    def loslassen(self, b):
        b.zustand = 'faellt'
        b.v = 0.0

    def weiter(self, dt):
        super().weiter(dt)
        s = self.s
        for b, ich in ((self.mein, True), (self.sein, False)):
            if not b.da:
                continue
            if b.zustand == 'hand':
                b.x, b.y = self.handort() if ich else self.w_hand()
                if not ich:
                    b.y -= RB * 0.4 * s
            elif b.zustand == 'faellt':
                b.v += SCHWERE * s * dt
                if ich:
                    nx, ny = self.netzort()
                    b.y += b.v * dt
                    b.x += (nx - b.x) * min(1.0, dt * 6)
                    b.dreh += 300 * dt
                    if b.y >= ny:
                        b.zustand = 'netz'
                        self.netz = 1.0
                else:
                    b.y -= b.v * dt
                    b.dreh -= 300 * dt
                    if b.y <= self.oben + RB * s:
                        b.y = self.oben + RB * s
                        b.zustand = 'decke'
                        b.v = 0.0
                        self.streue(b.x, self.oben, 5, [WEISS, QColor('#CFEFFF')], tempo=70, dauer=0.4,
                                    r=(2, 4), art='stern')
            elif b.zustand == 'netz':
                b.x, b.y = self.netzort()
                b.y -= RB * 0.5 * s
            elif b.zustand == 'decke':
                b.v = max(0.0, b.v)
        self.netz = max(0.0, self.netz - dt * 2.5) if self.mein.zustand != 'netz' else max(self.netz * 0.98, 0.4)

    # -- Zeichnen

    def zeichne(self, p):
        striche = self.striche, self.w.striche
        self.striche = self.w.striche = False
        super().zeichne(p)
        self.striche, self.w.striche = striche
        for an, fig in ((striche[0], self), (striche[1] and self.w.zeige_figur, self.w)):
            if an:
                q = fig.trafo().map(QPointF(4, -250 if fig is self else -184))
                p.save()
                p.translate(q.x(), q.y())
                p.scale(1, -1)
                zeichne_schreckstriche(p, 0, 0, self.s)
                p.restore()

    def zeichne_davor(self, p):
        s = self.s
        for b, ich in ((self.mein, True), (self.sein, False)):
            if not b.da:
                continue
            if b.zustand == 'hand' and not (self.zeige_figur if ich else self.w.zeige_figur):
                continue
            if b.zustand == 'netz' and not self.zeige_figur:
                continue
            p.save()
            p.translate(b.x, b.y)
            p.scale(s, s)
            zeichne_ball(p, 0, 0, RB, b.dreh, b.farbe, b.streifen)
            p.restore()
        p.setPen(KEIN_STIFT)

    def grenzen(self):
        s = self.s
        k = QRectF()
        if self.zeige_figur:
            k = self.figur_kasten().adjusted(-4 * s, 0, 4 * s, 40 * s * (1 + self.haare))
            hx, hy = hand_lokal(self.pose, False)
            q = self.trafo().map(QPointF(*kescher_mitte(hx, hy, K_WINKEL, STIEL, 1.0)))
            k = k.united(QRectF(q.x() - 30 * s, q.y() - 30 * s, 60 * s, 60 * s))
        for b in (self.mein, self.sein):
            if b.da:
                k = k.united(QRectF(b.x - RB * 2 * s, b.y - RB * 2 * s, RB * 4 * s, RB * 4 * s))
        for d in self.darsteller.values():
            if d.zeige_figur:
                k = k.united(d.kasten().adjusted(0, 0, 0, 34 * s if d.striche else 0))
        for liste in self.teilchen:
            k = k.united(teilchen_kasten(liste))
        return k.intersected(self.geo.adjusted(-400 * s, -400 * s, 400 * s, 0))

    # -- Schreck

    def schreck_ablauf(self):
        s = self.s
        self.nebenbei.clear()
        for b in (self.mein, self.sein):
            if b.zustand in ('faellt', 'decke'):
                b.da = False
                self.streue(b.x, b.y, 10, RAUCH, tempo=90, dauer=0.5, r=(5, 10))
        neu = []
        w = self.w
        if w.zeige_figur and w.figur_sichtbar():
            neu.append(Nebenbei(Mit('w', Erschrecke(0.3, 34)),
                                Mit('w', Wandel(0.35, y=lambda d: d.sz.oben - 240 * s)),
                                Mit('w', Setze(zeige_figur=False))))
        else:
            w.zeige_figur = False
        if self.zeige_figur and self.figur_sichtbar():
            neu += [HaareHoch(1.0), Erschrecke(0.3, 40), Wandel(0.35, y=lambda sz: sz.oben - 300 * s),
                    Setze(zeige_figur=False)]
        else:
            self.zeige_figur = False
        return neu + self._ende()
