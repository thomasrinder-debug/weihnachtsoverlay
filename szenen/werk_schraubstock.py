import math
import random

from PyQt6.QtCore import QRectF

from zeichnen.figur import Pose
from zeichnen.grundlagen import glatt
from zeichnen.figuren import WichtelSteif
from zeichnen.werkstatt import zeichne_bartstrang, zeichne_kiste, zeichne_schraubstock, zeichne_werkbank

from .basis import Erschrecke, Nebenbei, Renne, WarteNebenbei, Gehe, Jeweils, Mit, Schritt, Setze, Springe, Stehe, Szene, Tu, Warte, muetze_richten
from .werk_basis import STAUB, Blick, hand, schweiss, verpuffen, welt

WG = 0.6
BANK_B, BANK_H = 120, 90
WANNE_B, WANNE_H = 120, 50
BART = (22, -132)          # Bartspitze in Einheiten der Figur


def bart_an(sz, gx, gy):
    """Beugt den Weihnachtsmann so weit vor, dass seine Bartspitze bei (gx, gy) ist."""
    lo, hi = -40.0, 70.0
    for _ in range(18):
        mitte = (lo + hi) / 2
        sz.neigung = mitte
        if welt(sz, *BART)[1] < gy:
            lo = mitte
        else:
            hi = mitte
    bx, _ = welt(sz, *BART)
    sz.x += gx - bx


class Schraubstock(Szene):
    """Der Weihnachtsmann beugt sich neugierig über den Schraubstock, der Wichtel kurbelt eifrig zu,
    und der Bart steckt fest. Der Wichtel will aufdrehen: es klemmt, er hängt sich mit ganzem
    Gewicht an den Knebel, stemmt die Füße gegen; der Weihnachtsmann lehnt sich zurück, der Bart wird
    lang und länger. Pause. Dann springt der Schraubstock auf, der Weihnachtsmann fliegt rückwärts
    in die Spielzeugwanne und rollt darin aus dem Bild."""
    name, titel, reihenfolge = 'werk_schraubstock', 'Bart im Schraubstock', 907

    def vorbereiten(self):
        r, s = self.richtung, self.s
        self.r0 = r
        self.xb = self.vom_rand(0.2)
        self.oben_bank = self.boden - BANK_H * s
        self.vx = self.xb - r * 8 * s
        self.spalt, self.kurbel, self.vwackeln = 30.0, 0.0, 0.0
        self.xw = self.xb - r * 160 * s
        self.wanne_drall = 0.0
        self.in_wanne = False
        self.klemmt = False
        self.weg = False
        self.x = self.aussen(-r) - r * 40 * s
        self.pose_fest = {'sack': False}
        self.w = self.dazu('w', WichtelSteif, groesse=WG, knick=1.0)
        self.w.richtung = r
        self.w.tempo = self.tempo * 1.8

    def spalt_mitte(self):
        r, s = self.r0, self.s
        return self.vx + r * (self.spalt / 2) * s, self.oben_bank - 26 * s

    def knebel(self):
        r, s = self.r0, self.s
        return self.vx + r * (self.spalt + 34) * s, self.oben_bank - 21 * s

    def ablauf(self):
        r, s = self.r0, self.s
        w_platz = lambda sz: sz.knebel()[0] + r * 22 * s  # noqa: E731

        def kurbeln(sz, u, tempo=1.0, klemmt=False, haengen=0.0, stemmen=0.0):
            w = sz.w
            z = math.sin(u * 14 * tempo)
            if not klemmt:
                sz.kurbel += 0.4 * tempo
            else:
                sz.kurbel += 0.03 * z
                sz.vwackeln = 0.5
            w.richtung = -r
            w.pose = Pose(arm_v=-80 + 40 * z * (not klemmt), arm_h=-70 + 40 * z * (not klemmt),
                          kopf_vorn=klemmt, sorge=1.0 if klemmt else 0.0, mund_offen=klemmt,
                          bein_v=-60 * stemmen, bein_h=-50 * stemmen + 20 * haengen,
                          blick_y=0.5 if not klemmt else 0.0)
            w.x = w_platz(sz) + r * 6 * s * haengen - r * 10 * s * stemmen
            w.y = sz.oben_bank
            w.hopp = 14 * s * haengen * (0.8 + 0.2 * abs(math.sin(u * 12)))
            w.neigung = -25 * stemmen - 10 * haengen * math.sin(u * 10)
            if klemmt and random.random() < 0.1:
                schweiss(sz, w.x, w.y - 150 * WG * s)

        def beugen(sz, u):
            f = glatt(u / 0.5)
            sz.pose = Pose(sack=False, arm_v=-30, arm_h=-20, blick_y=0.8, auge_zu=False)
            x0, n0 = getattr(sz, '_b0', (sz.x, sz.neigung))
            sz.x = x0
            bart_an(sz, *sz.spalt_mitte())
            sz.x = x0 + (sz.x - x0) * f
            sz.neigung = n0 + (sz.neigung - n0) * f

        def zu(sz, u):
            kurbeln(sz, u, 1.6)
            sz.spalt = max(4.0, 30 - 30 * u / 0.6)
            beugen(sz, 1.0)
            if sz.spalt < 8:
                sz.pose = Pose(sack=False, arm_v=-60, arm_h=-40, kopf_vorn=True, schreck=1.0, mund_offen=True)

        def ruck(sz, u):
            k = math.sin(min(1.0, u / 0.35) * math.pi)
            beugen(sz, 1.0)
            sz.neigung -= 12 * k
            gx, gy = sz.spalt_mitte()
            sz.pose = Pose(sack=False, arm_v=-120, arm_h=-100, kopf_vorn=True, schreck=1.0, sorge=1.0,
                           mund_offen=True)
            sz.striche = k > 0.2
            sz.w.pose = Pose(arm_v=-60, arm_h=-50, kopf_vorn=True, schreck=0.6, blick_y=-0.3)

        class Zug(Schritt):
            """Er lehnt sich zurück, die Bartspitze bleibt im Schraubstock."""

            def __init__(self, weg, neigung, dauer, pause=False):
                self.weg, self.n, self.dauer, self.pause = weg, neigung, dauer, pause

            def beginn(self, sz):
                self.w0, self.n0 = sz.zugweg, sz.neigung

            def weiter(self, sz, u, dt):
                g = min(1.0, u / min(self.dauer, 0.5))
                sz.zugweg = self.w0 + (self.weg - self.w0) * g
                sz.neigung = self.n0 + (self.n - self.n0) * g
                sz.x = sz.stand_x - r * sz.zugweg * s
                if self.pause:
                    sz.pose = Pose(sack=False, arm_v=-20, arm_h=-10, kopf_vorn=True, sorge=0.6,
                                   auge_zu=0.3 < u < 0.45, bein_v=-30, bein_h=26)
                else:
                    z = math.sin(sz.t * 14)
                    sz.pose = Pose(sack=False, arm_v=-150 + 20 * z, arm_h=-140 - 20 * z, kopf_vorn=True,
                                   sorge=1.0, mund_offen=True, bein_v=-34, bein_h=30, hub=-2 * abs(z))

        def stand_merken(sz):
            sz.stand_x, sz.zugweg = sz.x, 0.0

        class Flug(Schritt):
            dauer = 0.5

            def beginn(self, sz):
                self.x0, self.y0 = sz.x, sz.y
                self.x1, self.y1 = sz.xw, sz.boden + 30 * s
                self.n0 = sz.neigung
                sz.klemmt = False
                sz.striche = True
                sz.streue(*sz.spalt_mitte(), 10, STAUB, tempo=120, dauer=0.5)

            def weiter(self, sz, u, dt):
                f = min(1.0, u / self.dauer)
                sz.x = self.x0 + (self.x1 - self.x0) * f
                sz.y = self.y0 + (self.y1 - self.y0) * f - 110 * s * 4 * f * (1 - f)
                sz.neigung = self.n0 + (-40 - self.n0) * f - 25 * math.sin(f * math.pi)
                sz.pose = Pose(sack=False, arm_v=-170, arm_h=-160, bein_v=-90 * f, bein_h=-70 * f,
                               kopf_vorn=True, schreck=1.0, mund_offen=True)
                sz.spalt = min(46.0, sz.spalt + 400 * dt)
                sz.kurbel += 1.2

            def ende(self, sz):
                sz.in_wanne = True
                sz.striche = False
                sz.streue(sz.xw, sz.boden - WANNE_H * s, 12, STAUB, tempo=110, dauer=0.6)

        def w_umfallen(sz, u):
            w = sz.w
            f = math.sin(min(1.0, u / 0.5) * math.pi)
            w.neigung = 30 * f
            w.hopp = 20 * s * f
            w.striche = u < 0.4
            w.pose = Pose(arm_v=-170, arm_h=-160, kopf_vorn=True, schreck=1.0, mund_offen=True)

        def wanne_wackelt(sz, u):
            sz.pose = Pose(sack=False, arm_v=-170 + 30 * math.sin(u * 20), arm_h=-150, bein_v=-100 + 20 * math.sin(u * 17),
                           bein_h=-85, kopf_vorn=True, auge_zu=u > 0.4, sorge=0.5)

        return [
            Nebenbei(Mit('w', Gehe(bis=lambda d: w_platz(d.sz) - r * 30 * s)),
                     Mit('w', Springe(nach=lambda d: (w_platz(d.sz), d.sz.oben_bank), dauer=0.4, hoehe=60)),
                     Mit('w', Setze(richtung=-r))),
            Gehe(bis=lambda sz: sz.vx - r * 95 * s, tempo=1.5),
            WarteNebenbei(),
            Tu(lambda sz: setattr(sz, '_b0', (sz.x, sz.neigung))),
            Jeweils(0.5, beugen),
            Tu(lambda sz: setattr(sz, '_b0', (sz.x, 0.0))),
            Jeweils(0.6, zu),
            Setze(klemmt=True),
            Jeweils(0.4, ruck),
            Setze(striche=False),
            Tu(stand_merken),
            Jeweils(0.8, lambda sz, u: (kurbeln(sz, u, klemmt=True), beugen(sz, 1.0),
                                        setattr(sz.pose, 'sorge', 0.8), setattr(sz.pose, 'kopf_vorn', True))),
            Nebenbei_w(0.9, lambda sz, u: kurbeln(sz, u, klemmt=True, haengen=1.0)),
            Zug(40, -2, 0.9),
            Nebenbei_w(1.0, lambda sz, u: kurbeln(sz, u, klemmt=True, stemmen=1.0)),
            Zug(80, -16, 1.0),
            Zug(80, -16, 0.7, pause=True),
            Flug(),
            Nebenbei_w(0.7, w_umfallen),
            Jeweils(0.5, wanne_wackelt),
            WanneRollt(2.2),
            Mit('w', Setze(neigung=0.0, hopp=0.0, striche=False)),
            *muetze_richten('w', 1.2),
            Mit('w', Springe(nach=lambda d: (d.sz.xb - r * 75 * s, d.sz.boden), dauer=0.4, hoehe=40)),
            Mit('w', Gehe(bis=None, tempo=1.2)),
            Tu(lambda sz: sz.aufraeumen()),
            Warte(0.6),
        ]

    def aufraeumen(self):
        verpuffen(self, self.xb, self.boden, BANK_B * self.s, BANK_H * self.s, 16)
        self.weg = True
        self.klemmt = False

    def schreck_ablauf(self):
        self.nebenbei.clear()
        self.klemmt = False
        self.striche = False
        if self.in_wanne:
            self.aufraeumen()
            w = self.w
            neu = []
            if w.zeige_figur and w.figur_sichtbar():
                w.y, w.neigung, w.hopp = self.boden, 0.0, 0.0
                neu.append(Nebenbei(Mit('w', Erschrecke(0.3, 40)), Mit('w', Renne(zum='rand'))))
            else:
                w.zeige_figur = False
            return neu + [WanneRollt(5.0), Setze(zeige_figur=False), WarteNebenbei(), Warte(0.6)]
        self.neigung, self.hopp, self.y = 0.0, 0.0, self.boden
        w = self.w
        w.y, w.neigung, w.hopp = self.boden, 0.0, 0.0
        self.aufraeumen()
        return self.schreck_alle()

    def weiter(self, dt):
        self.vwackeln = max(0.0, self.vwackeln - dt * 2)

    def zeichne_hinten(self, p):
        if self.weg:
            return
        s, r = self.s, self.r0
        p.save()
        p.translate(self.xb, self.boden)
        p.scale(r * s, s)
        zeichne_werkbank(p, BANK_B, BANK_H)
        p.restore()
        p.save()
        p.translate(self.vx, self.oben_bank)
        p.scale(r * s, s)
        zeichne_schraubstock(p, self.spalt, self.kurbel, self.vwackeln)
        p.restore()

    def zeichne_vorn(self, p):
        s, r = self.s, self.r0
        if self.klemmt and self.zeige_figur:
            bx, by = welt(self, *BART)
            gx, gy = self.spalt_mitte()
            if math.hypot(gx - bx, gy - by) > 2 * s:
                zeichne_bartstrang(p, bx, by, gx, gy, 7 * s)
        if self.in_wanne or not self.weg:
            p.save()
            p.translate(self.xw, self.boden)
            p.scale(r * s, s)
            zeichne_kiste(p, WANNE_B, WANNE_H, None, raeder=True, drall=self.wanne_drall)
            p.restore()

    def grenzen_extra(self):
        s = self.s
        k = QRectF(self.xw - 70 * s, self.boden - 70 * s, 140 * s, 72 * s)
        if not self.weg:
            k = k.united(QRectF(self.xb - 70 * s, self.boden - (BANK_H + 60) * s, 140 * s, (BANK_H + 62) * s))
            vx = self.vx + self.r0 * (self.spalt + 34) * s
            k = k.united(QRectF(min(self.vx, vx) - 30 * s, self.oben_bank - 70 * s, abs(vx - self.vx) + 60 * s, 70 * s))
        if self.zeige_figur and abs(self.neigung) > 15:
            k = k.united(QRectF(self.x - 280 * s, self.y - self.hopp - 300 * s, 560 * s, 330 * s))
        return k


class Nebenbei_w(Schritt):
    """Lässt eine Funktion eine Weile im Hintergrund laufen und geht sofort weiter."""

    def __init__(self, dauer, funktion):
        self.dauer_n, self.funktion = dauer, funktion

    def beginn(self, sz):
        from .basis import Jeweils, Nebenbei
        Nebenbei(Jeweils(self.dauer_n, self.funktion)).beginn(sz)


class WanneRollt(Schritt):
    """Die Spielzeugwanne rollt mit ihm zum Rand hinaus."""

    def __init__(self, tempo):
        self.tempo = tempo

    def weiter(self, sz, u, dt):
        s = sz.s
        seite = -1 if sz.xw - sz.geo.left() < sz.geo.right() - sz.xw else 1
        v = sz.tempo * self.tempo * min(1.0, 0.3 + u * 2)
        sz.xw += seite * v * dt
        sz.wanne_drall += seite * v * dt / (9 * s)
        if sz.in_wanne:
            sz.x += seite * v * dt
            sz.hopp = abs(math.sin(u * 16)) * 3 * s

    def fertig(self, sz, u):
        s = sz.s
        aus = not QRectF(sz.xw - 70 * s, sz.boden - 70 * s, 140 * s, 72 * s).intersects(sz.geo)
        return aus and (not sz.in_wanne or not sz.figur_sichtbar())
