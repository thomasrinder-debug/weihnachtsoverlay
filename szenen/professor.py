"""Grundlage der Professor-Szenen: der Professor ist hier die Hauptfigur statt des
Weihnachtsmanns, alle Schritte aus basis.py laufen mit ihm. Requisiten zeichnet die
Szene in zeichne_requisiten(), ihren Umriss liefert requisiten_kasten(); beim Schreck
verschwinden sie mit weg() in einer Wolke.

Running Gags: die Triumph-Pose (Füße breit, beide Hände offen), genau dann geht
etwas schief; danach der trockene Blick ins Publikum (Publikumsblick) mit
Blinzeln und einem Hustwölkchen. Nach einem Knall qualmen Haare und Mütze weiter
(qualm), bis die Szene endet.
"""
import math
import random
from dataclasses import replace

from PyQt6.QtCore import QPointF, QRectF
from PyQt6.QtGui import QColor

from zeichnen.figur import Pose
from zeichnen.grundlagen import KEIN_STIFT, WEISS, blinzeln, glatt, kreis, radial, stift, teilchen_kasten
from zeichnen.labor import (KREIDE, anschrieb_breite, kreide_striche, striche_spitze, tafel_flaeche, zeichne_kreide,
                            zeichne_schwamm, zeichne_striche, zeichne_tafel)
from zeichnen.professor import ARM_LAENGE, SCHULTER_Y, Professor, hand_lokal, professor_trafo

from .basis import (Erschrecke, Gehe, Mit, Nebenbei, Renne, Schritt, Setze, Stehe, Szene, Tu, Wandel, Warte, WarteBis,
                    WarteNebenbei)

RAUCH = [QColor(235, 235, 240, 220), QColor(200, 200, 210, 200), WEISS]
RUSS = [QColor(70, 64, 60, 220), QColor(110, 100, 95, 200), QColor(50, 46, 44, 230)]
FUNKEN = [QColor('#FFE38F'), QColor('#FFB43C'), WEISS]
STAUB = [QColor(210, 200, 185, 190), QColor(180, 170, 155, 170)]
QUALM = [QColor(80, 76, 74, 200), QColor(60, 57, 55, 190), QColor(130, 126, 122, 190)]


def triumph_pose(sz, u=0.0):
    """Ta-daa: beide Hände offen, Füße breit, strahlt ins Publikum."""
    return Pose(kopf_vorn=True, arm_v=-128, arm_h=-128, arm_v_x=14, bein_v=-14, bein_h=14, wipp=2 * math.sin(u * 6),
                mund_offen=u < 0.5, auge_zu=0.6 < u < 0.75)


def denk_pose(sz, u=0.0):
    """Hand am Kinn, Blick nach oben."""
    return Pose(arm_v=-150 + 6 * math.sin(u * 5), arm_v_x=12, blick_y=-0.8, auge_zu=blinzeln(sz.t))


def mit_arm(pose, **werte):
    return replace(pose, **werte)


class ProfSzene(Szene):
    """Basis für alle Szenen mit dem Professor (name leer: erscheint nicht im Menü)."""
    haare = 0.0
    haar_farbe = None
    gluehen = 0.0
    brille = 0.0
    halt = None
    halt_h = None
    weg_ist = False
    russ = 0.0
    verkohlt = 0.0
    qualm = 0.0          # 0..1: Haare und Mütze rauchen
    blitz_t = None       # Beginn des Explosionsblitzes
    blitz_ort = (0.0, 0.0)
    blitz_r = 0.0
    senke = 0.0          # Requisiten versinken beim Schreck unter der Unterkante
    mitnehmen = ()       # Namen von x-Werten (z. B. 'tafel_x'), die mit ihm mitwandern
    _x_alt = None

    def weiter(self, dt):
        if self.qualm and self.zeige_figur and not self.erschreckt and random.random() < self.qualm * 0.45:
            x, y = self.kopf_oben()
            self.streue(x + random.uniform(-14, 14) * self.s, y, 1, QUALM, tempo=45, dauer=1.2, r=(6, 11),
                        richtung=-math.pi / 2, streuung=0.4)
        if self.mitnehmen and self._x_alt is not None and not self.erschreckt:
            for name in self.mitnehmen:
                setattr(self, name, getattr(self, name) + self.x - self._x_alt)
        self._x_alt = self.x

    # -- Figur

    def trafo(self):
        return professor_trafo(self.x, self.y - self.hopp, self.s, self.richtung, self.stauchen, self.neigung)

    def zeichne_figur(self, p, zwischen=None):
        p.save()
        p.setTransform(self.trafo(), True)
        p.setPen(KEIN_STIFT)
        Professor.zeichne(p, self)
        p.restore()

    def figur_kasten(self):
        return self.trafo().mapRect(Professor.KASTEN)

    def figur_sichtbar(self):
        return self.figur_kasten().intersects(self.geo)

    def striche_punkt(self):
        q = self.trafo().map(QPointF(*Professor.KOPF))
        return q.x(), q.y()

    def kopf_oben(self):
        q = self.trafo().map(QPointF(4, -232 - 26 * self.haare))
        return q.x(), q.y()

    def mund(self):
        q = self.trafo().map(QPointF(6 if self.pose.kopf_vorn else 22, -160))
        return q.x(), q.y()

    def hand(self, vorn=True):
        q = self.trafo().map(QPointF(*hand_lokal(self.pose, vorn)))
        return q.x(), q.y()

    def arm_zu(self, x, y, vorn=True):
        """Armwinkel, mit dem die Hand auf den Weltpunkt (x, y) zeigt."""
        sx = self.pose.arm_v_x if vorn else -6
        q = self.trafo().map(QPointF(sx, SCHULTER_Y + self.pose.hub))
        dx = (x - q.x()) * self.richtung / self.s
        dy = (y - q.y()) / self.s
        return math.degrees(math.atan2(-dx, dy))

    def reichweite(self):
        return ARM_LAENGE * self.s

    # -- Requisiten

    def zeichne_requisiten(self, p):
        pass

    def zeichne_davor(self, p):
        pass

    def requisiten_kasten(self):
        return QRectF()

    def zeichne_hinten(self, p):
        if not self.weg_ist:
            p.save()
            p.translate(0, self.senke)
            self.zeichne_requisiten(p)
            p.restore()

    def zeichne_vorn(self, p):
        if not self.weg_ist:
            p.save()
            p.translate(0, self.senke)
            self.zeichne_davor(p)
            p.restore()
        b = self.blitz()
        if b:
            x, y, r, a = b
            p.setPen(KEIN_STIFT)
            p.setBrush(radial(x, y, r, QColor(255, 255, 235, int(250 * a)), QColor(255, 200, 80, 0)))
            kreis(p, x, y, r)

    def blitz(self):
        """(x, y, Radius, Deckkraft) des Explosionsblitzes oder None."""
        if self.blitz_t is None:
            return None
        u = (self.t - self.blitz_t) / 0.3
        if u >= 1:
            return None
        return self.blitz_ort[0], self.blitz_ort[1], self.blitz_r * (0.6 + 0.4 * u), 1 - u

    def grenzen_extra(self):
        if self.weg_ist:
            return QRectF()
        return self.requisiten_kasten().translated(0, self.senke).intersected(
            self.geo.adjusted(-400 * self.s, -400 * self.s, 400 * self.s, 0))

    def weg(self, farbe=None):
        """Requisiten verschwinden in einer Wolke."""
        if self.weg_ist:
            return
        self.weg_ist = True
        k = self.requisiten_kasten()
        if k.isEmpty():
            return
        n = max(8, int(k.width() * k.height() / (900 * self.s * self.s)))
        for _ in range(min(n, 40)):
            self.streue(random.uniform(k.left(), k.right()), random.uniform(k.top(), k.bottom()), 1,
                        farbe or RAUCH, tempo=90, dauer=0.7, r=(8, 16))

    def grenzen(self):
        k = QRectF()
        b = self.blitz()
        if b:
            x, y, r, _ = b
            k = QRectF(x - r, y - r, 2 * r, 2 * r).intersected(self.geo)
        if self.zeige_figur:
            k = self.figur_kasten().adjusted(-4 * self.s, -34 * self.s * (1 + self.haare), 4 * self.s, 0)
        k = k.united(self.grenzen_extra())
        for d in self.darsteller.values():
            if d.zeige_figur:
                k = k.united(d.kasten())
        for liste in self.teilchen:
            k = k.united(teilchen_kasten(liste))
        return k

    # -- Schreck-Varianten

    def schreck_ablauf(self):
        return self.schreck_rennen()

    def _vorher(self):
        self.nebenbei.clear()
        self.halt = self.halt_h = None
        self.weg()
        for name, d in self.darsteller.items():
            if not d.figur_sichtbar():
                d.zeige_figur = False

    def _andere(self):
        """Schreckschritte für die übrigen Darsteller (laufen nebenher)."""
        return [Nebenbei(Mit(n, Erschrecke(0.35, 40)), Mit(n, Renne(zum='rand')))
                for n, d in self.darsteller.items() if d.zeige_figur]

    def _ende(self):
        return [WarteNebenbei(), WarteBis(lambda sz: not sz.wolke and not sz.splitter)]

    def schreck_rennen(self):
        """Hüpfer, Haare stehen ab, weg zum nächsten Rand."""
        self._vorher()
        if not self.figur_sichtbar():
            self.zeige_figur = False
            return self._andere() + self._ende()
        return self._andere() + [HaareHoch(1.0), Erschrecke(0.35, 50), Renne(zum='rand', tempo=4.0)] + self._ende()

    def schreck_puff(self):
        """Hüpfer, dann löst er sich in einer Rauchwolke auf."""
        self._vorher()

        def puff(sz):
            if sz.zeige_figur:
                k = sz.figur_kasten()
                for _ in range(26):
                    sz.streue(random.uniform(k.left(), k.right()), random.uniform(k.top(), k.bottom()), 1, RAUCH,
                              tempo=120, dauer=0.7, r=(8, 18))
                sz.streue(k.center().x(), k.center().y(), 8, FUNKEN, tempo=260, dauer=0.6, r=(3, 6), art='stern')
            sz.zeige_figur = False
            for d in sz.darsteller.values():
                if d.zeige_figur:
                    q = d.kasten().center()
                    sz.streue(q.x(), q.y(), 14, RAUCH, tempo=120, dauer=0.6, r=(6, 14))
                    d.zeige_figur = False

        return [HaareHoch(1.0), Erschrecke(0.35, 46), Tu(puff)] + self._ende()

    def schreck_klappe(self):
        """Hüpfer, dann versinkt er wie durch eine Bodenklappe unter der Unterkante."""
        self._vorher()
        return self._andere() + [HaareHoch(1.0), Erschrecke(0.3, 46),
                                 Wandel(0.35, y=lambda sz: sz.boden + 300 * sz.s),
                                 Tu(lambda sz: setattr(sz, 'zeige_figur', False))] + self._ende()

    def schreck_versinken(self, schreck=0.3):
        """Hüpfer, dann versinkt alles gemeinsam (Figuren und Requisiten) unter der Unterkante."""
        self.nebenbei.clear()
        self.halt = self.halt_h = None
        tief = 330 * self.s
        neu = []
        for n, d in self.darsteller.items():
            if d.zeige_figur and d.figur_sichtbar():
                neu.append(Nebenbei(Mit(n, Erschrecke(schreck, 40)),
                                    Mit(n, Wandel(0.45, y=lambda d: d.y + tief))))
            else:
                d.zeige_figur = False
        sichtbar = self.zeige_figur and self.figur_sichtbar()
        if not sichtbar:
            self.zeige_figur = False
        neu += [HaareHoch(1.0), Erschrecke(schreck, 46) if sichtbar else Warte(schreck),
                Wandel(0.45, y=lambda sz: sz.y + tief, senke=tief),
                Tu(lambda sz: setattr(sz, 'zeige_figur', False))]
        return neu + self._ende()

    def schreck_kittel(self):
        """Hüpfer, dann zieht er sich wie eine Schildkröte in den Kittel zurück und huscht davon."""
        self._vorher()
        return self._andere() + [HaareHoch(1.0), Erschrecke(0.3, 46),
                                 Wandel(0.2, stauchen=0.55),
                                 Renne(zum='rand', tempo=4.5,
                                       haltung=lambda p, sz: replace(p, arm_v=-20, arm_h=20, schreck=1.0)),
                                 ] + self._ende()


class Knall(Tu):
    """Der große Knall: greller Blitz, Rauchwolke von zwei bis drei Figurenhöhen, danach
    Rußgesicht, Haare zu Berge, Brille schief, Mütze angesengt, alles qualmt.
    ort(sz) -> (x, y) Mittelpunkt, sonst kurz vor seinem Gesicht. groesse 1 = Standard."""

    def __init__(self, ort=None, groesse=1.0, russ=True):
        super().__init__(self.knallen)
        self.ort, self.groesse, self.russ = ort, groesse, russ

    def knallen(self, sz):
        s, g = sz.s, self.groesse
        x, y = self.ort(sz) if self.ort else sz.hand()
        sz.blitz_t, sz.blitz_ort, sz.blitz_r = sz.t, (x, y), 230 * s * g
        for _ in range(int(46 * g)):
            w = random.uniform(0, 2 * math.pi)
            d = random.uniform(0, 90) * s * g
            sz.streue(x + math.cos(w) * d, y + math.sin(w) * d * 0.7, 1, RAUCH + QUALM, tempo=280 * g, dauer=1.6,
                      r=(22 * g, 44 * g))
        sz.streue(x, y, int(16 * g), FUNKEN, tempo=420 * g, dauer=0.7, r=(3, 6), art='stern')
        if self.russ:
            sz.russ, sz.haare, sz.brille, sz.verkohlt, sz.qualm = 1.0, 1.0, 1.0, 1.0, 1.0


def explodiert(sz, u):
    """Pose nach dem Knall: steif wie ein Brett, Augen weit, Arme vom Körper."""
    return Pose(kopf_vorn=True, schreck=1.0 if u < 0.5 else 0.0, arm_v=-35, arm_h=35, bein_v=-6, bein_h=6,
                mund_offen=u >= 0.5, auge_zu=False)


class Publikumsblick(Stehe):
    """Der trockene Blick ins Publikum: steht still, schaut die Zuschauer an, blinzelt
    zweimal langsam und hustet ein Rauchwölkchen. Nach jedem Unglück derselbe Blick."""

    def __init__(self, dauer=1.2, husten=True):
        super().__init__(dauer, self.blick)
        self.husten, self.gehustet = husten, False

    def beginn(self, sz):
        self.gehustet = False

    @staticmethod
    def blick(sz, u):
        return Pose(kopf_vorn=True, auge_zu=0.25 < u < 0.42 or 0.8 < u < 0.95,
                    mund_offen=0.55 < u < 0.72, sorge=0.15)

    def weiter(self, sz, u, dt):
        super().weiter(sz, u, dt)
        if self.husten and not self.gehustet and u > 0.58:
            self.gehustet = True
            x, y = sz.mund()
            sz.streue(x, y, 5, QUALM, tempo=55, dauer=0.9, r=(5, 10), richtung=-math.pi / 2, streuung=0.8)
            sz.hopp = 0.0


def wuerde_pose(sz, u):
    """Würde reparieren: zieht mit beiden Händen den Kittel glatt, Kinn hoch, Augen zu."""
    zug = abs(math.sin(u * math.pi * 2.5))
    return Pose(kopf_vorn=True, arm_v=12 + 14 * zug, arm_h=-12 - 14 * zug, arm_v_x=14, hub=-2 * zug,
                auge_zu=True, blick_y=-0.5)


class Umkippen(Schritt):
    """Kippt steif wie ein Brett um (nach=-1 rückwärts, 1 vorwärts), federt kurz nach,
    Staub am Boden. Er bleibt liegen, bis ein späterer Schritt neigung zurücksetzt."""

    def __init__(self, dauer=0.5, nach=-1):
        self.dauer, self.nach = dauer, nach

    def weiter(self, sz, u, dt):
        f = min(1.0, u / self.dauer) ** 2
        sz.neigung = 88 * self.nach * f
        sz.pose = Pose(kopf_vorn=True, auge_zu=f > 0.9, arm_v=-8, arm_h=8, mund_offen=f < 0.9)

    def ende(self, sz):
        k = sz.figur_kasten()
        sz.streue(k.center().x(), sz.boden - 6 * sz.s, 10, STAUB, tempo=110, dauer=0.6, r=(5, 10),
                  richtung=-math.pi / 2, streuung=1.4)


class HaareHoch(Tu):
    def __init__(self, wert):
        super().__init__(lambda sz: setattr(sz, 'haare', max(sz.haare, wert)))


def schreib_stehe(dauer, ziel):
    """Steht an der Tafel und schreibt; ziel(sz, u) -> Weltpunkt der Kreide oder None."""
    def pose(sz, u):
        pz = ziel(sz, u)
        if pz is None:
            return Pose(arm_v=-60, auge_zu=blinzeln(sz.t))
        return Pose(arm_v=sz.arm_zu(*pz), blick_y=-0.2, auge_zu=blinzeln(sz.t))
    return Stehe(dauer, pose)



# ---------------------------------------------------------------- Tafel

class Anschrieb:
    """Ein Stück Kreideschrift auf der Tafel, in Tafel-Einheiten (Mitte unten der Tafel im Ursprung)."""

    def __init__(self, text, x, y, hoehe=22, farbe=None):
        self.text, self.x, self.y, self.hoehe = text, x, y, hoehe
        self.farbe = farbe
        self.anteil = 0.0
        self.durch = 0.0          # Durchstreichen 0..1
        self.deck = 1.0           # Deckkraft (Wischen)
        self.dreh = 0.0
        self.striche = kreide_striche(text, x, y, hoehe)

    def breite(self):
        return anschrieb_breite(self.text, self.hoehe)


class TafelSzene(ProfSzene):
    """Professor an einer kleinen Tafel; self.tafel_x ist die Mitte der Tafel."""
    tafel_x = 0.0
    kreide_da = True

    def tafel_vorbereiten(self, anteil=0.24):
        self.tafel_x = self.vom_rand(anteil)
        self.anschriebe = []
        self.wisch = []
        self.kreide_ort = None     # Weltpunkt der Kreide in der Hand, None: keine
        self.schwamm_ort = None

    def an_tafel(self, lx=75):
        """Steht rechts neben der Tafel (er schreibt immer von rechts, damit er nichts verdeckt)."""
        return [Gehe(bis=self.tafel_x + (lx + 52) * self.s), Setze(richtung=-1)]

    def tafel_abgang(self):
        """Nimmt die Tafel mit zum Rand, an dem die Szene begann."""
        rand = -self.richtung
        return [Setze(mitnehmen=('tafel_x',)),
                Gehe(bis=self.aussen(rand) + rand * 260 * self.s, haltung=ziehen if rand > 0 else schieben)]

    def schreib(self, text, x, y, hoehe=22):
        a = Anschrieb(text, x, y, hoehe)
        self.anschriebe.append(a)
        return a

    def welt(self, lx, ly):
        return self.tafel_x + lx * self.s, self.boden + ly * self.s

    def zeichne_tafel(self, p):
        p.save()
        p.translate(self.tafel_x, self.boden)
        p.scale(self.s, self.s)
        zeichne_tafel(p, wisch=self.wisch, kreide=self.kreide_da)
        for a in self.anschriebe:
            if a.deck <= 0 or a.anteil <= 0:
                continue
            p.save()
            if a.dreh:
                mx, my = a.x + a.breite() / 2, a.y + a.hoehe / 2
                p.translate(mx, my)
                p.rotate(a.dreh)
                p.translate(-mx, -my)
            farbe = QColor(KREIDE)
            farbe.setAlphaF(farbe.alphaF() * a.deck)
            zeichne_striche(p, a.striche, a.anteil, farbe, 2.2 * a.hoehe / 22)
            if a.durch > 0:
                p.setPen(stift(farbe, 2.4))
                y = a.y + a.hoehe * 0.55
                p.drawLine(QPointF(a.x - 3, y + 3), QPointF(a.x - 3 + (a.breite() + 6) * a.durch, y - 3))
                p.setPen(KEIN_STIFT)
            p.restore()
        p.restore()

    def zeichne_requisiten(self, p):
        self.zeichne_tafel(p)

    def zeichne_davor(self, p):
        if self.kreide_ort and self.zeige_figur:
            p.save()
            p.translate(*self.kreide_ort)
            p.scale(self.s, self.s)
            zeichne_kreide(p, 0, 0, -50 * self.richtung, 10)
            p.restore()
        if self.schwamm_ort and self.zeige_figur:
            p.save()
            p.translate(*self.schwamm_ort)
            p.scale(self.s, self.s)
            zeichne_schwamm(p, 0, 5)
            p.restore()

    def requisiten_kasten(self):
        f = tafel_flaeche()
        x0, y0 = self.welt(f.left() - 10, f.top() - 14)
        x1, _ = self.welt(f.right() + 10, 0)
        return QRectF(x0, y0, x1 - x0, self.boden - y0 + 2 * self.s)

    def schreck_ablauf(self):
        self.kreide_ort = self.schwamm_ort = None
        return self.schreck_rennen()


def ziehen(pose, sz):
    """Gangart, wenn er etwas hinter sich herzieht."""
    return replace(pose, arm_h=55, arm_v=35, sorge=0.3)


class Zurueck(Schritt):
    """Tritt ein Stück zurück, ohne sich umzudrehen (weite in Einheiten)."""

    def __init__(self, weite=50, dauer=0.6):
        self.weite, self.dauer = weite, dauer

    def beginn(self, sz):
        self.x0 = sz.x

    def weiter(self, sz, u, dt):
        f = glatt(u / self.dauer)
        sz.x = self.x0 - sz.richtung * self.weite * sz.s * f
        b = 16 * math.sin(f * math.pi * 2)
        sz.pose = Pose(bein_v=b, bein_h=-b, arm_v=-20, arm_h=20, auge_zu=blinzeln(sz.t))


def schieben(pose, sz):
    return replace(pose, arm_v=-75, arm_h=-70, arm_v_x=18)


class Schreibe(Schritt):
    """Schreibt einen Anschrieb in 'dauer' Sekunden, der Professor geht dabei mit."""

    def __init__(self, a, dauer, abstand=58, bis=1.0):
        self.a, self.dauer, self.abstand, self.bis = a, dauer, abstand, bis

    def beginn(self, sz):
        self.a0 = self.a.anteil

    def weiter(self, sz, u, dt):
        f = min(1.0, u / self.dauer)
        self.a.anteil = self.a0 + (self.bis - self.a0) * f
        lx, ly = striche_spitze(self.a.striche, self.a.anteil)
        wx, wy = sz.welt(lx, ly)
        ziel = wx - sz.richtung * self.abstand * sz.s
        schritt = max(-1.0, min(1.0, (ziel - sz.x) / (sz.s * 4))) * sz.tempo * 0.5 * dt
        sz.x += schritt
        sz.phase += abs(schritt) / (sz.s * 38)
        sz.kreide_ort = (wx, wy)
        bein = 14 * math.sin(sz.phase) if abs(schritt) > 0.05 * sz.s else 0
        sz.pose = Pose(arm_v=sz.arm_zu(wx, wy) + 4 * math.sin(u * 30), bein_v=-bein, bein_h=bein,
                       blick_y=-0.3, auge_zu=blinzeln(sz.t), wipp=math.sin(u * 8))


class Streiche(Schritt):
    def __init__(self, a, dauer=0.5):
        self.a, self.dauer = a, dauer

    def weiter(self, sz, u, dt):
        f = min(1.0, u / self.dauer)
        self.a.durch = f
        lx = self.a.x - 3 + (self.a.breite() + 6) * f
        wx, wy = sz.welt(lx, self.a.y + self.a.hoehe * 0.55)
        sz.kreide_ort = (wx, wy)
        sz.pose = Pose(arm_v=sz.arm_zu(wx, wy), blick_y=-0.3, sorge=0.6)


class Wische(Schritt):
    """Wischt mit dem Schwamm in Kreisen über die Anschriebe (liste) und macht sie blasser."""

    def __init__(self, liste, dauer=1.4, rest=0.0):
        self.liste, self.dauer, self.rest = liste, dauer, rest

    def beginn(self, sz):
        self.d0 = [a.deck for a in self.liste]
        xs = [a.x for a in self.liste] + [a.x + a.breite() for a in self.liste]
        ys = [a.y for a in self.liste] + [a.y + a.hoehe for a in self.liste]
        self.k = (min(xs), min(ys), max(xs), max(ys))
        sz.kreide_ort = None

    def weiter(self, sz, u, dt):
        f = min(1.0, u / self.dauer)
        x0, y0, x1, y1 = self.k
        lx = x0 + (x1 - x0) * (0.5 - 0.5 * math.cos(f * math.pi)) + math.cos(u * 14) * 8
        ly = (y0 + y1) / 2 + math.sin(u * 14) * (y1 - y0 + 6) / 2
        wx, wy = sz.welt(lx, ly)
        sz.schwamm_ort = (wx, wy)
        for a, d0 in zip(self.liste, self.d0):
            a.deck = d0 + (self.rest - d0) * f
        if random.random() < 0.25:
            sz.wisch.append((lx, ly, random.uniform(6, 10)))
            sz.streue(wx, wy, 1, [QColor(240, 240, 235, 160)], tempo=30, dauer=0.6, r=(3, 6))
        ziel = wx - sz.richtung * 58 * sz.s
        sz.x += max(-1.0, min(1.0, (ziel - sz.x) / (sz.s * 4))) * sz.tempo * 0.5 * dt
        sz.pose = Pose(arm_v=sz.arm_zu(wx, wy), blick_y=-0.3, auge_zu=blinzeln(sz.t))

    def ende(self, sz):
        sz.schwamm_ort = None
