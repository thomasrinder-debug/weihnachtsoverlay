import math
import random

from PyQt6.QtCore import QPointF, QRectF
from PyQt6.QtGui import QColor

from zeichnen.figur import Pose
from zeichnen.grundlagen import KEIN_STIFT, WEISS, blinzeln
from zeichnen.labor_a import (DUESE, kurbel_griff, zeichne_schneeball_po, zeichne_schneehuelle,
                              zeichne_schneemaschine)
from zeichnen.professor import SCHULTER_Y, _arm

from .basis import Erschrecke, Gehe, Jeweils, Schritt, Setze, Stehe, Tu, Wandel
from .professor import HaareHoch, ProfSzene, ziehen

SCHNEE = [WEISS, QColor('#E8F4FF'), QColor(255, 255, 255, 200)]
VOLL = 258.0


class Rollen(Schritt):
    """Liegt auf dem Rücken und rollt samt Maschine zum nächsten Rand."""

    def beginn(self, sz):
        sz.richtung = sz.naechster_rand()
        self.v = sz.tempo * 4.2

    def weiter(self, sz, u, dt):
        dx = sz.richtung * self.v * min(1.0, u / 0.15 + 0.3) * dt
        sz.x += dx
        sz.masch_x += dx
        sz.masch_dreh -= sz.richtung * 900 * dt
        sz.ball_dreh += 700 * dt
        sz.pose = Pose(arm_v=-170, arm_h=-160, bein_v=-30, bein_h=-10, schreck=1.0, kopf_vorn=True)

    def fertig(self, sz, u):
        m = QRectF(sz.masch_x - 60 * sz.s, sz.boden - 170 * sz.s, 120 * sz.s, 170 * sz.s)
        return u > 0.1 and not sz.figur_sichtbar() and not m.intersects(sz.geo)


class Eingeschneit(ProfSzene):
    """Er kurbelt an der Schneemaschine und schneit sich dabei selbst zum Schneemann ein.
    Ein Arm bricht heraus und kurbelt rückwärts, der Schnee fliegt zurück in die Düse,
    bis auf eine Schneekugel um seinen Hintern."""
    name, titel, reihenfolge = 'eingeschneit', 'Eingeschneit', 64

    def vorbereiten(self):
        r, s = self.richtung, self.s
        self.masch_x = self.vom_rand(0.2) + r * 40 * s
        self.px = self.masch_x - r * 80 * s
        self.kurbel = 90.0
        self.laeuft, self.rueck = 0.0, False
        self.masch_dreh = 0.0
        self.schnee_h, self.schnee_ab = 0.0, 0.0
        self.huelle_arm = True
        self.gesicht = 0.0
        self.arm_frei = False
        self.po_ball, self.ball_dreh = 0.0, 0.0
        self.rollt = False

    # -- Lagen

    def welt_masch(self, lx, ly):
        return self.masch_x + self.richtung * lx * self.s, self.boden + ly * self.s

    def griff(self):
        return self.welt_masch(*kurbel_griff(self.kurbel))

    # -- Zeichnen

    def zeichne_requisiten(self, p):
        s = self.s
        p.save()
        p.translate(self.masch_x, self.boden)
        p.scale(s * self.richtung, s)
        if self.masch_dreh:
            p.translate(0, -55)
            p.rotate(self.masch_dreh)
            p.translate(0, 55)
        zeichne_schneemaschine(p, self.kurbel, self.laeuft, self.t, self.rueck)
        p.restore()

    def zeichne_davor(self, p):
        if not self.zeige_figur:
            return
        p.save()
        p.translate(0, -self.senke)
        p.setTransform(self.trafo(), True)
        p.setPen(KEIN_STIFT)
        if self.schnee_h > 0:
            zeichne_schneehuelle(p, self.schnee_h, self.schnee_ab, self.huelle_arm, self.gesicht, self.t)
        if self.po_ball > 0:
            zeichne_schneeball_po(p, self.po_ball, self.t, self.ball_dreh)
        if self.arm_frei:
            pose = self.pose
            _arm(p, pose.arm_v_x, SCHULTER_Y + pose.hub, pose.arm_v, False)
        p.restore()

    def requisiten_kasten(self):
        s = self.s
        k = QRectF(self.masch_x - 60 * s, self.boden - 175 * s, 120 * s, 175 * s)
        if self.masch_dreh:
            k = k.adjusted(-30 * s, -20 * s, 30 * s, 0)
        if self.zeige_figur and (self.schnee_h > 0 or self.po_ball > 0):
            k = k.united(self.trafo().mapRect(QRectF(-70, -240, 140, 242)).translated(0, -self.senke))
        return k

    # -- Ablauf

    def ablauf(self):
        r, s = self.richtung, self.s
        self.x = self.aussen(-r)
        duese = lambda sz: sz.welt_masch(*DUESE)
        richtung_hin = math.pi - 0.3 if r > 0 else 0.3

        def kurbeln(sz, u):
            dauer = 4.6
            f = min(1.0, u / dauer)
            sz.kurbel += 420 * (1 - 0.3 * f) / 60
            sz.laeuft = 1.0
            sz.schnee_h = VOLL * min(1.0, f * 1.08) ** 0.9
            dx, dy = duese(sz)
            sz.streue(dx, dy, 2, SCHNEE, tempo=260, dauer=0.45, r=(2, 5), richtung=richtung_hin, streuung=0.35)
            if random.random() < 0.5:
                sz.streue(dx, dy, 1, SCHNEE, tempo=200, dauer=0.5, r=(2, 3), art='stern', richtung=richtung_hin,
                          streuung=0.3)
            sz.pose = Pose(arm_v=sz.arm_zu(*sz.griff()), blick_y=0.2 if u < 1.2 else -0.1, mund_offen=u < 1.0,
                           sorge=min(1.0, max(0.0, (u - 1.5) / 1.5)), auge_zu=u > 1.6 or blinzeln(sz.t))

        def ausbrechen(sz):
            sz.huelle_arm, sz.arm_frei, sz.rueck = False, True, True
            q = sz.trafo().map(QPointF(34, -118))
            sz.streue(q.x(), q.y(), 14, SCHNEE, tempo=200, dauer=0.7, r=(3, 7), schwer=True)
            sz.streue(q.x(), q.y(), 6, SCHNEE, tempo=80, dauer=0.5, r=(5, 9))

        def zurueck(sz, u):
            dauer = 2.4
            f = min(1.0, u / dauer)
            sz.kurbel -= 720 / 60
            sz.laeuft = 1.0
            sz.schnee_ab = VOLL - (VOLL - 112) * f
            sz.gesicht = max(0.0, 1 - f * 4)
            if random.random() < 0.8:
                q = sz.trafo().map(QPointF(random.uniform(-30, 40), -sz.schnee_ab + 6))
                dx, dy = duese(sz)
                w = math.atan2(dy - q.y(), dx - q.x())
                d = math.hypot(dx - q.x(), dy - q.y())
                sz.streue(q.x(), q.y(), 1, SCHNEE, tempo=d / s / 0.35, dauer=0.35, r=(2, 5), richtung=w,
                          streuung=0.08)
            sz.pose = Pose(arm_v=sz.arm_zu(*sz.griff()), auge_zu=sz.schnee_ab > 160 or blinzeln(sz.t),
                           sorge=0.5, mund_offen=sz.schnee_ab < 150)

        def kugel(sz):
            sz.schnee_h, sz.schnee_ab, sz.po_ball = 0.0, 0.0, 1.0
            sz.laeuft, sz.rueck, sz.arm_frei = 0.0, False, False
            q = sz.trafo().map(QPointF(-6, -90))
            sz.streue(q.x(), q.y(), 8, SCHNEE, tempo=70, dauer=0.5, r=(4, 8))

        return [
            Gehe(bis=self.px),
            Setze(richtung=r),
            Stehe(0.6, lambda sz, u: Pose(blick_y=-0.2, auge_zu=blinzeln(sz.t))),
            Stehe(0.4, lambda sz, u: Pose(arm_v=sz.arm_zu(*sz.griff()) * min(1, u / 0.3), blick_y=0.2)),
            Jeweils(4.6, kurbeln),
            Setze(laeuft=0.0, schnee_h=VOLL),
            Wandel(0.5, gesicht=1.0),
            Stehe(1.3, lambda sz, u: Pose(arm_v=sz.arm_zu(*sz.griff()), auge_zu=True)),
            Tu(ausbrechen),
            Stehe(0.4, lambda sz, u: Pose(arm_v=-170 + 40 * math.sin(u * 20), arm_v_x=12, auge_zu=True)),
            Stehe(0.3, lambda sz, u: Pose(arm_v=sz.arm_zu(*sz.griff()), auge_zu=True)),
            Jeweils(2.4, zurueck),
            Tu(kugel),
            Stehe(0.6, lambda sz, u: Pose(blick_y=0.2, auge_zu=0.2 < u < 0.32)),
            Stehe(1.2, lambda sz, u: Pose(blick_y=0.9, blick_x=-0.6, sorge=1.0, arm_h=40, arm_v=-10,
                                          auge_zu=0.7 < u < 0.82)),
            Stehe(1.2, lambda sz, u: Pose(kopf_vorn=True, sorge=0.7, mund_offen=False, arm_v=-20, arm_h=20,
                                          auge_zu=(u % 0.5) < 0.1, hub=-2 * abs(math.sin(u * 5)))),
            Setze(mitnehmen=('masch_x',)),
            Gehe(bis=self.aussen(-r) - r * 260 * s, tempo=0.75,
                 haltung=lambda p, sz: ziehen(p, sz)),
        ]

    def schreck_ablauf(self):
        self.nebenbei.clear()
        self.mitnehmen = ()
        self.laeuft = 0.0
        if not self.figur_sichtbar():
            self.zeige_figur = False
            self.weg(SCHNEE)
            return self._ende()
        if self.schnee_h > 0:
            k = self.trafo().mapRect(QRectF(-50, -min(self.schnee_h, self.schnee_ab or VOLL), 100, 120))
            for _ in range(16):
                self.streue(random.uniform(k.left(), k.right()), random.uniform(k.top(), k.bottom()), 1, SCHNEE,
                            tempo=160, dauer=0.6, r=(4, 9))
            self.schnee_h, self.schnee_ab, self.gesicht, self.po_ball = 0.0, 0.0, 0.0, 1.0
        return [HaareHoch(1.0), Erschrecke(0.3, 40),
                Tu(lambda sz: setattr(sz, 'arm_frei', False)),
                Wandel(0.18, neigung=-95.0, hopp=lambda sz: 34 * sz.s),
                Rollen()] + self._ende()
