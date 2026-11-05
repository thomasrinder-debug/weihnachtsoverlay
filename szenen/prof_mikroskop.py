import math
import random

from PyQt6.QtCore import QPointF, QRectF

from zeichnen.figur import Pose
from zeichnen.grundlagen import blinzeln, glatt
from zeichnen.labor_b import mikroskop_okular, zeichne_mikroskop
from zeichnen.labor_f import zeichne_riesenauge

from .basis import Gehe, Jeweils, Kurz, Nebenbei, Schritt, Setze, Stehe, Tu, Wandel, Warte, WarteBis
from .professor import STAUB, HaareHoch, ProfSzene

M = 1.9             # Standmikroskop, Okular etwa in Augenhöhe
AUGE_R = 38         # Riesenauge: 0,3 H Durchmesser
PIVOT = (6, -58)


class Laufend(Schritt):
    """Ruft eine Weile funktion(szene, u, dt) auf; liefert sie eine Pose, wird sie gesetzt."""

    def __init__(self, dauer, funktion):
        self.dauer, self.funktion = dauer, funktion

    def weiter(self, sz, u, dt):
        pose = self.funktion(sz, u, dt)
        if pose is not None:
            sz.pose = pose


class Mikroskop(ProfSzene):
    """Er beugt sich ans Okular, das Rohr wächst ihm nach. Er weicht zurück, lehnt
    sich weit nach hinten, das Rohr folgt. Dann öffnet sich vor seiner Nase ein
    riesiges Auge, er plumpst auf den Hintern. Das Auge blinzelt, er blinzelt zurück,
    schaut ins Publikum und schleicht rückwärts hinaus. Das Rohr schaut ihm nach,
    dann hüpft das Mikroskop hinterher."""
    name, titel, reihenfolge = 'mikroskop', 'Gegenbesichtigung', 68

    def vorbereiten(self):
        r, s = self.richtung, self.s
        self.mx = self.vom_rand(0.16)
        self.px = self.mx - r * 78 * s
        self.strecke = self.neig = 0.0
        self.folgt = 0.0            # 0..1: Rohr folgt seinem Auge
        self.abstand = 16.0         # Abstand Okular – Auge in Einheiten
        self.riesen = 0.0           # 0..1 Riesenauge geöffnet
        self.lid = 1.0
        self.m_hopp = 0.0
        self.m_kipp = 0.0
        self.knopf = 0.0
        self.blick = (0.0, 0.0)
        self.ziel = None            # fester Blickpunkt statt ihm
        self.richtung_m = -r

    # -- Geometrie

    def sx(self):
        return self.richtung_m

    def pivot(self):
        return (self.mx + self.sx() * PIVOT[0] * M * self.s,
                self.boden - self.m_hopp + PIVOT[1] * M * self.s)

    def okular(self):
        ox, oy = mikroskop_okular(self.strecke, self.neig)
        return self.mx + self.sx() * ox * M * self.s, self.boden - self.m_hopp + oy * M * self.s

    def auge_mitte(self):
        """Mitte des Riesenauges: es blüht hinter dem Okular auf, die Vorderkante bleibt am Okular."""
        ox, oy = self.okular()
        px, py = self.pivot()
        d = math.hypot(ox - px, oy - py) or 1.0
        a = AUGE_R * 1.15 * self.riesen * self.s
        return ox - (ox - px) / d * a, oy - (oy - py) / d * a

    def sein_auge(self):
        q = self.trafo().map(QPointF(22, -184))
        return q.x(), q.y()

    def rohr_ziel(self, tx, ty):
        """strecke und neig, mit denen das Okular auf (tx, ty) zeigt."""
        px, py = self.pivot()
        dx = (tx - px) / (self.sx() * M * self.s)
        dy = (ty - py) / (M * self.s)
        lang = math.hypot(dx, dy)
        neig = math.degrees(math.atan2(dx, -dy))
        return max(0.0, min(5.0, (lang - 36) / 30)), max(-120.0, min(120.0, neig))

    def weiter(self, dt):
        super().weiter(dt)
        if self.erschreckt:
            return
        ex, ey = self.sein_auge()
        if self.folgt > 0 and self.zeige_figur:
            g = self.abstand * self.s
            st, ng = self.rohr_ziel(ex + self.richtung * g, ey)
            k = min(1.0, dt * 9) * self.folgt
            self.strecke += (st - self.strecke) * k
            self.neig += (ng - self.neig) * k
        ox, oy = self.auge_mitte()
        zx, zy = self.ziel if self.ziel else (ex, ey)
        dx, dy = zx - ox, zy - oy
        n = math.hypot(dx, dy) or 1.0
        self.blick = (dx / n, dy / n * 0.8)

    # -- Ablauf

    def ablauf(self):
        r, s = self.richtung, self.s
        self.x = self.aussen(-r)
        rand_x = self.aussen(-r) - r * 60 * s

        def hinsehen(sz, u):
            sz.neigung = 18 * glatt(u / 0.3)
            kx, ky = sz.mx + sz.sx() * -10 * M * s, sz.boden - 30 * M * s
            sz.knopf = math.sin(u * 5) * 0.4
            return Pose(arm_v=-60 + 10 * math.sin(u * 14), blick_y=0.2, auge_zu=0.35 < u)

        def zurueck(lehne, dauer, weite):
            def pose(sz, u):
                f = glatt(u / dauer)
                sz.neigung = sz.n0 + (lehne - sz.n0) * f
                sz.x = sz.x0 - r * weite * s * f
                b = 12 * math.sin(f * math.pi)
                return Pose(arm_v=-30 - 50 * f, arm_h=20 + 30 * f, sorge=0.5 + 0.5 * f, blick_y=-0.1,
                            bein_v=b, bein_h=-b, auge_zu=False, schreck=0.25 * f)
            return pose

        def merke(sz):
            sz.n0, sz.x0 = sz.neigung, sz.x

        def ruderm(sz, u):
            w = 30 * math.sin(u * 18)
            sz.neigung = -30 + 2 * math.sin(u * 18)
            return Pose(arm_v=-120 + w, arm_h=-60 - w, arm_v_x=16, sorge=1.0, blick_y=0.0, bein_v=-14, bein_h=6)

        def plumps(sz):
            sz.neigung = -24
            sz.y = sz.boden + 42 * s
            sz.x -= r * 55 * s
            sz.haare, sz.brille = 1.0, 0.7
            sz.streue(sz.x, sz.boden - 4 * s, 12, STAUB, tempo=120, dauer=0.6, r=(5, 10), richtung=-math.pi / 2,
                      streuung=1.4)

        def sitzend(**werte):
            def pose(sz, u):
                p = dict(bein_v=-70, bein_h=-58, arm_v=50, arm_h=62, arm_v_x=8)
                p.update({k: (v(sz, u) if callable(v) else v) for k, v in werte.items()})
                return Pose(**p)
            return pose

        def auge_auf(sz, u):
            sz.riesen = glatt(u / 0.12)
            sz.lid = 1.0

        def augenspiel(sz, u):
            # Auge blinzelt (0,15–0,35), er blinzelt zurück (0,55–0,7), Auge noch einmal (0,95–1,05)
            sz.lid = 0.03 if 0.15 < u < 0.35 or 0.95 < u < 1.05 else 1.0
            sz.abstand = 22 - 8 * glatt(u / 0.6)

        def aufstehen(sz, u):
            f = glatt(u / 0.35)
            sz.y = sz.boden + 42 * s * (1 - f)
            sz.neigung = -24 * (1 - f)
            return Pose(bein_v=-70 * (1 - f), bein_h=-58 * (1 - f), arm_v=38 - 60 * f, arm_h=55 - 40 * f,
                        sorge=0.8, blick_y=0.0, auge_zu=blinzeln(sz.t))

        def rueckwaerts(sz, u, dt):
            v = sz.tempo * 1.1 * glatt(u / 0.2 + 0.3)
            sz.x -= r * v * dt
            sz.phase += v * dt / (s * 30)
            b = 22 * math.sin(sz.phase)
            return Pose(bein_v=b, bein_h=-b, arm_v=-60, arm_h=-40, sorge=1.0, blick_y=0.0,
                        hub=-abs(math.cos(sz.phase)) * 3, auge_zu=False)

        def nachschauen(sz):
            sz.folgt = 0.0
            sz.ziel = None

        def zum_publikum(sz):
            sz.ziel = (sz.mx, sz.boden + 400 * s)

        def hoppeln(sz, u, dt):
            k = u / 0.32
            f = k - int(k)
            sz.m_hopp = 34 * s * 4 * f * (1 - f)
            sz.m_kipp = -sz.sx() * 10 * math.sin(f * math.pi)
            sz.mx -= r * sz.tempo * 1.5 * dt * (1 if f < 0.85 else 0.2)
            sz.strecke += (0.3 - sz.strecke) * 0.08
            sz.neig += (40 - sz.neig) * 0.08

        return [
            Gehe(bis=self.px, tempo=1.8),
            Setze(richtung=r),
            Stehe(0.5, hinsehen),
            # das Rohr wächst nach
            Setze(folgt=1.0, abstand=4.0),
            Tu(merke),
            Stehe(0.45, zurueck(0.0, 0.35, 20)),
            Setze(abstand=6.0),
            Stehe(0.25, lambda sz, u: Pose(sorge=0.9, blick_y=0.0, arm_v=-80, arm_h=50, auge_zu=0.1 < u < 0.2)),
            Tu(merke),
            Stehe(0.6, zurueck(-24, 0.45, 26)),
            Stehe(0.5, ruderm),
            # Erwartungspause, dann das Auge
            Setze(abstand=20.0),
            Stehe(0.35, lambda sz, u: Pose(sorge=1.0, blick_y=0.0, arm_v=-100, arm_h=-60, bein_v=-14, bein_h=6)),
            Jeweils(0.14, auge_auf),
            Stehe(0.12, lambda sz, u: Pose(schreck=1.0, arm_v=-150, arm_h=-140, arm_v_x=18, bein_v=-30)),
            Tu(plumps),
            Stehe(0.45, sitzend(schreck=1.0, kopf_vorn=False, blick_y=-0.1)),
            Setze(abstand=22.0),
            Jeweils(1.1, augenspiel),
            Nebenbei(Stehe(1.1, sitzend(auge_zu=lambda sz, u: 0.55 < u < 0.7, sorge=0.9, blick_y=-0.1))),
            Warte(1.1),
            Stehe(0.9, sitzend(kopf_vorn=True, auge_zu=lambda sz, u: 0.3 < u < 0.45, sorge=0.3,
                                mund_offen=lambda sz, u: 0.6 < u < 0.85)),
            Stehe(0.4, aufstehen),
            Setze(abstand=20.0),
            Laufend(0.9, rueckwaerts),
            Tu(nachschauen),
            Nebenbei(Laufend(2.0, rueckwaerts)),
            Warte(0.5),
            Tu(zum_publikum),
            Kurz(0.15, lid=0.03),
            Warte(0.2),
            Wandel(0.2, riesen=0.0),
            Laufend(1.6, hoppeln),
            WarteBis(lambda sz: not sz.nebenbei),
        ]

    # -- Zeichnen

    def zeichne_requisiten(self, p):
        s = self.s
        p.save()
        p.translate(self.mx, self.boden - self.m_hopp)
        p.rotate(self.m_kipp)
        p.scale(self.sx() * s * M, s * M)
        zeichne_mikroskop(p, self.strecke, self.neig, 0.0, 0.0, self.blick, self.knopf, 1.0)
        p.restore()

    def zeichne_davor(self, p):
        if self.riesen <= 0:
            return
        s = self.s
        ox, oy = self.auge_mitte()
        p.save()
        p.translate(ox, oy)
        p.scale(s * self.riesen, s * self.riesen)
        zeichne_riesenauge(p, AUGE_R, self.lid, self.blick)
        p.restore()

    def requisiten_kasten(self):
        s = self.s
        ox, oy = self.okular()
        px, py = self.pivot()
        ax, ay = self.auge_mitte()
        rand = 16 * s
        ra = (AUGE_R * 1.3 * self.riesen + 8) * s
        xs = [self.mx - 30 * M * s, self.mx + 30 * M * s, ox - rand, ox + rand, px - 16 * s, px + 16 * s,
              ax - ra, ax + ra]
        top = min(oy - rand, py - 16 * s, ay - ra)
        return QRectF(min(xs), top, max(xs) - min(xs), self.boden - top + 4 * s)

    # -- Schreck

    def schreck_ablauf(self):
        self.folgt = 0.0
        self.riesen = 0.0
        self.ziel = None
        self.neigung = 0.0
        return self.schreck_versinken()
