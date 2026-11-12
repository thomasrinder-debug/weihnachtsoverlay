import random

from PyQt6.QtCore import QRectF

from zeichnen.figur import Pose
from zeichnen.figuren import Osterhase
from zeichnen.grundlagen import WEISS
from zeichnen.requisiten import EI_FARBEN

from .basis import (Ducke, Erschrecke, Gehe, Hoppel, Mit, Nebenbei, Rutsche, Setze, Stehe, Szene, Tu, Wandel,
                    Warte, WarteBis)
from .ostern import Ei


class Eiersuche(Szene):
    """Ein Osterhase hoppelt mit seinem Körbchen herein und versteckt drei bunte Eier am Rand.
    Der Weihnachtsmann findet sie und wirft sie eins nach dem anderen über die Schulter in
    seinen Sack. Das letzte Ei hüpft davon, beim zweiten Versuch über seinen Kopf hinweg; er
    hechtet bäuchlings hinterher. Danach hüpft das Ei zurück, und der Hase holt es sich."""
    name, titel, reihenfolge = 'eiersuche', 'Eiersuche', 93

    def vorbereiten(self):
        r = self.start = self.richtung
        self.hase = self.dazu('hase', Osterhase, groesse=0.55, korb=3, vorn=True)
        self.hase.x = self.aussen(-r)
        self.x = self.aussen(-r)
        farben = random.sample(EI_FARBEN, 3)
        self.eier = [Ei(0, 0, 15 * self.s, farben[i], i % 3) for i in range(3)]
        for e in self.eier:
            e.sichtbar = False

    def lege(self, i):
        h, e = self.hase, self.eier[i]
        e.x = h.x + h.richtung * 30 * h.s
        e.y = self.boden - e.r
        e.sichtbar = True
        h.korb -= 1

    def ei_legen(self, i, x):
        return [Mit('hase', Hoppel(bis=x, tempo=0.8, hoehe=22)),
                Mit('hase', Wandel(0.15, neigung=24)),
                Mit('hase', Stehe(0.15, Pose(arm_v=-40, blick_y=0.8))),
                Tu(lambda sz: sz.lege(i)),
                Mit('hase', Wandel(0.15, neigung=0)),
                Mit('hase', Stehe(0.2, Pose(kopf_vorn=True)))]

    def in_den_sack(self, i):
        e = self.eier[i]
        r, s = self.richtung, self.s
        e.bogen(self.t, self.x - self.richtung * 52 * s, self.y - 150 * s, 0.55, 70 * s, -r * 400, weg=True)

    def huepf(self, i, dx, hoehe, dauer):
        e = self.eier[i]
        e.bogen(self.t, e.x + dx, e.y, dauer, hoehe, self.richtung * 360)

    def ablauf(self):
        r, s = self.richtung, self.s
        bei = lambda i: (lambda sz: sz.eier[i].x - r * 62 * s)  # noqa: E731
        return [
            *self.ei_legen(0, self.vom_rand(0.24) - r * 17 * s),
            Mit('hase', Setze(richtung=-r)),
            *self.ei_legen(1, self.vom_rand(0.18) + r * 17 * s),
            *self.ei_legen(2, self.vom_rand(0.12) + r * 17 * s),
            Mit('hase', Stehe(0.5, Pose(kopf_vorn=True, auge_zu=True, mund_offen=True))),
            Mit('hase', Hoppel(tempo=0.9, hoehe=24)),
            Mit('hase', Setze(zeige_figur=False)),
            Gehe(bis=bei(2)),
            Stehe(0.4, Pose(kopf_vorn=True, blick_y=0.6, mund_offen=True)),
            Ducke(0.25), Tu(lambda sz: sz.in_den_sack(2)),
            Stehe(0.3, Pose(arm_v=-150, arm_v_x=16)),
            Gehe(bis=bei(1), tempo=0.8),
            Ducke(0.25), Tu(lambda sz: sz.in_den_sack(1)),
            Stehe(0.3, Pose(arm_v=-150, arm_v_x=16)),
            Gehe(bis=bei(0), tempo=0.8),
            Ducke(0.25), Tu(lambda sz: sz.huepf(0, r * 70 * s, 50 * s, 0.4)),
            Stehe(0.7, lambda sz, u: Pose(kopf_vorn=True, schreck=0.5 if u < 0.4 else 0.0, sorge=0.6,
                                          auge_zu=0.5 < u < 0.6)),
            Gehe(bis=bei(0), tempo=0.5),
            Ducke(0.3), Tu(lambda sz: sz.huepf(0, -r * 190 * s, 330 * s, 0.9)),
            Stehe(0.45, lambda sz, u: Pose(blick_y=-1.0, arm_v=-120, schreck=0.6)),
            Setze(richtung=-r),
            Stehe(0.35, Pose(blick_y=0.6, sorge=0.8)),
            Tu(lambda sz: setattr(sz.eier[0], 'flucht', -r * 520 * s)),
            Rutsche(zum='weiter', tempo=3.2),
            WarteBis(lambda sz: not sz.eier[0].im_bild(sz.geo)),
            Warte(0.6),
            Tu(lambda sz: sz.ei_zurueck()),
            WarteBis(lambda sz: sz.eier[0].bahn is None),
            Mit('hase', Setze(zeige_figur=True, richtung=r, x=self.aussen(-r))),
            Mit('hase', Hoppel(bis=lambda d: d.sz.eier[0].x - r * 40 * d.s, tempo=0.8, hoehe=22)),
            Mit('hase', Stehe(0.3, Pose(arm_v=-60))),
            Tu(lambda sz: sz.eier[0].bogen(sz.t, sz.hase.x + r * 2 * sz.hase.s, sz.hase.y - 70 * sz.hase.s,
                                           0.35, 40 * s, r * 360, weg=True)),
            Warte(0.35),
            Mit('hase', Setze(korb=1)),
            Mit('hase', Stehe(0.8, lambda d, u: Pose(kopf_vorn=True, auge_zu=0.3 < u < 0.5, mund_offen=u > 0.5))),
            Mit('hase', Setze(richtung=-r)),
            Mit('hase', Hoppel(tempo=0.9, hoehe=24)),
        ]

    def ei_zurueck(self):
        e = self.eier[0]
        r = self.start
        e.flucht = 0.0
        e.x = self.aussen(-r)
        e.bogen(self.t, self.vom_rand(0.1, -r), self.boden - e.r, 1.1, 60 * self.s, r * 720)

    def weiter(self, dt):
        for e in self.eier:
            e.schritt(self.t, dt, self.boden)
        if self.neigung > 60 and random.random() < 0.4:
            self.streue(self.x + self.richtung * 60 * self.s, self.boden - 3 * self.s, 1, WEISS, tempo=60,
                        dauer=0.45, r=(2, 4))

    def zeichne_hinten(self, p):
        for e in self.eier:
            if e.bahn and e.bahn[-1]:
                e.zeichne(p)

    def zeichne_vorn(self, p):
        for e in self.eier:
            if not (e.bahn and e.bahn[-1]):
                e.zeichne(p)

    def grenzen_extra(self):
        k = QRectF()
        for e in self.eier:
            k = k.united(e.kasten())
        return k

    def schreck_ablauf(self):
        for e in self.eier:
            if e.sichtbar:
                e.bahn = None
                e.y = self.boden - e.r
                e.flucht = (-1 if e.x < self.geo.center().x() else 1) * 700 * self.s
        h = self.hase
        neu = []
        if h.zeige_figur and h.figur_sichtbar():
            neu.append(Nebenbei(Mit('hase', Erschrecke(0.3, 50)), Mit('hase', Setze(richtung=h.naechster_rand())),
                                Mit('hase', Hoppel(tempo=3.5, hoehe=30))))
        return neu + self.schreck_alle(ausser=('hase',)) + [
            WarteBis(lambda sz: not any(e.im_bild(sz.geo) for e in sz.eier))]

