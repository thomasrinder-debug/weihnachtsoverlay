import math
import random

from PyQt6.QtCore import QRectF

from zeichnen.figur import Pose
from zeichnen.grundlagen import WEISS
from zeichnen.requisiten import zeichne_muetze_lose
from zeichnen.werkstatt import zeichne_aufziehmaus

from .basis import Erschrecke, Gehe, Jeweils, Nebenbei, Renne, Schritt, Setze, Szene, Tu, Wandel, Warte
from .werk_basis import STAUB, Blick, greife, haenge_an, schweiss, verpuffen

G = 1.7      # Größe der Maus


class Rasen(Schritt):
    """Die Maus rast los, bis sie aus dem Bild ist; mit_ihm: der Weihnachtsmann hängt am Schlüssel."""

    def __init__(self, seite=None, tempo=6.0, mit_ihm=False):
        self.seite_v, self.tempo, self.mit_ihm = seite, tempo, mit_ihm

    def beginn(self, sz):
        self.seite = self.seite_v if self.seite_v is not None else (
            -1 if sz.mx - sz.geo.left() < sz.geo.right() - sz.mx else 1)
        sz.mrichtung = self.seite

    def weiter(self, sz, u, dt):
        s = sz.s
        v = sz.tempo * self.tempo * min(1.0, 0.25 + u * 5)
        sz.mx += self.seite * v * dt
        sz.mtipp += 60 * dt
        sz.mzitt = 0.0
        sz.schl += 30 * dt
        if random.random() < 0.6:
            sz.streue(sz.mx - self.seite * 30 * s, sz.boden - 4 * s, 1, STAUB, tempo=40, dauer=0.5, r=(5, 10))
        if self.mit_ihm:
            sz.pose = Pose(sack=False, arm_v=-178, arm_h=-170, arm_v_x=16, bein_v=25 + 25 * math.sin(u * 30),
                           bein_h=40 - 25 * math.sin(u * 30), schreck=1.0, kopf_vorn=False, mund_offen=True,
                           wipp=8)
            sz.neigung = min(1.0, u / 0.08) * 84
            haenge_an(sz, *sz.schluessel_punkt())

    def fertig(self, sz, u):
        weg = not QRectF(sz.mx - 60 * sz.s, sz.boden - 80 * sz.s, 120 * sz.s, 80 * sz.s).intersects(sz.geo)
        return weg and (not self.mit_ihm or not sz.figur_sichtbar())


class Aufziehmaus(Szene):
    """Der Weihnachtsmann zieht eine Blechmaus auf; sie macht einen Hopser und kippt um. Er zieht
    sie wie verrückt auf, bis sie zittert, lässt los: nichts. Er beugt sich ganz nah heran und
    fasst den Schlüssel, da rast sie los und zieht ihn waagerecht wie einen Wasserskifahrer aus dem
    Bild. Die Mütze bleibt liegen; die Maus kommt zurück, setzt sie sich auf und fährt davon."""
    name, titel, reihenfolge = 'werk_maus', 'Aufziehmaus', 901

    def vorbereiten(self):
        r, s = self.richtung, self.s
        self.mx = self.vom_rand(0.2)
        self.mrichtung = -r
        self.mdreh, self.schl, self.mtipp, self.mzitt = 0.0, 0.0, 0.0, 0.0
        self.mhut, self.hut, self.maus_da = False, None, True
        self.x = self.aussen(-r)
        self.pose = Pose(sack=False)
        self.pose_fest = {'sack': False}

    def schluessel_punkt(self):
        return self.mx + self.mrichtung * -6 * self.s * G, self.boden - 50 * self.s * G

    def ablauf(self):
        r, s = self.richtung, self.s
        ziel = self.vom_rand(0.2) + r * 120 * s

        def ohne_sack(pose, sz):
            pose.sack = False
            return pose

        def buecken(sz, u, tief=26, aufziehen=0.0):
            f = min(1.0, u / 0.3)
            z = math.sin(sz.t * (10 + 30 * aufziehen))
            sz.pose = Pose(sack=False, arm_h=-30, bein_v=-8, bein_h=10, kopf_vorn=False, blick_y=0.6,
                           hub=aufziehen * 2.5 * z, sorge=aufziehen * 0.5, mund_offen=aufziehen > 0.6)
            greife(sz, *sz.schluessel_punkt(), neigung=tief * f)
            sz.pose.arm_v += 10 * z * (aufziehen > 0)
            if aufziehen:
                sz.schl += (0.15 + 0.9 * aufziehen) * (1 + z) * 0.5
                sz.mzitt = min(1.0, aufziehen * u / 1.4)
                sz.mtipp += 0.3
                if aufziehen > 0.5 and random.random() < 0.12:
                    schweiss(sz, *self_kopf(sz))

        def self_kopf(sz):
            from .werk_basis import welt
            return welt(sz, 10, -230)

        def aufrichten(sz, u):
            f = min(1.0, u / 0.25)
            sz.neigung *= (1 - f)
            sz.pose = Pose(sack=False, arm_v=-20 * (1 - f), kopf_vorn=False, blick_y=0.5)

        def hopser_kippt(sz, u):
            sz.mtipp += 0.2
            if u < 0.25:
                sz.mx += sz.mrichtung * 30 * s * (1 / 60) * 4
                sz.mdreh = 0.0
            else:
                f = min(1.0, (u - 0.25) / 0.3)
                sz.mdreh = -sz.mrichtung * 170 * f * f
            sz.pose = Pose(sack=False, kopf_vorn=u > 0.6, blick_y=0.4, sorge=0.5 if u > 0.6 else 0.0)

        def aufstellen(sz, u):
            buecken(sz, u, 30)
            sz.mdreh = sz.mdreh * (1 - min(1.0, u / 0.4))

        def nah_ran(sz, u):
            f = min(1.0, u / 0.5)
            sz.pose = Pose(sack=False, arm_h=-20, bein_v=-14, bein_h=14, blick_y=0.7, sorge=0.3,
                           auge_zu=0.9 < u < 1.0)
            greife(sz, *sz.schluessel_punkt(), neigung=30 + 18 * f)
            if 1.05 < u < 1.15:
                sz.mzitt = 0.4
                sz.mtipp += 1
            else:
                sz.mzitt = 0.0

        def hut_faellt(sz):
            from .werk_basis import welt
            x, y = welt(sz, 8, -210)
            sz.hut = {'x': x, 'y': y, 'vy': -120 * s, 'dreh': 0.0, 'liegt': False}
            sz.pose_fest = {'sack': False, 'muetze': False}

        return [
            Gehe(bis=ziel, tempo=1.8, haltung=ohne_sack),
            Setze(richtung=-r),
            Jeweils(0.35, lambda sz, u: buecken(sz, u)),
            Jeweils(0.5, lambda sz, u: buecken(sz, 1, aufziehen=0.3)),
            Jeweils(0.25, aufrichten),
            Jeweils(0.75, hopser_kippt),
            Blick(0.5, lambda sz, u: Pose(sack=False, kopf_vorn=True, sorge=0.5, auge_zu=0.2 < u < 0.32)),
            Jeweils(0.45, aufstellen),
            Jeweils(1.6, lambda sz, u: buecken(sz, u, 30, aufziehen=min(1.0, 0.3 + u / 1.2))),
            Jeweils(0.25, aufrichten),
            Setze(mzitt=0.0),
            Blick(0.8, lambda sz, u: Pose(sack=False, kopf_vorn=True, sorge=0.3, auge_zu=0.3 < u < 0.42)),
            Jeweils(1.3, nah_ran),
            Tu(hut_faellt),
            Rasen(-r, 3.8, mit_ihm=True),
            Setze(zeige_figur=False),
            Warte(0.7),
            Setze(mhut=False),
            ZurueckZumHut(),
            Warte(0.35),
            Setze(mhut=True, hut=None),
            Jeweils(0.4, lambda sz, u: setattr(sz, 'mzitt', 0.6)),
            Rasen(-r, 3.0),
        ]

    def schreck_ablauf(self):
        self.nebenbei.clear()
        neu = []
        if self.maus_da and QRectF(self.mx - 60 * self.s, self.boden - 80 * self.s, 120 * self.s,
                                   80 * self.s).intersects(self.geo):
            self.mdreh, self.mzitt = 0.0, 0.0
            neu.append(Nebenbei(Rasen(tempo=6.0)))
        if self.hut and self.hut['liegt']:
            verpuffen(self, self.hut['x'], self.hut['y'], 40 * self.s, 30 * self.s, 8)
            self.hut = None
        if self.zeige_figur and self.figur_sichtbar() and self.neigung < 60:
            self.neigung, self.hopp = 0.0, 0.0
            neu += [Erschrecke(0.35, 40), Renne(zum='rand')]
        elif self.neigung >= 60:
            neu.append(Rasen(-self.richtung, 6.5, mit_ihm=True))
        else:
            self.zeige_figur = False
        return neu + [Warte(0.05), WarteBisWeg()]

    def weiter(self, dt):
        h = self.hut
        if h and not h['liegt']:
            h['vy'] += 1300 * self.s * dt
            h['y'] += h['vy'] * dt
            h['dreh'] += 400 * dt
            if h['y'] >= self.boden - 2 * self.s:
                h.update(y=self.boden - 2 * self.s, liegt=True, dreh=0.0)
                self.streue(h['x'], self.boden, 6, STAUB, tempo=60, dauer=0.5)

    def zeichne_vorn(self, p):
        s = self.s
        if self.hut:
            p.save()
            p.translate(self.hut['x'], self.hut['y'])
            p.rotate(self.hut['dreh'])
            p.scale(s * -self.richtung, s)
            zeichne_muetze_lose(p)
            p.restore()
        if not self.maus_da:
            return
        p.save()
        p.translate(self.mx, self.boden - 20 * s * G)
        p.rotate(self.mdreh)
        p.translate(0, 20 * s * G)
        p.scale(self.mrichtung * s * G, s * G)
        zeichne_aufziehmaus(p, self.schl, self.mtipp, self.mzitt)
        if self.mhut:
            p.save()
            p.translate(2, -26)
            p.rotate(-8 + 4 * math.sin(self.t * 20))
            p.scale(-0.9, 0.9)
            zeichne_muetze_lose(p)
            p.restore()
        p.restore()

    def grenzen_extra(self):
        s = self.s
        k = QRectF(self.mx - 70 * s, self.boden - 110 * s, 140 * s, 112 * s)
        if self.hut:
            k = k.united(QRectF(self.hut['x'] - 60 * s, self.hut['y'] - 70 * s, 120 * s, 80 * s))
        if self.zeige_figur and self.neigung > 20:
            k = k.united(QRectF(self.x - 300 * s, self.y - self.hopp - 200 * s, 600 * s, 270 * s))
        return k


class ZurueckZumHut(Schritt):
    """Die Maus kommt allein zurück und hält genau unter der liegenden Mütze."""

    def beginn(self, sz):
        sz.mrichtung = sz.richtung

    def weiter(self, sz, u, dt):
        sz.mx += sz.richtung * sz.tempo * 4.5 * dt
        sz.mtipp += 1

    def fertig(self, sz, u):
        if (sz.mx - sz.hut['x']) * sz.richtung >= 0:
            sz.mx = sz.hut['x']
            return True
        return False


class WarteBisWeg(Schritt):
    def fertig(self, sz, u):
        return not sz.nebenbei and not sz.wolke and not sz.splitter
