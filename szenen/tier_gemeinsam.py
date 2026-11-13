"""Gemeinsame Bausteine der Wintertier-Szenen (szenen/tier_*.py)."""
import math

from PyQt6.QtGui import QColor

from zeichnen.figur import Pose, figur, zeichne_bein_ik
from zeichnen.grundlagen import GOLD_HELL, ROT_DUNKEL, ROT_HELL, WEISS, blinzeln, glatt, linear

from .basis import Folge, Mit, Schritt, Setze, Stehe, wert

SCHNEE = [QColor(255, 255, 255, 230), QColor(220, 235, 250, 220)]
FEDERN = [QColor(255, 255, 255, 240), QColor(235, 238, 245, 230)]


class Flug(Schritt):
    """Bogen von der aktuellen Lage nach 'nach' = (x, y), Scheitel 'hoehe' Einheiten über der
    Verbindungslinie, dreht dabei die Neigung auf 'neigung'. haengen: Sekunden Stillstand im
    Scheitel (Erwartungspause). pose: Pose oder Funktion (wer, f) mit f = Anteil des Wegs."""

    def __init__(self, nach, dauer, hoehe=0.0, neigung=None, haengen=0.0, pose=None, glatt_drehen=False):
        self.nach_v, self.dauer_v, self.hoehe = nach, dauer, hoehe
        self.neigung_v, self.haengen, self.pose = neigung, haengen, pose
        self.glatt_drehen = glatt_drehen

    def beginn(self, sz):
        self.x0, self.y0 = sz.x, sz.y
        self.x1, self.y1 = wert(self.nach_v, sz)
        self.n0 = sz.neigung
        self.n1 = self.n0 if self.neigung_v is None else wert(self.neigung_v, sz)
        self.flug = wert(self.dauer_v, sz)
        self.dauer = self.flug + self.haengen

    def anteil(self, u):
        h = self.flug / 2
        if u < h:
            return u / self.flug
        if u < h + self.haengen:
            return 0.5
        return min(1.0, (u - self.haengen) / self.flug)

    def weiter(self, sz, u, dt):
        f = self.anteil(u)
        sz.x = self.x0 + (self.x1 - self.x0) * f
        sz.y = self.y0 + (self.y1 - self.y0) * f - self.hoehe * sz.s * 4 * f * (1 - f)
        g = glatt(f) if self.glatt_drehen else f
        sz.neigung = self.n0 + (self.n1 - self.n0) * g
        if self.pose is not None:
            sz.pose = self.pose(sz, f) if callable(self.pose) else self.pose


def blick_pose(sz, u, **mehr):
    """Trockener Blick ins Publikum mit zwei Blinzlern."""
    return Pose(kopf_vorn=True, auge_zu=0.25 < u < 0.37 or 0.55 < u < 0.67, **mehr)


def publikumsblick(wer, dauer=1.0, **mehr):
    schritt = Stehe(dauer, lambda d, u: blick_pose(d, u, **mehr))
    return Mit(wer, schritt) if wer else schritt


def sterne(sz, x, y, anzahl=6):
    sz.streue(x, y, anzahl, GOLD_HELL, tempo=50, dauer=1.4, r=(4, 7), art='stern')


def puff(sz, x, y, anzahl=12, tempo=110, r=(4, 10)):
    sz.streue(x, y, anzahl, SCHNEE, tempo=tempo, dauer=0.6, r=r)


def schnee_pose(sz, u):
    return Pose(auge_zu=blinzeln(sz.t))


def zeichne_sitzbeine(p, x, y, s, richtung, stiefel=True, spreiz=0.0):
    """Beine des sitzenden Weihnachtsmanns (Pose sitzt=True), nach vorn ausgestreckt.
    stiefel=False: rote Hosenbeine mit weißen Socken (aus den Stiefeln gepustet)."""
    p.save()
    p.translate(x, y)
    p.scale(s * richtung, s)
    for hinten, dx in ((True, -6), (False, 4)):
        fx, fy = 64 + dx - 40 * spreiz * (1 if hinten else -0.3), -6 - 60 * spreiz * (0 if hinten else 1)
        if stiefel:
            zeichne_bein_ik(p, dx, -68, fx, fy, hinten)
        else:
            k = 128 if hinten else 100
            p.save()
            p.translate(dx, -68)
            p.rotate(-70 if not hinten else -60)
            p.setBrush(linear(-12, 0, 12, 0, ROT_HELL.darker(k), ROT_DUNKEL.darker(k)))
            p.drawRoundedRect(-12, -4, 24, 60, 9, 9)
            p.setBrush(WEISS.darker(k - 2))
            p.drawEllipse(-13, 50, 26, 18)
            p.restore()
    p.restore()


def figur_mit_beinen(sz, p, stiefel=True, spreiz=0.0, zwischen=None):
    """Zeichnet den Weihnachtsmann; sitzt er, mit ausgestreckten Beinen."""
    from dataclasses import replace
    pose = replace(sz.pose, **sz.pose_fest) if sz.pose_fest else sz.pose
    p.save()
    if sz.neigung:
        p.translate(sz.x, sz.y - sz.hopp)
        p.rotate(sz.neigung * sz.richtung)
        p.translate(-sz.x, -(sz.y - sz.hopp))
    if pose.sitzt:
        zeichne_sitzbeine(p, sz.x, sz.y - sz.hopp, sz.s * sz.stauchen, sz.richtung, stiefel, spreiz)
    figur(p, sz.x, sz.y - sz.hopp, sz.s, sz.richtung, pose, zwischen, sz.stauchen, 0.0)
    p.restore()


def wackel(u, staerke=1.0, tempo=30):
    return math.sin(u * tempo) * staerke


def wegfliegen(sz, name, dauer=0.7, hoch=260):
    """Ein Vogel flattert schräg nach oben zum nächsten Seitenrand hinaus (d.fliegt = True)."""
    d = sz.darsteller[name]
    seite = d.naechster_rand()
    return Mit(name, Folge(Setze(fliegt=True, richtung=seite, neigung=0.0),
                           Flug(lambda w: (sz.aussen(seite), w.y - hoch * sz.s), dauer, hoehe=0)))
