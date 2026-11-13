import math
import random

from PyQt6.QtCore import QRectF
from PyQt6.QtGui import QColor

from zeichnen.figur import Pose, hand_punkt
from zeichnen.figuren import Wichtel
from zeichnen.grundlagen import blinzeln
from zeichnen.hoersaal import zeichne_blatt, zeichne_haken, zeichne_stempel

from .basis import Gehe, Mit, Nebenbei, Setze, Stehe, Szene, Tu, Wandel, Warte
from .hs_basis import Publikumsblick, auf_figur

STAUB = [QColor(235, 230, 220, 210), QColor(210, 205, 195, 190)]
TINTE = [QColor(214, 24, 40, 220), QColor(250, 250, 245, 220)]
WG = 0.85          # Größe des Wichtels


class HsStempel(Szene):
    """Klausurkorrektur: Der Weihnachtsmann legt Blätter hin, der Wichtel-Tutor haut mit einem
    Riesenstempel Haken darauf, immer schneller, zuletzt mit geschlossenen Augen. Ein Blatt fällt
    herunter, er hebt es auf und hält es stolz hoch, während der Wichtel blind heranrückt.
    BAM: platt wie ein Pfannkuchen, mit rotem Haken auf der Mütze. Er ploppt nur halb wieder
    hoch und watschelt breit hinaus."""
    name, titel, reihenfolge = 'hs_stempel', 'Klausurstempel', 1004

    def vorbereiten(self):
        r, s = self.richtung, self.s
        self.r0 = r
        self.xw = self.vom_rand(random.uniform(0.09, 0.11))
        self.xp = self.xw + r * 50 * WG * s
        self.lift = 0.0
        self.blind = False
        self.blatt_da = False
        self.flieger = []          # [x, y, vx, vy, dreh]
        self.stapel = 0
        self.faellt = None         # (x, y0, t0) des heruntergefallenen Blatts
        self.haelt = False
        self.trifft = False
        self.haken_kopf = False
        self.w = self.dazu('w', Wichtel, groesse=WG)
        self.w.x = self.aussen(-r) - r * 40 * s

    def stempel_x(self):
        w = self.w
        return w.x + w.richtung * 50 * w.s

    def stempel_unten(self):
        s = self.s
        if self.trifft:
            return self.y - 262 * s * self.stauchen
        return self.boden - 3 * s - self.lift * 115 * s - self.w.hopp

    def ablauf(self):
        r, s = self.richtung, self.s
        self.x = self.aussen(-r)
        xm = self.xp + r * 92 * s

        def legen(dauer):
            return [Stehe(dauer * 0.3, lambda sz, u: Pose(arm_v=-45, arm_v_x=14, blick_y=0.6, auge_zu=False)),
                    Setze(blatt_da=True, pose=Pose(arm_v=10, blick_y=0.4)),
                    Wandel(dauer * 0.22, lift=0.0),
                    Tu(lambda sz: sz.bam()),
                    Wandel(dauer * 0.3, lift=1.0)]

        takte = []
        for d in (0.95, 0.7, 0.5, 0.38, 0.32):
            takte += legen(d)

        return [
            Nebenbei(Warte(0.35), Mit('w', Gehe(bis=self.xw, tempo=1.1)), Mit('w', Setze(richtung=r))),
            Gehe(bis=xm),
            Setze(richtung=-r),
            Wandel(0.25, lift=1.0),
            *takte,
            Setze(blind=True),
            # Ein Blatt rutscht ihm weg, er hebt es auf
            Tu(lambda sz: sz.fallen_lassen()),
            Stehe(0.45, lambda sz, u: Pose(arm_v=-70 + 40 * u, arm_v_x=14, schreck=0.4, blick_y=0.9)),
            Nebenbei(Wandel(0.5, lift=0.6)),
            Nebenbei(Mit('w', Gehe(bis=lambda d: d.sz.unter_kopf(), tempo=0.35))),
            Wandel(0.3, neigung=32.0),
            Stehe(0.2, Pose(arm_v=-10, arm_v_x=14, blick_y=1.0)),
            Setze(faellt=None, haelt=True),
            Wandel(0.25, neigung=0.0),
            # Stolz hält er das Blatt hoch, über ihm schwebt der Stempel (Erwartungspause)
            Stehe(0.85, lambda sz, u: Pose(kopf_vorn=True, arm_v=-150, arm_v_x=14, mund_offen=u < 0.4,
                                           auge_zu=0.5 < u < 0.62)),
            Nebenbei(Mit('w', Wandel(0.3, stauchen=0.8))),
            Stehe(0.35, Pose(kopf_vorn=False, schreck=1.0, sorge=1.0, blick_x=-1, arm_v=-150, arm_v_x=14)),
            # BAM: der Wichtel springt hoch und haut zu
            Mit('w', Setze(stauchen=1.0)),
            Mit('w', Wandel(0.18, hopp=lambda d: 230 * d.sz.s)),
            Setze(trifft=True, haelt=False),
            Wandel(0.07, stauchen=0.48),
            Tu(lambda sz: sz.platt()),
            Stehe(0.4, Pose(auge_zu=True, kopf_vorn=True, arm_v=60, arm_h=-60, bein_v=-30, bein_h=30)),
            Setze(trifft=False, haken_kopf=True, blind=False, lift=lambda sz: 2.0),
            Nebenbei(Mit('w', Wandel(0.25, hopp=0.0))),
            Wandel(0.25, lift=1.0),
            Nebenbei(Mit('w', Stehe(0.9, Pose(kopf_vorn=True, schreck=1.0, sorge=1.0, arm_v=-120, arm_h=-120)))),
            Publikumsblick(0.85, arm_v=60, arm_h=-60, bein_v=-30, bein_h=30),
            # Er ploppt halb hoch und watschelt breit hinaus
            Wandel(0.12, stauchen=0.8),
            Wandel(0.12, stauchen=0.7),
            Nebenbei(Warte(0.4), Mit('w', Setze(richtung=-r)), Mit('w', Gehe(bis=None, tempo=1.4))),
            Gehe(bis=None, tempo=0.8, haltung=lambda pose, sz: Pose(bein_v=pose.bein_v * 1.4, bein_h=pose.bein_h * 1.4,
                                                                  arm_v=60, arm_h=-60, hub=pose.hub * 2,
                                                                  auge_zu=pose.auge_zu, kopf_vorn=True),
                 neigung=0.0),
            Tu(lambda sz: sz.nebenbei.clear()),
        ]

    def unter_kopf(self):
        x, _ = auf_figur(self, 8, -186)
        return x - self.w.richtung * 50 * self.w.s

    def bam(self):
        s, r = self.s, self.r0
        x = self.stempel_x()
        self.streue(x, self.boden - 4 * s, 6, STAUB, tempo=120, dauer=0.4, r=(4, 8))
        if self.blatt_da:
            self.blatt_da = False
            self.flieger.append([x, self.boden - 30 * s, -r * random.uniform(160, 260) * s,
                                 -random.uniform(320, 420) * s, 0.0])

    def platt(self):
        s = self.s
        self.streue(self.x, self.boden - 10 * s, 14, STAUB, tempo=200, dauer=0.6, r=(7, 13))
        x, y = auf_figur(self, 0, -250)
        self.streue(x, y, 10, TINTE, tempo=200, dauer=0.5, r=(2, 5), schwer=True)

    def fallen_lassen(self):
        self.faellt = (self.stempel_x() + self.richtung * 20 * self.s, self.boden - 120 * self.s, self.t)

    def weiter(self, dt):
        s, r = self.s, self.richtung
        w = self.w
        for f in self.flieger:
            f[0] += f[2] * dt
            f[1] += f[3] * dt
            f[3] += 900 * s * dt
            f[4] += 600 * dt
            if f[1] > self.boden - 10 * s and f[3] > 0:
                f[3] = None
        if any(f[3] is None for f in self.flieger):
            self.stapel += sum(1 for f in self.flieger if f[3] is None)
            self.flieger = [f for f in self.flieger if f[3] is not None]
        if self.trifft:
            w.hopp = max(0.0, self.boden - self.stempel_unten() - self.lift * 115 * s)
        if w.zeige_figur and not self.erschreckt and self.aktuell is not None:
            heben = min(1.0, self.lift)
            if not (w.pose.kopf_vorn and w.pose.schreck > 0.5):
                w.pose = Pose(arm_v=-95 - 60 * heben, arm_h=-90 - 60 * heben, kopf_vorn=False,
                              auge_zu=self.blind or blinzeln(self.t), mund_offen=self.blind,
                              bein_v=w.pose.bein_v, bein_h=w.pose.bein_h, hub=w.pose.hub)

    def zeichne_vorn(self, p):
        s, r = self.s, self.r0
        w = self.w
        # Stapel gestempelter Blätter hinter dem Wichtel
        if self.stapel and (w.zeige_figur or self.zeige_figur):
            for k in range(self.stapel):
                p.save()
                p.translate(self.xw - r * 70 * s + math.sin(k * 2.3) * 3 * s, self.boden - (4 + k * 4) * s)
                p.scale(s * 0.8, s * 0.25)
                p.rotate(math.sin(k * 1.7) * 4)
                zeichne_blatt(p, True)
                p.restore()
        if self.blatt_da:
            p.save()
            p.translate(self.stempel_x(), self.boden - 5 * s)
            p.scale(s * 0.9, s * 0.28)
            zeichne_blatt(p)
            p.restore()
        for f in self.flieger:
            p.save()
            p.translate(f[0], f[1])
            p.scale(s * 0.8, s * 0.8)
            p.rotate(f[4])
            zeichne_blatt(p, True)
            p.restore()
        if self.faellt:
            x, y0, t0 = self.faellt
            u = self.t - t0
            y = min(self.boden - 5 * s, y0 + 260 * s * u)
            liegt = y >= self.boden - 5 * s
            p.save()
            p.translate(x + math.sin(u * 9) * 14 * s * (not liegt), y)
            p.scale(s * 0.9, s * (0.28 if liegt else 0.9))
            p.rotate(0 if liegt else math.sin(u * 9) * 25)
            zeichne_blatt(p)
            p.restore()
        if self.haelt:
            hx, hy = hand_punkt(self.x, self.y - self.hopp, s, self.richtung, self.pose, self.stauchen, self.neigung)
            p.save()
            p.translate(hx, hy - 30 * s)
            p.scale(s, s)
            zeichne_blatt(p, True)
            p.restore()
        if self.haken_kopf and self.zeige_figur:
            x, y = auf_figur(self, 2, -232)
            zeichne_haken(p, x, y, 13 * s * 1.3, breite=3.2 * s)
        if w.zeige_figur:
            p.save()
            p.translate(self.stempel_x(), self.stempel_unten())
            p.scale(s, s)
            zeichne_stempel(p)
            p.restore()

    def grenzen_extra(self):
        s, r = self.s, self.richtung
        k = QRectF(self.stempel_x() - 40 * s, self.stempel_unten() - 100 * s, 80 * s, 100 * s)
        if self.stapel:
            r = self.r0
            k = k.united(QRectF(self.xw - r * 70 * s - 40 * s, self.boden - (40 + self.stapel * 4) * s,
                                80 * s, (40 + self.stapel * 4) * s))
        for f in self.flieger:
            k = k.united(QRectF(f[0] - 45 * s, f[1] - 45 * s, 90 * s, 90 * s))
        if self.faellt or self.blatt_da:
            k = k.united(QRectF(self.stempel_x() - 80 * s, self.boden - 160 * s, 160 * s, 160 * s))
        if self.haelt:
            hx, hy = hand_punkt(self.x, self.y - self.hopp, s, r, self.pose, self.stauchen, self.neigung)
            k = k.united(QRectF(hx - 40 * s, hy - 80 * s, 80 * s, 100 * s))
        if self.haken_kopf:
            x, y = auf_figur(self, 2, -232)
            k = k.united(QRectF(x - 25 * s, y - 25 * s, 50 * s, 50 * s))
        return k

    def schreck_ablauf(self):
        self.trifft = self.haelt = self.blind = False
        self.faellt = None
        self.blatt_da = False
        self.flieger.clear()
        self.stauchen, self.neigung = 1.0, 0.0
        self.w.hopp, self.w.stauchen = 0.0, 1.0
        if not self.w.figur_sichtbar():
            self.stapel = 0
        neu = self.schreck_alle()
        return [Setze(stapel=0)] + neu
