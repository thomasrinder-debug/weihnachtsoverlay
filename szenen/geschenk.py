import math
import random

from PyQt6.QtCore import QRectF
from PyQt6.QtGui import QColor

from zeichnen.figur import Pose
from zeichnen.figuren import Wichtel
from zeichnen.grundlagen import GOLD_HELL, blinzeln, glatt
from zeichnen.requisiten import zeichne_feder, zeichne_geschenk

from .basis import Jeweils, Mit, Schritt, Setze, Stehe, Szene, Wandel, Warte

B, H = 110, 100          # Größe der Schachtel in Einheiten
LILA = QColor('#7B3FB8')


class Huepfe(Schritt):
    """Die Schachtel hüpft bis x=bis (None: aus dem Bild), ein Hüpfer dauert 'takt' Sekunden."""

    def __init__(self, bis=None, takt=0.42, weite=70, hoehe=45):
        self.bis, self.takt, self.weite, self.hoehe = bis, takt, weite, hoehe

    def beginn(self, sz):
        ziel = self.bis if self.bis is not None else sz.aussen(sz.naechster_rand_box())
        self.ziel = ziel
        self.r = 1 if ziel > sz.bx else -1
        self.v = self.weite * sz.s / self.takt

    def weiter(self, sz, u, dt):
        f = (u / self.takt) % 1.0
        sz.bx += self.r * self.v * dt
        sz.bhopp = math.sin(math.pi * f) * self.hoehe * sz.s
        sz.bstauch = 1 - 0.12 * max(0.0, 1 - f / 0.15) - 0.12 * max(0.0, (f - 0.85) / 0.15)

    def fertig(self, sz, u):
        return (sz.bx - self.ziel) * self.r >= 0

    def ende(self, sz):
        sz.bx, sz.bhopp, sz.bstauch = self.ziel, 0.0, 1.0


class Geschenk(Szene):
    """Ein Geschenk hüpft herein, wackelt, der Deckel fliegt weg und ein Wichtel
    schnellt auf einer Sprungfeder heraus. Er schaut sich um, winkt, taucht wieder
    ab, der Deckel klappt zu und das Paket hüpft davon."""
    name, titel, reihenfolge = 'geschenk', 'Überraschungspaket', 15

    def vorbereiten(self):
        self.zeige_figur = False
        self.w = self.dazu('w', Wichtel, groesse=0.52)
        self.w.richtung = self.richtung
        self.bx = self.aussen(-self.richtung)
        self.bhopp, self.bstauch, self.bdreh = 0.0, 1.0, 0.0
        self.ddx = self.ddy = self.ddreh = 0.0     # Deckel
        self.feder = 0.0                          # wie weit der Wichtel herausschaut (Einheiten)
        self.farbe = random.choice((LILA, QColor('#D3172E'), QColor('#2A6FD6')))

    def naechster_rand_box(self):
        return -1 if self.bx - self.geo.left() < self.geo.right() - self.bx else 1

    def deckel_flug(self, dauer, nach, hoehe):
        def f(sz, u):
            g = min(1.0, u / dauer)
            a = sz._von
            sz.ddx = a[0] + (nach[0] - a[0]) * g
            sz.ddy = a[1] + (nach[1] - a[1]) * g - hoehe * 4 * g * (1 - g)
            sz.ddreh = a[2] + (nach[2] - a[2]) * g
        return [Setze(_von=lambda sz: (sz.ddx, sz.ddy, sz.ddreh)), Jeweils(dauer, f)]

    def boing(self, dauer, hoehe):
        def f(sz, u):
            sz.feder = hoehe * (1 - math.exp(-4 * u) * math.cos(16 * u))
        return Jeweils(dauer, f)

    def ablauf(self):
        weg = (130, H - 1, 360)
        um = lambda d, u: Pose(kopf_vorn=u > 0.9, blick_x=math.sin(u * 4.5) if u < 0.9 else 0,  # noqa: E731
                               mund_offen=False, auge_zu=blinzeln(d.t, 0.5))
        return [
            Huepfe(self.vom_rand(random.uniform(0.12, 0.17))),
            Warte(0.7),
            Jeweils(0.9, lambda sz, u: setattr(sz, 'bdreh', math.sin(u * 38) * 7 * (1 - u / 0.9))),
            Setze(bdreh=0.0), Warte(0.3),
            Jeweils(0.5, lambda sz, u: setattr(sz, 'bdreh', math.sin(u * 50) * 10)),
            Setze(bdreh=0.0),
            *self.deckel_flug(0.6, weg, 150),
            Mit('w', Setze(pose=Pose(arm_v=-150, arm_h=-150, mund_offen=True))),
            self.boing(1.1, 140),
            Mit('w', Stehe(2.0, um)),
            Mit('w', Stehe(1.2, lambda d, u: Pose(kopf_vorn=True, arm_v=-125 + 22 * math.sin(u * 10), arm_v_x=8,
                                                  mund_offen=(u * 4) % 2 < 1))),
            Mit('w', Stehe(0.5, Pose(kopf_vorn=True, auge_zu=True))),
            Jeweils(0.3, lambda sz, u: setattr(sz, 'feder', 140 * (1 - glatt(u / 0.3)))),
            Setze(feder=0.0),
            *self.deckel_flug(0.45, (0, 0, 0), 120),
            Warte(0.5),
            Huepfe(None, takt=0.36),
        ]

    def schreck_ablauf(self):
        self.nebenbei.clear()
        neu = []
        if self.feder > 5:
            neu += [Mit('w', Setze(striche=True, pose=Pose(kopf_vorn=True, schreck=1.0, arm_v=-150, arm_h=-150))),
                    Wandel(0.15, feder=lambda sz: sz.feder + 20), Warte(0.1), Wandel(0.12, feder=0.0), Mit('w', Setze(striche=False))]
        if abs(self.ddx) + abs(self.ddy) > 1:
            neu += self.deckel_flug(0.2, (0, 0, 0), 30)
        return neu + [Setze(bdreh=0.0), Huepfe(None, takt=0.22, weite=90, hoehe=60)]

    # -- Zeichnen

    def box_trafo(self, p):
        p.translate(self.bx, self.boden - self.bhopp)
        p.rotate(self.bdreh)
        p.scale(self.s * (2 - self.bstauch), self.s * self.bstauch)

    def weiter(self, dt):
        w = self.w
        w.zeige_figur = self.feder > 1
        w.x = self.bx
        w.y = self.boden - self.bhopp + (14 - self.feder) * self.s

    def zeichne_hinten(self, p):
        if self.feder > 1:
            p.save()
            self.box_trafo(p)
            zeichne_feder(p, 0, -10, 14 - self.feder, 18, 5)
            p.restore()

    def zeichne_vorn(self, p):
        p.save()
        self.box_trafo(p)
        zeichne_geschenk(p, B, H, self.farbe, GOLD_HELL.darker(110), (self.ddx, self.ddy, self.ddreh))
        p.restore()

    def grenzen_extra(self):
        s = self.s
        return QRectF(self.bx - 110 * s, self.boden - self.bhopp - 230 * s, 240 * s, 236 * s)
