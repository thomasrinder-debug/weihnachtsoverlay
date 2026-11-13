import math
import random

from PyQt6.QtCore import QRectF
from PyQt6.QtGui import QColor

from zeichnen.figur import Pose
from zeichnen.grundlagen import blinzeln
from zeichnen.hoersaal import mikro_kopf, zeichne_kreischen, zeichne_mikrofon, zeichne_schallringe

from .basis import Erschrecke, Gehe, Jeweils, Renne, Setze, Stehe, Szene, Tu, Wandel
from .hs_basis import Publikumsblick, auf_figur

HOEHE = 150                   # Mikrofonständer in Einheiten
STAUB = [QColor(225, 220, 210, 200), QColor(200, 195, 185, 180)]
GRIFF = (14.9, -195.8)        # Fäustling bei arm_v=-175 in Figur-Einheiten


class HsMikro(Szene):
    """Mikrofonprobe: Antippen gibt kleine Schallringe, Pusten größere, die Mützenspitze
    flattert. Er holt tief Luft, und die Rückkopplung bläst ihn waagerecht vom Boden; er
    klammert sich am Ständer fest, flattert wie eine Fahne und schaut dabei ins Publikum.
    Dann ist es still, er klatscht bäuchlings hin. Beim Hinausschleichen piept es noch einmal."""
    name, titel, reihenfolge = 'hs_mikro', 'Rückkopplung', 1003

    def vorbereiten(self):
        r, s = self.richtung, self.s
        self.xs = self.vom_rand(random.uniform(0.17, 0.21))
        self.ein = 0.0
        self.ring = 0.0
        self.kreisch = 0.0
        self.kippe = 0.0
        self.flagge = False

    def kopf(self):
        kx, ky = mikro_kopf(HOEHE)
        return self.xs - self.richtung * kx * self.s, self.boden + (ky + (1 - self.ein) * 200) * self.s

    def ablauf(self):
        r, s = self.richtung, self.s
        self.x = self.aussen(-r)
        xw = self.xs - r * 62 * s

        def tippen(sz, u):
            k = (u * 5) % 1 < 0.5
            return Pose(arm_v=-95 if k else -80, arm_v_x=14, blick_y=0.2, auge_zu=blinzeln(sz.t))

        def zuckt(sz, u):
            sz.hopp = math.sin(min(1.0, u / 0.25) * math.pi) * 8 * s
            return Pose(schreck=0.6, sorge=0.6, arm_v=30, arm_h=-30, wipp=-6)

        def pusten(sz, u):
            return Pose(mund_offen=True, arm_v=-80, arm_v_x=14, wipp=-10 + 12 * math.sin(u * 30), sorge=0.5,
                        auge_zu=u > 0.3)

        def luft_holen(sz, u):
            sz.stauchen = 1 + 0.06 * min(1.0, u / 0.5)
            return Pose(arm_v=30, arm_h=40, auge_zu=True, kopf_vorn=False, hub=-3 * min(1.0, u / 0.5))

        return [
            Wandel(0.3, ein=1.0),
            Gehe(bis=xw),
            # Versuch 1: antippen
            Stehe(0.5, tippen),
            Wandel(0.12, ring=0.3),
            Stehe(0.35, zuckt),
            Wandel(0.2, ring=0.0),
            # Versuch 2: pusten
            Stehe(0.25, Pose(mund_offen=False, arm_v=-80, arm_v_x=14)),
            Wandel(0.15, ring=0.6, kreisch=0.3),
            Stehe(0.7, pusten),
            Wandel(0.15, ring=0.0, kreisch=0.0),
            Stehe(0.4, lambda sz, u: Pose(kopf_vorn=True, sorge=0.7, auge_zu=0.1 < u < 0.22, wipp=-4)),
            # Erwartungspause: tief Luft holen
            Stehe(0.8, luft_holen),
            Setze(stauchen=1.0),
            # Knall: Rückkopplung bläst ihn waagerecht, er hält sich am Ständer fest
            Setze(ring=1.0, kreisch=1.0, flagge=True, pose=Pose(arm_v=-175, arm_h=-170, schreck=1.0)),
            Jeweils(0.7, lambda sz, u: sz.flattern(u, False)),
            Jeweils(0.9, lambda sz, u: sz.flattern(u, True)),
            # Stille, Bauchklatscher
            Setze(ring=0.0, kreisch=0.0, flagge=False),
            Wandel(0.16, y=lambda sz: sz.boden, hopp=lambda sz: 48 * sz.s, neigung=90.0, kippe=0.0),
            Tu(lambda sz: sz.platsch()),
            Stehe(0.55, Pose(arm_v=-175, arm_h=-175, sack=True, auge_zu=True, mund_offen=True, wipp=-8)),
            Wandel(0.35, neigung=0.0, hopp=0.0, x=lambda sz: sz.x + r * 40 * s),
            Publikumsblick(0.6, sorge=0.5),
            # Hinausschleichen, ein letzter Pieps
            Setze(richtung=-r),
            Gehe(dauer=0.6, tempo=0.45, neigung=4),
            Wandel(0.1, ring=0.25),
            Erschrecke(0.3, 30),
            Wandel(0.05, ring=0.0),
            Renne(zum='rand', tempo=3.4),
            Wandel(0.3, ein=0.0),
        ]

    def flattern(self, u, blick):
        r, s = self.richtung, self.s
        self.neigung = 88 + 9 * math.sin(u * 23)
        self.kippe = -10 - 4 * math.sin(u * 23)
        k = math.sin(u * 31) * 28
        self.pose = Pose(arm_v=-175, arm_h=-168, bein_v=-10 + k, bein_h=15 - k, schreck=0.8, sorge=1.0,
                         wipp=-12 + 8 * math.sin(u * 40), mund_offen=not blick, kopf_vorn=blick,
                         auge_zu=blick and (0.35 < u < 0.47 or 0.6 < u < 0.72), blick_y=0.1)
        # Fäustling bleibt am Ständer
        self.hopp = 0.0
        self.y = self.boden
        gx, gy = auf_figur(self, *GRIFF)
        zx = self.xs - r * 2 * s
        zy = self.boden - 140 * s
        self.x += zx - gx
        self.y += zy - gy

    def platsch(self):
        s = self.s
        x, _ = auf_figur(self, 0, -110)
        self.streue(x, self.boden - 6 * s, 14, STAUB, tempo=170, dauer=0.6, r=(7, 14))

    def zeichne_hinten(self, p):
        if self.ein <= 0:
            return
        s, r = self.s, self.richtung
        kx, ky = self.kopf()
        phase = (self.t * (1.4 + 1.5 * self.ring)) % 1.0
        zeichne_schallringe(p, kx, ky, -r, self.ring, phase, s, 80)
        zeichne_schallringe(p, kx, ky, r, self.ring * 0.5, phase, s, 60)
        zeichne_kreischen(p, kx, ky - 30 * s * self.kreisch, -r, self.kreisch, self.t, s)

    def zeichne_vorn(self, p):
        if self.ein <= 0:
            return
        s, r = self.s, self.richtung
        p.save()
        p.translate(self.xs, self.boden + (1 - self.ein) * 200 * s)
        p.rotate(self.kippe * r)
        p.scale(-r * s, s)
        zeichne_mikrofon(p, HOEHE, math.sin(self.t * 50) * 6 * self.kreisch)
        p.restore()

    def grenzen_extra(self):
        s = self.s
        k = QRectF(self.xs - 70 * s, self.boden - (HOEHE + 40) * s, 140 * s, (HOEHE + 40) * s)
        if self.ring > 0 or self.kreisch > 0:
            w = (60 + 300 * self.ring) * s
            kx, ky = self.kopf()
            k = k.united(QRectF(kx - w, ky - w, 2 * w, 2 * w))
        if abs(self.neigung) > 1:
            k = k.united(QRectF(self.x - 50 * s, self.boden - 320 * s, 100 * s, 320 * s))
            x, y = auf_figur(self, 0, -250)
            k = k.united(QRectF(x - 80 * s, y - 80 * s, 160 * s, 160 * s))
        return k

    def schreck_ablauf(self):
        self.flagge = False
        self.ring = self.kreisch = self.kippe = 0.0
        self.neigung, self.hopp, self.stauchen = 0.0, 0.0, 1.0
        self.y = self.boden
        return [Erschrecke(), Renne(zum='rand'), Wandel(0.25, ein=0.0)]
