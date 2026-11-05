import math
import random

from PyQt6.QtCore import QPointF, QRectF
from PyQt6.QtGui import QColor, QTransform

from zeichnen.figur import Pose
from zeichnen.grundlagen import blinzeln, glatt
from zeichnen.labor import GLAS_RAND, zeichne_brenner, zeichne_kolben, zeichne_labortisch, zeichne_stativ
from zeichnen.labor_a import muetze_trafo, zeichne_explosion
from zeichnen.professor import zeichne_muetze_prof

from .basis import Gehe, Setze, Stehe, Tu, Wandel, WarteBis
from .professor import QUALM, RAUCH, Knall, ProfSzene, Publikumsblick, Umkippen, explodiert, triumph_pose

GIFTGRUEN = QColor('#5BD16A')
TISCH_H = 72
RING_H = 62
HUT_FLUG = 2.9


class Bumm(ProfSzene):
    """Kolben über dem Brenner. Erst ein Pff, er guckt verdutzt und dreht die Flamme
    hoch. Es brodelt wild, Triumph-Pose, Bumm: Blitz, riesige Wolke, Rußgesicht, Haare
    qualmen zu Berge. Trockener Blick ins Publikum, Husten, die Mütze landet obenauf,
    und er kippt steif wie ein Brett um."""
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

        def blubb(staerke):
            def pose(sz, u):
                sz.blasen = min(1.0, 0.4 + u)
                sz.wackel = staerke
                if random.random() < 0.1 + 0.3 * staerke:
                    x, y = sz.kolben_mitte()
                    sz.streue(x, y - 26 * s, 1, RAUCH, tempo=40 + 60 * staerke, dauer=0.7, r=(4, 9),
                              richtung=-math.pi / 2, streuung=0.5)
                return Pose(blick_y=0.5, arm_v=-150, arm_v_x=12, auge_zu=blinzeln(sz.t))
            return pose

        def puff(sz):
            x, y = sz.kolben_mitte()
            sz.streue(x, y - 24 * s, 6, RAUCH, tempo=70, dauer=0.6, r=(6, 11), richtung=-math.pi / 2, streuung=0.6)
            sz.haare = 0.35

        def hochdrehen(sz, u):
            sz.flamme = 1.0 + 0.8 * min(1.0, u / 0.3)
            ziel = (sz.geraet_x() + r * 12 * s, sz.boden - (TISCH_H + 10) * s)
            return Pose(arm_v=sz.arm_zu(*ziel), blick_y=0.6, mund_offen=True)

        def triumph(sz, u):
            sz.wackel = 1.0 + 0.6 * u
            if random.random() < 0.3:
                x, y = sz.kolben_mitte()
                sz.streue(x, y - 26 * s, 1, RAUCH, tempo=80, dauer=0.6, r=(5, 10), richtung=-math.pi / 2,
                          streuung=0.6)
            return triumph_pose(sz, u)

        def knall(sz):
            x, y = sz.kolben_mitte()
            sz.knall_t, sz.hut_t = sz.t, sz.t
            sz.kolben_da, sz.flamme, sz.blasen, sz.wackel = False, 0.0, 0.0, 0.0
            sz.muetze = False
            sz.streue(x, y, 12, [QColor(215, 238, 255, 200), GLAS_RAND], tempo=300, dauer=0.8, r=(2, 4),
                      schwer=True)

        def landen(sz):
            sz.hut_t, sz.muetze = None, True
            sz.streue(sz.x, sz.y - 300 * s, 6, QUALM, tempo=40, dauer=0.5, r=(4, 7))

        def weg_im_rauch(sz):
            sz.weg(QUALM)
            k = sz.figur_kasten()
            for _ in range(14):
                sz.streue(random.uniform(k.left(), k.right()), random.uniform(k.top(), k.bottom()), 1, QUALM,
                          tempo=80, dauer=0.8, r=(10, 18))
            sz.zeige_figur, sz.qualm = False, 0.0

        return [
            Gehe(bis=self.px, tempo=1.8),
            Setze(richtung=r),
            Stehe(0.35, anzuenden),
            Tu(lambda sz: setattr(sz, 'flamme', 1.0)),
            Stehe(0.8, blubb(0.15)),
            Tu(puff),
            Stehe(0.6, lambda sz, u: Pose(kopf_vorn=True, auge_zu=0.1 < u < 0.3, blick_y=-0.3)),
            Wandel(0.15, haare=0.0),
            Stehe(0.5, hochdrehen),
            Stehe(0.8, blubb(0.6)),
            Stehe(1.0, triumph),
            Knall(lambda sz: sz.kolben_mitte(), groesse=1.3),
            Tu(knall),
            Stehe(0.7, explodiert),
            Publikumsblick(),
            Tu(landen),
            Stehe(0.45, lambda sz, u: Pose(kopf_vorn=True, auge_zu=True, hub=-3 * math.sin(min(1, u / 0.2) * math.pi))),
            Umkippen(0.5),
            Stehe(0.7, lambda sz, u: Pose(kopf_vorn=True, auge_zu=True, arm_v=-8, arm_h=8)),
            Tu(weg_im_rauch),
            WarteBis(lambda sz: not sz.wolke and not sz.splitter),
        ]

    def schreck_ablauf(self):
        if self.hut_t is not None:
            k = self.hut_trafo().mapRect(QRectF(-40, -60, 80, 72))
            self.streue(k.center().x(), k.center().y(), 10, RAUCH, tempo=90, dauer=0.6, r=(6, 12))
            self.hut_t = None
        self.knall_t = None
        if abs(self.neigung) > 20:
            self.weg(QUALM)
            return self.schreck_puff()
        return self.schreck_kittel()
