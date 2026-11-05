import math

from PyQt6.QtCore import QPointF, QRectF

from zeichnen.figur import Pose
from zeichnen.grundlagen import WEISS, blinzeln
from zeichnen.requisiten import zeichne_topf

from .basis import Gehe, Jeweils, Mit, Setze, Stehe, Tu, Wandel, Warte, WarteBis
from .schneemann_bau import SchneemannBau

KOPF_OBEN = (4, -214)        # Scheitel des Schneemanns, darauf sitzt der Topf


class SchneemannTopf(SchneemannBau):
    """Drei Kugeln rollen herein und stapeln sich zum Schneemann ohne Mütze. Ein alter
    Kochtopf fliegt herein, landet auf dem Kopf und drückt ihn wie eine Ziehharmonika
    zusammen; erst als er den Topf mit den Zweigarmen anhebt, schnellt er wieder hoch."""
    name, titel, reihenfolge = 'topf', 'Schneemann mit Topf', 33

    def vorbereiten(self):
        super().vorbereiten()
        self.sm.muetze = False
        self.topf = None          # None, 'auf' oder Flugbahn [x, y, vx, vy, dreh]
        self.topf_f = 0.0         # Flug von der Seite auf den Kopf, 0..1
        self.topf_hoch = 0.0      # Abstand über dem Kopf (Einheiten)
        self.topf_kipp = 0.0

    def kopf_welt(self):
        q = self.sm.trafo().map(QPointF(KOPF_OBEN[0], KOPF_OBEN[1] - self.topf_hoch))
        return q.x(), q.y()

    def ablauf(self):
        r, s = self.richtung, self.s
        start = (self.aussen(-r), self.boden - 330 * s)

        def flug(sz, u):
            f = min(1.0, u / 0.9)
            kx, ky = sz.kopf_welt()
            sz.topf = [start[0] + (kx - start[0]) * f, start[1] + (ky - start[1]) * f - 160 * s * 4 * f * (1 - f),
                       0, 0, -540 * (1 - f)]

        def quetschen(sz, u):
            sz.sm.stauchen = 0.55 + 0.08 * math.sin(u * 30) * math.exp(-u * 5)

        def schnellen(sz, u):
            sz.sm.stauchen = 1 + 0.25 * math.exp(-u * 4) * math.cos(u * 18)

        return [
            Mit('sm', Setze(pose=Pose(auge_zu=True))),
            *self.rolle(0, 0, 1.2),
            *self.rolle(1, -95, 1.1),
            *self.springe(1, 0.45),
            *self.rolle(2, -80, 1.0),
            *self.springe(2, 0.5, 150),
            Mit('sm', Stehe(1.2, lambda d, u: Pose(kopf_vorn=u > 0.4, auge_zu=blinzeln(d.t) or u < 0.4,
                                                    sorge=0.2))),
            Mit('sm', Setze(pose=Pose(kopf_vorn=True, blick_x=-0.6, blick_y=-1, sorge=0.6))),
            Jeweils(0.9, flug),
            Setze(topf='auf'),
            Tu(lambda sz: sz.streue(*sz.kopf_welt(), 10, WEISS, tempo=120, dauer=0.5, r=(3, 6))),
            Mit('sm', Setze(pose=Pose(kopf_vorn=True, auge_zu=True, sorge=1.0))),
            Jeweils(0.8, quetschen),
            Mit('sm', Stehe(1.4, lambda d, u: Pose(kopf_vorn=True, sorge=1.0, blick_x=math.sin(u * 3),
                                                    auge_zu=0.6 < u < 0.75))),
            Mit('sm', Stehe(0.5, lambda d, u: Pose(kopf_vorn=True, sorge=0.8, arm_v=-200 * min(1.0, u / 0.4),
                                                    arm_h=-200 * min(1.0, u / 0.4)))),
            Wandel(0.12, topf_hoch=30),
            Jeweils(1.0, schnellen),
            Mit('sm', Setze(stauchen=1.0)),
            Mit('sm', Stehe(0.6, Pose(kopf_vorn=True, mund_offen=True, arm_v=-200, arm_h=-200))),
            Wandel(0.3, topf_hoch=0.0),
            Mit('sm', Stehe(0.4, Pose(kopf_vorn=True, auge_zu=True))),
            Wandel(0.25, topf_kipp=-25),
            Mit('sm', Stehe(0.8, Pose(kopf_vorn=True, arm_v=-140, mund_offen=True))),
            Wandel(0.2, topf_kipp=0.0),
            Mit('sm', Gehe(bis=self.aussen(-r), tempo=1.1)),
        ]

    def schreck_ablauf(self):
        neu = super().schreck_ablauf()
        self.sm.stauchen = 1.0
        if self.topf is not None:
            x, y = self.kopf_welt() if self.topf == 'auf' else self.topf[:2]
            self.topf = [x, y, self.sm.naechster_rand() * 900 * self.s, -700 * self.s, 0.0]
        return neu + [WarteBis(lambda sz: sz.topf is None)]

    def weiter(self, dt):
        super().weiter(dt)
        t = self.topf
        if self.erschreckt and isinstance(t, list):
            t[3] += 1400 * self.s * dt
            t[0] += t[2] * dt
            t[1] += t[3] * dt
            t[4] += 700 * dt
            if not self.geo.adjusted(-80, -80, 80, 80).contains(QPointF(t[0], t[1])):
                self.topf = None

    def zeichne_vorn(self, p):
        if self.topf is None:
            return
        p.save()
        if self.topf == 'auf':
            p.setTransform(self.sm.trafo(), True)
            dx = self.sm.teile[2][0]
            p.translate(KOPF_OBEN[0] + dx, KOPF_OBEN[1] + 6 - self.topf_hoch)
            p.rotate(self.topf_kipp)
        else:
            p.translate(self.topf[0], self.topf[1])
            p.rotate(self.topf[4])
            p.scale(self.sm.s, self.sm.s)
        zeichne_topf(p)
        p.restore()

    def grenzen_extra(self):
        k = super().grenzen_extra()
        if self.topf is not None:
            x, y = self.kopf_welt() if self.topf == 'auf' else self.topf[:2]
            r = 60 * self.s
            k = k.united(QRectF(x - r, y - r, 2 * r, 2 * r))
        return k
