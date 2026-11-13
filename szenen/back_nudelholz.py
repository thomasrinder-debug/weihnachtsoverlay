import math

from PyQt6.QtCore import QRectF

from zeichnen.baeckerei import TEIG, TEIG_DUNKEL, zeichne_nudelholz, zeichne_teig, zeichne_teiggesicht
from zeichnen.figur import Pose
from zeichnen.grundlagen import blinzeln, linear

from .back_bausteine import hand, publikum, zittern
from .basis import Erschrecke, Gehe, Hoppel, Jeweils, Renne, Setze, Stehe, Szene, Wandel

MENGE = 80 * 64          # Teig bleibt gleich viel: Breite · Höhe


class BackNudelholz(Szene):
    """Er rollt einen Teigklumpen aus, der jedes Mal zurückfedert und ihn böse anschaut.
    Beim dritten Mal wirft er sich mit ganzem Gewicht darauf, der Teig liegt hauchdünn,
    Triumph. Dann schnurrt der Teig zur Kugel zusammen, springt ihn an und wickelt ihn ein;
    er hoppelt als Teigrolle davon, der Teig grinst auf seinem Bauch."""
    name, titel, reihenfolge = 'back_nudelholz', 'Widerspenstiger Teig', 800

    def vorbereiten(self):
        r = self.richtung
        self.x = self.aussen(-r)
        self.x0 = self.vom_rand(0.15)
        self.tx = self.x0 + r * 118 * self.s
        self.teig_h = self.flach = 64.0
        self.pose_fest = {'sack': False}
        self.rollen = False          # Teighöhe folgt dem Nudelholz
        self.augen = False
        self.boese = 0.0
        self.grinsen = False
        self.teig_xy = None          # fliegender Teigball
        self.kokon = False
        self.holz = None             # [x, y, winkel] wenn nicht in der Hand
        self.holz_vy = 0.0

    # -- Abläufe

    def ablauf(self):
        r = self.richtung
        tragen = lambda p, sz: Pose(bein_v=p.bein_v, bein_h=p.bein_h, hub=p.hub, arm_v=-75,  # noqa: E731
                                    arm_h=p.arm_h, auge_zu=p.auge_zu)

        def rollen(dauer, tief, tempo, neigung, ziel):
            def f(sz, u):
                g = min(1.0, u / 0.4)
                if u < 0.02:
                    sz.flach = sz.teig_h
                sz.teig_h = sz.flach + (ziel - sz.flach) * min(1.0, u / (dauer * 0.8)) + zittern(u, tempo, 1.5)
                sz.neigung = neigung * g
                sz.pose = Pose(arm_v=-55 - tief * g + zittern(u, tempo, 14), arm_h=-50 - tief * g,
                               arm_v_x=14, bein_v=-14 * g, bein_h=24 * g + 10 * (neigung > 40),
                               mund_offen=neigung > 40, sorge=0.3)
            return Jeweils(dauer, f)

        def federn(sz, u):
            f = min(1.0, u / 0.35)
            sz.teig_h = sz.flach + (64 - sz.flach) * f + math.sin(f * math.pi) * 22 * (1 - f * 0.3)

        def zurueck(sz, u):
            sz.neigung = max(0.0, sz.neigung - 200 * 1 / 60)
            sz.pose = Pose(kopf_vorn=True, schreck=0.8, arm_v=-70, arm_h=-60, arm_v_x=14, sorge=0.8)

        def schnurren(sz, u):
            f = min(1.0, u / 0.25)
            sz.teig_h = sz.flach + (60 - sz.flach) * f + math.sin(f * math.pi) * 26

        def anspringen(sz, u):
            f = min(1.0, u / 0.45)
            x0, x1 = sz.tx, sz.x + r * 6 * sz.s
            y0, y1 = sz.boden, sz.boden - 30 * sz.s
            sz.teig_xy = (x0 + (x1 - x0) * f, y0 + (y1 - y0) * f - 120 * sz.s * 4 * f * (1 - f))
            sz.pose = Pose(kopf_vorn=True, schreck=1.0, arm_v=-120, arm_h=-110, arm_v_x=14)

        def merken(sz):
            sz.flach = sz.teig_h

        return [
            Gehe(bis=self.x0, haltung=tragen),
            Setze(rollen=True),
            rollen(1.1, 10, 14, 22, 30),
            Setze(rollen=False), Jeweils(0.01, lambda sz, u: merken(sz)),
            Setze(augen=True, boese=1.0, striche=True),
            Jeweils(0.4, lambda sz, u: (federn(sz, u), zurueck(sz, u))),
            Setze(striche=False, neigung=0.0),
            Stehe(0.6, lambda sz, u: Pose(arm_v=-60, arm_v_x=14, blick_x=1, sorge=0.5, auge_zu=blinzeln(sz.t))),
            Setze(rollen=True),
            rollen(1.2, 22, 26, 34, 16),
            Setze(rollen=False), Jeweils(0.01, lambda sz, u: merken(sz)),
            Setze(striche=True),
            Jeweils(0.4, lambda sz, u: (federn(sz, u), zurueck(sz, u))),
            Setze(striche=False, neigung=0.0),
            publikum(0.8, arm_v=-60, arm_v_x=14, sorge=0.4),
            Setze(rollen=True, augen=False),
            rollen(1.3, 38, 34, 52, 6),
            Setze(rollen=False), Jeweils(0.01, lambda sz, u: merken(sz)),
            Wandel(0.35, neigung=0.0),
            Stehe(0.9, lambda sz, u: Pose(arm_v=-150, arm_h=-140, arm_v_x=20, bein_v=-14, bein_h=14,
                                         mund_offen=u < 0.4, auge_zu=u > 0.4)),
            Setze(augen=True, boese=1.0),
            Jeweils(0.3, schnurren),
            Setze(grinsen=True),
            Stehe(0.35, Pose(kopf_vorn=True, sorge=1.0, schreck=0.3, arm_v=-90, arm_v_x=14)),
            Setze(striche=True, teig_xy=lambda sz: (sz.tx, sz.boden)),
            Jeweils(0.45, anspringen),
            Setze(kokon=True, teig_xy=None, striche=False, holz=lambda sz: sz.holz_los()),
            publikum(1.3, sorge=0.7),
            Setze(richtung=lambda sz: sz.naechster_rand()),
            Hoppel(tempo=1.4, hoehe=16,
                   haltung=lambda p, sz: Pose(hub=p.hub, kopf_vorn=True, sorge=0.7, auge_zu=p.auge_zu)),
        ]

    def schreck_ablauf(self):
        self.rollen, self.teig_xy = False, None
        if self.holz is None:
            self.holz = self.holz_los()
        if self.kokon:
            return [Setze(striche=True, richtung=self.naechster_rand()), Hoppel(tempo=3.0, hoehe=26, haltung=lambda p, sz: Pose(
                hub=p.hub, kopf_vorn=True, schreck=1.0))]
        self.teig_h = 64
        self.augen = True
        return [Setze(neigung=0.0), Erschrecke(), Renne(zum='rand')]

    def holz_los(self):
        x, y = hand(self)
        self.holz_vy = -260 * self.s
        return [x, y, 0.0]

    # -- Zustand

    def weiter(self, dt):
        if self.holz is not None and self.holz[1] < self.boden - 7 * self.s:
            self.holz_vy += 1400 * self.s * dt
            self.holz[1] = min(self.boden - 7 * self.s, self.holz[1] + self.holz_vy * dt)
            self.holz[2] += 400 * dt * self.richtung
            if self.holz[1] >= self.boden - 7 * self.s:
                self.holz[2] = 0.0

    def teig_b(self):
        return min(300.0, MENGE / self.teig_h)

    # -- Zeichnen

    def zeichne_hinten(self, p):
        s = self.s
        if self.teig_xy is None and not self.kokon:
            p.save()
            p.translate(self.tx, self.boden)
            p.scale(s, s)
            pose = Pose(blick_x=-self.richtung, auge_zu=blinzeln(self.t, 0.7))
            zeichne_teig(p, self.teig_b(), self.teig_h, pose if self.augen else None, self.boese, self.grinsen)
            p.restore()

    def zeichne_vorn(self, p):
        s, r = self.s, self.richtung
        if self.teig_xy is not None:
            x, y = self.teig_xy
            p.save()
            p.translate(x, y)
            p.scale(s, s)
            zeichne_teig(p, 70, 62, Pose(blick_x=r * -1), 1.0, True)
            p.restore()
        if self.kokon and self.zeige_figur:
            p.save()
            p.translate(self.x, self.y - self.hopp)
            p.scale(s * r, s)
            p.setBrush(linear(-44, 0, 44, 0, TEIG.lighter(106), TEIG_DUNKEL))
            p.drawRoundedRect(QRectF(-46, -156, 92, 150), 30, 30)
            p.setBrush(TEIG_DUNKEL.darker(108))
            for y in (-118, -76, -36):
                p.drawRoundedRect(QRectF(-44, y, 88, 3), 1.5, 1.5)
            p.translate(0, -50)
            zeichne_teiggesicht(p, -24, Pose(auge_zu=blinzeln(self.t, 1.3)), 0.6, True)
            p.restore()
        if self.zeige_figur or self.holz is not None:
            if self.holz is not None:
                x, y, w = self.holz
            else:
                x, y = hand(self)
                w = 0.0
                if self.rollen:
                    y = self.boden - (self.teig_h + 9) * s
            p.save()
            p.translate(x, y)
            p.rotate(w)
            p.scale(s, s)
            zeichne_nudelholz(p)
            p.restore()

    def grenzen_extra(self):
        s = self.s
        b = self.teig_b() * s
        k = QRectF(self.tx - b / 2 - 10 * s, self.boden - 110 * s, b + 20 * s, 110 * s)
        if self.holz is not None:
            k = k.united(QRectF(self.holz[0] - 50 * s, self.holz[1] - 50 * s, 100 * s, 100 * s))
        else:
            x, y = hand(self)
            k = k.united(QRectF(x - 50 * s, y - 20 * s, 100 * s, 40 * s))
        if self.teig_xy is not None:
            x, y = self.teig_xy
            k = k.united(QRectF(x - 40 * s, y - 60 * s, 80 * s, 70 * s))
        return k
