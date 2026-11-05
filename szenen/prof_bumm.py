import math
import random

from PyQt6.QtCore import QPointF, QRectF
from PyQt6.QtGui import QColor, QTransform

from zeichnen.figur import Pose
from zeichnen.grundlagen import blinzeln, glatt
from zeichnen.labor import GLAS_RAND, zeichne_brenner, zeichne_kolben, zeichne_labortisch, zeichne_stativ
from zeichnen.labor_a import muetze_trafo, zeichne_explosion
from zeichnen.professor import zeichne_muetze_prof

from .basis import Gehe, Setze, Stehe, Tu
from .professor import FUNKEN, RAUCH, RUSS, ProfSzene, triumph_pose, ziehen

GIFTGRUEN = QColor('#5BD16A')
TISCH_H = 72
RING_H = 62
HUT_FLUG = 2.9


class Bumm(ProfSzene):
    """Kolben über dem Brenner, Triumph-Pose, Bumm: Rußgesicht, Haare senkrecht, Brille
    schief. Er blinzelt, und die Mütze segelt verspätet herab und landet obenauf."""
    name, titel, reihenfolge = 'bumm', 'Bumm!', 61

    def vorbereiten(self):
        r, s = self.richtung, self.s
        self.tisch_x = self.vom_rand(0.2) + r * 40 * s
        self.px = self.tisch_x - r * 98 * s
        self.flamme, self.blasen, self.wackel = 0.0, 0.0, 0.0
        self.kolben_da = True
        self.knall_t = None
        self.hut_t = None

    def geraet_x(self):
        return self.tisch_x + self.richtung * 6 * self.s

    def kolben_mitte(self):
        return self.geraet_x(), self.boden - (TISCH_H + RING_H + 16) * self.s

    # -- Mütze im Flug

    def hut_versatz(self):
        u = self.t - self.hut_t
        r = self.richtung
        hoch = 300.0
        if u < 0.45:
            f = glatt(u / 0.45)
            return r * 30 * f, -hoch * f, 720 * f * r
        v = min(1.0, (u - 0.45) / (HUT_FLUG - 0.45))
        pendel = math.sin(v * math.pi * 3)
        return r * 30 * (1 - v) + 46 * pendel * (1 - v), -hoch * (1 - v) ** 1.3, 28 * pendel * (1 - v) + 0

    def hut_trafo(self):
        tr = muetze_trafo(self.pose, 1.0, vorn=True) * self.trafo()
        q = tr.map(QPointF(0, -10))
        dx, dy, dreh = self.hut_versatz()
        f = QTransform()
        f.translate(q.x() + dx * self.s, q.y() + dy * self.s)
        f.rotate(dreh)
        f.translate(-q.x(), -q.y())
        return tr * f

    # -- Zeichnen

    def zeichne_requisiten(self, p):
        s, r = self.s, self.richtung
        p.save()
        p.translate(self.tisch_x, self.boden)
        p.scale(s, s)
        zeichne_labortisch(p)
        p.restore()
        p.save()
        p.translate(self.geraet_x(), self.boden - TISCH_H * s)
        p.scale(s * r, s)
        zeichne_stativ(p, 0, 0, RING_H)
        zeichne_brenner(p, 0, 0, self.flamme, self.t)
        if self.kolben_da:
            p.save()
            p.translate(0, -RING_H)
            p.rotate(self.wackel * 7 * math.sin(self.t * 38))
            zeichne_kolben(p, 0, 0, GIFTGRUEN, 0.55, 'rund', groesse=0.9, blasen=self.blasen, t=self.t)
            p.restore()
        else:
            p.setPen(QColor(40, 36, 34, 200))
            for k in range(5):
                p.drawLine(QPointF(-10 + k * 5, -RING_H - 1), QPointF(-11 + k * 5.5, -RING_H - 5 - (k % 2) * 3))
        p.restore()

    def zeichne_davor(self, p):
        if self.knall_t is not None:
            x, y = self.kolben_mitte()
            p.save()
            p.translate(x, y)
            p.scale(self.s, self.s)
            zeichne_explosion(p, 0, 0, (self.t - self.knall_t) / 0.4, 75)
            p.restore()
        if self.hut_t is not None:
            p.save()
            p.setTransform(self.hut_trafo(), True)
            zeichne_muetze_prof(p, 0, 0, 4 * math.sin(self.t * 5))
            p.restore()

    def requisiten_kasten(self):
        s = self.s
        x, y = self.kolben_mitte()
        k = QRectF(self.tisch_x - 70 * s, self.boden - 175 * s, 140 * s, 175 * s)
        if self.knall_t is not None and self.t - self.knall_t < 0.4:
            k = k.united(QRectF(x - 125 * s, y - 125 * s, 250 * s, 250 * s))
        if self.hut_t is not None:
            k = k.united(self.hut_trafo().mapRect(QRectF(-40, -60, 80, 72)))
        return k

    # -- Ablauf

    def ablauf(self):
        r, s = self.richtung, self.s
        self.x = self.aussen(-r)

        def anzuenden(sz, u):
            ziel = (sz.geraet_x() + r * 12 * s, sz.boden - (TISCH_H + 10) * s)
            return Pose(arm_v=sz.arm_zu(*ziel), blick_y=0.6, auge_zu=blinzeln(sz.t))

        def kochen(sz, u):
            sz.blasen = min(1.0, u / 1.0)
            sz.wackel = max(0.0, (u - 0.9) / 1.2) * 0.4
            if random.random() < 0.06:
                x, y = sz.kolben_mitte()
                sz.streue(x, y - 26 * s, 1, RAUCH, tempo=30, dauer=0.8, r=(4, 8), richtung=-math.pi / 2,
                          streuung=0.4)
            return Pose(blick_y=0.3, arm_v=-150, arm_v_x=12, auge_zu=blinzeln(sz.t), mund_offen=u > 1.2)

        def triumph(sz, u):
            sz.wackel = 0.4 + 0.6 * min(1.0, u / 1.2)
            if random.random() < 0.15:
                x, y = sz.kolben_mitte()
                sz.streue(x, y - 26 * s, 1, RAUCH, tempo=50, dauer=0.6, r=(4, 9), richtung=-math.pi / 2,
                          streuung=0.6)
            return triumph_pose(sz, u)

        def knall(sz):
            x, y = sz.kolben_mitte()
            sz.knall_t, sz.hut_t = sz.t, sz.t
            sz.kolben_da, sz.flamme, sz.blasen, sz.wackel = False, 0.0, 0.0, 0.0
            sz.russ, sz.haare, sz.brille, sz.muetze = 1.0, 1.0, 1.0, False
            sz.streue(x, y, 26, RUSS + RAUCH, tempo=170, dauer=1.0, r=(10, 20))
            sz.streue(x, y, 12, FUNKEN, tempo=300, dauer=0.6, r=(3, 6), art='stern')
            sz.streue(x, y, 10, [QColor(215, 238, 255, 200), GLAS_RAND], tempo=260, dauer=0.8, r=(2, 4),
                      schwer=True)

        def benommen(sz, u):
            return Pose(kopf_vorn=True, arm_v=-12, arm_h=12, auge_zu=(u % 0.9) < 0.18, blick_y=-0.6 * min(1, u),
                        mund_offen=True)

        def landen(sz):
            sz.hut_t, sz.muetze = None, True
            sz.streue(sz.x, sz.y - 300 * s, 6, RAUCH, tempo=40, dauer=0.5, r=(4, 7))

        def husten(sz, u):
            if 0.3 < u < 0.32 or 0.75 < u < 0.77:
                q = sz.trafo().map(QPointF(5, -165))
                sz.streue(q.x(), q.y(), 5, RUSS, tempo=60, dauer=0.7, r=(5, 9), richtung=math.pi / 2 - r * 1.2,
                          streuung=0.4)
            return Pose(kopf_vorn=True, arm_v=-60 if (u % 0.45) < 0.25 else -40, arm_v_x=16, auge_zu=True,
                        mund_offen=(u % 0.45) < 0.2, hub=2 * math.sin(u * 14))

        return [
            Gehe(bis=self.px),
            Setze(richtung=r),
            Stehe(0.5, lambda sz, u: Pose(blick_y=0.5, auge_zu=blinzeln(sz.t))),
            Stehe(0.5, anzuenden),
            Tu(lambda sz: setattr(sz, 'flamme', 1.0)),
            Stehe(0.3, anzuenden),
            Stehe(2.0, kochen),
            Stehe(1.5, triumph),
            Tu(knall),
            Stehe(HUT_FLUG, benommen),
            Tu(landen),
            Stehe(0.7, lambda sz, u: Pose(kopf_vorn=True, arm_v=-12, arm_h=12, auge_zu=0.25 < u < 0.4,
                                          blick_y=-0.8, sorge=0.5, hub=-2 * math.sin(min(1, u / 0.2) * math.pi))),
            Stehe(1.1, husten),
            Stehe(0.8, lambda sz, u: Pose(kopf_vorn=True, arm_v=-20, arm_h=20, auge_zu=blinzeln(sz.t),
                                          sorge=0.3)),
            Setze(mitnehmen=('tisch_x',)),
            Gehe(bis=self.aussen(-r) - r * 260 * s, haltung=ziehen),
        ]

    def schreck_ablauf(self):
        if self.hut_t is not None:
            k = self.hut_trafo().mapRect(QRectF(-40, -60, 80, 72))
            self.streue(k.center().x(), k.center().y(), 10, RAUCH, tempo=90, dauer=0.6, r=(6, 12))
            self.hut_t = None
        self.knall_t = None
        return self.schreck_kittel()
