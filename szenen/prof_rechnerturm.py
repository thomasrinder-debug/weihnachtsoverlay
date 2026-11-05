import math
import random
from dataclasses import replace

from PyQt6.QtCore import QPointF, QRectF
from PyQt6.QtGui import QColor

from zeichnen.figur import Pose
from zeichnen.grundlagen import blinzeln, glatt
from zeichnen.labor import zeichne_turm
from zeichnen.labor_d import TURM, Truemmer, zeichne_schraube

from .basis import Erschrecke, Gehe, Gleite, Jeweils, Schaue, Schritt, Setze, Stehe, Tu, Wandel
from .professor import FUNKEN, RAUCH, HaareHoch, ProfSzene, triumph_pose
from .prof_klopfen import STAUB, Hau

SCHRAUBE_G = 2.6     # die große Schraube


class Tritt(Schritt):
    """Holt mit dem vorderen Bein aus und tritt zu; treffer(sz) beim Aufprall."""

    def __init__(self, treffer=None, ausholen=0.55, nach=0.45):
        self.treffer, self.ausholen, self.nach = treffer, ausholen, nach
        self.dauer = ausholen + 0.12 + nach

    def beginn(self, sz):
        self.getroffen = False

    def weiter(self, sz, u, dt):
        if u < self.ausholen:
            f = glatt(u / self.ausholen)
            bein, arm = 45 * f, -60 * f
            sz.neigung = -4 * f
        elif u < self.ausholen + 0.12:
            f = (u - self.ausholen) / 0.12
            bein, arm = 45 - 140 * f * f, -60 + 120 * f
            sz.neigung = 6 * f
        else:
            bein, arm = -95, 60
            sz.neigung = 6
            if not self.getroffen:
                self.getroffen = True
                if self.treffer:
                    self.treffer(sz)
        sz.pose = Pose(bein_v=bein, bein_h=6, arm_v=arm, arm_h=-arm - 40, arm_v_x=14, hub=-4,
                       mund_offen=u > self.ausholen, auge_zu=self.ausholen < u < self.ausholen + 0.2,
                       sorge=0.0, wipp=4)

    def ende(self, sz):
        sz.neigung = 0.0


class Turm(ProfSzene):
    """Ein Tritt zerlegt den Rechnerturm; nach einer Pause rollt eine Schraube nach,
    er stellt triumphierend den Fuß darauf und rutscht aus."""
    name, titel, reihenfolge = 'rechnerturm', 'Schraube locker', 85

    def vorbereiten(self):
        self.rand = -self.richtung
        self.tx = self.vom_rand(0.1)
        self.ganz = True
        self.zittern = 0.4
        self.truemmer = []
        self.schraube = None          # [x, dreh] der großen Schraube
        self.sterne = False
        self._qualm = 0.0

    def weiter(self, dt):
        super().weiter(dt)
        for t in self.truemmer:
            t.schritt(dt, self.boden, self.s)
        self.truemmer = [t for t in self.truemmer if t.y < self.boden + 120 * self.s]
        if self.ganz and not self.erschreckt:
            self._qualm -= dt
            if self._qualm <= 0:
                self._qualm = 0.9 - 0.5 * self.zittern
                x, y = self.tx, self.boden - 64 * TURM * self.s
                self.streue(x, y, 2 + int(3 * self.zittern), RAUCH, tempo=40, dauer=0.9, r=(4, 9),
                            richtung=-math.pi / 2, streuung=0.5)
        if self.sterne and self.zeige_figur and int(self.t * 8) != int((self.t - dt) * 8):
            q = self.trafo().map(QPointF(4, -232))
            w = self.t * 7
            self.streue(q.x() + math.cos(w) * 26 * self.s, q.y() + math.sin(w) * 8 * self.s, 1, FUNKEN,
                        tempo=10, dauer=0.5, r=(3, 5), art='stern')

    # -- Turm

    def teil(self, art, dx, dy, vx, vy, groesse=TURM, durch=False):
        s = self.s
        self.truemmer.append(Truemmer(art, self.tx + dx * s, self.boden - dy * s,
                                      self.rand * vx * s + random.uniform(-40, 40) * s,
                                      -vy * s * random.uniform(0.85, 1.15),
                                      random.uniform(-20, 20), random.uniform(-700, 700), groesse, durch=durch))

    def zerlegen(self, sz):
        self.ganz = False
        s = self.s
        for art, dx, dy, vx, vy in (('wand', 0, 60, 120, 420), ('front', -10, 56, 70, 520), ('wand', 8, 56, 260, 300),
                                    ('platine', 0, 70, 180, 640), ('luefter', 0, 40, 100, 560),
                                    ('laufwerk', 0, 90, 330, 380), ('laufwerk', 0, 84, 40, 700),
                                    ('netzteil', 0, 30, 220, 250), ('feder', 0, 70, 60, 650),
                                    ('feder', 0, 60, 200, 500)):
            self.teil(art, dx, dy, vx, vy)
        for _ in range(5):
            self.teil('schraube', 0, 60, random.uniform(20, 300), random.uniform(300, 650), 0.8)
        x, y = self.tx, self.boden - 50 * TURM * s
        self.streue(x, y, 22, RAUCH, tempo=170, dauer=0.9, r=(8, 18))
        self.streue(x, y, 12, FUNKEN, tempo=330, dauer=0.6, r=(3, 7), art='stern')
        self.streue(x, self.boden - 4 * s, 10, STAUB, tempo=140, dauer=0.8, r=(6, 12))

    def wegtreten(self, sz):
        for t in self.truemmer:
            t.ruht, t.durch = False, True
            t.vx = self.rand * random.uniform(500, 900) * self.s
            t.vy = -random.uniform(250, 650) * self.s
            t.vdreh = random.uniform(-900, 900)
        if self.schraube:
            x, d = self.schraube
            self.truemmer.append(Truemmer('schraube', x, self.boden - 8 * self.s, self.rand * 800 * self.s,
                                          -500 * self.s, d, 900, SCHRAUBE_G, durch=True))
            self.schraube = None
        x = self.tx + self.rand * 20 * self.s
        self.streue(x, self.boden - 20 * self.s, 14, STAUB, tempo=170, dauer=0.8, r=(6, 14))
        self.streue(x, self.boden - 30 * self.s, 6, FUNKEN, tempo=220, dauer=0.5, r=(3, 6), art='stern')

    # -- Schraube

    def fuss_x(self):
        return self.x + self.richtung * 14 * self.s

    def schraube_rollt(self, dauer, von, nach):
        """Die Schraube rollt (liegend, rollt um ihre Achse) von x0 nach x1."""
        def f(sz, u):
            g = min(1.0, u / dauer)
            x0, x1 = von(sz), nach(sz)
            x = x0 + (x1 - x0) * (1 - (1 - g) ** 2)
            sz.schraube = [x, 90 + 25 * math.sin(u * 14) * (1 - g)]
        return Jeweils(dauer, f)

    def rutsch(self, sz):
        x, d = self.schraube
        self.truemmer.append(Truemmer('schraube', x, self.boden - 5.5 * SCHRAUBE_G * self.s,
                                      self.rand * 420 * self.s, -260 * self.s, d, 1400, SCHRAUBE_G))
        self.schraube = None

    def landung(self, sz):
        q = self.trafo().map(QPointF(-40, -100))
        self.streue(q.x(), self.boden - 6 * self.s, 14, STAUB, tempo=150, dauer=0.8, r=(6, 13))
        self.sterne = True

    # -- Zeichnen

    def zeichne_requisiten(self, p):
        if self.ganz:
            p.save()
            p.translate(self.tx, self.boden)
            p.scale(self.s * TURM, self.s * TURM)
            dreh = self.zittern * 2.5 * math.sin(self.t * 47)
            zeichne_turm(p, 0, 0, 0.0, dreh, self.t)
            if self.zittern > 0.5:
                p.setBrush(QColor('#FF4F4F') if (self.t * 5) % 1 < 0.5 else QColor('#5A5A50'))
                p.drawEllipse(QPointF(7, -12), 1.8, 1.8)
            p.restore()
        for t in self.truemmer:
            t.zeichne(p, self.s)

    def zeichne_davor(self, p):
        if self.schraube:
            x, d = self.schraube
            zeichne_schraube(p, x, self.boden - 5.5 * SCHRAUBE_G * self.s, d, self.s * SCHRAUBE_G)

    def requisiten_kasten(self):
        s = self.s
        k = QRectF(self.tx - 20 * TURM * s, self.boden - 66 * TURM * s, 40 * TURM * s, 66 * TURM * s) \
            if self.ganz else QRectF()
        for t in self.truemmer:
            k = k.united(t.kasten(s))
        if self.schraube:
            x, _ = self.schraube
            k = k.united(QRectF(x - 12 * s * SCHRAUBE_G, self.boden - 14 * s * SCHRAUBE_G, 24 * s * SCHRAUBE_G,
                                14 * s * SCHRAUBE_G))
        return k

    # -- Ablauf

    def ablauf(self):
        self.x = self.aussen(self.rand)
        r = self.rand
        abstand = (14 * TURM + 70) * self.s
        oben = lambda sz: (sz.tx - r * 8 * sz.s, sz.boden - 62 * TURM * sz.s)
        haufen = lambda sz: sz.tx + r * 40 * sz.s
        liegend = Pose(bein_v=-70, bein_h=-40, arm_v=-150, arm_h=-120, arm_v_x=14, auge_zu=False, schreck=0.0,
                       sorge=0.6, mund_offen=True)
        return [
            Gehe(bis=self.tx - r * abstand),
            Setze(richtung=r),
            Stehe(0.9, lambda sz, u: Pose(sorge=0.5, blick_y=0.2, auge_zu=blinzeln(sz.t))),
            Hau(oben, n=2, takt=0.4, holen=-40, nach=0.3, sorge=0.5,
                treffer=lambda sz, k: setattr(sz, 'zittern', min(1.0, sz.zittern + 0.3))),
            Stehe(0.6, lambda sz, u: Pose(sorge=1.0, blick_y=0.1, arm_v=-30)),
            HaareHoch(0.4),
            Tritt(self.zerlegen),
            Setze(haare=0.0),
            Stehe(0.9, lambda sz, u: Pose(arm_v=-70 + 18 * math.sin(u * 22), arm_h=-70 - 18 * math.sin(u * 22),
                                          arm_v_x=14, blick_y=0.3, auge_zu=blinzeln(sz.t))),
            Stehe(1.2, lambda sz, u: Pose(kopf_vorn=True, auge_zu=True, hub=-3 * abs(math.sin(u * 6)),
                                          arm_v=-20, arm_h=20)),
            self.schraube_rollt(1.7, haufen, lambda sz: sz.fuss_x() + r * 34 * sz.s),
            Stehe(0.7, lambda sz, u: Pose(blick_y=0.9, sorge=0.0, auge_zu=blinzeln(sz.t), mund_offen=u > 0.4)),
            Schaue(0.9),
            Gleite(lambda sz: sz.x + r * 30 * sz.s, 0.35,
                   lambda sz, u: Pose(bein_v=-30 * math.sin(min(1, u / 0.35) * math.pi), blick_y=0.6)),
            Stehe(1.0, triumph_pose),
            Tu(self.rutsch),
            Wandel(0.25, neigung=-82, hopp=lambda sz: 70 * sz.s),
            Wandel(0.18, hopp=lambda sz: 38 * sz.s),
            Tu(self.landung),
            Stehe(1.5, lambda sz, u: replace(liegend, auge_zu=(u * 3) % 1 < 0.2)),
            Setze(sterne=False),
            Wandel(0.5, neigung=0.0, hopp=0.0),
            Stehe(0.6, lambda sz, u: Pose(sorge=0.8, blick_y=0.4, arm_v=-20)),
            HaareHoch(0.5),
            Tritt(self.wegtreten, ausholen=0.4, nach=0.4),
            Setze(haare=0.0),
            Gehe(bis=lambda sz: sz.aussen(r), tempo=0.8,
                 haltung=lambda pose, sz: Pose(bein_v=-55, bein_h=pose.bein_h * 0.4, arm_v=30, arm_h=-20,
                                               hub=-10 * abs(math.sin(sz.t * 8)), sorge=1.0,
                                               auge_zu=blinzeln(sz.t))),
        ]

    def schreck_ablauf(self):
        self.nebenbei.clear()
        self.halt = self.halt_h = None
        self.sterne = False
        tief = 340 * self.s
        sichtbar = self.zeige_figur and self.figur_sichtbar()
        if not sichtbar:
            self.zeige_figur = False
        return [HaareHoch(1.0), Erschrecke(0.3, 46) if sichtbar else Setze(),
                Setze(neigung=0.0, hopp=0.0),
                Wandel(0.18, stauchen=0.45),
                Wandel(0.45, y=lambda sz: sz.y + tief, senke=tief),
                Tu(lambda sz: setattr(sz, 'zeige_figur', False))] + self._ende()
