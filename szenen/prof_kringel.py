import math
from dataclasses import replace

from PyQt6.QtCore import QRectF
from PyQt6.QtGui import QColor

from zeichnen.figur import Pose, renn_pose
from zeichnen.grundlagen import blinzeln, glatt
from zeichnen.labor import GLAS_RAND
from zeichnen.labor_d import MON, WAGEN_B, zeichne_hammer_gross, zeichne_kringel
from zeichnen.professor import SCHULTER_Y

from .basis import Erschrecke, Gehe, Schaue, Schritt, Setze, Springe, Stehe, Tu
from .professor import FUNKEN, RAUCH, HaareHoch, denk_pose
from .prof_klopfen import ComputerSzene, Hau

RAD = 140            # Radius des großen Kringels in Einheiten
HAMMER = 1.6 * 44    # Hammerlänge in Einheiten (Griff bis Kopf)


class Laufrad(Schritt):
    """Er rennt im Kringel: tempo 0 auf der Stelle (Hamsterrad), sonst rollt das Rad mit.
    bis: Ziel-x (None: bis das Rad aus dem Bild ist); kopf_vorn(u) schaut ins Publikum."""

    def __init__(self, dauer=None, tempo=0.0, bis=None, kopf=None, renn=9.0):
        self.dauer_v, self.tempo, self.bis, self.kopf, self.renn = dauer, tempo, bis, kopf, renn

    def beginn(self, sz):
        self.ziel = sz.aussen(sz.richtung) + sz.richtung * (RAD + 40) * sz.s if self.bis is None else self.bis

    def weiter(self, sz, u, dt):
        v = self.tempo * sz.tempo * min(1.0, u / 0.4 + 0.2)
        dx = sz.richtung * v * dt
        sz.ring_x += dx
        sz.x = sz.ring_x
        sz.phase += self.renn * dt
        sz.ring_dreh += dx / (RAD * sz.s) - sz.richtung * self.renn * 0.9 * dt * (1 if not self.tempo else 0.15)
        sz.schiebe_wagen()
        p = renn_pose(sz.phase)
        vorn = bool(self.kopf and self.kopf(u))
        sz.pose = Pose(bein_v=p.bein_v, bein_h=p.bein_h, arm_v=p.arm_v, arm_h=p.arm_h, hub=p.hub, wipp=p.wipp,
                       mund_offen=True, kopf_vorn=vorn, sorge=0.5 if vorn else 0.0)
        sz.y = sz.ring_y() + (RAD - 8) * sz.s

    def fertig(self, sz, u):
        if self.dauer_v is not None:
            return u >= self.dauer_v
        return (sz.ring_x - self.ziel) * sz.richtung >= 0


class Kringel(ComputerSzene):
    """Der Ladekringel dreht und dreht, er holt den Hammer; der Kringel fällt aus dem
    Bildschirm und rollt davon, er rennt hinterher und läuft darin wie im Hamsterrad."""
    name, titel, reihenfolge = 'kringel', 'Ladehemmung', 84

    def vorbereiten(self):
        self.computer_vorbereiten(0.1)
        self.ring = None          # 'fall', 'roll', 'steht', 'rad'
        self.ring_x = self.ring_yy = 0.0
        self.ring_r = 10 * MON
        self.ring_dreh = 0.0
        self.ring_v = 0.0
        self.ring_t = 0.0
        self.hammer = False

    def weiter(self, dt):
        super().weiter(dt)
        if self.ring is None:
            self.kringel = self.t * 6
        if self.ring == 'fall':
            self.ring_v += 1500 * self.s * dt
            self.ring_yy += self.ring_v * dt
            self.ring_x -= self.rand * 60 * self.s * dt
            if self.ring_yy >= self.boden - self.ring_r * self.s:
                self.ring_yy = self.boden - self.ring_r * self.s
                if self.ring_v > 200 * self.s:
                    self.ring_v *= -0.35
                else:
                    self.ring, self.ring_t, self.ring_x0 = 'roll', 0.0, self.ring_x
        elif self.ring == 'roll':
            self.ring_t += dt
            f = min(1.0, self.ring_t / 1.9)
            alt = self.ring_x
            self.ring_x = self.ring_x0 + (self.roll_ziel - self.ring_x0) * (1 - (1 - f) ** 2)
            self.ring_r = 10 * MON + (RAD - 10 * MON) * glatt(min(1.0, self.ring_t / 1.1))
            self.ring_yy = self.boden - self.ring_r * self.s
            self.ring_dreh += (self.ring_x - alt) / (self.ring_r * self.s)
            if f >= 1:
                self.ring = 'steht'
        elif self.ring == 'rad':
            self.ring_yy = self.boden - RAD * self.s

    def ring_y(self):
        return self.ring_yy

    def schiebe_wagen(self):
        """Rollt das Rad gegen den Wagen, schiebt es ihn vor sich her."""
        if self.weg_ist:
            return
        vorn = self.ring_x + self.rand * RAD * self.s
        rand_wagen = self.wx - self.rand * (WAGEN_B / 2) * self.s
        if (vorn - rand_wagen) * self.rand > 0:
            self.wx += vorn - rand_wagen

    # -- Schläge

    def schirm(self, sz):
        return sz.mon_punkt(-sz.rand * 4, -50)

    def hammer_ziel(self, sz):
        """Hand so, dass der Hammerkopf den Schirm trifft."""
        zx, zy = self.schirm(sz)
        sx, sy = sz.x + sz.richtung * 10 * sz.s, sz.y + SCHULTER_Y * sz.s
        d = math.hypot(zx - sx, zy - sy) or 1
        k = max(0.3, (d - HAMMER * 0.85 * sz.s) / d)
        return sx + (zx - sx) * k, sy + (zy - sy) * k

    def kringel_raus(self, sz, k):
        self.stoss(14, 1.0)
        self.kringel = None
        self.bild, self.sprung = 0.55, 1.0
        x, y = self.schirm(sz)
        self.streue(x, y, 8, FUNKEN, tempo=230, dauer=0.6, r=(3, 6), art='stern')
        self.streue(x, y, 10, [GLAS_RAND, QColor(200, 240, 255, 220)], tempo=230, dauer=0.8, r=(2, 4), schwer=True,
                    richtung=-math.pi / 2, streuung=1.4)
        self.ring = 'fall'
        self.ring_x, self.ring_yy = self.mon_punkt(0, -50)
        self.ring_v = -250 * self.s
        self.roll_ziel = self.vom_rand(0.27, self.rand)

    def hammer_halten(self, p, hx, hy):
        zeichne_hammer_gross(p, hx, hy, self.pose.arm_v)

    # -- Zeichnen

    def ring_zeichnen(self, p):
        if self.ring:
            zeichne_kringel(p, self.ring_x, self.ring_yy, self.ring_r * self.s, self.ring_dreh)

    def zeichne_hinten(self, p):
        super().zeichne_hinten(p)
        if self.ring == 'rad':
            self.ring_zeichnen(p)

    def zeichne_vorn(self, p):
        super().zeichne_vorn(p)
        if self.ring and self.ring != 'rad':
            self.ring_zeichnen(p)

    def grenzen_extra(self):
        k = super().grenzen_extra()
        if self.ring:
            r = self.ring_r * self.s * 1.15
            k = k.united(QRectF(self.ring_x - r, self.ring_yy - r, 2 * r, 2 * r).intersected(
                self.geo.adjusted(-400 * self.s, -400 * self.s, 400 * self.s, 0)))
        return k

    # -- Ablauf

    def ablauf(self):
        self.x = self.aussen(self.rand)
        r = self.rand
        warten = lambda sz, u: Pose(arm_v=-55, arm_h=-50, arm_v_x=16, bein_v=-14 * abs(math.sin(u * 9)),
                                    blick_y=-0.3, auge_zu=blinzeln(sz.t))
        trommeln = lambda sz, u: Pose(arm_v=sz.arm_zu(*sz.mon_punkt(-r * 30, 8)) + 6 * math.sin(u * 30),
                                      sorge=0.5, blick_y=-0.3, auge_zu=blinzeln(sz.t))
        return [
            Gehe(bis=self.innen(100)),
            Setze(richtung=r),
            Stehe(1.6, warten),
            Schaue(1.2),
            Setze(richtung=r),
            Stehe(1.0, trommeln),
            Stehe(0.9, denk_pose),
            Stehe(0.35, lambda sz, u: Pose(arm_v=-10 - 140 * min(1, u * 3), arm_v_x=6, kopf_vorn=True,
                                           mund_offen=True)),
            Setze(halt=lambda sz: sz.hammer_halten),
            Stehe(0.6, lambda sz, u: Pose(arm_v=-160, arm_v_x=12, kopf_vorn=True, mund_offen=True, sorge=0.0)),
            HaareHoch(0.4),
            Hau(self.hammer_ziel, n=1, takt=0.75, holen=-90, treffer=self.kringel_raus, nach=0.5),
            Setze(haare=0.0, richtung=-r),
            Stehe(0.6, lambda sz, u: Pose(arm_v=-40, schreck=0.6, blick_y=0.6, mund_offen=True)),
            Setze(halt=None),
            Gehe(bis=lambda sz: sz.roll_ziel + r * (RAD + 70) * sz.s, tempo=2.4,
                 haltung=lambda pose, sz: replace(pose, arm_v=-100, mund_offen=True)),
            Stehe(0.3, Pose(arm_v=-110, arm_h=-90, sorge=0.3, bein_v=-10, bein_h=20)),
            Springe(lambda sz: (sz.ring_x, sz.boden - 8 * sz.s), dauer=0.6, hoehe=150),
            Tu(lambda sz: setattr(sz, 'ring', 'rad')),
            Laufrad(dauer=1.4),
            Laufrad(dauer=1.8, kopf=lambda u: 0.3 < u < 1.5),
            Setze(richtung=r),
            Laufrad(dauer=0.5, renn=14),
            Laufrad(tempo=2.2, renn=12),
        ]

    def schreck_ablauf(self):
        if self.ring == 'rad' and self.zeige_figur:
            self._vorher()
            r = self.naechster_rand()
            return [HaareHoch(1.0), Erschrecke(0.3, 30), Setze(richtung=r, y=lambda sz: sz.boden - 8 * sz.s),
                    Laufrad(tempo=4.5, renn=18)] + self._ende()
        if self.ring:
            k = QRectF(self.ring_x - self.ring_r * self.s, self.ring_yy - self.ring_r * self.s,
                       2 * self.ring_r * self.s, 2 * self.ring_r * self.s)
            self.streue(k.center().x(), k.center().y(), 14, RAUCH, tempo=120, dauer=0.6, r=(6, 14))
            self.ring = None
        return self.schreck_rennen()
