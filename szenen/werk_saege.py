import math
import random

from PyQt6.QtCore import QRectF
from PyQt6.QtGui import QColor

from zeichnen.figur import Pose
from zeichnen.figuren import WichtelSteif
from zeichnen.werkstatt import zeichne_brett, zeichne_saege, zeichne_saegebock

from .basis import Gehe, Jeweils, Mit, Setze, Springe, Stehe, Szene, Tu, Wandel, Warte, muetze_richten
from .werk_basis import SPAENE, STAUB, Blick, hand, schweiss, verpuffen

WG = 0.62
BG = 1.15                  # Größe des Sägebocks
BRETT_D = 9


class Saegebock(Szene):
    """Ein Wichtel sitzt auf einem Brett über dem Sägebock und sägt genau in der Mitte. Die Säge
    klemmt; er ruckt, stemmt den Fuß dagegen, sie kommt frei und er kippt fast hintenüber. Dann
    sägt er wie wild durch: das äußere Brettstück fällt, ihm passiert nichts, er zeigt stolz die
    leeren Hände. Pause. Es knarzt: der mitdurchgesägte Bock klappt in zwei Hälften auseinander
    und er klatscht flach auf den Boden."""
    name, titel, reihenfolge = 'werk_saege', 'Am falschen Ende gesägt', 904

    def vorbereiten(self):
        self.zeige_figur = False
        r, s = self.richtung, self.s
        self.xs = self.vom_rand(0.12)
        self.bock_h = 62 * BG
        self.kipp = 0.0
        self.schnitt = 0.0
        self.brett_y = self.boden - (self.bock_h + BRETT_D) * s     # Oberkante des Bretts
        self.innen_y, self.innen_w = self.brett_y, 0.0
        self.stueck = {'dx': 0.0, 'dy': 0.0, 'w': 0.0}
        self.durch = False
        self.saege = 'hand'          # 'hand', 'boden', None
        self.saege_lose = (0.0, 0.0, 0.0)
        self.zug = 0.0               # Säge vor und zurück
        self.weg = False
        self.w = self.dazu('w', WichtelSteif, groesse=WG, knick=1.0)
        self.w.richtung = r
        self.sitz_x = self.xs + r * 44 * s

    def sitz_y(self):
        return self.innen_y + 48 * WG * self.s

    def schnitt_punkt(self):
        return self.xs, self.brett_y + (2 + self.schnitt * (BRETT_D + 9)) * self.s

    def ablauf(self):
        r, s = self.richtung, self.s

        def sitzen(pose):
            pose.bein_v, pose.bein_h = -25, -5
            return pose

        def saegen(sz, u, tempo=0.0, klemmt=False, ruck=0.0):
            w = sz.w
            z = math.sin(u * (6 + 22 * tempo))
            if klemmt:
                z = 0.0
            w.pose = sitzen(Pose(arm_v=-55 + 22 * z, arm_h=-40 + 10 * z, kopf_vorn=klemmt or tempo > 0.8,
                                 blick_y=0.6 if not klemmt else 0.0, sorge=0.8 if klemmt else 0.2 * tempo,
                                 mund_offen=klemmt or tempo > 0.6))
            sz.zug = z
            w.neigung = -ruck
            if tempo and random.random() < 0.5 * tempo:
                x, y = sz.schnitt_punkt()
                sz.streue(x, y + 6 * s, 1, SPAENE, tempo=90, dauer=0.6, r=(1.5, 3), schwer=True,
                          richtung=math.pi / 2 + r * 0.6, streuung=0.7)
            if tempo > 0.7 and random.random() < 0.08:
                schweiss(sz, w.x, w.y - 150 * WG * s)

        def ruckeln(sz, u, staerke):
            k = abs(math.sin(u * 9)) * staerke
            saegen(sz, u, klemmt=True, ruck=k * 14)
            sz.w.pose.bein_v = -25 - 70 * (staerke > 1.2)
            sz.w.striche = staerke > 1.2 and u > 0.3

        def frei(sz, u):
            f = math.sin(min(1.0, u / 0.5) * math.pi)
            w = sz.w
            w.neigung = -45 * f
            w.pose = sitzen(Pose(arm_v=-150 + 60 * math.sin(u * 30), arm_h=-140 - 60 * math.sin(u * 30 + 1),
                                 kopf_vorn=True, schreck=f, mund_offen=True))
            w.striche = False
            sz.zug = -1.0

        def schneiden(sz, u):
            saegen(sz, u, tempo=min(1.0, 0.4 + u))
            sz.schnitt = min(1.0, u / 1.0)

        def abfallen(sz, u):
            f = min(1.0, u / 0.45)
            sz.stueck = {'dx': -r * 34 * s * f, 'dy': (sz.boden - BRETT_D * s - sz.brett_y) * f * f,
                         'w': -r * 55 * math.sin(f * math.pi) * (1 - 0.2 * f)}
            sz.w.pose = sitzen(Pose(arm_v=-60, arm_h=-40, kopf_vorn=False, blick_y=0.7))
            if f >= 1 and not getattr(sz, '_klapp', False):
                sz._klapp = True
                sz.streue(sz.xs - r * 60 * s, sz.boden, 8, STAUB, tempo=80, dauer=0.5)

        def saege_ablegen(sz):
            sz.saege = 'boden'
            sz.saege_lose = (sz.sitz_x + r * 30 * s, sz.boden - 2 * s, 0.0)

        def triumph(sz, u):
            z = math.sin(u * 8)
            sz.w.pose = sitzen(Pose(arm_v=-165 + 8 * z, arm_h=-155 - 8 * z, arm_v_x=12, kopf_vorn=True,
                                    mund_offen=u < 0.6, auge_zu=0.7 < u < 0.85, blick_y=-0.3))

        def knarzen(sz, u):
            sz.kipp = 4 * (u / 0.9) ** 2 + math.sin(u * 40) * 0.6
            sz.innen_y = sz.brett_y + sz.kipp * 0.3 * s
            sz.innen_w = r * sz.kipp * 0.6
            sz.w.y = sz.sitz_y()
            sz.w.pose = sitzen(Pose(arm_v=-165, arm_h=-155, arm_v_x=12, kopf_vorn=True, sorge=min(1.0, u * 1.5),
                                    blick_y=0.8 if u > 0.4 else 0.0, auge_zu=False))

        def zusammenbruch(sz, u):
            f = min(1.0, u / 0.32)
            sz.kipp = 4 + 58 * f * f
            sz.innen_y = sz.brett_y + (sz.boden - BRETT_D * s - sz.brett_y) * f * f
            sz.innen_w = r * 2 * (1 - f)
            w = sz.w
            w.x = sz.sitz_x
            w.y = sz.sitz_y() + 30 * s * f
            w.neigung = -95 * f
            w.pose = Pose(arm_v=-175, arm_h=-170, bein_v=-80, bein_h=-60, kopf_vorn=True, schreck=1.0,
                          mund_offen=True)

        def platt(sz, u):
            w = sz.w
            w.stauchen = 1.0 + 0.25 * math.exp(-u * 8) * math.cos(u * 30)
            w.pose = Pose(arm_v=-175, arm_h=-170, bein_v=-85, bein_h=-70, kopf_vorn=True, auge_zu=u > 0.25,
                          schreck=max(0.0, 1 - u * 3))

        def aufstehen(sz, u):
            w = sz.w
            f = min(1.0, u / 0.35)
            w.neigung = -95 * (1 - f)
            w.y = sz.boden
            w.x = sz.sitz_x
            w.stauchen = 1.0
            w.pose = Pose(arm_v=-40, arm_h=-30, kopf_vorn=True, sorge=0.6)

        def aufschlag(sz):
            sz.streue(sz.sitz_x, sz.boden, 20, STAUB, tempo=150, dauer=0.7, r=(8, 15))
            sz.streue(sz.sitz_x, sz.boden - 10 * s, 10, SPAENE, tempo=160, dauer=0.8, r=(1.5, 3), schwer=True,
                      richtung=-math.pi / 2, streuung=1.2)

        return [
            Mit('w', Gehe(bis=self.sitz_x + r * 30 * s, tempo=1.5)),
            Mit('w', Setze(richtung=-r)),
            Mit('w', Springe(nach=(self.sitz_x, self.sitz_y()), dauer=0.45, hoehe=60)),
            Jeweils(0.35, lambda sz, u: saegen(sz, u, tempo=0.3)),
            Jeweils(0.55, lambda sz, u: ruckeln(sz, u, 1.0)),
            Jeweils(0.65, lambda sz, u: ruckeln(sz, u, 1.6)),
            Jeweils(0.55, frei),
            Mit('w', Setze(neigung=0.0)),
            Jeweils(1.1, schneiden),
            Setze(durch=True),
            Jeweils(0.55, abfallen),
            Tu(saege_ablegen),
            Jeweils(0.9, triumph),
            Jeweils(0.9, knarzen),
            Jeweils(0.32, zusammenbruch),
            Tu(aufschlag),
            Jeweils(0.6, platt),
            Jeweils(0.4, aufstehen),
            *muetze_richten('w', 1.2),
            Mit('w', Gehe(bis=None, tempo=1.2, haltung=_humpeln)),
            Tu(lambda sz: sz.aufraeumen()),
            Warte(0.6),
        ]

    def aufraeumen(self):
        s = self.s
        verpuffen(self, self.xs, self.boden, 170 * s, 80 * s, 18)
        self.weg = True
        self.saege = None

    def schreck_ablauf(self):
        self.nebenbei.clear()
        w = self.w
        w.neigung, w.stauchen, w.y, w.hopp = 0.0, 1.0, self.boden, 0.0
        self.aufraeumen()
        return self.schreck_alle(weihnachtsmann=False)

    def zeichne_hinten(self, p):
        if self.weg:
            return
        s, r = self.s, self.richtung
        p.save()
        p.translate(self.xs, self.boden)
        p.scale(s * BG, s * BG)
        zeichne_saegebock(p, (self.kipp, self.kipp), 0.0 if self.durch else self.schnitt)
        p.restore()
        # inneres Brettstück (mit dem Wichtel)
        p.save()
        p.translate(self.xs, self.innen_y)
        p.rotate(self.innen_w)
        p.scale(r * s, s)
        zeichne_brett(p, 84, BRETT_D)
        p.restore()
        # äußeres Stück
        a = self.stueck
        p.save()
        p.translate(self.xs + a['dx'], self.brett_y + a['dy'])
        p.rotate(a['w'])
        p.scale(-r * s, s)
        zeichne_brett(p, 74, BRETT_D)
        if not self.durch and self.schnitt > 0:
            p.setBrush(QColor('#3B2412'))
            p.drawRect(QRectF(-1, 0, 2.5, BRETT_D * min(1.0, self.schnitt * 2)))
        p.restore()

    def zeichne_vorn(self, p):
        s = self.s
        if self.saege == 'hand' and self.w.zeige_figur:
            hx, hy = hand(self.w, True)
            cx, cy = self.schnitt_punkt()
            winkel = math.degrees(math.atan2(cy - hy, cx - hx))
            p.save()
            p.translate(hx, hy)
            p.rotate(winkel)
            p.translate(self.zug * 6 * s, 0)
            p.scale(WG * s, WG * s * (1 if abs(winkel) < 90 else -1))
            zeichne_saege(p)
            p.restore()
        elif self.saege == 'boden':
            x, y, w = self.saege_lose
            p.save()
            p.translate(x, y)
            p.scale(WG * s * -self.richtung, WG * s)
            zeichne_saege(p)
            p.restore()

    def grenzen_extra(self):
        s = self.s
        if self.weg:
            return QRectF()
        return QRectF(self.xs - 140 * s, self.boden - 110 * s, 280 * s, 112 * s)


def _humpeln(pose, d):
    d.hopp = abs(math.sin(d.phase)) * 5 * d.sz.s
    pose.kopf_vorn = False
    pose.sorge = 0.5
    return pose
