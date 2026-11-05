import math
import random

from PyQt6.QtCore import QRectF
from PyQt6.QtGui import QColor

from zeichnen.figur import Pose
from zeichnen.grundlagen import blinzeln, glatt
from zeichnen.labor import METALL
from zeichnen.labor_e import SCHRAUB_OBEN, harmonika_breite, zeichne_harmonika, zeichne_schraubstock

from .basis import Erschrecke, Gehe, Jeweils, Schaue, Setze, Stehe, Tu, Wandel, Warte
from .professor import HaareHoch, denk_pose, schieben, triumph_pose
from .prof_laptop import GeraetSzene, Hieb

G = 1.3
SPALT0 = 71.0
FUNKEN_METALL = [QColor('#FFFFFF'), QColor('#D8E2EE'), METALL]


class Harmonika(GeraetSzene):
    """Der Monitor flackert, ein Hieb hilft nicht. Der Professor spannt ihn in den Schraubstock
    und dreht, bis der Monitor zur Ziehharmonika gefaltet ist. Das Flackern läuft unbeirrt
    über die Falten weiter. Er rollt das Ganze davon, die Falten wippen mit."""
    name, titel, reihenfolge = 'harmonika', 'Reparaturharmonika', 91

    def vorbereiten(self):
        r = self.seite = self.richtung
        self.sx = self.vom_rand(0.1)
        self.spalt = SPALT0
        self.quetsch = 0.0
        self.kurbel = 0.0
        self.bild = 1.0
        self.kaputt = 0.0
        self.wipp = 0.0
        self.stand = self.sx + r * 108 * G * self.s

    def griff(self):
        kx = -46 + self.spalt + 37
        return (self.sx + self.seite * kx * G * self.s,
                self.boden + (SCHRAUB_OBEN - 15 - 16 * math.cos(self.kurbel)) * G * self.s)

    def monitor_oben(self):
        b = harmonika_breite(self.quetsch)
        return self.sx + self.seite * (-46 + b / 2) * G * self.s, self.boden + (SCHRAUB_OBEN - 78) * G * self.s

    def zeichne_requisiten(self, p):
        p.save()
        p.translate(self.sx + self.zitter(), self.boden)
        p.scale(self.seite * G * self.s, G * self.s)
        zeichne_schraubstock(p, 0, 0, self.spalt, self.kurbel, hinten=True)
        q = min(1.0, max(0.0, self.quetsch + self.wipp))
        zeichne_harmonika(p, -46, SCHRAUB_OBEN, q, self.t, self.bild, True, kaputt=self.kaputt)
        zeichne_schraubstock(p, 0, 0, self.spalt, self.kurbel, hinten=False)
        p.restore()

    def requisiten_kasten(self):
        s = self.s * G
        x0 = self.sx + self.seite * -66 * s
        x1 = self.sx + self.seite * (-46 + self.spalt + 60) * s
        return QRectF(min(x0, x1), self.boden - (-SCHRAUB_OBEN + 86) * s, abs(x1 - x0), (-SCHRAUB_OBEN + 86) * s)

    def ablauf(self):
        r, s = self.richtung, self.s
        self.x = self.aussen(-r)

        def flimmer_schauen(sz, u):
            sz.pose = Pose(arm_v=-30, blick_y=-0.2, sorge=min(1.0, u) * 0.8, auge_zu=blinzeln(sz.t),
                           wipp=2 * math.sin(u * 3))

        def getroffen(sz):
            sz.kaputt = 0.35
            sz.haare = 0.3

        def kurbeln(dauer, ziel):
            start = {}

            def f(sz, u):
                if 'q' not in start:
                    start['q'] = sz.quetsch
                a = min(1.0, u / dauer)
                sz.kurbel = u * 9.0
                sz.quetsch = start['q'] + (ziel - start['q']) * glatt(a)
                sz.spalt = harmonika_breite(sz.quetsch) + 3 * (1 - sz.quetsch)
                gx, gy = sz.griff()
                sz.x = gx + r * 48 * s
                sz.pose = Pose(arm_v=sz.arm_zu(gx, gy), arm_h=-40, bein_v=-12, bein_h=12, sorge=0.4,
                               mund_offen=(u * 3) % 1 < 0.3, auge_zu=blinzeln(sz.t), wipp=3 * math.sin(u * 9))
                if random.random() < 0.12:
                    mx, my = sz.monitor_oben()
                    sz.streue(mx, my + 40 * s, 1, FUNKEN_METALL, tempo=120, dauer=0.4, r=(2, 4), art='stern')
            return f

        def schnaufen(sz, u):
            sz.wipp = -0.12 * math.sin(u * 5) * (1 - min(1.0, u / 2.0))
            sz.pose = Pose(sorge=0.8, blick_y=-0.3, auge_zu=blinzeln(sz.t))

        def rollen_wipp(pose, sz):
            sz.wipp = -0.08 * abs(math.sin(sz.phase))
            return schieben(pose, sz)

        return [
            Gehe(bis=self.stand),
            Setze(richtung=-r),
            Jeweils(1.8, flimmer_schauen),
            Hieb(lambda sz: sz.monitor_oben(), getroffen),
            Stehe(0.8, lambda sz, u: Pose(sorge=1.0, blick_y=-0.3, auge_zu=blinzeln(sz.t))),
            Schaue(0.9),
            Setze(richtung=-r),
            Stehe(1.0, lambda sz, u: denk_pose(sz, u)),
            Stehe(0.3, lambda sz, u: Pose(arm_v=-170, arm_v_x=12, mund_offen=True)),
            Gehe(bis=lambda sz: sz.griff()[0] + r * 48 * s, tempo=0.4),
            Setze(richtung=-r),
            Jeweils(3.0, kurbeln(3.0, 0.8)),
            Stehe(0.4),
            Gehe(bis=self.stand + r * 30 * s, tempo=0.5),
            Setze(richtung=-r),
            Jeweils(2.2, schnaufen),
            Setze(wipp=0.0),
            Schaue(1.2),
            Setze(richtung=-r),
            Stehe(1.6, lambda sz, u: triumph_pose(sz, u)),
            Gehe(bis=lambda sz: sz.griff()[0] + r * 46 * s, tempo=0.5),
            Setze(mitnehmen=('sx',)),
            Gehe(bis=self.aussen(-r) - r * 160 * s, haltung=rollen_wipp),
        ]

    def schreck_ablauf(self):
        """Vor Schreck wird er flach und versinkt mit dem Gerät."""
        self.nebenbei.clear()
        self.halt = self.halt_h = None
        tief = 330 * self.s
        if not (self.zeige_figur and self.figur_sichtbar()):
            self.zeige_figur = False
            return [Warte(0.25), Wandel(0.45, senke=tief), Tu(lambda sz: setattr(sz, 'weg_ist', True))] + self._ende()
        return [HaareHoch(1.0), Erschrecke(0.3, 46),
                Wandel(0.12, stauchen=0.45),
                Wandel(0.45, y=lambda sz: sz.y + tief, senke=tief),
                Tu(lambda sz: setattr(sz, 'zeige_figur', False))] + self._ende()
