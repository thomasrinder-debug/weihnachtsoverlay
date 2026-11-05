import math
import random

from PyQt6.QtCore import QPointF, QRectF

from zeichnen.figur import Pose
from zeichnen.grundlagen import KEIN_STIFT, blinzeln, linear
from zeichnen.labor import METALL, METALL_DUNKEL, zeichne_blitz, zeichne_teslaspule
from zeichnen.labor_a import bommel_lokal, zeichne_kabel_bogen, zeichne_kippschalter, zeichne_leuchtbommel

from .basis import Erschrecke, Gehe, Jeweils, Setze, Stehe, Tu, Wandel
from .professor import FUNKEN, ProfSzene, triumph_pose, ziehen

PULT_H = 92


class Leuchtbommel(ProfSzene):
    """Ein Funke der Tesla-Spule stellt ihm die Haare auf, die Bommel glüht. Er schaltet
    die Spule aus, sie wird dunkel, er aber leuchtet weiter und präsentiert sich stolz als Lampe."""
    name, titel, reihenfolge = 'leuchtbommel', 'Leuchtbommel', 62

    def vorbereiten(self):
        r, s = self.richtung, self.s
        self.spule_x = self.vom_rand(0.2) + r * 50 * s
        self.px = self.spule_x - r * 104 * s
        self.pult_x = self.spule_x - r * 50 * s
        self.an, self.schalter = 0.0, False
        self.bommel = 0.0
        self.funke = False

    # -- Lagen

    def kugel(self):
        return self.spule_x, self.boden - 96 * self.s

    def schalter_ort(self):
        return self.pult_x, self.boden - (PULT_H + 8) * self.s

    def bommel_welt(self):
        q = self.trafo().map(QPointF(*bommel_lokal(self.pose, self.haare)))
        return q.x(), q.y()

    # -- Zeichnen

    def zeichne_requisiten(self, p):
        s, r = self.s, self.richtung
        p.save()
        p.translate(0, self.boden)
        p.scale(s, s)
        sx, px = self.spule_x / s, self.pult_x / s
        zeichne_kabel_bogen(p, px, -6, sx - r * 20, -6, 6)
        p.setPen(KEIN_STIFT)
        p.setBrush(linear(px - 3, 0, px + 3, 0, METALL, METALL_DUNKEL))
        p.drawRect(QRectF(px - 2.5, -PULT_H, 5, PULT_H))
        p.drawRoundedRect(QRectF(px - 12, -4, 24, 4), 2, 2)
        zeichne_kippschalter(p, px, -PULT_H, self.schalter)
        zeichne_teslaspule(p, sx, 0, self.an, self.t)
        p.restore()

    def zeichne_davor(self, p):
        s = self.s
        if self.funke and self.zeige_figur:
            kx, ky = self.kugel()
            hx, hy = self.trafo().map(QPointF(-8, -232)).x(), self.trafo().map(QPointF(-8, -232)).y()
            saat = int(self.t * 20)
            for k in range(2):
                p.save()
                p.translate(kx, ky)
                p.scale(s, s)
                zeichne_blitz(p, -self.richtung * 14 * k, -4 * k, (hx - kx) / s, (hy - ky) / s + 10 * k, saat + k,
                              2.6 - k)
                p.restore()
        if self.bommel > 0 and self.zeige_figur:
            bx, by = self.bommel_welt()
            p.save()
            p.translate(bx, by)
            p.scale(s * 1.12, s * 1.12)
            zeichne_leuchtbommel(p, 0, 0, self.bommel, self.t)
            p.restore()

    def requisiten_kasten(self):
        s = self.s
        k = QRectF(self.spule_x - 46 * s, self.boden - 140 * s, 92 * s, 140 * s)
        k = k.united(QRectF(self.pult_x - 14 * s, self.boden - (PULT_H + 26) * s, 28 * s, (PULT_H + 26) * s))
        if self.bommel > 0 and self.zeige_figur:
            bx, by = self.bommel_welt()
            k = k.united(QRectF(bx - 80 * s, by - 80 * s, 160 * s, 160 * s))
        return k

    # -- Ablauf

    def ablauf(self):
        r, s = self.richtung, self.s
        self.x = self.aussen(-r)

        def schalten(sz, u):
            return Pose(arm_v=sz.arm_zu(*sz.schalter_ort()), blick_y=0.5, auge_zu=blinzeln(sz.t))

        def staunen(sz, u):
            return Pose(blick_y=-0.6, mund_offen=True, arm_v=-150, arm_v_x=12, auge_zu=blinzeln(sz.t))

        def zucken(sz, u):
            if random.random() < 0.3:
                bx, by = sz.trafo().map(QPointF(-6, -225)).x(), sz.trafo().map(QPointF(-6, -225)).y()
                sz.streue(bx, by, 1, FUNKEN, tempo=150, dauer=0.4, r=(3, 5), art='stern')
            z = math.sin(u * 60)
            return Pose(kopf_vorn=True, schreck=1.0, arm_v=-40 + 15 * z, arm_h=40 - 15 * z, arm_v_x=18,
                        bein_v=-6 * z, bein_h=6 * z, hub=-3 * abs(z))

        def lampe(sz, u):
            sz.bommel = 1.0 + 0.15 * math.sin(u * 4)
            return triumph_pose(sz, u)

        return [
            Gehe(bis=self.px),
            Setze(richtung=r),
            Stehe(0.5, lambda sz, u: Pose(blick_y=-0.2, auge_zu=blinzeln(sz.t))),
            Stehe(0.4, schalten),
            Setze(schalter=True),
            Wandel(0.5, an=1.0),
            Stehe(1.2, staunen),
            Wandel(0.6, neigung=9.0),
            Stehe(0.5, lambda sz, u: Pose(blick_y=-0.7, arm_v=-100 - 20 * u, arm_v_x=14, mund_offen=True)),
            Setze(funke=True),
            Jeweils(0.9, lambda sz, u: setattr(sz, 'pose', zucken(sz, u))),
            Wandel(0.01, haare=1.0, gluehen=1.0, neigung=0.0),
            Setze(funke=False),
            Wandel(0.4, bommel=1.0),
            Stehe(1.4, lambda sz, u: Pose(blick_y=-0.9, sorge=0.4, auge_zu=(u % 0.7) < 0.12, mund_offen=u > 0.7)),
            Stehe(0.5, schalten),
            Setze(schalter=False),
            Wandel(0.5, an=0.0),
            Stehe(0.9, lambda sz, u: Pose(blick_y=0.1, auge_zu=0.4 < u < 0.55)),
            Stehe(0.7, lambda sz, u: Pose(kopf_vorn=True, blick_y=-0.8, sorge=0.3)),
            Stehe(2.0, lampe),
            Setze(bommel=1.0, mitnehmen=('spule_x', 'pult_x')),
            Gehe(bis=self.aussen(-r) - r * 220 * s, haltung=ziehen),
        ]

    def schreck_ablauf(self):
        self.nebenbei.clear()
        self.funke = False
        tief = 330 * self.s
        sichtbar = self.zeige_figur and self.figur_sichtbar()
        if not sichtbar:
            self.zeige_figur = False
            return [Wandel(0.45, senke=tief)] + self._ende()
        return [Erschrecke(0.3, 46),
                Wandel(0.12, haare=0.0, gluehen=0.0, bommel=0.0, an=0.0),
                Wandel(0.45, y=lambda sz: sz.y + tief, senke=tief),
                Tu(lambda sz: setattr(sz, 'zeige_figur', False))] + self._ende()
