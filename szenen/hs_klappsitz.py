import math
import random

from PyQt6.QtCore import QRectF
from PyQt6.QtGui import QColor

from zeichnen.figur import Pose, zeichne_bein, zeichne_bein_ik, zeichne_weihnachtsmann
from zeichnen.grundlagen import blinzeln
from zeichnen.hoersaal import zeichne_klappsitz, zeichne_sitzflaeche_vorn

from .basis import Gehe, Jeweils, Setze, Stehe, Szene, Tu, Wandel
from .hs_basis import Plumps, rueckenlage

STAUB = [QColor(225, 220, 210, 210), QColor(200, 195, 185, 190)]
SITZ = 66             # Höhe der Sitzfläche in Einheiten
STEHT = 54            # Höhe seines Hosenbodens im Stehen


class HsKlappsitz(Szene):
    """Hörsaal-Klappsitz: Er setzt sich, der Sitz ist hochgeklappt, Plumps auf den Boden.
    Er drückt ihn herunter, dreht sich um, der Sitz schnellt zu früh hoch, er kippt rücklings
    um. Beim dritten Mal hält er ihn fest, sitzt, federt zweimal nach und lehnt sich zufrieden
    zurück. Stille. Zuschnapp: zusammengeklappt, die Stiefel neben dem Kopf, hüpft der Sitz mit
    ihm hinaus."""
    name, titel, reihenfolge = 'hs_klappsitz', 'Klappsitz', 1007

    def vorbereiten(self):
        r, s = self.richtung, self.s
        self.sx = self.vom_rand(random.uniform(0.15, 0.19))
        self.rs = r                 # der Sitz schaut nach innen
        self.ein = 0.0
        self.klappe = 1.0
        self.sitzt = False
        self.sitz_h = STEHT
        self.geklemmt = False
        self.sitz_hopp = 0.0
        self.pose_fest = {'sack': False}

    def platz(self):
        return self.sx + self.rs * 26 * self.s

    def ablauf(self):
        r, s = self.richtung, self.s
        self.x = self.aussen(-r)

        def sitzpose(**extra):
            werte = dict(sitzt=True, sack=False, auge_zu=False)
            werte.update(extra)
            return Pose(**werte)

        def staub(sz):
            sz.streue(sz.x, sz.boden - 6 * s, 12, STAUB, tempo=170, dauer=0.6, r=(7, 13))

        def federn(sz, u):
            sz.sitz_h = SITZ - 7 * abs(math.sin(u * math.pi / 0.3))
            sz.pose = sitzpose(kopf_vorn=True, mund_offen=True, arm_v=-40, arm_h=-40, blick_y=0.2)

        def zuruecklehnen(sz, u):
            f = min(1.0, u / 0.35)
            sz.pose = sitzpose(arm_v=-175 * f, arm_h=-170 * f, arm_v_x=8, auge_zu=u > 0.3, kopf_vorn=False,
                               hub=2 * f)

        return [
            Wandel(0.3, ein=1.0),
            Gehe(bis=self.platz()),
            Stehe(0.3, Pose(kopf_vorn=True, auge_zu=blinzeln(self.t), sack=False)),
            # Versuch 1: der Sitz ist hochgeklappt
            Setze(sitzt=True, sitz_h=STEHT, pose=sitzpose(schreck=0.4)),
            Wandel(0.25, sitz_h=0.0),
            Tu(staub),
            Stehe(0.6, lambda sz, u: sitzpose(schreck=0.6 if u < 0.25 else 0.0, sorge=0.8, kopf_vorn=u > 0.25,
                                              auge_zu=0.4 < u < 0.52)),
            Wandel(0.25, sitz_h=STEHT),
            Setze(sitzt=False),
            # Versuch 2: herunterdrücken, umdrehen, zu früh losgelassen
            Setze(richtung=-r),
            Stehe(0.15, Pose(arm_v=-100, arm_v_x=14, sack=False)),
            Wandel(0.25, klappe=0.0),
            Stehe(0.15, Pose(arm_v=-30, arm_v_x=14, sack=False, auge_zu=True)),
            Setze(richtung=r),
            Wandel(0.08, klappe=1.0),
            Setze(sitzt=True, sitz_h=STEHT, pose=sitzpose()),
            Wandel(0.22, sitz_h=0.0),
            Setze(sitzt=False, y=lambda sz: sz.boden),
            Plumps(-90, 0.28, 44, rueckenlage),
            Tu(staub),
            Stehe(0.4, rueckenlage),
            Wandel(0.3, neigung=0.0, hopp=0.0),
            # Versuch 3: festhalten, setzen, nachfedern, zurücklehnen
            Setze(richtung=-r),
            Stehe(0.15, Pose(arm_v=-100, arm_v_x=14, sack=False)),
            Wandel(0.25, klappe=0.0),
            Setze(richtung=r),
            Setze(sitzt=True, sitz_h=STEHT, pose=sitzpose(arm_h=30, sorge=0.6)),
            Wandel(0.35, sitz_h=SITZ),
            Jeweils(0.6, federn),
            Setze(sitz_h=SITZ),
            Jeweils(0.55, zuruecklehnen),
            # Erwartungspause: völlige Ruhe
            Stehe(0.5, sitzpose(arm_v=-175, arm_h=-170, arm_v_x=8, auge_zu=True, hub=2)),
            # Zuschnapp
            Setze(geklemmt=True, sitzt=False),
            Wandel(0.08, klappe=1.0),
            Tu(staub),
            Stehe(0.9, lambda sz, u: Pose(kopf_vorn=True, sitzt=True, sack=False, schreck=1.0 if u < 0.3 else 0.3,
                                          sorge=1.0, auge_zu=0.5 < u < 0.6 or 0.7 < u < 0.8,
                                          arm_v=-175, arm_h=-175)),
            Jeweils(1.6, lambda sz, u: sz.huepfen(u)),
        ]

    def huepfen(self, u):
        s = self.s
        e = -self.rs
        self.sx += e * self.tempo * 1.6 / 60
        self.x = self.platz()
        k = (u * 2.6) % 1.0
        self.sitz_hopp = math.sin(k * math.pi) * 40 * s
        self.pose = Pose(kopf_vorn=True, sitzt=True, sack=False, schreck=0.4, sorge=1.0, arm_v=-175, arm_h=-175,
                         mund_offen=k < 0.5)
        if not self.grenzen().intersects(self.geo):
            self.zeige_figur = False
            self.ein = 0.0

    def figur_sichtbar(self):
        if self.sitzt or self.geklemmt:
            return self.grenzen().intersects(self.geo)
        return super().figur_sichtbar()

    def zeichne_figur(self, p, zwischen=None):
        s = self.s
        if self.geklemmt:
            # zusammengeklappt zwischen Sitz und Lehne, die Stiefel neben dem Kopf
            p.save()
            p.translate(self.sx, self.boden - self.sitz_hopp - (52 - STEHT + 4) * s)
            p.scale(s * self.rs, s)
            p.save()
            p.scale(0.72, 0.78)
            zeichne_weihnachtsmann(p, self.pose)
            p.restore()
            for k, (dx, w) in enumerate(((-30, 160), (44, 200))):
                p.save()
                p.translate(dx, -100)
                zeichne_bein(p, 0, w + math.sin(self.t * 14 + k) * 8, k == 0)
                p.restore()
            zeichne_sitzflaeche_vorn(p, -40, 46, -128, -40)
            p.restore()
            return
        if not self.sitzt:
            return super().zeichne_figur(p, zwischen)
        r = self.richtung
        h = self.sitz_h
        boden_lokal = h - STEHT
        p.save()
        p.translate(self.x, self.boden - (h - STEHT) * s - self.hopp)
        p.scale(s * r, s)
        if h > 30:
            zeichne_bein_ik(p, -6, -66, 34, boden_lokal - 2, True)
            zeichne_bein_ik(p, 6, -66, 48, boden_lokal, False)
        else:
            zeichne_bein_ik(p, -6, -66, 66, boden_lokal - 4, True)
            zeichne_bein_ik(p, 6, -66, 80, boden_lokal - 2, False)
        zeichne_weihnachtsmann(p, self.pose)
        p.restore()

    def zeichne_hinten(self, p):
        if self.ein <= 0 or self.geklemmt:
            return
        self.zeichne_sitz(p)

    def zeichne_vorn(self, p):
        if self.ein > 0 and self.geklemmt:
            self.zeichne_sitz(p)

    def zeichne_sitz(self, p):
        s = self.s
        p.save()
        p.translate(self.sx, self.boden + (1 - self.ein) * 140 * s - self.sitz_hopp)
        p.scale(s * self.rs * 1.35, s)
        zeichne_klappsitz(p, self.klappe)
        p.restore()

    def grenzen_extra(self):
        s = self.s
        k = QRectF(self.sx - 90 * s, self.boden - 300 * s - self.sitz_hopp, 180 * s, 300 * s + self.sitz_hopp)
        if self.sitzt:
            k = k.united(QRectF(self.x - 130 * s, self.boden - 300 * s, 260 * s, 300 * s))
        if abs(self.neigung) > 1:
            k = k.united(QRectF(self.x - 330 * s, self.boden - 160 * s, 660 * s, 160 * s))
        return k

    def schreck_ablauf(self):
        if self.geklemmt:
            self.x = self.platz()
        self.geklemmt = self.sitzt = False
        self.neigung, self.hopp, self.sitz_hopp = 0.0, 0.0, 0.0
        self.y = self.boden
        self.zeige_figur = True
        if not self.figur_sichtbar():
            self.zeige_figur = False
        return self.schreck_alle() + [Wandel(0.2, ein=0.0)]

