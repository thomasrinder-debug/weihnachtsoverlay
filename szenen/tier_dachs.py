import math

from PyQt6.QtCore import QRectF

from zeichnen.figur import Pose
from zeichnen.grundlagen import KEIN_STIFT, blinzeln
from zeichnen.requisiten import zeichne_muetze_lose, zeichne_schneehaufen
from zeichnen.tiere import Dachs

from .basis import (Erschrecke, Falle, Gehe, Jeweils, Mit, Renne, Setze, Springe, Stehe, Szene, Tu,
                    Wandel, Warte, WarteNebenbei, Nebenbei)
from .tier_gemeinsam import figur_mit_beinen, puff, sterne

SITZ = 58          # Fußpunkt unter dem Boden, wenn er sitzt (Einheiten)


class Huegel(Szene):
    """Ein Schneehügel wandert unter der Schneedecke heran und taucht zwischen seinen Stiefeln
    auf. Er hüpft beiseite, der Hügel folgt; noch einmal, er folgt wieder. Breitbeinig bleibt er
    stehen – da wächst der Hügel unter ihm zur Säule und hebt ihn im Spagat hoch. Oben ein Blick
    ins Publikum, dann ist der Hügel weg und er klappt auf den Hosenboden. Neben ihm schaut ein
    Dachs heraus, mit seiner Mütze auf dem Kopf."""
    name, titel, reihenfolge = 'tier_dachs', 'Dachs im Untergrund', 740

    def vorbereiten(self):
        r = self.richtung
        self.x = self.aussen(-r)
        self.hx = self.aussen(-r)
        self.hh = 0.0
        self.hmuetze = False
        self.reiten = False
        self.spreiz = 0.0
        self.da = self.dazu('da', Dachs, groesse=1.1, vorn=True, muetze=False)
        self.da.zeige_figur = False

    def weiter(self, dt):
        if self.reiten:
            self.y = self.boden - self.hh * 0.98 * self.s

    def zeichne_figur(self, p, zwischen=None):
        figur_mit_beinen(self, p, spreiz=self.spreiz)

    def ablauf(self):
        r, s = self.richtung, self.s
        x0 = self.vom_rand(0.13)
        x1, x2 = x0 + r * 85 * s, x0 + r * 170 * s
        bang = lambda sz, u: Pose(blick_y=0.9, sorge=0.8, auge_zu=blinzeln(sz.t))  # noqa: E731
        breit = Pose(bein_v=-24, bein_h=24, arm_v=25, arm_h=25, kopf_vorn=True, blick_y=0.2)
        spagat = lambda sz, u: Pose(bein_v=-75, bein_h=75, arm_v=-120 + 30 * math.sin(u * 20),  # noqa: E731
                                     arm_h=-100 - 30 * math.sin(u * 20), schreck=1.0, kopf_vorn=True)
        return [
            Nebenbei(Wandel(0.6, hh=22.0)),
            Gehe(bis=x0, tempo=1.0),
            Stehe(0.2),
            Wandel(0.45, hx=x0),
            Wandel(0.12, hh=62.0),
            # 1. beiseite
            Erschrecke(0.25, 30),
            Springe((x1, self.boden), 0.4, 70),
            Wandel(0.1, hh=22.0),
            Stehe(0.35, bang),
            Wandel(0.35, hx=x1),
            Wandel(0.1, hh=62.0),
            # 2. noch einmal
            Erschrecke(0.2, 30),
            Springe((x2, self.boden), 0.4, 80),
            Wandel(0.1, hh=22.0),
            Setze(richtung=-r),
            Stehe(0.3, bang),
            # 3. breitbeinig stehen bleiben
            Setze(pose=breit),
            Wandel(0.3, hx=x2),
            Stehe(0.35, breit),
            Setze(reiten=True),
            Wandel(0.85, hh=185.0, spreiz=0.0),
            Jeweils(0.5, spagat),
            Stehe(0.6, lambda sz, u: Pose(bein_v=-75, bein_h=75, kopf_vorn=True, sorge=1.0,
                                          auge_zu=0.3 < u < 0.42)),
            # der Hügel ist weg
            Tu(lambda sz: puff(sz, sz.hx, sz.boden - 80 * sz.s, 30, 200, (8, 16))),
            Setze(hh=0.0, reiten=False),
            Stehe(0.15, Pose(bein_v=-75, bein_h=75, kopf_vorn=True, schreck=1.0)),
            Falle(lambda sz: sz.y >= sz.boden + SITZ * sz.s),
            Setze(y=self.boden + SITZ * s, pose=Pose(sitzt=True, kopf_vorn=True, schreck=0.6),
                  pose_fest={'muetze': False}),
            Tu(lambda sz: sz.gelandet()),
            Wandel(0.08, stauchen=0.7),
            Wandel(0.15, stauchen=1.0),
            Stehe(0.5, Pose(sitzt=True, auge_zu=True, sorge=1.0)),
            # der Dachs mit der Mütze
            Mit('da', Setze(zeige_figur=True, muetze=True, richtung=r, x=x2 - r * 235 * s,
                            y=self.boden + 70 * s)),
            Mit('da', Wandel(0.25, y=self.boden + 12 * s)),
            Tu(lambda sz: puff(sz, sz.da.x, sz.boden, 8, 80)),
            Stehe(0.1, Pose(sitzt=True, sorge=1.0)),
            Mit('da', Stehe(0.5, lambda d, u: Pose(blick_x=-1.0))),
            Setze(pose=Pose(sitzt=True, kopf_vorn=True, blick_x=-r * 0.9, sorge=0.6)),
            Mit('da', Stehe(0.6, lambda d, u: Pose(kopf_vorn=True, auge_zu=0.25 < u < 0.37))),
            Mit('da', Wandel(0.2, y=self.boden + 90 * s)),
            Mit('da', Setze(zeige_figur=False)),
            Setze(hx=x2 - r * 235 * s, hh=30.0, hmuetze=True),
            Nebenbei(Wandel(1.0, hx=self.aussen(-r))),
            Setze(pose=Pose(sitzt=True, kopf_vorn=True, schreck=0.8)),
            Warte(0.3),
            Setze(y=self.boden, richtung=-r),
            Erschrecke(0.25, 25),
            Renne(zum='weiter', tempo=2.8),
            WarteNebenbei(),
        ]

    def gelandet(self):
        puff(self, self.x, self.boden, 18, 160)
        sterne(self, self.x, self.boden - 180 * self.s)

    def schreck_ablauf(self):
        self.nebenbei.clear()
        self.reiten = False
        neu = []
        if self.da.zeige_figur:
            neu.append(Nebenbei(Mit('da', Wandel(0.2, y=self.boden + 90 * self.s)),
                                Mit('da', Setze(zeige_figur=False))))
        neu.append(Nebenbei(Wandel(0.3, hh=0.0)))
        if self.figur_sichtbar():
            self.y = self.boden
            self.pose = Pose()
            self.stauchen = 1.0
            return neu + [Erschrecke(0.35, 40), Renne(zum='rand'), WarteNebenbei()]
        self.zeige_figur = False
        return neu + [WarteNebenbei()]

    def zeichne_hinten(self, p):
        if self.hh <= 0.5:
            return
        p.save()
        p.translate(self.hx, self.boden)
        p.scale(self.s, self.s)
        p.setPen(KEIN_STIFT)
        b = 80 + self.hh * 0.55
        zeichne_schneehaufen(p, 0, 2, b, self.hh)
        if self.hmuetze:
            p.translate(0, -self.hh + 6)
            p.rotate(-12 + 6 * math.sin(self.t * 12))
            p.scale(0.6, 0.6)
            zeichne_muetze_lose(p)
        p.restore()

    def zeichne_vorn(self, p):
        if not self.da.zeige_figur:
            return
        p.save()
        p.setPen(KEIN_STIFT)
        zeichne_schneehaufen(p, self.da.x, self.boden + 2, 150 * self.s, 26 * self.s)
        p.restore()

    def grenzen_extra(self):
        k = QRectF()
        if self.hh > 0.5:
            b = (60 + self.hh * 0.3) * self.s
            k = QRectF(self.hx - b, self.boden - (self.hh + 30) * self.s, 2 * b, (self.hh + 30) * self.s)
        if self.pose.sitzt:
            k = k.united(QRectF(self.x - 130 * self.s, self.y - 290 * self.s, 260 * self.s, 290 * self.s))
        return k
