import math
import random

from PyQt6.QtCore import QRectF

from zeichnen.figur import Pose
from zeichnen.figuren import WichtelSteif
from zeichnen.grundlagen import WEISS, blinzeln
from zeichnen.requisiten import zeichne_besen, zeichne_kehrblech

from .basis import Erschrecke, Gehe, Jeweils, Mit, Nebenbei, Schritt, Setze, Stehe, Szene, Tu, Wandel, Warte, muetze_richten

FEGEN = lambda p, d: Pose(bein_v=p.bein_v, bein_h=p.bein_h, hub=p.hub, arm_v=-45, arm_h=-35,  # noqa: E731
                          auge_zu=p.auge_zu)


class Mitnehmen(Schritt):
    """Besen, Kehrblech und Wichtel (falls drauf) bewegen sich gemeinsam bis aus dem Bild."""

    def __init__(self, seite, tempo):
        self.seite_v, self.tempo = seite, tempo

    def beginn(self, sz):
        self.seite = self.seite_v(sz) if callable(self.seite_v) else self.seite_v

    def weiter(self, sz, u, dt):
        v = self.seite * sz.tempo * self.tempo * min(1.0, u * 3 + 0.3) * dt
        sz.bx += v
        sz.kx += v
        sz.w.x += v
        sz.bw = -self.seite * sz.richtung * 15 + math.sin(u * 20) * 6

    def fertig(self, sz, u):
        return not sz.grenzen().intersects(sz.geo)


class Besen(Szene):
    """Ein Wichtel fegt Schnee, stellt den Besen ab und ruht sich aus. Da wird der Besen
    lebendig, fegt den protestierenden Wichtel auf ein winziges Kehrblech, klopft zufrieden
    seine Borsten aus und schiebt alles hinaus. Der Wichtel richtet derweil seine Mütze."""
    name, titel, reihenfolge = 'besen', 'Besen kehrt zurück', 37

    def vorbereiten(self):
        self.zeige_figur = False
        r = self.richtung
        self.w = self.dazu('w', WichtelSteif, groesse=0.55, knick=1.0, vorn=False)
        self.w.richtung = r
        self.w.tempo = self.tempo * 0.6
        self.halten = True
        self.bx, self.bw, self.bhopp = self.aussen(-r), 0.0, 0.0
        self.ziel = self.vom_rand(random.uniform(0.17, 0.21))
        self.kx = self.ziel - r * 110 * self.s

    def ablauf(self):
        r, s = self.richtung, self.s

        def gefegt(sz, u):
            f = min(1.0, u / 1.4)
            w = sz.w
            sz.bx = sz.ziel + r * 50 * s + (sz.kx + r * 45 * s - sz.ziel - r * 50 * s) * f
            sz.bw = r * (25 + 18 * math.sin(u * 16))
            w.x = sz.ziel - r * 4 * s + (sz.kx - r * 22 * s - sz.ziel + r * 4 * s) * f
            w.neigung = -20 * math.sin(u * 12)
            w.pose = Pose(kopf_vorn=True, schreck=0.6, sorge=1.0, arm_v=-150 + 40 * math.sin(u * 20),
                          arm_h=-140, bein_v=-40, bein_h=30, mund_offen=True)
            if random.random() < 0.4:
                sz.streue(sz.bx, sz.boden - 4 * s, 2, WEISS, tempo=90, dauer=0.5, r=(2, 5))

        def klopfen(sz, u):
            sz.bhopp = abs(math.sin(u * 9)) * 14 * s
            sz.bw = 0.0
            if (u * 9 / math.pi) % 1 < 0.08:
                sz.streue(sz.bx, sz.boden - 6 * s, 4, WEISS, tempo=80, dauer=0.5, r=(3, 6))

        return [
            Mit('w', Gehe(bis=self.ziel, haltung=FEGEN)),
            Mit('w', Stehe(0.5, Pose(arm_v=-45, arm_h=-35))),
            Setze(halten=False, bw=0.0),
            Mit('w', Wandel(0.3, x=lambda d: d.sz.ziel - r * 4 * s)),
            Mit('w', Stehe(1.6, lambda d, u: Pose(kopf_vorn=True, arm_v=-160 if u < 0.8 else 0, arm_v_x=8,
                                                  auge_zu=u > 0.8, mund_offen=u < 0.8))),
            Jeweils(1.0, lambda sz, u: setattr(sz, 'bw', math.sin(u * 30) * 8 * (u < 0.7))),
            Jeweils(0.5, lambda sz, u: setattr(sz, 'bhopp', math.sin(math.pi * min(1.0, u / 0.5)) * 30 * s)),
            Mit('w', Setze(striche=True, pose=Pose(kopf_vorn=True, schreck=1.0))), Warte(0.3),
            Mit('w', Setze(striche=False)),
            Jeweils(1.4, gefegt),
            Mit('w', Setze(neigung=0, hopp=lambda d: 8 * d.sz.s)),
            Jeweils(1.4, klopfen),
            Setze(bhopp=0.0),
            Mit('w', Stehe(1.2, lambda d, u: Pose(kopf_vorn=True, sorge=1.0, mund_offen=(u * 6) % 2 < 1,
                                                  arm_v=-120 + 30 * math.sin(u * 14), arm_h=-110,
                                                  bein_v=-70, bein_h=-60))),
            *muetze_richten('w'),
            Mitnehmen(-r, 1.4),
        ]

    def schreck_ablauf(self):
        self.nebenbei.clear()
        neu = [Setze(halten=False), Mit('w', Setze(neigung=0, knick=1.0))]
        if self.w.figur_sichtbar():
            hops = Jeweils(0.3, lambda sz, u: setattr(sz, 'bhopp', math.sin(math.pi * u / 0.3) * 40 * sz.s))
            neu += [Nebenbei(hops, Setze(bhopp=0.0)), Mit('w', Erschrecke(0.3, 35))]
        return neu + [Mitnehmen(lambda sz: sz.w.naechster_rand(), 4.0)]

    def weiter(self, dt):
        w, s = self.w, self.s
        if self.halten:
            self.bx = w.x + w.richtung * 30 * s
            self.bw = w.richtung * (20 + 14 * math.sin(w.phase * 2))
            if w.figur_sichtbar() and random.random() < 0.3:
                self.streue(self.bx, self.boden - 3 * s, 1, WEISS, tempo=80, dauer=0.5, r=(2, 5))

    def zeichne_hinten(self, p):
        p.save()
        p.translate(self.kx, self.boden)
        p.scale(self.s * self.richtung * 0.8, self.s * 0.8)
        zeichne_kehrblech(p)
        p.restore()

    def zeichne_vorn(self, p):
        p.save()
        p.translate(self.bx, self.boden - self.bhopp)
        p.scale(self.s * 0.8, self.s * 0.8)
        zeichne_besen(p, self.bw)
        p.restore()

    def grenzen_extra(self):
        s = self.s
        a, b = sorted((self.bx, self.kx))
        return QRectF(a - 90 * s, self.boden - 160 * s, b - a + 180 * s, 160 * s)

