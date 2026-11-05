import math
import random

from zeichnen.figur import Pose
from zeichnen.figuren import Pinguin
from zeichnen.grundlagen import WEISS, blinzeln

from .basis import (Erschrecke, Gehe, Gleite, Jeweils, Mit, Nebenbei, Rutsche, Setze, Stehe, Szene, Wandel, Warte,
                    WarteNebenbei)

GLEITEN = Pose(arm_v=12, arm_h=-12, bein_v=20, bein_h=30, mund_offen=True)
KINDER = ('k1', 'k2', 'k3')


class Pinguinfamilie(Szene):
    """Mama Pinguin rutscht auf dem Bauch herein, drei Küken sausen hinterher und reihen sich
    auf. Das Kleinste schafft es nicht, purzelt und dreht sich, Mama watschelt zurück und schubst
    es an; dann rutscht die ganze Familie im Gänsemarsch davon."""
    name, titel, reihenfolge = 'pinguinfamilie', 'Pinguinfamilie', 44

    def vorbereiten(self):
        self.zeige_figur = False
        r = self.richtung
        self.mama = self.dazu('mama', Pinguin, groesse=0.8)
        for i, n in enumerate(KINDER):
            k = self.dazu(n, Pinguin, groesse=0.42 - 0.04 * i, vorn=True)
            k.x = self.aussen(-r)
        self.mama.x = self.aussen(-r)

    def rein(self, wer, bis, dauer):
        hoch = lambda d: 28 * d.s  # noqa: E731
        return [Mit(wer, Setze(neigung=80, hopp=hoch, pose=GLEITEN)), Mit(wer, Gleite(bis, dauer)),
                Mit(wer, Wandel(0.3, neigung=0, hopp=0)),
                Mit(wer, Setze(pose=Pose(kopf_vorn=True, auge_zu=False)))]

    def ablauf(self):
        r, s = self.richtung, self.s
        ziel = self.vom_rand(0.24)
        hoch = lambda d: 28 * d.s  # noqa: E731
        return [
            Nebenbei(*self.rein('mama', ziel, 1.6)),
            Warte(0.5),
            Nebenbei(*self.rein('k1', ziel - r * 70 * s, 1.5)),
            Warte(0.35),
            Nebenbei(*self.rein('k2', ziel - r * 115 * s, 1.5)),
            Warte(0.35),
            *self.rein('k3', self.vom_rand(0.06), 1.0),
            WarteNebenbei(),
            Mit('k3', Stehe(0.6, lambda d, u: Pose(kopf_vorn=True, sorge=1.0, blick_x=1))),
            Mit('k3', Gehe(bis=lambda d: d.sz.vom_rand(0.1), tempo=0.35)),
            Mit('k3', Wandel(0.2, neigung=-80, hopp=lambda d: 40 * d.s)),
            Mit('k3', Jeweils(1.0, lambda d, u: setattr(d, 'pose', Pose(arm_v=-150, arm_h=-150,
                                                                         bein_v=-30 * math.sin(u * 20),
                                                                         mund_offen=True)))),
            Mit('mama', Setze(richtung=-r)),
            Mit('mama', Gehe(bis=lambda d: d.sz.darsteller['k3'].x + r * 55 * s, tempo=0.6)),
            Mit('k3', Wandel(0.3, neigung=0, hopp=0)),
            Mit('k3', Setze(pose=Pose(kopf_vorn=True, auge_zu=True))),
            Mit('mama', Stehe(0.7, Pose(kopf_vorn=True, arm_v=-100, arm_h=-100))),
            *[Mit(n, Setze(richtung=-r)) for n in KINDER],
            Mit('mama', Setze(neigung=80, hopp=hoch, pose=GLEITEN)),
            *[Mit(n, Setze(neigung=80, hopp=hoch, pose=GLEITEN)) for n in KINDER],
            Nebenbei(Mit('k3', Rutsche(zum='weiter', tempo=3.0, hoehe=28, pose=GLEITEN))),
            Nebenbei(Warte(0.15), Mit('mama', Rutsche(zum='weiter', tempo=3.0, hoehe=28, pose=GLEITEN))),
            Nebenbei(Warte(0.35), Mit('k1', Rutsche(zum='weiter', tempo=3.2, hoehe=28, pose=GLEITEN))),
            Nebenbei(Warte(0.5), Mit('k2', Rutsche(zum='weiter', tempo=3.4, hoehe=28, pose=GLEITEN))),
            WarteNebenbei(),
        ]

    def schreck_ablauf(self):
        self.nebenbei.clear()
        neu = []
        for n, d in self.darsteller.items():
            if d.figur_sichtbar():
                neu.append(Nebenbei(Mit(n, Setze(neigung=0, hopp=0)), Mit(n, Erschrecke(0.3, 45)),
                                    Mit(n, Rutsche(zum='rand', tempo=5.0, hoehe=28, pose=GLEITEN))))
            else:
                d.zeige_figur = False
        return neu + [WarteNebenbei()]

    def weiter(self, dt):
        for d in self.darsteller.values():
            if d.zeige_figur and d.neigung > 60 and random.random() < 0.35:
                self.streue(d.x + d.richtung * 60 * d.s, self.boden - 3 * self.s, 1, WEISS, tempo=60,
                            dauer=0.45, r=(2, 4))
