import math
from dataclasses import replace

from PyQt6.QtCore import QPointF, QRectF
from PyQt6.QtGui import QColor, QPainterPath

from zeichnen.figur import Pose
from zeichnen.grundlagen import HAUT, HAUT_DUNKEL, KEIN_STIFT, blinzeln, glatt, kreis, linear, radial
from zeichnen.labor import zeichne_labortisch
from zeichnen.professor import HANDSCHUH, HANDSCHUH_DUNKEL, SCHULTER_Y

from .basis import Gehe, Jeweils, Setze, Stehe, Tu, WarteBis
from .professor import FUNKEN, STAUB, HaareHoch, ProfSzene

TISCH_H = 64
TISCH_B = 130


def handschuh_haube(p, droop, t, pop=1.0):
    """Riesiger Gummihandschuh über Kopf und Mütze (Figur-Einheiten, Kopfmitte im Ursprung).
    droop: fünf Werte 0..1, wie weit jeder Finger heruntergeklappt ist."""
    p.save()
    p.scale(pop, pop)
    p.setPen(KEIN_STIFT)
    # Handfläche als Haube
    haube = QPainterPath()
    haube.moveTo(-40, 32)
    haube.cubicTo(-48, -10, -46, -60, -30, -70)
    haube.cubicTo(-10, -80, 10, -80, 30, -70)
    haube.cubicTo(46, -60, 48, -10, 40, 32)
    haube.closeSubpath()
    p.setBrush(radial(-10, -40, 80, HANDSCHUH.lighter(125), HANDSCHUH_DUNKEL))
    p.drawPath(haube)
    p.setBrush(QColor(255, 255, 255, 80))
    p.drawEllipse(QPointF(-20, -45), 7, 16)
    # Beule der Mütze und Stulpe
    p.setBrush(QColor(150, 100, 10, 60))
    p.drawEllipse(QPointF(4, -50), 20, 8)
    p.setBrush(linear(0, 22, 0, 38, HANDSCHUH.lighter(110), HANDSCHUH_DUNKEL))
    p.drawRoundedRect(QRectF(-44, 22, 88, 15), 7, 7)
    # Finger, schlaff über die Haube geklappt
    basis = (-30, -15, 0, 15, 30)
    for k, bx in enumerate(basis):
        seite = -1 if k < 2 else 1
        w = seite * (110 + 25 * abs(k - 2)) * glatt(droop[k]) + 3 * math.sin(t * 9 + k) * (1 - droop[k])
        p.save()
        p.translate(bx, -66 + abs(bx) * 0.35)
        p.rotate(w + bx * 0.6)
        lang = 54 - abs(bx) * 0.25
        p.setBrush(linear(-8, 0, 8, 0, HANDSCHUH.lighter(118), HANDSCHUH_DUNKEL))
        p.drawRoundedRect(QRectF(-7.5, -lang, 15, lang + 8), 7.5, 7.5)
        p.setBrush(QColor(255, 255, 255, 70))
        p.drawRoundedRect(QRectF(-4.5, -lang + 4, 3.5, lang * 0.6), 1.7, 1.7)
        p.restore()
    # Daumen seitlich
    p.save()
    p.translate(40, -26)
    p.rotate(55 + 90 * glatt(droop[4]))
    p.setBrush(linear(-8, 0, 8, 0, HANDSCHUH.lighter(118), HANDSCHUH_DUNKEL))
    p.drawRoundedRect(QRectF(-7, -34, 14, 40), 7, 7)
    p.restore()
    p.restore()


class Handschuh(ProfSzene):
    """Der Gummihandschuh klemmt. Erst zieht die andere Hand, dann der Fuß, dann hakt er
    ihn unter den Tisch und stemmt sich mit dem ganzen Körper zurück; der Handschuh dehnt
    sich über eine Figurenhöhe. Er rutscht ab, schnellt zurück und stülpt sich riesig über
    Kopf und Mütze, er kippt um. Wieder oben klappen die fünf Finger einer nach dem anderen
    herunter, und er tastet sich blind hinaus."""
    name, titel, reihenfolge = 'handschuh', 'Gummihandschuh', 77

    def vorbereiten(self):
        r, s = self.richtung, self.s
        self.tisch_x = self.vom_rand(0.24)
        self.haken = (self.tisch_x - r * (TISCH_B / 2 - 2) * s, self.boden - (TISCH_H + 2) * s)
        self.band = None          # Fingerspitzen des gedehnten Handschuhs (Welt) oder None
        self.zittern = 0.0
        self.haube = 0.0          # 0: Handschuh an der Hand, sonst auf dem Kopf (Pop-Größe)
        self.haube_t = None
        self.droop = [0.0] * 5
        self.nackt = False

    # -- Zeichnen

    def zeichne_requisiten(self, p):
        p.save()
        p.translate(self.tisch_x, self.boden)
        p.scale(self.s, self.s)
        zeichne_labortisch(p, TISCH_B, TISCH_H)
        p.restore()

    def kopf_trafo(self):
        tr = self.trafo()
        p = tr.map(QPointF(5, -180 + self.pose.hub))
        return tr, p

    def zeichne_davor(self, p):
        if self.band and self.zeige_figur:
            self.zeichne_band(p)
        if not self.zeige_figur:
            return
        if self.nackt:
            p.save()
            p.setTransform(self.trafo(), True)
            p.translate(self.pose.arm_v_x, SCHULTER_Y + self.pose.hub)
            p.rotate(self.pose.arm_v)
            p.setPen(KEIN_STIFT)
            p.setBrush(radial(-2, 48, 11, HAUT, HAUT_DUNKEL))
            p.drawRoundedRect(QRectF(-6.5, 38, 13, 7), 3, 3)
            kreis(p, 0, 49, 7.5)
            p.drawEllipse(QPointF(6.5, 44), 3, 4.5)
            p.restore()
        if self.haube:
            p.save()
            p.setTransform(self.trafo(), True)
            p.translate(5, -180 + self.pose.hub)
            p.scale(1.12, 1.12)
            handschuh_haube(p, self.droop, self.t, self.haube)
            p.restore()

    def zeichne_band(self, p):
        s = self.s
        hx, hy = self.hand()
        tx, ty = self.band
        dx, dy = tx - hx, ty - hy
        lang = math.hypot(dx, dy) or 1.0
        nx, ny = -dy / lang, dx / lang
        dehn = min(1.0, lang / (150 * s))
        breit0, breit1 = 7 * s, (6 - 3 * dehn) * s
        z = self.zittern * 5 * s * math.sin(self.t * 70)
        mx, my = (hx + tx) / 2 + nx * z, (hy + ty) / 2 + ny * z
        pfad = QPainterPath()
        pfad.moveTo(hx + nx * breit0, hy + ny * breit0)
        pfad.quadTo(mx + nx * breit1 * 0.6, my + ny * breit1 * 0.6, tx + nx * breit1, ty + ny * breit1)
        pfad.lineTo(tx - nx * breit1, ty - ny * breit1)
        pfad.quadTo(mx - nx * breit1 * 0.6, my - ny * breit1 * 0.6, hx - nx * breit0, hy - ny * breit0)
        pfad.closeSubpath()
        p.setPen(KEIN_STIFT)
        p.setBrush(linear(hx + nx * breit0, hy + ny * breit0, hx - nx * breit0, hy - ny * breit0,
                          HANDSCHUH.lighter(120), HANDSCHUH_DUNKEL))
        p.drawPath(pfad)
        # gespreizte Fingerkuppen am Ende
        ux, uy = dx / lang, dy / lang
        p.setBrush(HANDSCHUH)
        for k in range(5):
            q = (k - 2) * 2.6 * s
            kreis(p, tx + nx * q + ux * (3 - abs(k - 2)) * s, ty + ny * q + uy * (3 - abs(k - 2)) * s, 3 * s)
        p.setBrush(QColor(255, 255, 255, 90))
        p.drawEllipse(QPointF(mx + nx * breit1 * 0.3, my + ny * breit1 * 0.3), lang * 0.2, 1.4 * s)

    def requisiten_kasten(self):
        s = self.s
        k = QRectF(self.tisch_x - (TISCH_B / 2 + 4) * s, self.boden - (TISCH_H + 10) * s, (TISCH_B + 8) * s,
                   (TISCH_H + 10) * s)
        if self.band:
            hx, hy = self.hand()
            tx, ty = self.band
            r = 12 * s
            k = k.united(QRectF(min(hx, tx) - r, min(hy, ty) - r, abs(hx - tx) + 2 * r, abs(hy - ty) + 2 * r))
        if self.haube and self.zeige_figur:
            k = k.united(self.trafo().mapRect(QRectF(-95, -320, 200, 190)))
        return k

    # -- Ablauf

    def ablauf(self):
        r, s = self.richtung, self.s
        self.x = self.aussen(-r)
        px = self.tisch_x - r * (TISCH_B / 2 + 70) * s
        weit = self.haken[0] - r * 330 * s

        def fuss_spitze(sz, bein):
            w = math.radians(bein)
            fx, fy = 22 * math.cos(w) - 58 * math.sin(w), 22 * math.sin(w) + 58 * math.cos(w) - 62
            q = sz.trafo().map(QPointF(fx, fy))
            return q.x(), q.y()

        def hand_zieht(sz, u):
            f = glatt(min(1.0, u / 0.6))
            sz.pose = Pose(arm_v=-95 - 25 * f, arm_h=-60 + 35 * f, arm_v_x=12, blick_y=0.2, sorge=0.5 * f,
                           mund_offen=f > 0.6, hub=2 * f)
            sz.band = sz.hand(vorn=False)
            sz.zittern = 0.3 * f

        def pling(sz):
            if sz.band:
                sz.streue(*sz.band, 6, FUNKEN, tempo=160, dauer=0.3, r=(2, 4), art='stern')
            sz.band, sz.zittern = None, 0.0

        def schuetteln(sz, u):
            return Pose(arm_v=-60 + 25 * math.sin(u * 40), arm_h=20, schreck=1.0 if u < 0.15 else 0.0, sorge=0.7,
                        blick_y=0.3, auge_zu=u > 0.15)

        def bein_hoch(sz, u):
            f = glatt(min(1.0, u / 0.25))
            sz.pose = Pose(bein_v=-75 * f, arm_v=-60 + 40 * f, arm_h=30, blick_y=0.6, sorge=0.3)
            if u > 0.18:
                sz.band = fuss_spitze(sz, -75 * f)

        def fuss_zieht(sz, u):
            f = glatt(min(1.0, u / 0.55))
            wackel = 6 * math.sin(u * 13)
            sz.hopp = 10 * s * abs(math.sin(u * 11))
            sz.pose = Pose(bein_v=-75 - 20 * f, bein_h=wackel * 0.5, arm_v=-20 - 140 * f, arm_h=40 + wackel,
                           sorge=0.8 * f, mund_offen=True, blick_y=-0.3, hub=-2 * f, wipp=wackel)
            sz.band = fuss_spitze(sz, -75 - 20 * f)
            sz.zittern = 0.5 * f

        def strauchel(sz, u):
            sz.hopp = 18 * s * math.sin(min(1.0, u / 0.35) * math.pi)
            sz.x -= r * 60 * s / 60
            return Pose(bein_v=-30, bein_h=20, arm_v=-120 + 30 * math.sin(u * 30), arm_h=-110, schreck=0.8,
                        sorge=0.8, mund_offen=True)

        def einhaken(sz, u):
            f = glatt(min(1.0, u / 0.3))
            hx, hy = sz.haken
            sz.pose = Pose(arm_v=sz.arm_zu(hx, hy), arm_h=-20, blick_y=0.7, hub=4 * f)
            if u > 0.2:
                sz.band = sz.haken

        def zurueckstemmen(sz, u, dt):
            f = min(1.0, u / 1.1)
            sz.x = start_x[0] + (weit - start_x[0]) * glatt(f)
            sz.neigung = -30 * glatt(min(1.0, u / 0.5))
            b = 18 * math.sin(u * 14)
            sz.band = sz.haken
            sz.zittern = 0.4 + 0.6 * f
            sz.pose = Pose(arm_v=sz.arm_zu(*sz.haken), arm_h=sz.arm_zu(*sz.haken, vorn=False) + 8,
                           bein_v=-25 + b, bein_h=10 - b, sorge=1.0, mund_offen=f > 0.5, blick_y=0.1,
                           schreck=0.3 * f)

        start_x = [0.0]

        def warten(sz, u):
            sz.zittern = 1.0
            sz.band = sz.haken
            w = 2 * math.sin(u * 50)
            return Pose(arm_v=sz.arm_zu(*sz.haken) + w, arm_h=sz.arm_zu(*sz.haken, vorn=False) + 8 - w,
                        bein_v=-30, bein_h=18, sorge=1.0, auge_zu=True, hub=1.5 * math.sin(u * 40))

        flug = {}

        def schnalzen(sz, u):
            if 'von' not in flug:
                flug['von'] = sz.haken
                sz.streue(*sz.haken, 6, STAUB, tempo=60, dauer=0.4, r=(3, 6))
            f = min(1.0, u / 0.14)
            kx, ky = sz.fig(40, -185)
            vx, vy = flug['von']
            sz.band = (vx + (kx - vx) * f, vy + (ky - vy) * f - 40 * s * math.sin(f * math.pi))
            sz.zittern = 0.0
            return Pose(arm_v=-80, arm_h=-60, schreck=1.0, sorge=1.0, bein_v=-30, bein_h=18)

        def aufsetzen(sz):
            sz.band = None
            sz.haube, sz.haube_t, sz.nackt = 1.5, sz.t, True
            sz.muetze = False
            x, y = sz.fig(5, -200)
            sz.streue(x, y, 10, FUNKEN, tempo=200, dauer=0.4, r=(3, 6), art='stern')

        def umfallen(sz, u):
            f = min(1.0, u / 0.35)
            sz.haube = 1.0 + 0.5 * max(0.0, 1 - u / 0.2) * math.cos(u * 40)
            sz.neigung = -30 - 58 * f * f
            sz.x -= r * 90 * s / 60 * (1 - f)
            return Pose(arm_v=-150, arm_h=-130, arm_v_x=14, bein_v=-40, bein_h=10)

        def liegen_staub(sz):
            sz.haube = 1.0
            x, _ = sz.fig(-120, -40)
            sz.streue(x, sz.boden - 6 * s, 12, STAUB, tempo=120, dauer=0.6, r=(5, 10), richtung=-math.pi / 2,
                      streuung=1.4)

        def strampeln(sz, u):
            b = 25 * math.sin(u * 22)
            return Pose(arm_v=-100 + b, arm_h=-80 - b, bein_v=-40 + b, bein_h=-10 - b)

        def aufrichten(sz, u):
            f = glatt(min(1.0, u / 0.4))
            sz.neigung = -88 * (1 - f)
            return Pose(arm_v=-8, arm_h=8)

        def klappen(sz, u):
            # Finger klappen einer nach dem anderen herunter
            for k, i in enumerate((2, 1, 3, 0, 4)):
                sz.droop[i] = min(1.0, max(0.0, (u - k * 0.14) / 0.18))
            return Pose(arm_v=-8, arm_h=8, hub=1.5 * math.sin(u * 30) if u > 0.4 else 0.0)

        def tasten(pose, sz):
            w = 8 * math.sin(sz.t * 5)
            return replace(pose, arm_v=-95 + w, arm_h=-80 - w, arm_v_x=14)

        def ende(sz):
            sz.weg(STAUB)

        return [
            Gehe(bis=px, tempo=1.8),
            Setze(richtung=r),
            Stehe(0.2, lambda sz, u: Pose(arm_v=-95, arm_h=-60, arm_v_x=12, blick_y=0.2, auge_zu=blinzeln(sz.t))),
            Jeweils(0.6, hand_zieht),
            Tu(pling),
            Stehe(0.35, schuetteln),
            Jeweils(0.25, bein_hoch),
            Jeweils(0.6, fuss_zieht),
            Tu(pling),
            Setze(hopp=0.0),
            Stehe(0.35, strauchel),
            Setze(hopp=0.0),
            Gehe(bis=lambda sz: sz.haken[0] - r * 62 * s, tempo=1.2),
            Setze(richtung=r),
            Jeweils(0.3, einhaken),
            Tu(lambda sz: start_x.__setitem__(0, sz.x)),
            JeweilsDt(1.1, zurueckstemmen),
            Stehe(0.35, warten),
            HaareHoch(0.5),
            Stehe(0.14, schnalzen),
            Tu(aufsetzen),
            Stehe(0.35, umfallen),
            Tu(liegen_staub),
            Stehe(0.45, strampeln),
            Stehe(0.4, aufrichten),
            Setze(neigung=0.0),
            Stehe(0.85, klappen),
            Stehe(0.6, lambda sz, u: Pose(kopf_vorn=True, arm_v=-8, arm_h=8)),
            GeheHinaus(-r, tasten),
            Tu(ende),
            WarteBis(lambda sz: not sz.wolke and not sz.splitter),
        ]

    def fig(self, fx, fy):
        q = self.trafo().map(QPointF(fx, fy))
        return q.x(), q.y()

    def schreck_ablauf(self):
        self.band = None
        self.neigung = 0.0
        self.hopp = 0.0
        return self.schreck_rennen()


class JeweilsDt(Jeweils):
    """Wie Jeweils, aber funktion(szene, u, dt)."""

    def weiter(self, sz, u, dt):
        self.funktion(sz, u, dt)


class GeheHinaus(Gehe):
    """Geht tastend zur Seite seite hinaus."""

    def __init__(self, seite, haltung):
        super().__init__(None, 0.9, haltung=haltung)
        self.seite = seite

    def beginn(self, sz):
        sz.richtung = self.seite
        super().beginn(sz)
