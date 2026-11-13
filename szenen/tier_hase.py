import math

from zeichnen.figur import Pose
from zeichnen.tiere import Schneehase

from .basis import (Ducke, Erschrecke, Gehe, Hoppel, Mit, Nebenbei, Renne, Setze, Stehe, Szene, Tu, Wandel,
                    WarteNebenbei)
from .tier_gemeinsam import Flug, figur_mit_beinen, publikumsblick, puff, sterne

SITZ = 58          # Fußpunkt unter dem Boden, wenn er auf dem Boden sitzt (Einheiten)
HASE_G = 0.95


class Sitzplatz(Szene):
    """Müde sucht er einen Sitzplatz und setzt sich auf einen Schneehaufen – der ist ein
    Schneehase und hoppelt weg, er plumpst auf den Hosenboden. Beim zweiten Mal springt der Hase
    über ihn hinweg. Beim dritten Mal hält er den Haufen mit beiden Händen fest und setzt sich
    triumphierend darauf. Pause. Dann macht der Hase einen gewaltigen Satz und schleudert ihn in
    einen Rückwärtssalto."""
    name, titel, reihenfolge = 'tier_hase', 'Sitzplatz', 750

    def vorbereiten(self):
        r = self.richtung
        self.x = self.aussen(-r)
        self.hx0 = self.vom_rand(0.2)
        self.h = self.dazu('h', Schneehase, groesse=HASE_G, haufen=1.0, sprung=0.0)
        self.h.x, self.h.richtung = self.hx0, r

    def zeichne_figur(self, p, zwischen=None):
        figur_mit_beinen(self, p)

    def hinsetzen(self, x, y, dauer=0.3):
        return [Ducke(0.2), Setze(pose=Pose(sitzt=True, mund_offen=True)),
                Flug((x, y), dauer, hoehe=-10, pose=Pose(sitzt=True, mund_offen=True))]

    def hasensprung(self, nach, hoehe=70, dauer=0.45, richtung=None):
        r = richtung if richtung is not None else (1 if nach > self.h.x else -1)
        return [Mit('h', Setze(haufen=0.0, richtung=r)),
                Mit('h', Flug((nach, self.boden), dauer, hoehe=hoehe, pose=Pose(bein_v=40))),
                Mit('h', Setze(pose=Pose())),
                Tu(lambda sz: puff(sz, sz.h.x, sz.boden, 6, 60)),
                Mit('h', Wandel(0.2, haufen=1.0))]

    def plumps(self, staerke=1.0):
        return [Setze(y=self.boden + SITZ * self.s, pose=Pose(sitzt=True, schreck=0.7, kopf_vorn=True)),
                Tu(lambda sz: puff(sz, sz.x, sz.boden, int(12 * staerke), 140 * staerke)),
                Wandel(0.07, stauchen=0.75), Wandel(0.15, stauchen=1.0)]

    def aufstehen(self):
        return [Setze(y=self.boden, pose=Pose(), stauchen=1.0)]

    def ablauf(self):
        r, s = self.richtung, self.s
        h0 = self.hx0
        h1 = h0 - r * 150 * s
        h2 = h1 + r * 260 * s
        muede = lambda pose, sz: Pose(**{**pose.__dict__, 'sorge': 0.6})  # noqa: E731
        stolz = lambda sz, u: Pose(sitzt=True, kopf_vorn=True, arm_v=-120, arm_h=-110, arm_v_x=24,  # noqa: E731
                                    auge_zu=0.3 < u < 0.42 or 0.7 < u < 0.82)
        return [
            Gehe(bis=h0 + r * 46 * s, tempo=1.0, haltung=muede),
            Stehe(0.25, Pose(arm_v=-160, arm_v_x=18, auge_zu=True, sorge=0.6)),
            # 1. Versuch
            *self.hinsetzen(h0 + r * 6 * s, self.boden - 10 * s, 0.2),
            Nebenbei(*self.hasensprung(h1)),
            Setze(pose=Pose(sitzt=True, schreck=1.0)),
            Wandel(0.2, y=self.boden + SITZ * s),
            *self.plumps(),
            publikumsblick(None, 0.5, sitzt=True, sorge=0.8),
            # 2. Versuch: der Hase springt über ihn hinweg
            *self.aufstehen(),
            Gehe(bis=h1 + r * 46 * s, tempo=1.4),
            Setze(richtung=r),
            *self.hinsetzen(h1 + r * 6 * s, self.boden - 10 * s, 0.15),
            Nebenbei(*self.hasensprung(h2, hoehe=230, dauer=0.7)),
            Setze(pose=Pose(sitzt=True, schreck=1.0, blick_y=-1.0)),
            Wandel(0.18, y=self.boden + SITZ * s),
            *self.plumps(1.5),
            Stehe(0.35, Pose(sitzt=True, sorge=1.0, blick_x=1.0)),
            # 3. Versuch: festhalten und draufsetzen
            *self.aufstehen(),
            Gehe(bis=h2 - r * 70 * s, tempo=1.5),
            Setze(richtung=r),
            Stehe(0.4, lambda sz, u: Pose(arm_v=-30 + 10 * math.sin(u * 20), arm_h=-35, arm_v_x=22, hub=4,
                                          sorge=0.3)),
            Setze(richtung=-r),
            *self.hinsetzen(h2, self.boden - 4 * s, 0.45),
            Stehe(0.9, stolz),
            Mit('h', Setze(haufen=0.0)),
            Stehe(0.35, lambda sz, u: Pose(sitzt=True, schreck=1.0, kopf_vorn=True, blick_y=0.9)),
            # Riesensatz, Rückwärtssalto
            Nebenbei(*self.hasensprung(h0 - r * 60 * s, hoehe=120, dauer=0.7, richtung=-r)),
            Flug((h2 + r * 40 * s, self.boden + SITZ * s), 0.85, hoehe=230, neigung=360,
                 pose=Pose(sitzt=True, schreck=1.0, arm_v=-150, arm_h=-140)),
            Setze(neigung=0.0),
            *self.plumps(1.6),
            Tu(lambda sz: sterne(sz, sz.x, sz.y - 250 * sz.s)),
            Stehe(0.4, Pose(sitzt=True, auge_zu=True, sorge=1.0)),
            publikumsblick(None, 0.8, sitzt=True, sorge=0.5),
            Mit('h', Setze(haufen=0.0, richtung=-r)),
            Nebenbei(Mit('h', Hoppel(tempo=1.6, hoehe=30))),
            *self.aufstehen(),
            Setze(richtung=-r),
            Gehe(tempo=1.8, haltung=muede),
            WarteNebenbei(),
        ]

    def schreck_ablauf(self):
        self.nebenbei.clear()
        neu = []
        h = self.h
        if h.figur_sichtbar():
            h.haufen, h.y = 0.0, self.boden
            neu.append(Nebenbei(Mit('h', Setze(richtung=h.naechster_rand(), pose=Pose(schreck=1.0))),
                                Mit('h', Hoppel(tempo=3.5, hoehe=34))))
        else:
            h.zeige_figur = False
        if self.figur_sichtbar():
            self.y, self.neigung, self.stauchen = self.boden, 0.0, 1.0
            return neu + [Erschrecke(0.35, 40), Renne(zum='rand'), WarteNebenbei()]
        self.zeige_figur = False
        return neu + [WarteNebenbei()]
