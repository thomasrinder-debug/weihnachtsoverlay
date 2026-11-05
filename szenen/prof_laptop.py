import math
import random

from PyQt6.QtCore import QPointF, QRectF
from PyQt6.QtGui import QColor

from zeichnen.figur import Pose
from zeichnen.grundlagen import blinzeln, glatt
from zeichnen.labor import zeichne_labortisch
from zeichnen.labor_e import zeichne_kappe, zeichne_laptop, zeichne_laptop_klein

from .basis import Gehe, Jeweils, Nebenbei, Schaue, Schritt, Setze, Stehe, Tu, Wandel
from .professor import FUNKEN, RAUCH, ProfSzene, Zurueck, triumph_pose, ziehen


# ---------------------------------------------------------------- gemeinsam für die Computer-Szenen

QUALM = [QColor(150, 150, 160, 210), QColor(115, 112, 118, 200), QColor(190, 190, 198, 200)]


def hieb_funken(sz, x, y, staerke=1.0):
    """Wirkung eines Faustschlags auf ein Gerät: Funken, Qualm, das Gerät wackelt."""
    sz.streue(x, y, int(10 * staerke), FUNKEN, tempo=280, dauer=0.5, r=(3, 6), art='stern')
    sz.streue(x, y - 6 * sz.s, int(6 * staerke), RAUCH, tempo=50, dauer=1.0, r=(6, 13),
              richtung=-math.pi / 2, streuung=0.8)
    sz.wackel = 1.0


def qualm(sz, x, y, dichte=0.25):
    """Für Jeweils: steigender Qualm aus einem Gerät."""
    if random.random() < dichte:
        sz.streue(x + random.uniform(-6, 6) * sz.s, y, 1, QUALM, tempo=85, dauer=1.5, r=(7, 17),
                  richtung=-math.pi / 2, streuung=0.4)


class Hieb(Schritt):
    """Holt weit über den Kopf aus und haut mit der Faust auf ziel(sz) -> Weltpunkt;
    beim Aufprall Funken und wirkung(sz)."""

    def __init__(self, ziel, wirkung=None, aushol=0.5, nach=0.45, staerke=1.0):
        self.ziel, self.wirkung, self.aushol, self.staerke = ziel, wirkung, aushol, staerke
        self.dauer = aushol + 0.07 + nach

    def beginn(self, sz):
        self.getroffen = False
        self.n0 = sz.neigung

    def weiter(self, sz, u, dt):
        x, y = self.ziel(sz)
        a = sz.arm_zu(x, y)
        if u < self.aushol:
            f = glatt(u / self.aushol)
            sz.neigung = self.n0 - 8 * f
            sz.pose = Pose(arm_v=-40 - 150 * f, arm_h=20 + 10 * f, bein_v=-16, bein_h=12, sorge=0.7 * f,
                           blick_y=0.3, wipp=-4 * f)
            return
        f = min(1.0, (u - self.aushol) / 0.07)
        sz.neigung = self.n0 - 8 + 14 * f
        sz.pose = Pose(arm_v=-190 + (a + 190) * f, arm_h=40, bein_v=-16, bein_h=12, mund_offen=True,
                       auge_zu=f >= 1, wipp=8 * f)
        if f >= 1 and not self.getroffen:
            self.getroffen = True
            hieb_funken(sz, x, y, self.staerke)
            if self.wirkung:
                self.wirkung(sz)

    def ende(self, sz):
        sz.neigung = self.n0


class GeraetSzene(ProfSzene):
    """Gemeinsames der Computer-Szenen: wackel klingt nach einem Hieb ab."""
    wackel = 0.0

    def weiter(self, dt):
        super().weiter(dt)
        self.wackel = max(0.0, self.wackel - dt * 2.2)

    def zitter(self):
        return math.sin(self.t * 60) * 3 * self.wackel * self.s


# ---------------------------------------------------------------- Szene

G = 1.35                 # Laptop etwas größer gezeichnet, damit die Pointe lesbar bleibt
TISCH_H = 80
RAND_L, RAND_R = (-20, -199), (24, -199)     # Mützenrand am Kopf, Figur-Einheiten
BOMMEL = (-30, -226)


class Laptop(GeraetSzene):
    """Der Laptop zeigt einen Fehler, der Professor haut drauf. Er beugt sich zum Schirm,
    der Deckel schnappt zu und hält die Bommel fest. Er zieht und zieht, kommt frei,
    und nun trägt der Laptop seine Mütze. Erleichterte Triumph-Pose."""
    name, titel, reihenfolge = 'laptop', 'Mützenfänger', 87

    def vorbereiten(self):
        r = self.seite = self.richtung
        self.tisch_x = self.vom_rand(0.14)
        self.deckel = 0.0
        self.bild = 0.0
        self.fehler = 0.0
        self.kaputt = 0.0
        self.kappe = 'kopf'      # kopf, frei, klemmt, fliegt, laptop
        self.haengen = 0.0       # 0: Bommel hinten, 1: hängt auf die Tastatur
        self.flug = 0.0
        self.stand = self.tisch_x - r * 104 * self.s

    # -- Orte

    def laptop_ort(self):
        return self.tisch_x + self.seite * 6 * self.s + self.zitter(), self.boden - (TISCH_H + 8) * self.s

    def am_laptop(self, lx, ly):
        x, y = self.laptop_ort()
        return x + lx * G * self.s, y + ly * G * self.s

    def am_kopf(self, punkt):
        q = self.trafo().map(QPointF(*punkt))
        return q.x(), q.y()

    def kappe_punkte(self):
        """(links, rechts, bommel) der Mütze in Weltkoordinaten."""
        kl, kr = self.am_kopf(RAND_L), self.am_kopf(RAND_R)
        hinten = self.am_kopf(BOMMEL)
        ziel_l = self.am_laptop(-14, -66)
        ziel_r = self.am_laptop(14, -68)
        ziel_b = self.am_laptop(-30, -86)
        klemm = self.am_laptop(4, -1)
        if self.kappe == 'frei':
            h = glatt(self.haengen)
            tasten = self.am_laptop(4, -12)
            b = (hinten[0] + (tasten[0] - hinten[0]) * h, hinten[1] + (tasten[1] - hinten[1]) * h)
            return kl, kr, b
        if self.kappe == 'klemmt':
            return kl, kr, klemm
        if self.kappe == 'fliegt':
            f = glatt(self.flug)
            bogen = -60 * self.s * math.sin(f * math.pi)

            def misch(a, b):
                return a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f + bogen

            return misch(kl, ziel_l), misch(kr, ziel_r), misch(klemm, ziel_b)
        return ziel_l, ziel_r, ziel_b

    # -- Zeichnen

    def zeichne_requisiten(self, p):
        p.save()
        p.translate(self.tisch_x, self.boden)
        p.scale(self.s, self.s)
        zeichne_labortisch(p, 130, TISCH_H)
        p.restore()
        p.save()
        p.translate(*self.laptop_ort())
        p.scale(G * self.s, G * self.s)
        zeichne_laptop(p, 0, 0, self.deckel, self.bild, self.t, self.fehler, self.kaputt)
        p.restore()
        if self.kappe == 'klemmt' and self.zeige_figur:
            _, _, b = self.kappe_punkte()
            zeichne_kappe(p, b, b, b, self.s * 1.12, teile='b')
            p.save()
            p.translate(*self.laptop_ort())
            p.scale(G * self.s, G * self.s)
            zeichne_laptop(p, 0, 0, self.deckel, nur_deckel=True)
            p.restore()

    def zeichne_davor(self, p):
        if self.kappe == 'kopf' or (self.kappe in ('frei', 'klemmt') and not self.zeige_figur):
            return
        l, r, b = self.kappe_punkte()
        if self.kappe in ('frei', 'klemmt'):
            # der Zipfel läuft im Bogen vor dem Gesicht vorbei
            zug = self.am_kopf((70, -250))
            zeichne_kappe(p, l, r, b, self.s * 1.12, teile='kr', zug=zug)
        elif self.kappe == 'fliegt':
            f = glatt(self.flug)
            a, z = self.am_kopf((70, -250)), self.am_laptop(-10, -110)
            zug = (a[0] + (z[0] - a[0]) * f, a[1] + (z[1] - a[1]) * f)
            zeichne_kappe(p, l, r, b, self.s * 1.12, zug=zug)
        else:
            zeichne_kappe(p, l, r, b, self.s * 1.12)

    def requisiten_kasten(self):
        s = self.s
        k = QRectF(self.tisch_x - 72 * s, self.boden - (TISCH_H + 8 + 70 * G) * s, 144 * s, (TISCH_H + 8 + 70 * G) * s)
        if self.kappe != 'kopf':
            for x, y in self.kappe_punkte():
                k = k.united(QRectF(x - 30 * s, y - 30 * s, 60 * s, 60 * s))
        return k

    # -- Ablauf

    def ablauf(self):
        r, s = self.richtung, self.s
        self.x = self.aussen(-r)

        def deckel_auf(sz, u):
            sz.deckel = glatt(u / 0.6)
            sz.pose = Pose(arm_v=sz.arm_zu(*sz.am_laptop(0, -14 - 52 * sz.deckel)), auge_zu=blinzeln(sz.t))
            if u > 0.5:
                sz.bild = min(1.0, (u - 0.5) * 3)

        def tippen(schnell):
            def f(sz, u):
                tx, ty = sz.am_laptop(0, -8)
                w = 8 * math.sin(u * (34 if schnell else 18))
                sz.pose = Pose(arm_v=sz.arm_zu(tx, ty) + w, arm_h=sz.arm_zu(tx, ty) - w - 10, blick_y=0.35,
                               sorge=0.7 if schnell else 0.0, auge_zu=blinzeln(sz.t),
                               mund_offen=schnell and (u * 6) % 2 < 1)
            return f

        def getroffen(sz):
            sz.kaputt, sz.fehler, sz.bild = 0.7, 0.0, 0.7
            sz.haare = 0.25

        def ziehen_fn(sz, u):
            ruck = abs(math.sin(u * 7.5))
            sz.neigung = 34 - 20 * min(1.0, u / 1.6) - 10 * ruck
            sz.x = self.stand - r * (8 + 18 * min(1.0, u / 1.6) + 6 * ruck) * s
            kx, ky = sz.am_kopf((4, -215))
            sz.pose = Pose(arm_v=-165 + 10 * ruck, arm_h=-150 + 10 * ruck, arm_v_x=8, bein_v=-24, bein_h=20,
                           sorge=1.0, auge_zu=ruck > 0.8, mund_offen=ruck > 0.5, blick_y=0.2)
            sz.wackel = max(sz.wackel, 0.35 * ruck)

        def frei(sz):
            sz.kappe = 'fliegt'
            sz.flug = 0.0
            sz.haare = 0.9
            sz.striche = True
            x, y = sz.am_laptop(4, -1)
            sz.streue(x, y, 8, FUNKEN, tempo=200, dauer=0.5, r=(3, 6), art='stern')

        return [
            Gehe(bis=self.stand),
            Stehe(0.3),
            Setze(neigung=14),
            Jeweils(0.9, deckel_auf),
            Jeweils(1.6, tippen(False)),
            Setze(fehler=1.0),
            Stehe(0.5, lambda sz, u: Pose(arm_v=-60, arm_h=-50, schreck=0.6, sorge=0.6, blick_y=0.3)),
            Jeweils(1.0, tippen(True)),
            Setze(neigung=0),
            Schaue(0.9),
            Setze(richtung=r),
            Hieb(lambda sz: sz.am_laptop(0, -66), getroffen),
            Stehe(0.5, lambda sz, u: Pose(arm_v=-40, blick_y=0.3, auge_zu=blinzeln(sz.t))),
            # neugierig ganz nah an den Schirm
            Setze(kappe='frei', muetze=False),
            Wandel(0.7, neigung=36, haengen=1.0, x=self.stand + r * 4 * s),
            Stehe(1.0, lambda sz, u: Pose(arm_v=-20, arm_h=20, blick_y=0.6, auge_zu=blinzeln(sz.t),
                                          hub=2 * math.sin(u * 3))),
            Wandel(0.07, deckel=0.0),
            Setze(kappe='klemmt', striche=True, bild=0.0, wackel=1.0),
            Stehe(0.5, lambda sz, u: Pose(schreck=1.0, sorge=0.6, arm_v=-120, arm_h=-110, arm_v_x=16)),
            Setze(striche=False),
            Jeweils(1.8, ziehen_fn),
            Tu(frei),
            Nebenbei(Wandel(0.12, deckel=1.0), Wandel(0.45, flug=1.0), Setze(kappe='laptop', bild=0.6)),
            Wandel(0.01, neigung=0),
            Zurueck(45, 0.45),
            Setze(striche=False),
            Stehe(0.6, lambda sz, u: Pose(sorge=1.0, blick_y=0.2, auge_zu=blinzeln(sz.t))),
            Wandel(0.8, haare=0.45),
            Setze(richtung=-r),
            Stehe(1.6, lambda sz, u: triumph_pose(sz, u)),
            Setze(richtung=r),
            Stehe(0.9, lambda sz, u: Pose(arm_v=-150, arm_v_x=12, blick_y=-0.2, auge_zu=blinzeln(sz.t))),
            Stehe(0.5, lambda sz, u: Pose(kopf_vorn=True, auge_zu=True)),
            Setze(mitnehmen=('tisch_x',)),
            Gehe(bis=self.aussen(-r) - r * 280 * s, haltung=ziehen),
        ]

    def schreck_ablauf(self):
        mit_kappe = self.kappe in ('laptop', 'fliegt')
        if not mit_kappe:
            self.muetze = True
        neu = self.schreck_rennen()
        if self.zeige_figur:
            self.halt = lambda p, hx, hy: zeichne_laptop_klein(p, 12, -116, -8, mit_kappe)
        return neu
