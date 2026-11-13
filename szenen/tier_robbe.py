import math

from PyQt6.QtCore import QRectF
from PyQt6.QtGui import QColor

from zeichnen.figur import Pose
from zeichnen.grundlagen import KEIN_STIFT, blinzeln
from zeichnen.tiere import Robbe, zeichne_eisloch_hinten, zeichne_eisloch_vorn

from .basis import Gleite, Jeweils, Mit, Setze, Stehe, Szene, Tu, Wandel, Warte, WarteNebenbei
from .tier_gemeinsam import Flug, puff

LOCH_B = 150       # Einheiten
TIEF = 25          # Fußpunkt der Robbe unter der Bildkante, Einheiten
LIEGT = 46         # Fußpunkt über dem Boden, wenn sie liegt
EIS = [QColor(235, 248, 255, 240), QColor(180, 215, 245, 230)]
WASSER = [QColor(120, 175, 225, 220), QColor(200, 230, 255, 220)]


class Korken(Szene):
    """Eine Robbe taucht im Eisloch auf, da friert das Loch um sie herum zu. Flossen stemmen,
    Zappeln, schließlich zieht sie sich lang wie eine Ziehharmonika, hält kurz inne – und schießt
    wie ein Sektkorken heraus, wirbelt durch die Luft und rutscht auf dem Bauch davon. Dann
    rutscht sie rückwärts genau wieder ins Loch, steckt so fest wie vorher und verschränkt
    beleidigt die Flossen."""
    name, titel, reihenfolge = 'tier_robbe', 'Robbe als Korken', 720

    def vorbereiten(self):
        self.zeige_figur = False
        self.hx = self.vom_rand(0.13)
        self.rand = 0.0
        self.deck = 0.0
        self.drin = True
        self.rb = self.dazu('rb', Robbe, groesse=1.35, zieh=1.0, flosse=0.0, verschraenkt=False, schwanz=False)
        self.rb.x, self.rb.y = self.hx, self.boden + 280 * self.s
        self.rb.richtung = self.richtung

    def unten(self):
        return self.boden + TIEF * self.s

    def ablauf(self):
        r, s = self.richtung, self.s
        x1 = self.hx + r * self.geo.width() * 0.13
        froh = lambda d, u: Pose(mund_offen=0.2 < u < 0.5, auge_zu=blinzeln(d.t), blick_x=math.sin(u * 3))  # noqa: E731
        stemmen = lambda d, u: (setattr(d, 'y', self.unten() - 4 * s * abs(math.sin(u * 22))),  # noqa: E731
                                setattr(d, 'pose', Pose(sorge=1.0, mund_offen=True)))
        zappeln = lambda d, u: (setattr(d, 'neigung', 14 * math.sin(u * 20)),  # noqa: E731
                                setattr(d, 'flosse', 40 * math.sin(u * 30)),
                                setattr(d, 'pose', Pose(sorge=1.0, schreck=0.4)))
        ziehen = lambda d, u: (setattr(d, 'neigung', 2 * math.sin(u * 50)),  # noqa: E731
                               setattr(d, 'pose', Pose(auge_zu=True, sorge=1.0)))
        return [
            Wandel(0.3, deck=1.0),
            Mit('rb', Wandel(0.35, y=self.unten())),
            Tu(lambda sz: sz.spritzer()),
            Mit('rb', Stehe(0.6, froh)),
            # das Loch friert zu
            Tu(lambda sz: sz.knistern()),
            Wandel(0.7, rand=1.0),
            Mit('rb', Stehe(0.35, Pose(blick_y=1.0, schreck=0.7))),
            # 1. Flossen stemmen
            Mit('rb', Setze(flosse=-75.0)),
            Mit('rb', Jeweils(0.6, stemmen)),
            Mit('rb', Setze(flosse=0.0, y=self.unten())),
            # 2. Zappeln
            Mit('rb', Jeweils(0.7, zappeln)),
            Mit('rb', Setze(neigung=0.0, flosse=0.0)),
            # 3. Ziehharmonika, Pause, Plopp
            Mit('rb', Wandel(0.8, zieh=1.9)),
            Mit('rb', Jeweils(0.25, ziehen)),
            Mit('rb', Setze(neigung=0.0)),
            Mit('rb', Stehe(0.55, lambda d, u: Pose(blick_y=0.3, auge_zu=0.25 < u < 0.35))),
            Mit('rb', Wandel(0.07, zieh=1.0)),
            Setze(drin=False),
            Mit('rb', Setze(schwanz=True)),
            Tu(lambda sz: sz.plopp()),
            Mit('rb', Flug((x1, self.boden - LIEGT * s), 0.9, hoehe=230, neigung=450,
                           pose=Pose(schreck=1.0))),
            Mit('rb', Setze(neigung=90.0)),
            Tu(lambda sz: puff(sz, sz.rb.x, sz.boden, 14, 150)),
            Mit('rb', Gleite(x1 + r * 100 * s, 0.6, Pose(schreck=0.5))),
            Mit('rb', Stehe(0.45, Pose(auge_zu=True))),
            # rückwärts zurück ins Loch
            Mit('rb', Gleite(self.hx + r * 40 * s, 0.85,
                             lambda d, u: Pose(schreck=1.0, blick_x=-r))),
            Mit('rb', Setze(flosse=0.0)),
            Mit('rb', Flug((self.hx, self.unten()), 0.25, hoehe=20, neigung=0.0, pose=Pose(schreck=1.0))),
            Mit('rb', Setze(schwanz=False)),
            Setze(drin=True),
            Tu(lambda sz: sz.spritzer()),
            Mit('rb', Stehe(0.3, Pose(schreck=0.4))),
            Mit('rb', Setze(verschraenkt=True)),
            Mit('rb', Stehe(1.3, lambda d, u: Pose(sorge=-0.9, auge_zu=0.5 < u < 0.62, blick_x=0.6 * (u > 0.7)))),
            # das Eis bricht, sie versinkt würdevoll
            Tu(lambda sz: sz.knistern(18)),
            Wandel(0.2, rand=0.0),
            Mit('rb', Wandel(0.6, y=self.boden + 290 * s)),
            Tu(lambda sz: sz.spritzer()),
            Wandel(0.3, deck=0.0),
        ]

    def spritzer(self):
        self.streue(self.hx, self.boden - 6 * self.s, 14, WASSER, tempo=170, dauer=0.6, r=(2, 5), schwer=True,
                    richtung=-math.pi / 2, streuung=0.9)

    def knistern(self, n=10):
        self.streue(self.hx, self.boden - 8 * self.s, n, EIS, tempo=90, dauer=0.5, r=(1.5, 3.5), schwer=True,
                    richtung=-math.pi / 2, streuung=1.3)

    def plopp(self):
        puff(self, self.hx, self.boden - 20 * self.s, 18, 220, (5, 12))
        self.spritzer()

    def schreck_ablauf(self):
        self.nebenbei.clear()
        rb = self.rb
        if self.drin or not rb.figur_sichtbar():
            return [Mit('rb', Setze(pose=Pose(schreck=1.0), zieh=1.0, neigung=0.0, verschraenkt=False)),
                    Wandel(0.12, rand=0.0),
                    Mit('rb', Wandel(0.35, y=self.boden + 300 * self.s)),
                    Tu(lambda sz: sz.spritzer()),
                    Wandel(0.25, deck=0.0), WarteNebenbei()]
        seite = rb.naechster_rand()
        return [Mit('rb', Setze(pose=Pose(schreck=1.0), neigung=90.0, richtung=seite, y=self.boden - LIEGT * self.s,
                                schwanz=True)),
                Mit('rb', Gleite(self.aussen(seite), 0.9, Pose(schreck=1.0))),
                Wandel(0.15, deck=0.0)]

    def zeichne_hinten(self, p):
        p.save()
        p.setOpacity(self.deck)
        p.translate(self.hx, self.boden)
        p.scale(self.s, self.s)
        p.setPen(KEIN_STIFT)
        zeichne_eisloch_hinten(p, LOCH_B)
        p.restore()

    def zeichne_vorn(self, p):
        p.save()
        p.setOpacity(self.deck)
        p.translate(self.hx, self.boden)
        p.scale(self.s, self.s)
        p.setPen(KEIN_STIFT)
        zeichne_eisloch_vorn(p, LOCH_B, self.rand)
        p.restore()

    def grenzen_extra(self):
        b = (LOCH_B / 2 + 40) * self.s
        return QRectF(self.hx - b, self.boden - 40 * self.s, 2 * b, 40 * self.s)
