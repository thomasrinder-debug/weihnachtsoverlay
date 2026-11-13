import math
import random

from PyQt6.QtCore import QRectF
from PyQt6.QtGui import QColor

from zeichnen.figur import Pose
from zeichnen.figuren import WichtelSteif
from zeichnen.grundlagen import WEISS
from zeichnen.werkstatt import zeichne_gleis, zeichne_lok, zeichne_wagen

from .basis import Gehe, Jeweils, Mit, Nebenbei, Schritt, Setze, Szene, Tu, Warte, muetze_richten
from .werk_basis import verpuffen

GZ = 1.5                                  # Größe der Bahn
ZUG = (('lok', 0), ('flach', -60), ('hoch', -124))
DAMPF = (QColor(240, 240, 245, 220), QColor(210, 215, 225, 200))


class Fahre(Schritt):
    """Der Zug fährt (vorwärts oder rückwärts) nach xt=ziel, gleichmäßig mit tempo."""

    def __init__(self, ziel, tempo):
        self.ziel_v, self.tempo = ziel, tempo

    def beginn(self, sz):
        self.ziel = self.ziel_v(sz) if callable(self.ziel_v) else self.ziel_v
        self.seite = 1 if self.ziel > sz.xt else -1

    def weiter(self, sz, u, dt):
        v = sz.tempo * self.tempo * min(1.0, 0.3 + u * 4)
        sz.xt += self.seite * v * dt
        sz.drall += self.seite * sz.richtung * v * dt / (7 * GZ * sz.s)
        if (sz.xt - self.ziel) * self.seite >= 0:
            sz.xt = self.ziel

    def fertig(self, sz, u):
        return sz.xt == self.ziel


class Hinaus(Schritt):
    """Der Zug fährt rückwärts aus dem Bild, der Wichtel thront oben drauf."""

    def __init__(self, tempo=2.2):
        self.tempo = tempo

    def weiter(self, sz, u, dt):
        v = sz.tempo * self.tempo * min(1.0, 0.2 + u * 2)
        sz.xt -= sz.richtung * v * dt
        sz.drall -= v * dt / (7 * GZ * sz.s)

    def fertig(self, sz, u):
        return not sz.zug_kasten().intersects(sz.geo) and not sz.w.figur_sichtbar()


class Holzbahn(Szene):
    """Ein Wichtel stellt sich breitbeinig über die Holzschiene; Lok und Flachwagen sausen unter
    ihm durch, er schaut stolz zwischen seinen Beinen hinab. Der hohe Güterwagen bleibt an ihm
    hängen. Zweimal ruckt der Zug, er zieht den Bauch ein und steht auf Zehenspitzen. Der Zug
    setzt zurück, dampft, nimmt Anlauf: Rums, der Wichtel sitzt oben auf dem Wagen, schaut
    beleidigt ins Publikum, richtet die Mütze und wird rückwärts hinausgefahren."""
    name, titel, reihenfolge = 'werk_bahn', 'Holzeisenbahn', 902

    def vorbereiten(self):
        self.zeige_figur = False
        r, s = self.richtung, self.s
        self.rand = self.geo.left() if r > 0 else self.geo.right()
        self.xw = self.vom_rand(0.2)
        self.xt = self.aussen(-r)
        self.drall, self.ruettel = 0.0, 0.0
        # Zugspitze, bei der die Vorderkante des hohen Wagens am Wichtel ansteht
        self.xt_stoss = self.xw - r * 12 * s + r * (124 - 30) * GZ * s
        self.weg = False
        self.wmodus = 'gehen'
        self.w = self.dazu('w', WichtelSteif, groesse=0.7, knick=1.0)
        self.w.richtung = r

    def wagen_x(self, versatz):
        return self.xt + self.richtung * versatz * GZ * self.s

    def dach_y(self):
        return self.boden - 64 * GZ * self.s

    def ablauf(self):
        r, s = self.richtung, self.s

        def stoss(sz, hoch=10):
            sz.ruettel = 1.0
            sz.streue(sz.xw, sz.boden - 40 * s, 5, WEISS, tempo=70, dauer=0.4, r=(3, 6))
            sz.w.striche = True
            sz.w.hopp = hoch * s

        def dampf(sz, u, staerke=1.0):
            sz.drall += 0.6 * staerke * r
            sz.ruettel = 0.5 * staerke
            if random.random() < 0.5 * staerke:
                x = sz.wagen_x(4)
                sz.streue(x, sz.boden - 46 * GZ * s, 1, DAMPF, tempo=60, dauer=0.8, r=(6, 12),
                          richtung=-math.pi / 2, streuung=0.5)

        def aufladen(sz):
            sz.wmodus = 'sitzt'
            sz.w.striche = True
            sz.streue(sz.xw, sz.dach_y(), 8, WEISS, tempo=90, dauer=0.5)

        return [
            Nebenbei(Mit('w', Gehe(bis=self.xw, tempo=1.5)), Setze(wmodus='spreiz'), Mit('w', Setze(richtung=-r))),
            Warte(0.45),
            Fahre(self.xt_stoss, 1.6),
            Tu(stoss),
            Setze(wmodus='zehen'),
            Warte(0.35),
            Mit('w', Setze(striche=False)),
            Fahre(self.xt_stoss - r * 30 * s, 0.6),
            Fahre(self.xt_stoss + r * 4 * s, 1.8),
            Tu(lambda sz: stoss(sz, 18)),
            Warte(0.3),
            Mit('w', Setze(striche=False)),
            Fahre(self.xt_stoss - r * 80 * s, 0.7),
            Setze(wmodus='bange'),
            Jeweils(1.2, lambda sz, u: dampf(sz, u, min(1.0, 0.3 + u))),
            Setze(ruettel=0.0),
            Fahre(self.xt_stoss, 3.5),
            Tu(aufladen),
            Fahre(self.xt_stoss + r * 70 * s, 2.0),
            Setze(ruettel=1.0),
            Mit('w', Setze(striche=False)),
            Warte(0.3),
            Setze(wmodus='beleidigt'),
            Warte(0.9),
            Setze(wmodus='richten'),
            *muetze_richten('w', 1.2),
            Setze(wmodus='sitzt'),
            Tu(lambda sz: sz.streue(sz.wagen_x(4), sz.boden - 46 * GZ * s, 6, DAMPF, tempo=80, dauer=0.8,
                                    r=(6, 12), richtung=-math.pi / 2, streuung=0.6)),
            Warte(0.3),
            Hinaus(),
            Tu(lambda sz: sz.aufraeumen()),
            Warte(0.6),
        ]

    def aufraeumen(self):
        s = self.s
        a, b = sorted((self.rand, self.xw + self.richtung * 170 * s))
        verpuffen(self, (a + b) / 2, self.boden, b - a, 12 * s, 14)
        self.weg = True

    def schreck_ablauf(self):
        self.nebenbei.clear()
        neu = []
        if self.wmodus in ('sitzt', 'beleidigt', 'richten'):
            self.w.striche = True
            return [Hinaus(5.0), Tu(lambda sz: sz.aufraeumen()), Warte(0.6)]
        if self.zug_kasten().intersects(self.geo):
            neu.append(Nebenbei(Hinaus(5.0)))
        self.wmodus = 'flieht'
        self.w.hopp, self.w.y = 0.0, self.boden
        return neu + [Tu(lambda sz: sz.aufraeumen())] + self.schreck_alle(weihnachtsmann=False)

    def weiter(self, dt):
        w, s, r = self.w, self.s, self.richtung
        self.ruettel = max(0.0, self.ruettel - dt * 2.5)
        m = self.wmodus
        if m in ('spreiz', 'zehen', 'bange'):
            lok_unter = abs(self.wagen_x(0) - self.xw) < 50 * s or abs(self.wagen_x(-60) - self.xw) < 40 * s
            hoch = {'spreiz': 0.0, 'zehen': 6.0, 'bange': 6.0}[m] * s
            if w.hopp > hoch:
                w.hopp = max(hoch, w.hopp - 60 * s * dt)
            else:
                w.hopp = hoch
            if m == 'spreiz':
                w.pose = Pose(bein_v=-24, bein_h=24, arm_v=-30, arm_h=-20, blick_y=0.8 if lok_unter else 0.0,
                              kopf_vorn=lok_unter, auge_zu=(self.t % 3.4) < 0.14)
                w.stauchen = 1.0
            else:
                z = math.sin(self.t * 25)
                w.pose = Pose(bein_v=-14, bein_h=14, arm_v=-165 + 8 * z, arm_h=-160 - 8 * z, kopf_vorn=True,
                              sorge=1.0, schreck=0.4 if m == 'bange' else 0.2, blick_y=-0.3 if m == 'zehen' else 0.0,
                              blick_x=-r * 0.6 if m == 'bange' and self.t % 1.0 < 0.5 else 0.0)
                w.stauchen = 1.07 + 0.01 * z
        elif m in ('sitzt', 'beleidigt', 'richten'):
            w.x = self.wagen_x(-124)
            w.y = self.dach_y() + 36 * s
            w.stauchen = 1.0
            w.hopp = abs(math.sin(self.t * 18)) * 3 * s * (self.ruettel > 0.05)
            if m == 'sitzt':
                w.pose = Pose(bein_v=-10, bein_h=10, arm_v=-140, arm_h=-130, mund_offen=True, kopf_vorn=True,
                              schreck=0.6 * self.ruettel)
            elif m == 'beleidigt':
                w.pose = Pose(bein_v=-6, bein_h=6, arm_v=-40, arm_h=-35, arm_v_x=-6, kopf_vorn=True,
                              auge_zu=self.t % 1.1 < 0.5, blick_y=-0.4)

    def zug_kasten(self):
        s, r = self.s, self.richtung
        a, b = sorted((self.xt + r * 36 * GZ * s, self.xt - r * 160 * GZ * s))
        return QRectF(a, self.boden - 70 * GZ * s, b - a, 70 * GZ * s)

    def zeichne_vorn(self, p):
        s, r = self.s, self.richtung
        if not self.weg:
            a, b = sorted((self.rand - r * 20 * s, self.xw + r * 170 * s))
            p.save()
            p.translate(a, self.boden)
            p.scale(s, s)
            zeichne_gleis(p, 0, (b - a) / s)
            p.restore()
        rt = self.ruettel
        for art, versatz in ZUG:
            x = self.wagen_x(versatz)
            p.save()
            p.translate(x + math.sin(self.t * 70 + versatz) * rt * 1.2 * s, self.boden - 7 * s)
            p.scale(r * s * GZ, s * GZ)
            if art == 'lok':
                zeichne_lok(p, self.drall)
            else:
                zeichne_wagen(p, self.drall, hoch=art == 'hoch')
            p.restore()

    def grenzen_extra(self):
        s, r = self.s, self.richtung
        k = self.zug_kasten().adjusted(-6 * s, -50 * s, 6 * s, 2 * s)
        if not self.weg:
            a, b = sorted((self.rand - r * 20 * s, self.xw + r * 170 * s))
            k = k.united(QRectF(a, self.boden - 10 * s, b - a, 10 * s))
        return k
