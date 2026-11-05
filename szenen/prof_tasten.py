import math
import random

from PyQt6.QtCore import QPointF, QRectF
from PyQt6.QtGui import QColor

from zeichnen.figur import Pose
from zeichnen.grundlagen import blinzeln, glatt
from zeichnen.labor_d import Truemmer, WAGEN_OBEN, zeichne_tastatur_gross
from zeichnen.labor import zeichne_taste

from .basis import Gehe, Jeweils, Nebenbei, Schaue, Setze, Stehe, Tu, Wandel
from .professor import FUNKEN, HaareHoch, triumph_pose
from .prof_klopfen import STAUB, ComputerSzene, Hau, wuetend

TASTEN_FARBEN = [QColor('#F6F1E2'), QColor('#F6F1E2'), QColor('#C9BFA4'), QColor('#E8E2D0'),
                 QColor('#EC3A4F'), QColor('#3FA65A'), QColor('#FFD84F')]
TASTE_G = 2.4        # fliegende Tasten, vergrößert
KOPF_TASTE = (-2, -232)


class Tasten(ComputerSzene):
    """Er haut auf die Tastatur, die Tasten fliegen wie Konfetti; nach einer Pause
    fällt die letzte auf seinen Kopf, er schaut empört nach oben."""
    name, titel, reihenfolge = 'tasten', 'Tastenregen', 83

    def vorbereiten(self):
        self.computer_vorbereiten(0.1)
        self.fehlt = 0
        self.letzte = None          # (x, y, dreh) der letzten Taste im Flug
        self.auf_kopf = False

    def tastatur_punkt(self, sz=None, dx=0):
        return self.wx - self.rand * (14 - dx) * self.s, self.boden - (WAGEN_OBEN + 6) * self.s

    # -- Tasten

    def tasten_fliegen(self, sz, k, anzahl=16):
        self.fehlt = min(18, self.fehlt + 10)
        self.stoss(10, 1.0)
        x0, y0 = self.tastatur_punkt()
        for _ in range(anzahl):
            x = x0 + random.uniform(-45, 45) * self.s
            self.truemmer.append(Truemmer(
                'taste', x, y0 - 4 * self.s, random.uniform(-260, 260) * self.s, -random.uniform(420, 720) * self.s,
                random.uniform(0, 360), random.uniform(-900, 900), TASTE_G, random.choice(TASTEN_FARBEN),
                durch=True, flattern=random.uniform(170, 300)))
        self.streue(x0, y0, 6, FUNKEN, tempo=220, dauer=0.5, r=(3, 6), art='stern')
        self.streue(x0, y0, 8, STAUB, tempo=110, dauer=0.6, r=(4, 9))

    def blauer_schirm(self, sz):
        self.farbe, self.gesicht = 'blau', -1.0
        self.stoss(0, 0.4)

    def letzte_flug(self, dauer):
        """Die letzte Taste: steil nach oben, schwebt, trudelt dann genau auf seinen Kopf."""
        x0, y0 = self.tastatur_punkt()
        hoch = self.boden - 360 * self.s
        ox = x0 - self.rand * 30 * self.s

        def flug(sz, u):
            if u < 0.55:
                f = 1 - (1 - u / 0.55) ** 2
                sz.letzte = (x0 + (ox - x0) * f, y0 + (hoch - y0) * f, u * 900)
                return
            q = sz.trafo().map(QPointF(*KOPF_TASTE))
            f = min(1.0, (u - 0.55) / (dauer - 0.55))
            g = f * f * (0.4 + 0.6 * f)
            x = ox + (q.x() - ox) * glatt(f) + math.sin(u * 4.5) * 34 * sz.s * (1 - f)
            y = hoch + (q.y() - hoch) * g
            sz.letzte = (x, y, 30 * math.sin(u * 4.5) * (1 - f) + 15 * f)
        return Nebenbei(Jeweils(dauer, flug))

    def zweiter_schlag(self, dauer):
        self.tasten_fliegen(self, 1, 14)
        self.letzte_flug(dauer).beginn(self)

    def bonk(self, sz):
        self.letzte = None
        self.auf_kopf = True
        q = self.trafo().map(QPointF(*KOPF_TASTE))
        self.streue(q.x(), q.y(), 6, FUNKEN, tempo=150, dauer=0.6, r=(3, 6), art='stern')

    # -- Zeichnen

    def zeichne_requisiten(self, p):
        self.zeichne_wagen(p)
        self.zeichne_monitor(p)
        x, y = self.tastatur_punkt()
        p.save()
        p.translate(x, y + 6 * self.s - self.mon_hopp * 0.5)
        p.scale(self.s, self.s)
        zeichne_tastatur_gross(p, 0, 0, self.fehlt)
        p.restore()

    def zeichne_davor(self, p):
        self.zeichne_truemmer(p)
        if self.letzte:
            x, y, d = self.letzte
            self.taste(p, x, y, d)
        if self.auf_kopf and self.zeige_figur:
            q = self.trafo().map(QPointF(*KOPF_TASTE))
            self.taste(p, q.x(), q.y() - self.haare * 20 * self.s, 12 * self.richtung)

    def taste(self, p, x, y, dreh):
        p.save()
        p.translate(x, y)
        p.scale(self.s * 3.8, self.s * 3.8)
        zeichne_taste(p, 0, 0, dreh, QColor('#EC3A4F'))
        p.restore()

    def requisiten_kasten(self):
        k = super().requisiten_kasten()
        if self.letzte:
            x, y, _ = self.letzte
            k = k.united(QRectF(x - 12 * self.s, y - 12 * self.s, 24 * self.s, 24 * self.s))
        return k

    def grenzen(self):
        k = super().grenzen()
        if self.auf_kopf and self.zeige_figur:
            q = self.trafo().map(QPointF(*KOPF_TASTE))
            k = k.united(QRectF(q.x() - 12 * self.s, q.y() - 34 * self.s, 24 * self.s, 30 * self.s))
        return k

    # -- Ablauf

    def ablauf(self):
        self.x = self.aussen(self.rand)
        tippen = lambda sz, u: Pose(arm_v=sz.arm_zu(*sz.tastatur_punkt(dx=6)) + 10 * math.sin(u * 22),
                                    arm_h=sz.arm_zu(*sz.tastatur_punkt(dx=-6)) - 10 * math.sin(u * 22),
                                    arm_v_x=14, blick_y=-0.2, auge_zu=blinzeln(sz.t))
        haemmern = lambda sz, u: Pose(arm_v=sz.arm_zu(*sz.tastatur_punkt(dx=6)) + 20 * math.sin(u * 40),
                                      arm_h=sz.arm_zu(*sz.tastatur_punkt(dx=-6)) - 20 * math.sin(u * 40),
                                      arm_v_x=14, blick_y=-0.3, sorge=0.8, wipp=3 * math.sin(u * 30))
        ziel = lambda sz: sz.tastatur_punkt()
        nach_letzter = 1.0 + 1.1 + 1.5
        return [
            Gehe(bis=self.innen(98)),
            Setze(richtung=self.rand),
            Stehe(1.4, tippen),
            Tu(self.blauer_schirm),
            Stehe(0.5, lambda sz, u: Pose(arm_v=-60, sorge=0.6, blick_y=-0.4)),
            Stehe(1.0, haemmern),
            Stehe(0.4, lambda sz, u: Pose(arm_v=-50, sorge=1.0, blick_y=-0.4)),
            HaareHoch(0.4),
            wuetend(0.4),
            Hau(ziel, n=1, takt=0.8, holen=-110, beide=True, treffer=self.tasten_fliegen, nach=0.45),
            Hau(ziel, n=1, takt=0.7, holen=-110, beide=True,
                treffer=lambda sz, k: self.zweiter_schlag(nach_letzter + 0.3), nach=0.3),
            Setze(haare=0.0),
            Stehe(1.0, lambda sz, u: Pose(blick_y=0.3, arm_v=-20, auge_zu=blinzeln(sz.t), mund_offen=u > 0.5)),
            Schaue(1.1),
            Stehe(1.5, triumph_pose),
            Tu(self.bonk),
            Wandel(0.07, stauchen=0.84),
            Wandel(0.18, stauchen=1.0),
            Stehe(0.25, Pose(kopf_vorn=True, auge_zu=True, arm_v=-20, arm_h=20)),
            HaareHoch(0.3),
            Stehe(1.7, lambda sz, u: Pose(blick_y=-1.0, sorge=0.2, arm_v=-35, arm_h=35, arm_v_x=16,
                                          auge_zu=0.9 < u < 1.0, wipp=1.5 * math.sin(u * 3))),
            Stehe(0.9, lambda sz, u: Pose(kopf_vorn=True, blick_y=-0.6, arm_v=-35, arm_h=35, arm_v_x=16)),
            Setze(haare=0.0),
            *self.schieb_abgang(),
        ]

    def schreck_ablauf(self):
        self.letzte = None
        self.auf_kopf = False
        return self.schreck_puff()
