"""Sicherheitsklopfer, dazu die gemeinsame Grundlage der Computer-Szenen
(Rollwagen mit Röhrenmonitor, herumfliegende Trümmer, Schlagen, Wagen wegschieben)."""
import math
import random

from PyQt6.QtCore import QRectF
from PyQt6.QtGui import QColor

from zeichnen.figur import Pose
from zeichnen.grundlagen import blinzeln, glatt
from zeichnen.labor import BEIGE, BEIGE_DUNKEL
from zeichnen.labor_d import MON, WAGEN_B, WAGEN_OBEN, zeichne_gehaeuse, zeichne_roehre, zeichne_rollwagen

from .basis import Erschrecke, Gehe, Gleite, Schaue, Schritt, Setze, Stehe, Tu, Wandel, wert
from .professor import FUNKEN, RAUCH, HaareHoch, ProfSzene, denk_pose, schieben, triumph_pose

STAUB = [QColor(225, 215, 195, 200), QColor(200, 190, 170, 180), QColor(240, 235, 225, 190)]


class Hau(Schritt):
    """Holt aus und schlägt n-mal auf den Weltpunkt ziel(sz) (Hand landet dort).
    holen: Ausholwinkel relativ zum Zielwinkel (negativ = weiter nach oben),
    treffer(sz, k) beim Aufprall, beide=True: mit beiden Fäusten."""

    def __init__(self, ziel, n=1, takt=0.6, holen=-80, treffer=None, beide=False, nach=0.25, sorge=0.0):
        self.ziel, self.n, self.takt, self.holen = ziel, n, takt, holen
        self.treffer, self.beide, self.nach, self.sorge = treffer, beide, nach, sorge
        self.dauer = n * takt + nach

    def beginn(self, sz):
        self.k = 0

    def weiter(self, sz, u, dt):
        zx, zy = self.ziel(sz)
        a_t = sz.arm_zu(zx, zy)
        k = min(self.n - 1, int(u / self.takt))
        f = min(1.0, (u - k * self.takt) / self.takt)
        a_w = a_t + self.holen
        if f < 0.62:
            a = a_t + (a_w - a_t) * glatt(f / 0.62)
            lehne = -3 * glatt(f / 0.62)
        elif f < 0.78:
            a = a_w + (a_t - a_w) * ((f - 0.62) / 0.16) ** 2
            lehne = 4
        else:
            a = a_t
            lehne = 4
        if f >= 0.78 and self.k <= k:
            self.k = k + 1
            if self.treffer:
                self.treffer(sz, k)
        sz.neigung = lehne
        sz.pose = Pose(arm_v=a, arm_h=a + 8 if self.beide else 25, arm_v_x=14, bein_v=-12, bein_h=12,
                       sorge=self.sorge, blick_y=-0.1, mund_offen=f > 0.62, auge_zu=0.7 < f < 0.85)

    def ende(self, sz):
        sz.neigung = 0.0


class ComputerSzene(ProfSzene):
    """Rollwagen mit Röhrenmonitor am Rand, an dem die Szene beginnt (wx: Mitte des Wagens)."""
    mitnehmen = ()

    def computer_vorbereiten(self, anteil=0.1, monitor=True):
        self.rand = -self.richtung
        self.wx = self.vom_rand(anteil)
        self.monitor = monitor
        self.mon_hopp = self.mon_vy = 0.0
        self.wackel = 0.0
        self.bild, self.flackern, self.stoerung = 1.0, 0.0, 0.0
        self.kringel, self.farbe, self.gesicht, self.sprung = None, 'gruen', 0.0, 0.0
        self.truemmer = []
        self.roll = 0.0
        self._wx_alt = self.wx

    def innen(self, abstand=100):
        """x auf der Innenseite des Wagens (zur Bildmitte hin)."""
        return self.wx - self.rand * abstand * self.s

    def mon_punkt(self, lx, ly):
        """Weltpunkt zu Monitor-Koordinaten (Fuß im Ursprung, ungespiegelt)."""
        return (self.wx + lx * MON * self.s,
                self.boden + (-WAGEN_OBEN + ly * MON) * self.s - self.mon_hopp)

    def stoss(self, hopp=0.0, wackel=1.0):
        self.mon_vy = -hopp * self.s
        self.wackel = max(self.wackel, wackel)

    def weiter(self, dt):
        super().weiter(dt)
        self.roll += (self.wx - self._wx_alt) / (6 * self.s)
        self._wx_alt = self.wx
        if self.mon_hopp > 0 or self.mon_vy:
            self.mon_vy += 1600 * self.s * dt
            self.mon_hopp -= self.mon_vy * dt
            if self.mon_hopp <= 0:
                self.mon_hopp, self.mon_vy = 0.0, 0.0
        self.wackel = max(0.0, self.wackel - dt * 2.5)
        for t in self.truemmer:
            t.schritt(dt, self.boden, self.s)
        self.truemmer = [t for t in self.truemmer if t.y < self.boden + 80 * self.s]

    # -- Zeichnen

    def mon_dreh(self):
        return self.wackel * 5 * math.sin(self.t * 38)

    def schirm_werte(self):
        return dict(bild=self.bild, t=self.t, flackern=self.flackern, stoerung=self.stoerung,
                    kringel=self.kringel, farbe=self.farbe, gesicht=self.gesicht, sprung=self.sprung)

    def zeichne_wagen(self, p):
        p.save()
        p.translate(self.wx, self.boden)
        p.scale(self.s, self.s)
        zeichne_rollwagen(p, 0, 0, self.roll)
        p.restore()

    def zeichne_monitor(self, p, gehaeuse=True):
        x, y = self.mon_punkt(0, 0)
        zeichne_roehre(p, x, y, self.s * MON, self.mon_dreh(), gehaeuse, **self.schirm_werte())

    def zeichne_truemmer(self, p):
        for t in self.truemmer:
            t.zeichne(p, self.s)

    def zeichne_requisiten(self, p):
        self.zeichne_wagen(p)
        if self.monitor:
            self.zeichne_monitor(p)
        self.zeichne_truemmer(p)

    def wagen_kasten(self):
        s = self.s
        oben = WAGEN_OBEN + (82 * MON if self.monitor else 0)
        return QRectF(self.wx - (WAGEN_B / 2 + 4) * s, self.boden - oben * s - self.mon_hopp,
                      (WAGEN_B + 8) * s, oben * s + self.mon_hopp + 2 * s)

    def requisiten_kasten(self):
        k = self.wagen_kasten()
        for t in self.truemmer:
            k = k.united(t.kasten(self.s))
        return k

    def schieb_abgang(self):
        """Schiebt den Wagen zum Rand hinaus, an dem die Szene begann."""
        return [Setze(richtung=self.rand, mitnehmen=('wx',)),
                Gehe(bis=lambda sz: sz.aussen(sz.rand) + sz.rand * 330 * sz.s, haltung=schieben)]


def wuetend(dauer=0.5):
    return Stehe(dauer, lambda sz, u: Pose(arm_v=-40 - 30 * min(1, u * 3), arm_h=40, sorge=0.0, blick_y=-0.2,
                                           bein_v=-6, bein_h=6, wipp=2 * math.sin(u * 30)))


class Klopfen(ComputerSzene):
    """Der Röhrenmonitor flackert, Klopfen hilft, Triumph-Pose; dann ein Sicherheits-
    klopfer: das Gehäuse kippt vom Wagen, der nackte Bildschirm steht allein und leuchtet."""
    name, titel, reihenfolge = 'klopfen', 'Sicherheitsklopfer', 82

    def vorbereiten(self):
        self.computer_vorbereiten(0.1)
        self.flackern, self.stoerung = 1.0, 1.0
        self.g_phase, self.g_t, self.g_dreh, self.g_dy, self.g_v = None, 0.0, 0.0, 0.0, 0.0
        self.versteckt = False

    # -- Gehäuse

    def gehaeuse_fallen(self, sz=None):
        self.g_phase, self.g_t = 'wackel', 0.0

    def weiter(self, dt):
        super().weiter(dt)
        if self.g_phase == 'wackel':
            self.g_t += dt
            self.g_dreh = 3 * math.sin(self.g_t * 34)
            if self.g_t > 0.5:
                self.g_phase, self.g_t = 'kipp', 0.0
        elif self.g_phase == 'kipp':
            self.g_t += dt
            self.g_dreh = 90 * min(1.0, (self.g_t / 0.42) ** 2)
            if self.g_t >= 0.42:
                self.g_phase, self.g_v = 'fall', 0.0
        elif self.g_phase == 'fall':
            tief = (WAGEN_OBEN + 16 * MON) * self.s
            self.g_v += 1600 * self.s * dt
            self.g_dy += self.g_v * dt
            if self.g_dy >= tief:
                self.g_dy = tief
                if self.g_v > 250 * self.s:
                    erst = self.g_v > 600 * self.s
                    self.g_v *= -0.25
                    if erst and not self.erschreckt:
                        x = self.wx + self.rand * (34 + 31) * MON * self.s
                        self.streue(x, self.boden - 6 * self.s, 18, STAUB, tempo=150, dauer=0.8, r=(6, 14))
                        self.streue(x, self.boden - 20 * self.s, 6, [BEIGE, BEIGE_DUNKEL], tempo=200, dauer=0.7,
                                    r=(2, 4), schwer=True, richtung=-math.pi / 2, streuung=1.2)
                        self.stoss(6, 0.6)
                else:
                    self.g_phase = 'liegt'

    def zeichne_gehaeuse_los(self, p):
        x, y = self.mon_punkt(0, 0)
        p.save()
        p.translate(x, y + self.g_dy)
        p.scale(self.s * MON, self.s * MON)
        px, py = self.rand * 34, -16
        p.translate(px, py)
        p.rotate(self.rand * self.g_dreh)
        p.translate(-px, -py)
        zeichne_gehaeuse(p, an=False, leer=self.g_phase != 'wackel')
        p.restore()

    def zeichne_alles(self, p):
        self.zeichne_wagen(p)
        if self.g_phase is None:
            self.zeichne_monitor(p)
        elif self.g_phase == 'wackel':
            self.zeichne_monitor(p, gehaeuse=False)
            self.zeichne_gehaeuse_los(p)
        else:
            self.zeichne_gehaeuse_los(p)
            self.zeichne_monitor(p, gehaeuse=False)

    def zeichne_requisiten(self, p):
        if not self.versteckt:
            self.zeichne_alles(p)

    def zeichne_davor(self, p):
        if self.versteckt:
            self.zeichne_alles(p)

    def requisiten_kasten(self):
        k = self.wagen_kasten()
        if self.g_phase:
            s = self.s * MON
            x, y = self.mon_punkt(0, 0)
            x0 = x + self.rand * 34 * s
            k = k.united(QRectF(min(x0, x0 + self.rand * 66 * s), y - 82 * s,
                                66 * s, 82 * s + self.g_dy + 20 * self.s).adjusted(0, 0, 0, 0))
            k = k.united(QRectF(x - 40 * s, y - 82 * s, 80 * s, 82 * s))
        return k

    # -- Schläge

    def mon_seite(self, sz):
        return sz.mon_punkt(-sz.rand * 37, -54)

    def mon_oben(self, sz):
        return sz.mon_punkt(-sz.rand * 14, -80)

    def klopf_klein(self, sz, k):
        sz.stoss(0, 0.5)
        x, y = self.mon_seite(sz)
        sz.streue(x, y, 2, STAUB, tempo=40, dauer=0.4, r=(3, 6))

    def klopf_gross(self, sz, k):
        sz.stoss(16, 1.0)
        sz.flackern = sz.stoerung = 0.0
        sz.gesicht = 1.0
        x, y = self.mon_oben(sz)
        sz.streue(x, y, 7, FUNKEN, tempo=200, dauer=0.55, r=(3, 6), art='stern')
        sz.streue(x, y, 6, STAUB, tempo=90, dauer=0.6, r=(4, 9))

    def sicherheit(self, sz, k):
        sz.stoss(2, 0.3)
        self.gehaeuse_fallen()

    # -- Ablauf

    def ablauf(self):
        self.x = self.aussen(self.rand)
        r = self.rand
        return [
            Gehe(bis=self.innen(102)),
            Setze(richtung=r),
            Stehe(0.9, lambda sz, u: Pose(sorge=0.6, blick_y=-0.3, auge_zu=blinzeln(sz.t))),
            Hau(self.mon_seite, n=3, takt=0.38, holen=40, treffer=self.klopf_klein, nach=0.3, sorge=0.5),
            Stehe(0.5, lambda sz, u: Pose(sorge=0.7, blick_y=-0.3)),
            Stehe(0.9, denk_pose),
            HaareHoch(0.35),
            wuetend(0.45),
            Hau(self.mon_oben, n=1, takt=0.75, holen=-95, treffer=self.klopf_gross, nach=0.35),
            Setze(haare=0.0),
            Stehe(0.6, lambda sz, u: Pose(blick_y=-0.3, auge_zu=blinzeln(sz.t), mund_offen=u > 0.3)),
            Stehe(1.5, triumph_pose),
            Stehe(0.45, lambda sz, u: Pose(blick_y=-0.3, arm_v=-40, auge_zu=u > 0.2)),
            Hau(self.mon_oben, n=1, takt=0.5, holen=-25, treffer=self.sicherheit, nach=0.1),
            Stehe(1.5, lambda sz, u: Pose(arm_v=-60 + 30 * min(1, u * 2), arm_h=20, blick_y=-0.2,
                                          sorge=min(1.0, u * 1.5), mund_offen=u > 0.6, schreck=0.0)),
            Stehe(0.8, lambda sz, u: Pose(blick_y=-0.4, sorge=0.5, auge_zu=0.3 < u < 0.42)),
            Schaue(1.3),
            Stehe(1.4, triumph_pose),
            *self.schieb_abgang(),
        ]

    def schreck_ablauf(self):
        self.nebenbei.clear()
        self.halt = self.halt_h = None
        sichtbar = self.zeige_figur and self.figur_sichtbar()
        nah = sichtbar and abs(self.x - self.wx) < 300 * self.s and self.wagen_kasten().intersects(self.geo)
        if not nah:
            return self.schreck_versinken()
        tief = 340 * self.s
        hinter = self.wx + self.rand * 8 * self.s
        return [HaareHoch(1.0), Erschrecke(0.3, 46),
                Setze(versteckt=True),
                Gleite(hinter, 0.22, Pose(kopf_vorn=True, schreck=1.0, arm_v=-20, arm_h=20, bein_v=-30, bein_h=30)),
                Wandel(0.12, stauchen=0.72),
                Stehe(0.25, Pose(kopf_vorn=True, schreck=0.6, sorge=1.0, arm_v=-10, arm_h=10)),
                Wandel(0.45, y=lambda sz: sz.y + tief, senke=tief),
                Tu(lambda sz: setattr(sz, 'zeige_figur', False))] + self._ende()
