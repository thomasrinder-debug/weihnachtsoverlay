import math

from zeichnen.figur import Pose
from zeichnen.grundlagen import KEIN_STIFT, blinzeln
from zeichnen.requisiten import zeichne_schneehaufen
from zeichnen.tiere import Fuchs, zeichne_fuchsbein, zeichne_fuchskopf, zeichne_fuchsschwanz

from PyQt6.QtCore import QRectF

from .basis import Gehe, Jeweils, Mit, Schritt, Setze, Stehe, Szene, Tu, Wandel, Warte, WarteNebenbei
from .tier_gemeinsam import Flug, publikumsblick, puff

WEHE_B, WEHE_H = 290, 100       # Einheiten
NASE = (76, 112)               # Schnauzenspitze bei Neigung 100, vom Fußpunkt aus


class Wandern(Schritt):
    """Die Schneewehe läuft auf Fuchsbeinen zum Rand hinaus."""

    def __init__(self, tempo=1.2):
        self.tempo = tempo

    def weiter(self, sz, u, dt):
        v = sz.tempo * self.tempo
        sz.wx += sz.wdir * v * dt
        sz.wphase += v * dt / (sz.s * 26)

    def fertig(self, sz, u):
        return not sz.wehe_kasten().intersects(sz.geo)


class Maeuselsprung(Szene):
    """Der Fuchs lauscht an einer Schneewehe und springt kopfüber hinein: erst steckt nur die
    Schnauze, dann der halbe Fuchs mit strampelnden Beinen. Beim dritten Mal holt er weit aus,
    hängt im Scheitel kurz in der Luft und taucht ganz ein. Dann steht die Wehe auf vier
    Fuchsbeinen auf, schaut ins Publikum und marschiert davon."""
    name, titel, reihenfolge = 'tier_fuchs', 'Mäuselsprung', 700

    def vorbereiten(self):
        self.zeige_figur = False
        r = self.richtung
        self.wx = self.vom_rand(0.17)
        self.wdir = -r
        self.wphase = 0.0
        self.wandernd = False
        self.gesicht = 0.0
        self.deck = 1.0
        self.lift = 0.0
        self.f = self.dazu('f', Fuchs, lauer=0.0, schnee=0.0)
        self.f.richtung = r
        self.stand = self.wx - r * (WEHE_B / 2 + 108) * self.s

    def ziel(self, vorn, tief):
        """Fußpunkt, damit die Schnauze 'vorn' Einheiten hinter dem Wehenrand 'tief' unter der Kuppe steckt."""
        r, s = self.richtung, self.s
        nx = self.wx - r * (WEHE_B / 2 - vorn) * s
        ny = self.boden - (WEHE_H - tief) * s
        return nx - r * NASE[0] * s, ny - NASE[1] * s

    def ablauf(self):
        r, s = self.richtung, self.s
        lausch = lambda d, u: Pose(blick_x=0.4, blick_y=0.6, auge_zu=blinzeln(d.t))  # noqa: E731
        sprung = lambda d, f: Pose(bein_v=-40, bein_h=40, mund_offen=True)  # noqa: E731
        strampeln = lambda sz, u: setattr(sz.f, 'pose', Pose(bein_v=45 * math.sin(u * 28),  # noqa: E731
                                                              bein_h=-45 * math.sin(u * 28)))
        raus = Pose(schreck=0.6, bein_v=-30, bein_h=30)
        return [
            Mit('f', Gehe(bis=self.stand, tempo=1.4)),
            Mit('f', Setze(pose=Pose())),
            Mit('f', Wandel(0.25, lauer=1.0)),
            Mit('f', Stehe(0.55, lausch)),
            # 1. Sprung: nur die Schnauze
            Mit('f', Flug(lambda d: self.ziel(125, 40), 0.55, hoehe=90, neigung=100, pose=sprung)),
            Tu(lambda sz: puff(sz, *sz.schnauze(), 8, 70)),
            Mit('f', Setze(lauer=0.0)),
            Mit('f', Stehe(0.3, Pose(bein_v=-10, bein_h=10))),
            Mit('f', Flug((self.stand, self.boden), 0.4, hoehe=40, neigung=0, pose=raus)),
            Mit('f', Setze(schnee=1.0)),
            Mit('f', Jeweils(0.45, lambda d, u: setattr(d, 'neigung', 6 * math.sin(u * 40)))),
            Tu(lambda sz: puff(sz, *sz.kopf_punkt(), 10, 120, (3, 6))),
            Mit('f', Setze(schnee=0.0, neigung=0.0)),
            Mit('f', Stehe(0.35, Pose(kopf_vorn=True, sorge=0.6))),
            # 2. Sprung: bis zur Hüfte
            Mit('f', Wandel(0.2, lauer=1.0)),
            Mit('f', Flug(lambda d: self.ziel(135, 120), 0.6, hoehe=150, neigung=100, pose=sprung)),
            Tu(lambda sz: puff(sz, *sz.schnauze(), 14, 120)),
            Mit('f', Setze(lauer=0.0)),
            Jeweils(0.8, strampeln),
            Mit('f', Flug((self.stand, self.boden), 0.45, hoehe=70, neigung=-360, pose=raus)),
            Mit('f', Setze(neigung=0.0, schnee=1.0)),
            Mit('f', Stehe(0.25, Pose(schreck=0.3))),
            Mit('f', Setze(schnee=0.6)),
            publikumsblick('f', 0.6, sorge=0.8),
            Mit('f', Setze(schnee=0.0)),
            # 3. Sprung: Anlauf, Hängen im Scheitel, ganz hinein
            Mit('f', Wandel(0.35, lauer=1.0)),
            Mit('f', Setze(lauer=0.0)),
            Mit('f', Flug(lambda d: (self.wx - r * NASE[0] * s * 0.6, self.boden - 40 * s), 0.8, hoehe=300,
                          neigung=100, haengen=0.55,
                          pose=lambda d, f: Pose(kopf_vorn=True, sorge=1.0, bein_v=-50, bein_h=50)
                          if f == 0.5 else Pose(bein_v=-40, bein_h=40, mund_offen=True))),
            Mit('f', Setze(zeige_figur=False)),
            Tu(lambda sz: puff(sz, sz.wx, sz.boden - WEHE_H * sz.s, 26, 200, (6, 14))),
            Warte(0.45),
            Wandel(0.3, lift=46.0),
            Setze(wandernd=True),
            Wandel(0.35, gesicht=1.0),
            Warte(0.6),
            Tu(lambda sz: puff(sz, sz.wx + sz.wdir * (WEHE_B / 2 + 30) * sz.s, sz.boden - 70 * sz.s, 8, 90)),
            Warte(0.2),
            Wandern(1.7),
        ]

    def schnauze(self):
        f = self.f
        p = f.trafo().map(__import__('PyQt6.QtCore', fromlist=['QPointF']).QPointF(98, -95))
        return p.x(), p.y()

    def kopf_punkt(self):
        f = self.f
        p = f.trafo().map(__import__('PyQt6.QtCore', fromlist=['QPointF']).QPointF(70, -96))
        return p.x(), p.y()

    def schreck_ablauf(self):
        self.nebenbei.clear()
        if self.wandernd or not self.f.zeige_figur:
            self.wandernd = True
            self.f.zeige_figur = False
            self.gesicht = 0.0
            self.wdir = -1 if self.wx - self.geo.left() < self.geo.right() - self.wx else 1
            return [Wandel(0.12, lift=40.0), Wandern(4.5)]
        f = self.f
        f.neigung, f.lauer = 0.0, 0.0
        f.y = self.boden
        return self.schreck_alle(weihnachtsmann=False)[:-2] + [Wandel(0.3, deck=0.0), WarteNebenbei()]

    # -- Zeichnen

    def wehe_kasten(self):
        s = self.s
        b = (WEHE_B / 2 + 110) * s
        return QRectF(self.wx - b, self.boden - (WEHE_H + self.lift + 60) * s, 2 * b, (WEHE_H + self.lift + 60) * s)

    def _wehe_trafo(self, p):
        p.translate(self.wx, self.boden)
        p.scale(self.s * self.wdir, self.s)

    def zeichne_hinten(self, p):
        if not self.wandernd:
            return
        p.save()
        p.setOpacity(self.deck)
        self._wehe_trafo(p)
        p.setPen(KEIN_STIFT)
        zeichne_fuchsschwanz(p, -WEHE_B / 2 + 16, -self.lift - 28, math.sin(self.t * 5) * 8, 0.6)
        ph = self.wphase
        for dx, k in ((-70, 0), (40, 1), (-50, 2), (60, 3)):
            zeichne_fuchsbein(p, dx, -48, 30 * math.sin(ph + k * math.pi / 2 + (k > 1) * math.pi), k < 2)
        p.restore()

    def zeichne_vorn(self, p):
        p.save()
        p.setOpacity(self.deck)
        self._wehe_trafo(p)
        p.setPen(KEIN_STIFT)
        zeichne_schneehaufen(p, 0, -self.lift + 4, WEHE_B, WEHE_H + (8 if self.lift else 0))
        if self.gesicht > 0:
            u = self.t
            pose = Pose(kopf_vorn=True, blick_x=0.0, auge_zu=(u % 1.6) < 0.12)
            zeichne_fuchskopf(p, WEHE_B / 2 - 30 + 26 * self.gesicht, -self.lift - 46, pose, 1.0)
        p.restore()

    def grenzen_extra(self):
        return self.wehe_kasten()
