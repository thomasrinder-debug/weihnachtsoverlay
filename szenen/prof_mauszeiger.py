import math
from dataclasses import replace

from PyQt6.QtCore import QPointF, QRectF
from PyQt6.QtGui import QColor, QPainterPath

from zeichnen.figur import Pose
from zeichnen.figuren import Katze
from zeichnen.grundlagen import KEIN_PINSEL, blinzeln, glatt, stift
from zeichnen.labor import zeichne_monitor
from zeichnen.labor_e import zeichne_mauszeiger

from .basis import Gehe, Jeweils, Mit, Nebenbei, Setze, Springe, Stehe, Tu, WarteNebenbei
from .geraet import GeraetSzene, Solange
from .professor import Publikumsblick

G = 1.9
KATZE = 0.8
GROSS = 4.2            # Zeiger draußen: 21 Einheiten · 4,2 ≈ 0,35 H


class Mauszeiger(GeraetSzene):
    """Die Katze verfolgt gebannt den Mauszeiger auf dem Monitor. Der Professor tippt dagegen,
    der Zeiger springt heraus und wächst zu einem Riesenpfeil, der auf ihn zeigt. Die Katze
    macht einen Buckel, duckt sich, der Zeiger flitzt zurück in den Schirm, die Katze springt
    hinterher und steckt mit dem Vorderteil im Bildschirm, die Hinterbeine strampeln. Er zieht
    sie heraus, plumpst hin, und sie trägt den Riesenzeiger quer im Maul davon. Der Monitor
    hüpft beleidigt hinterher."""
    name, titel, reihenfolge = 'mauszeiger', 'Mäusejagd', 89

    def vorbereiten(self):
        r = self.seite = self.richtung
        s = self.s
        self.mon_x = self.vom_rand(0.09)
        self.mon_hopp = 0.0
        self.mon_dreh = 0.0
        self.zeiger = 'schirm'           # schirm, frei, maul, weg
        self.zx, self.zy = 0.0, -50.0    # schirm: Monitor-Einheiten; frei: Weltpunkt der Spitze
        self.zg = 0.6
        self.zw = 0.0
        self.beine = 0.0
        self.steckt = False
        self.zug = 0.0
        k = self.k = self.dazu('katze', Katze, groesse=KATZE, vorn=True, sitzt=True, buckel=0.0)
        k.x = self.mon_x + r * 98 * s
        k.richtung = -r
        k.tempo = self.tempo * 1.2

    # -- Orte

    def am_monitor(self, lx, ly):
        return (self.mon_x + self.seite * 0 + lx * G * self.s + self.zitter(),
                self.boden - self.mon_hopp + ly * G * self.s)

    def schirm_welt(self):
        x0, y0 = self.am_monitor(-27, -72)
        x1, y1 = self.am_monitor(27, -28)
        return QRectF(x0, y0, x1 - x0, y1 - y0)

    def katze_steckt_ort(self):
        q = self.schirm_welt()
        k = self.k
        kopf_x = q.center().x() + self.seite * 8 * self.s + self.seite * self.zug * 10 * self.s
        return kopf_x + self.seite * 44 * k.s, q.center().y() + 62 * k.s

    def katze_hinten(self):
        q = self.k.trafo().map(QPointF(-38, -52))
        return q.x(), q.y()

    def maul(self):
        q = self.k.trafo().map(QPointF(50, -72))
        return q.x(), q.y()

    def weiter(self, dt):
        super().weiter(dt)
        if self.erschreckt:
            return
        k = self.k
        if self.steckt:
            k.x, k.y = self.katze_steckt_ort()
            w = math.sin(self.t * 19)
            k.pose = Pose(bein_v=55 * w, bein_h=-55 * w)
        if self.zeiger == 'maul':
            self.zx, self.zy = self.maul()

    # -- Zeichnen

    def zeichne_requisiten(self, p):
        s = self.s
        x, y = self.am_monitor(0, 0)
        p.save()
        p.translate(x, y)
        p.scale(G * s, G * s)
        zeichne_monitor(p, 0, 0, 1.0, self.t, 0.0, dreh=self.mon_dreh * self.seite)
        p.restore()
        if self.zeiger == 'schirm':
            zx, zy = self.am_monitor(self.zx, self.zy)
            zeichne_mauszeiger(p, zx, zy, self.zg * G * s)

    def zeichne_davor(self, p):
        s = self.s
        if self.steckt:
            q = self.schirm_welt()
            aussen = QPainterPath()
            aussen.addRect(q.adjusted(-400 * s, -400 * s, 400 * s, 400 * s))
            innen = QPainterPath()
            innen.addRoundedRect(q, 8 * G * s, 8 * G * s)
            k = self.k
            k.zeige_figur = True
            p.save()
            p.setClipPath(aussen.subtracted(innen))
            k.zeichne(p)
            p.restore()
            p.save()                      # Kopf und Zeiger schimmern grünlich hinter dem Glas
            p.setClipPath(innen)
            p.setOpacity(0.5)
            k.zeichne(p)
            zx, zy = self.am_monitor(-14 * self.seite + 5 * math.sin(self.t * 13), -62)
            zeichne_mauszeiger(p, zx, zy, 2.2 * G * s, 20 * math.sin(self.t * 9))
            p.setOpacity(1.0)
            p.setBrush(QColor(90, 230, 150, 90))
            p.drawRect(q)
            p.restore()
            k.zeige_figur = False
            p.setPen(stift(QColor(220, 255, 235, 170), 1.5 * s))
            p.setBrush(KEIN_PINSEL)
            rx = q.right() if self.seite > 0 else q.left()
            w = 1 + 0.1 * math.sin(self.t * 9)
            p.drawEllipse(QRectF(rx - 7 * s * w, q.center().y() - 26 * s * w, 14 * s * w, 52 * s * w))
            p.setPen(QColor(0, 0, 0, 0))
        if self.zeiger in ('frei', 'maul'):
            zeichne_mauszeiger(p, *self.zeiger_spitze(), self.zg * s, self.zw, self.beine, self.t * 14)

    def zeiger_spitze(self):
        """Weltpunkt der Pfeilspitze; im Maul liegt die Pfeilmitte zwischen den Zähnen."""
        if self.zeiger != 'maul':
            return self.zx, self.zy
        w = math.radians(self.zw)
        g = self.zg * self.s
        mx, my = 6 * g, 11 * g
        return (self.zx - (mx * math.cos(w) - my * math.sin(w)),
                self.zy - (mx * math.sin(w) + my * math.cos(w)))

    def requisiten_kasten(self):
        s = self.s
        x, y = self.am_monitor(0, 0)
        k = QRectF(x - 52 * G * s, y - 92 * G * s, 104 * G * s, 92 * G * s + self.mon_hopp)
        if self.zeiger in ('frei', 'maul'):
            zx, zy = self.zeiger_spitze()
            g = self.zg * s
            k = k.united(QRectF(zx - 30 * g, zy - 30 * g, 60 * g, 60 * g))
        if self.steckt:
            k = k.united(self.k.kasten().adjusted(-10 * s, -10 * s, 10 * s, 10 * s))
        return k

    # -- Ablauf

    def ablauf(self):
        r, s = self.richtung, self.s
        self.x = self.aussen(-r)
        k = self.k
        stand = self.mon_x + r * 168 * s
        boden_ziel = (self.mon_x + r * 66 * s, self.boden - 2 * s)

        def gucken(sz, u):
            sz.zx = 14 * math.sin(sz.t * 3.1)
            sz.zy = -50 + 8 * math.sin(sz.t * 4.3)
            k.pose = Pose(blick_x=0.7 * math.sin(sz.t * 3.1) * -r, blick_y=-0.6, auge_zu=blinzeln(sz.t, 1.3))

        def tippen(sz, u):
            gucken(sz, u)
            sz.neigung = 26 * glatt(min(1.0, u / 0.2))
            stoss = (u * 3.3) % 1 < 0.35 and u > 0.2
            ziel = sz.am_monitor(0, -50)
            ziel = (ziel[0] + r * (10 if stoss else 22) * s, ziel[1])
            sz.pose = Pose(arm_v=sz.arm_zu(*ziel), arm_v_x=14, blick_y=0.2, auge_zu=blinzeln(sz.t))
            if stoss:
                sz.wackel = max(sz.wackel, 0.4)

        start = {}

        def heraus(sz, u):
            f = min(1.0, u / 0.35)
            if 'p' not in start:
                start['p'] = sz.am_monitor(sz.zx, sz.zy)
                sz.zeiger = 'frei'
                sz.neigung = 0
            x0, y0 = start['p']
            x1, y1 = boden_ziel
            sz.zx = x0 + (x1 - x0) * f
            sz.zy = y0 + (y1 - y0) * f - 70 * s * math.sin(f * math.pi) - 21 * sz.zg * s * f
            sz.zg = 0.6 * G + (1.4 - 0.6 * G) * f
            sz.zw = -r * 360 * f
            sz.pose = Pose(arm_v=-60, schreck=0.8 * f, blick_y=0.4)
            k.pose = Pose(blick_x=0.5 * r, blick_y=0.3 * f, schreck=0.5 * f)

        def wachsen(sz, u):
            stufe = min(2, int(u / 0.22))
            v = (u - stufe * 0.22) / 0.22
            g0 = (1.4, 2.4, 3.3)[stufe]
            g1 = (2.4, 3.3, GROSS)[stufe]
            sz.zg = g0 + (g1 - g0) * min(1.0, v * 2.5) * (1 + 0.25 * math.sin(min(1.0, v * 2.5) * math.pi))
            sz.zw = 0.0
            sz.zx, sz.zy = boden_ziel[0], sz.boden - 21 * sz.zg * s
            sz.pose = Pose(arm_v=-150, arm_h=-130, arm_v_x=16, schreck=1.0, sorge=1.0)
            sz.x = stand + r * 36 * s * glatt(min(1.0, u / 0.66))
            k.sitzt = False
            k.buckel = min(1.0, u * 3)
            k.striche = u > 0.3
            k.pose = Pose(schreck=1.0, kopf_vorn=True)

        def zeigen(sz, u):
            # der Riesenpfeil kippt und zeigt auf den Professor
            f = glatt(min(1.0, u / 0.3))
            sz.zw = -r * 62 * f
            sz.beine = 1.0
            sz.zx = boden_ziel[0] + r * 30 * s * f
            sz.zy = sz.boden - 60 * s - 20 * s * f
            sz.hopp = 18 * s * math.sin(min(1.0, u / 0.25) * math.pi)
            sz.pose = Pose(arm_v=-170, arm_h=-160, arm_v_x=16, schreck=1.0, sorge=1.0, kopf_vorn=True,
                           bein_v=-20, bein_h=10)
            sz.haare = 0.6

        def lauern(sz, u):
            k.buckel = 0.0
            k.striche = False
            k.stauchen = 0.82
            k.hopp = -4 * s
            k.neigung = -6 * math.sin(u * 30)
            k.pose = Pose(bein_v=-20, bein_h=24, blick_y=0.2)
            sz.pose = Pose(arm_v=-150, arm_h=-140, arm_v_x=16, sorge=1.0, kopf_vorn=False, blick_y=0.4)
            sz.zx = boden_ziel[0] + r * 30 * s + 4 * s * math.sin(u * 40)

        def zurueck(sz, u):
            f = min(1.0, u / 0.25)
            if 'q' not in start:
                start['q'] = (sz.zx, sz.zy, sz.zg)
                k.stauchen, k.hopp, k.neigung = 1.0, 0.0, 0.0
            x0, y0, g0 = start['q']
            x1, y1 = sz.am_monitor(-6 * r, -60)
            sz.zx = x0 + (x1 - x0) * f
            sz.zy = y0 + (y1 - y0) * f - 40 * s * math.sin(f * math.pi)
            sz.zg = g0 + (2.2 * G - g0) * f
            sz.zw = -r * 62 * (1 - f)
            if f >= 1:
                sz.zeiger = 'weg'

        def steckt(sz):
            sz.steckt = True
            k.zeige_figur = False
            k.neigung = -14
            sz.wackel = 1.0
            sz.streue(*sz.am_monitor(0, -50), 10, [QColor(150, 255, 190), QColor(230, 255, 240)], tempo=150,
                      dauer=0.5, r=(3, 6), art='stern')

        def hin(sz, u):
            hx, hy = sz.katze_hinten()
            sz.pose = Pose(arm_v=sz.arm_zu(hx, hy), arm_h=sz.arm_zu(hx, hy, False), arm_v_x=14, sorge=0.6,
                           blick_y=0.4, auge_zu=blinzeln(sz.t))

        def ziehen(staerke, dauer):
            def f(sz, u):
                v = min(1.0, u / dauer)
                ruck = math.sin(v * math.pi)
                sz.zug = ruck * (0.3 + 0.7 * staerke)
                sz.mon_dreh = 9 * ruck * staerke
                sz.neigung = -(8 + 16 * staerke) * ruck
                hx, hy = sz.katze_hinten()
                sz.pose = Pose(arm_v=sz.arm_zu(hx, hy), arm_h=sz.arm_zu(hx, hy, False), arm_v_x=14,
                               bein_v=-30 * ruck, bein_h=22 * ruck, sorge=1.0, mund_offen=ruck > 0.5,
                               auge_zu=ruck > 0.6)
                nx, _ = sz.hand(True)
                sz.x += hx - nx
            return f

        def plopp(sz):
            sz.steckt = False
            sz.zug, sz.mon_dreh = 0.0, 0.0
            k.zeige_figur, k.neigung = True, 0.0
            k.pose = Pose()
            sz.zeiger, sz.zg, sz.zw, sz.beine = 'maul', GROSS, 90 * r, 0.0
            sz.zx, sz.zy = sz.maul()
            sz.wackel = 1.0
            sz.streue(sz.schirm_welt().center().x() + r * 30 * s, sz.schirm_welt().center().y(), 12,
                      [QColor(150, 255, 190), QColor(230, 255, 240)], tempo=200, dauer=0.5, r=(3, 6), art='stern')

        def plumps(sz, u):
            f = min(1.0, u / 0.35)
            if 'x' not in start:
                start['x'] = sz.x
            sz.x = start['x'] + r * 40 * s * (1 - (1 - f) ** 2)
            sz.neigung = -30 * math.sin(f * math.pi) - 8 * f
            sz.hopp = 30 * s * math.sin(f * math.pi) - 52 * s * f ** 3
            sz.pose = Pose(arm_v=-140, arm_h=-120, arm_v_x=14, kopf_vorn=True, schreck=1.0, mund_offen=True,
                           bein_v=-115 * f, bein_h=-95 * f)

        def sitzen(sz, u):
            return Pose(arm_v=-60, arm_h=-40, bein_v=-115 + 12 * math.sin(u * 9), bein_h=-95, kopf_vorn=u > 0.45, auge_zu=0.6 < u < 0.75,
                        sorge=0.4, blick_x=-0.6 * r if u < 0.45 else 0.0)

        def aufstehen(sz, u):
            f = glatt(min(1.0, u / 0.3))
            sz.hopp = -52 * s * (1 - f)
            sz.neigung = -8 * (1 - f)
            sz.pose = Pose(bein_v=-115 * (1 - f), bein_h=-95 * (1 - f), arm_v=-60, sorge=0.5)

        def monitor_huepft(sz, u):
            phase = (u * 2.6) % 1
            sz.mon_hopp = 26 * s * math.sin(phase * math.pi)
            sz.mon_x -= r * sz.tempo * 1.25 * min(1.0, u / 0.3) / 60
            sz.mon_dreh = -6 * math.sin(phase * math.pi)

        def verblueffte_haltung(pose, sz):
            return replace(pose, arm_v=-100, arm_v_x=16, sorge=0.7)

        return [
            Nebenbei(Solange(gucken, lambda sz: sz.zeiger != 'schirm')),
            Gehe(bis=stand, tempo=2.2),
            Setze(richtung=-r),
            Jeweils(0.7, tippen),
            Jeweils(0.35, heraus),
            Jeweils(0.66, wachsen),
            Jeweils(0.4, zeigen),
            Setze(hopp=0.0),
            Jeweils(0.35, lauern),
            Jeweils(0.25, zurueck),
            Mit('katze', Springe(nach=lambda d: d.sz.katze_steckt_ort(), dauer=0.3, hoehe=40)),
            Tu(steckt),
            Publikumsblick(0.8, husten=False),
            Setze(haare=0.3),
            Gehe(bis=lambda sz: sz.katze_hinten()[0] + r * 62 * s, tempo=1.0),
            Setze(richtung=-r),
            Jeweils(0.15, hin),
            Jeweils(0.45, ziehen(0.2, 0.45)),
            Jeweils(0.4, ziehen(0.6, 0.4)),
            Jeweils(0.3, ziehen(1.0, 0.6)),
            Tu(plopp),
            Nebenbei(Mit('katze', Springe(nach=lambda d: (d.x + r * 60 * s, d.sz.boden), dauer=0.4, hoehe=50)),
                     Mit('katze', Stehe(0.35, lambda d, u: Pose(kopf_vorn=True, blick_x=0.0))),
                     Mit('katze', Gehe(tempo=1.3))),
            Jeweils(0.4, plumps),
            Stehe(0.8, sitzen),
            Nebenbei(Solange(monitor_huepft, lambda sz: (sz.mon_x - sz.aussen(-r)) * -r > 0)),
            Jeweils(0.3, aufstehen),
            Setze(hopp=0.0, neigung=0.0),
            Gehe(tempo=1.5, haltung=verblueffte_haltung),
            WarteNebenbei(),
        ]

    def schreck_ablauf(self):
        k = self.k
        if self.steckt:
            self.steckt = False
            k.x += self.seite * 30 * self.s
        k.zeige_figur = k.figur_sichtbar()
        k.sitzt, k.buckel, k.striche, k.stauchen, k.hopp, k.neigung = False, 0.0, False, 1.0, 0.0, 0.0
        k.y = self.boden
        self.zeiger = 'weg'
        self.neigung, self.hopp = 0.0, 0.0
        return self.schreck_rennen()
