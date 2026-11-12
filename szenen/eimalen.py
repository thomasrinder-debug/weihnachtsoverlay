import math

from zeichnen.figur import Pose
from zeichnen.figuren import Osterhase
from zeichnen.grundlagen import WEISS
from zeichnen.requisiten import EI_FARBEN

from .basis import Erschrecke, Gehe, Hoppel, Jeweils, Kurz, Mit, Nebenbei, Setze, Stehe, Szene, Tu, Wandel, Warte, \
    WarteBis
from .ostern import Ei


def schiebe(pose, d):
    pose.arm_v, pose.arm_h, pose.arm_v_x = -80, -75, 14
    return pose


class Eimalen(Szene):
    """Ein Osterhase rollt ein riesiges weißes Ei herein und bemalt es mit drei bunten Bändern und
    Tupfen. Stolz reckt er die Arme hoch, da kippelt das Ei, rollt davon, hält an, kommt zurück
    und überrollt ihn. Er liegt platt da, springt wieder auf und ist jetzt selbst gestreift."""
    name, titel, reihenfolge = 'eimalen', 'Ei bemalen', 94

    def vorbereiten(self):
        r = self.richtung
        self.zeige_figur = False
        self.hase = self.dazu('hase', Osterhase, groesse=0.6, pinsel=None)
        self.hase.x = self.aussen(-r) - r * 40 * self.s
        self.ei = Ei(0, 0, 36 * self.s, None)
        self.ei.bemalt = 0.0
        self.ei.y = self.boden - self.ei.r
        self.ei_x = self.ei.x = self.hase.x + r * 95 * self.s
        self.schieben = True
        self.platt = False
        self.ei_hopp = 0.0

    def ablauf(self):
        r, s = self.richtung, self.s
        h = lambda d, u: Pose(arm_v=-70 + 30 * math.sin(u * 22), arm_v_x=14, blick_y=0.2)  # noqa: E731

        def malen(sz, u, von, bis, dauer):
            sz.ei.bemalt = von + (bis - von) * min(1.0, u / dauer)
            sz.hase.pinsel = EI_FARBEN[(min(2, int(sz.ei.bemalt)) * 2) % len(EI_FARBEN)]
            sz.hase.pose = h(sz.hase, u)

        return [
            Mit('hase', Gehe(bis=self.vom_rand(0.1), tempo=0.55, haltung=schiebe)),
            Setze(schieben=False),
            Tu(lambda sz: setattr(sz, 'ei_dreh0', sz.ei.dreh % 360)),
            Jeweils(0.4, lambda sz, u: setattr(sz.ei, 'dreh', sz.ei_dreh0 + (360 - sz.ei_dreh0) * min(1, u / 0.4)
                                               if sz.ei_dreh0 > 180 else sz.ei_dreh0 * (1 - min(1, u / 0.4)))),
            Mit('hase', Stehe(0.4, Pose(kopf_vorn=True, auge_zu=True, mund_offen=True))),
            Mit('hase', Setze(pinsel=EI_FARBEN[0])),
            Jeweils(2.4, lambda sz, u: malen(sz, u, 0.0, 3.0, 2.4)),
            Jeweils(0.6, lambda sz, u: malen(sz, u, 3.0, 4.0, 0.6)),
            Mit('hase', Setze(pinsel=None)),
            Mit('hase', Stehe(0.9, lambda d, u: Pose(kopf_vorn=True, arm_v=-160, arm_h=-155, mund_offen=True,
                                                     auge_zu=0.5 < u < 0.65))),
            Jeweils(1.0, lambda sz, u: setattr(sz.ei, 'dreh', 14 * math.sin(u * 16) * u)),
            Mit('hase', Setze(pose=Pose(kopf_vorn=True, sorge=1.0, schreck=0.5, arm_v=-160, arm_h=-155))),
            Warte(0.3),
            Tu(lambda sz: sz.rollen(r * 110 * s, 0.9)),
            Mit('hase', Erschrecke(0.3, 30)),
            Mit('hase', Hoppel(bis=lambda d: d.sz.ei_x - r * 140 * s, tempo=1.0, hoehe=22)),
            Mit('hase', Stehe(0.4, Pose(blick_x=1, sorge=0.6))),
            Tu(lambda sz: sz.rollen(None, 1.3)),
            Mit('hase', Stehe(0.35, Pose(kopf_vorn=True, schreck=1.0, arm_v=-120, arm_h=-110))),
            WarteBis(lambda sz: sz.platt),
            Warte(0.6),
            Mit('hase', Wandel(0.18, stauchen=1.15)),
            Mit('hase', Kurz(0.12, stauchen=0.92)),
            Mit('hase', Setze(stauchen=1.0)),
            Mit('hase', Stehe(0.7, Pose(blick_y=1.0, sorge=0.8))),
            Mit('hase', Stehe(0.8, lambda d, u: Pose(kopf_vorn=True, auge_zu=0.25 < u < 0.38 or 0.5 < u < 0.63))),
            Mit('hase', Setze(richtung=-r)),
            Mit('hase', Hoppel(tempo=1.0, hoehe=24)),
        ]

    def rollen(self, dx, dauer):
        """Ei rollt um dx (None: hinaus zum Rand, an dem die Szene beginnt)."""
        ziel = self.aussen(-self.richtung) if dx is None else self.ei_x + dx
        self.nebenbei.append((Wandel(dauer, ei_x=ziel), self.t))
        self.nebenbei[-1][0].beginn(self)

    def weiter(self, dt):
        e, h = self.ei, self.hase
        if self.schieben:
            self.ei_x = h.x + h.richtung * (28 * h.s + e.r)
        alt = e.x
        e.x = self.ei_x
        if e.x != alt:
            e.dreh += math.degrees((e.x - alt) / (e.r * 1.1))
        abstand = abs(e.x - h.x)
        if not self.platt and not self.schieben and abstand < 20 * self.s and self.ei.bemalt >= 4:
            self.platt = True
            h.stauchen = 0.28
            h.streifen = True
            h.pose = Pose(auge_zu=True, sorge=1.0)
            self.streue(h.x, self.boden - 10 * self.s, 10, WEISS, tempo=120, dauer=0.5, r=(3, 7))
        uber = max(0.0, 1 - abstand / (e.r * 1.4)) if self.platt else 0.0
        e.y = self.boden - e.r - uber * 22 * self.s
        if self.platt and h.stauchen < 0.5:
            h.pose = Pose(auge_zu=True, sorge=1.0)

    def zeichne_vorn(self, p):
        self.ei.zeichne(p)

    def grenzen_extra(self):
        return self.ei.kasten()

    def schreck_ablauf(self):
        self.nebenbei.clear()
        e = self.ei
        e.flucht = 0.0
        ziel = self.aussen(-1 if e.x < self.geo.center().x() else 1)
        self.platt = True
        neu = [Nebenbei(Wandel(0.9, ei_x=ziel))]
        h = self.hase
        h.stauchen = 1.0
        if h.figur_sichtbar():
            neu += [Nebenbei(Mit('hase', Erschrecke(0.3, 50)), Mit('hase', Setze(richtung=h.naechster_rand())),
                             Mit('hase', Hoppel(tempo=3.5, hoehe=30)))]
        else:
            h.zeige_figur = False
        return neu + [WarteBis(lambda sz: not sz.nebenbei)]
