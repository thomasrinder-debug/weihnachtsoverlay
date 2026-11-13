import math
import random

from PyQt6.QtCore import QRectF

from zeichnen.baeckerei import KRUEMEL, zeichne_dosendeckel, zeichne_keksberg, zeichne_keksdose
from zeichnen.figur import Pose
from zeichnen.grundlagen import blinzeln
from zeichnen.requisiten import zeichne_keks

from .back_bausteine import figur_trafo, hand, kopf, publikum, zittern
from .basis import Gehe, Jeweils, Schritt, Setze, Stehe, Szene, Tu

SITZ = 62         # so tief sitzt er mit ausgestreckten Beinen (Einheiten unter dem Fußpunkt)


class BackKeksdose(Szene):
    """Die Keksdose geht nicht auf: er hebt am Deckel gleich die ganze Dose hoch, stemmt den Fuß
    dagegen, schüttelt sie über dem Kopf und horcht daran. Da knallt der Deckel davon, eine
    Keksfontäne begräbt ihn unter einem Berg, aus dem nur die Mützenspitze ragt. Der Berg wird
    schmatzend kleiner, kugelrund sitzt er da, der Deckel landet ihm auf dem Kopf, und weil er
    nicht mehr aufstehen kann, rollt er davon."""
    name, titel, reihenfolge = 'back_keksdose', 'Keksdose', 807

    def vorbereiten(self):
        r = self.richtung
        self.x = self.aussen(-r)
        self.x0 = self.vom_rand(0.13)
        self.dx = self.x0 + r * 66 * self.s
        self.pose_fest = {'sack': False}
        self.dose = [self.dx, self.boden]      # Fußpunkt der Dose
        self.in_hand = False
        self.deckel = 'drauf'                   # 'drauf', 'flug', 'kopf'
        self.deckel_xy = [0.0, 0.0, 0.0]
        self.deckel_v = 0.0
        self.kekse = []                         # fliegende Kekse [x, y, vx, vy, w]
        self.berg = 0.0
        self.spruehen = False

    def ablauf(self):
        r, s = self.richtung, self.s

        def anheben(sz, u):
            if u < 0.35:
                f = u / 0.35
                sz.neigung = 32 * f
                sz.pose = Pose(arm_v=-10, arm_v_x=14, blick_y=0.7, bein_v=-10 * f, bein_h=20 * f)
            elif u < 1.0:
                f = (u - 0.35) / 0.65
                sz.in_hand = True
                sz.neigung = 32 * (1 - f)
                sz.pose = Pose(arm_v=-10 - 60 * f + zittern(u, 40, 4), arm_v_x=14, mund_offen=True, sorge=0.6,
                               blick_y=0.4)
            else:
                sz.in_hand = False
                sz.pose = Pose(arm_v=-70, arm_v_x=14, kopf_vorn=True, sorge=1.0, schreck=0.5)

        def stemmen(sz, u):
            sz.neigung = -18 + zittern(u, 30, 3)
            sz.pose = Pose(arm_v=-40 + zittern(u, 45, 5), arm_v_x=14, bein_v=-62, bein_h=10, auge_zu=True,
                           mund_offen=True, wipp=zittern(u, 30, 4))

        def schuetteln(sz, u):
            sz.in_hand = True
            sz.pose = Pose(arm_v=-165 + zittern(u, 50, 12), arm_h=-150, arm_v_x=20, mund_offen=True,
                           kopf_vorn=True, auge_zu=True)
            if int(u * 12) != int((u - 1 / 60) * 12):
                x, y = hand(sz)
                sz.streue(x, y, 2, KRUEMEL, tempo=120, r=(1.5, 3), schwer=True)

        def horchen(sz, u):
            sz.in_hand = True
            sz.pose = Pose(arm_v=-150, arm_v_x=12, blick_x=-0.6, blick_y=-0.4, auge_zu=0.4 < u < 0.52)

        def plopp(sz):
            sz.in_hand = False
            x, y = hand(sz)
            sz.dose = [x, sz.boden]
            sz.deckel = 'flug'
            sz.deckel_xy = [x, y - 60 * s, 0.0]
            sz.deckel_v = -1350 * s
            for i in range(42):
                sz.kekse.append([x, y - 40 * s, random.uniform(-260, 260) * s, random.uniform(-1300, -500) * s,
                                 random.uniform(0, 360), random.uniform(0, 0.9)])
            sz.striche = True

        def begraben(sz, u):
            sz.pose = Pose(kopf_vorn=True, schreck=1.0, arm_v=-150, arm_h=-140, arm_v_x=20)

        def futtern(sz, u):
            sz.striche = False
            sz.berg = max(0.0, 230 * (1 - u / 1.3))
            sz.stauchen = 1 - 0.18 * min(1.0, u / 1.3)
            sz.y = sz.boden + SITZ * s
            sz.pose = Pose(bein_v=-88, bein_h=-84, arm_v=-60, arm_h=-50, kopf_vorn=True, auge_zu=True,
                           mund_offen=(u * 7) % 2 < 1)
            if int(u * 20) != int((u - 1 / 60) * 20):
                for z in (-1, 1):
                    sz.streue(sz.x + z * 50 * s, sz.boden - sz.berg * s * 0.6, 2, KRUEMEL, tempo=220, r=(1.5, 3.5),
                              schwer=True, richtung=-math.pi / 2 - z * 0.9, streuung=0.5)

        def sitzen(sz, u):
            sz.pose = Pose(bein_v=-88, bein_h=-84, arm_v=-50 + 10 * math.sin(u * 4), arm_h=-40, kopf_vorn=True,
                           auge_zu=blinzeln(sz.t) or (0.35 < u < 0.47), mund_offen=False)

        def deckel_kommt(sz, u):
            f = min(1.0, u / 0.45)
            x, y = kopf(sz, 6, -222)
            sz.deckel_xy = [x, y - (1 - f) ** 2 * 500 * s, 0.0]
            if f >= 1:
                sz.deckel = 'kopf'
            sitzen(sz, 0.0)

        return [
            Gehe(bis=self.x0),
            Jeweils(1.4, anheben),
            Tu(lambda sz: sz.streue(sz.dx, sz.boden, 6, KRUEMEL, tempo=120, r=(1.5, 3), schwer=True)),
            Setze(neigung=0.0, x=lambda sz: sz.dx - r * 50 * s),
            Jeweils(1.0, stemmen),
            Setze(neigung=0.0),
            publikum(0.5, sorge=0.8),
            Jeweils(0.8, schuetteln),
            Jeweils(0.8, horchen),
            Tu(plopp),
            Jeweils(1.3, begraben),
            Stehe(0.4, Pose(kopf_vorn=True, schreck=1.0)),
            Jeweils(1.3, futtern),
            Setze(berg=0.0),
            Jeweils(0.5, deckel_kommt),
            Setze(striche=True),
            publikum(0.8, bein_v=-88, bein_h=-84, arm_v=-50, arm_h=-40),
            Setze(striche=False),
            _Roll(1.6),
        ]

    def schreck_ablauf(self):
        self.in_hand = False
        if self.stauchen < 1:
            return [Setze(striche=True), _Roll(2.6)]
        self.berg = 0.0
        self.kekse.clear()
        return [Setze(neigung=0.0), *super().schreck_ablauf()]

    def weiter(self, dt):
        s = self.s
        if self.deckel == 'flug' and self.deckel_v < 0:
            self.deckel_v += 450 * s * dt
            self.deckel_xy[1] += self.deckel_v * dt
            self.deckel_xy[2] += 900 * dt
        rest = []
        for k in self.kekse:
            if k[5] > 0:
                k[5] -= dt
                rest.append(k)
                continue
            k[3] += 1500 * s * dt
            k[0] += k[2] * dt
            k[1] += k[3] * dt
            k[4] += 500 * dt
            if k[3] > 0 and k[1] > self.boden - self.berg * s * 0.85:
                self.berg = min(230.0, self.berg + 6)
            else:
                rest.append(k)
        self.kekse = rest

    def zeichne_hinten(self, p):
        s = self.s
        if not self.in_hand:
            p.save()
            p.translate(*self.dose)
            p.scale(s, s)
            zeichne_keksdose(p, offen=self.deckel != 'drauf')
            p.restore()

    def dosen_punkt(self):
        x, y = hand(self)
        return x, y + 46 * self.s

    def zeichne_vorn(self, p):
        s = self.s
        if self.in_hand:
            x, y = self.dosen_punkt()
            p.save()
            p.translate(x, y)
            p.scale(s, s)
            zeichne_keksdose(p)
            p.restore()
        for k in self.kekse:
            if k[5] > 0:
                continue
            p.save()
            p.translate(k[0], k[1])
            p.rotate(k[4])
            p.scale(s, s * 0.85)
            zeichne_keks(p, 11)
            p.restore()
        if self.berg > 0:
            p.save()
            p.translate(self.x, self.boden)
            p.scale(s, s)
            zeichne_keksberg(p, 70 + self.berg * 1.4, self.berg)
            p.restore()
        if self.deckel == 'flug':
            x, y, w = self.deckel_xy
            p.save()
            p.translate(x, y)
            p.rotate(w)
            p.scale(s, s)
            zeichne_dosendeckel(p)
            p.restore()
        elif self.deckel == 'kopf' and self.zeige_figur:
            p.save()
            p.setTransform(figur_trafo(self), True)
            p.translate(6, -222 + self.pose.hub)
            zeichne_dosendeckel(p)
            p.restore()

    def grenzen_extra(self):
        s = self.s
        k = QRectF(self.dose[0] - 50 * s, self.dose[1] - 70 * s, 100 * s, 70 * s)
        if self.in_hand:
            x, y = self.dosen_punkt()
            k = k.united(QRectF(x - 50 * s, y - 70 * s, 100 * s, 80 * s))
        if self.kekse:
            xs = [q[0] for q in self.kekse]
            ys = [q[1] for q in self.kekse]
            k = k.united(QRectF(min(xs) - 15 * s, min(ys) - 15 * s, max(xs) - min(xs) + 30 * s,
                                max(ys) - min(ys) + 30 * s))
        if self.berg > 0:
            b = (70 + self.berg * 1.4) * s
            k = k.united(QRectF(self.x - b / 2, self.boden - self.berg * s - 15 * s, b, self.berg * s + 15 * s))
        if self.deckel == 'flug':
            k = k.united(QRectF(self.deckel_xy[0] - 50 * s, self.deckel_xy[1] - 50 * s, 100 * s, 100 * s))
        if self.zeige_figur:
            x, y = kopf(self, 6, -222)
            k = k.united(QRectF(x - 60 * s, y - 40 * s, 120 * s, 60 * s))
        return k


class _Roll(Schritt):
    """Kugelrund davonrollen, bis er aus dem Bild ist; tempo in Umdrehungen je Sekunde."""

    def __init__(self, tempo):
        self.tempo = tempo

    def beginn(self, sz):
        sz.richtung = sz.naechster_rand()
        self.L = 105 * sz.s
        self.mitte = (sz.x, sz.y - self.L)

    def weiter(self, sz, u, dt):
        a = 360 * self.tempo * (u * u / 0.5 if u < 0.25 else u - 0.125)
        sz.neigung = a
        cx = self.mitte[0] + sz.richtung * math.radians(a) * self.L
        sz.x = cx - self.L * math.sin(math.radians(a * sz.richtung))
        sz.y = self.mitte[1] + self.L * math.cos(math.radians(a * sz.richtung))
        sz.pose = Pose(bein_v=-88, bein_h=-84, arm_v=-60, arm_h=-50, kopf_vorn=True, schreck=0.6)

    def fertig(self, sz, u):
        return u > 0.3 and not sz.figur_sichtbar()
