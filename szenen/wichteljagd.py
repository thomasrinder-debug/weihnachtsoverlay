import random

from zeichnen.figur import renn_pose
from zeichnen.figuren import Pinguin, Wichtel
from zeichnen.grundlagen import WEISS

from .basis import Erschrecke, Gehe, Mit, Nebenbei, Renne, Rutsche, Schaue, Setze, Szene, Warte, WarteNebenbei


def flucht(pose, sz):
    p = renn_pose(sz.phase)
    p.kopf_vorn, p.sorge, p.schreck = True, 1.0, 0.5
    return p


def jagd(pose, sz):
    p = renn_pose(sz.phase)
    p.arm_v, p.arm_v_x, p.sorge = -150 + (sz.t * 12 % 2) * 20, 22, 0.0
    return p


class Wichteljagd(Szene):
    """Ein Wichtel jagt ihn am unteren Rand entlang, dann jagt er den Wichtel zurück.
    Beim dritten Mal schlendern beide friedlich herein, bis ein Pinguin auf dem Bauch
    angerauscht kommt und beide Hals über Kopf fliehen."""
    name, titel, reihenfolge = 'jagd', 'Verfolgungsjagd', 13

    def vorbereiten(self):
        s, r = self.s, self.richtung
        self.w = self.dazu('w', Wichtel, groesse=0.72, vorn=True)
        self.pg = self.dazu('pg', Pinguin, groesse=0.7)
        self.pg.zeige_figur = False
        self.links, self.rechts = self.aussen(-r), self.aussen(r)
        self.abstand = 230 * s

    def ablauf(self):
        r, a = self.richtung, self.abstand
        self.x = self.links
        self.w.x = self.links - r * a
        renn = dict(tempo=2.6, neigung=10)
        return [
            Nebenbei(Mit('w', Gehe(bis=self.rechts + r * a * 0.6, haltung=jagd, **renn))),
            Gehe(bis=self.rechts + r * a, haltung=flucht, **renn),
            WarteNebenbei(), Warte(0.7),
            # zurück, jetzt jagt er
            Nebenbei(Mit('w', Gehe(bis=self.links - r * a * 0.6, haltung=flucht, **renn))),
            Warte(0.35),
            Gehe(bis=self.links - r * a, haltung=jagd, **renn),
            WarteNebenbei(), Warte(0.6),
            # friedlich zu zweit
            Mit('w', Setze(x=self.links - r * 120 * self.s)),
            Nebenbei(Mit('w', Gehe(bis=self.vom_rand(0.2) + r * 70 * self.s))),
            Gehe(bis=self.vom_rand(0.2) - r * 60 * self.s),
            WarteNebenbei(),
            Schaue(1.2),
            Mit('pg', Setze(zeige_figur=True, x=self.rechts, richtung=-r)),
            Nebenbei(Mit('pg', Rutsche(zum='weiter', tempo=6.5, hoehe=28))),
            Warte(0.5),
            Nebenbei(Mit('w', Erschrecke(0.35, 50)), Mit('w', Renne(zum='rand', tempo=3.8))),
            Erschrecke(0.35, 50), Renne(zum='rand', tempo=3.4),
            WarteNebenbei(),
        ]

    def schreck_ablauf(self):
        return self.schreck_alle()

    def weiter(self, dt):
        pg = self.pg
        if pg.zeige_figur and pg.neigung > 60 and random.random() < 0.6:
            self.streue(pg.x, self.boden - 4 * self.s, 1, WEISS, tempo=60, dauer=0.5, r=(2, 5))
