import math
import random

from PyQt6.QtCore import QPointF, QRectF
from PyQt6.QtGui import QColor

from zeichnen.figur import Pose
from zeichnen.figuren import Eichhoernchen
from zeichnen.grundlagen import blinzeln
from zeichnen.requisiten import zeichne_zimtstern

from .basis import Gehe, Jeweils, Mit, Schritt, Setze, Stehe, Szene, Tu, Wandel, Warte

STERN_R = 46        # Einheiten
KRUEMEL = [QColor('#A8692F'), QColor('#7A4520'), QColor('#FFFFFF')]


class Rollen(Schritt):
    """Der Stern rollt (kippelnd, wenn eine Zacke fehlt) bis x=bis, das Eichhörnchen schiebt."""

    def __init__(self, bis, tempo, schieben=True):
        self.bis, self.tempo, self.schieben = bis, tempo, schieben

    def beginn(self, sz):
        self.ziel = self.bis(sz) if callable(self.bis) else self.bis
        self.r = -sz.richtung if self.ziel is None else (1 if self.ziel > sz.sx else -1)

    def weiter(self, sz, u, dt):
        v = self.r * sz.tempo * self.tempo
        sz.sx += v * dt
        sz.sdreh += math.degrees(v * dt / (STERN_R * sz.s * 0.8))
        if self.schieben:
            e = sz.eh
            e.richtung = self.r
            e.x = sz.sx - self.r * (STERN_R + 26) * sz.s
            e.phase += abs(v) * dt / (e.s * 30)
            e.pose = Pose(bein_v=-30 * math.sin(e.phase), arm_v=-90, mund_offen=True, sorge=0.3)

    def fertig(self, sz, u):
        if self.ziel is None:
            return not sz.grenzen().intersects(sz.geo)
        return (sz.sx - self.ziel) * self.r >= 0


class Zimtstern(Szene):
    """Ein riesiger Zimtstern rollt herein, ein Eichhörnchen hüpft hinterher und zerrt
    vergeblich daran. Es beißt eine Zacke ab und rollt den nun kippelnden Stern davon."""
    name, titel, reihenfolge = 'zimtstern', 'Eichhörnchen und Zimtstern', 34

    def vorbereiten(self):
        self.zeige_figur = False
        r = self.richtung
        self.sx = self.aussen(-r)
        self.sdreh = 0.0
        self.fehlt = -1
        self.vors_gesicht = False
        self.eh = self.dazu('eh', Eichhoernchen, groesse=0.7)
        self.eh.richtung = r

    def kipp(self):
        """Höhe der Sternmitte: mit fehlender Zacke rumpelt er."""
        h = STERN_R * 0.88
        if self.fehlt >= 0:
            h -= abs(math.sin(math.radians(self.sdreh * 2.5))) * 9
        return h

    def ablauf(self):
        r, s = self.richtung, self.s
        ziel = self.vom_rand(random.uniform(0.15, 0.19))
        zerren = lambda d, u: Pose(arm_v=-80, bein_v=-40, mund_offen=True, sorge=1.0,  # noqa: E731
                                   kopf_vorn=False)
        return [
            Rollen(ziel, 1.6, schieben=False),
            Mit('eh', Setze(x=self.aussen(-r))),
            Mit('eh', Gehe(bis=lambda d: d.sz.sx + r * (STERN_R + 12) * s, tempo=1.0)),
            Mit('eh', Setze(richtung=-r)),
            Mit('eh', Stehe(0.8, lambda d, u: Pose(kopf_vorn=True, blick_x=-0.5, blick_y=-0.5, auge_zu=blinzeln(d.t)))),
            Mit('eh', Setze(neigung=-14)),
            Jeweils(1.6, lambda sz, u: (setattr(sz.eh, 'pose', zerren(sz.eh, u)),
                                         setattr(sz.eh, 'x', sz.sx + r * (STERN_R + 12 + 4 * math.sin(u * 30)) * s),
                                         setattr(sz, 'sdreh', math.sin(u * 30) * 2))),
            Mit('eh', Setze(neigung=0)),
            Mit('eh', Stehe(0.8, Pose(kopf_vorn=True, sorge=1.0, auge_zu=False))),
            Mit('eh', Wandel(0.25, x=lambda d: d.sz.sx + r * (STERN_R + 2) * s)),
            Tu(lambda sz: sz.abbeissen()),
            Mit('eh', Stehe(1.0, lambda d, u: Pose(mund_offen=(u * 8) % 2 < 1, auge_zu=True))),
            Mit('eh', Stehe(0.6, Pose(kopf_vorn=True, blick_y=0.4))),
            Mit('eh', Setze(richtung=-r)),
            Rollen(None, 1.3),
        ]

    def schreck_ablauf(self):
        self.nebenbei.clear()
        e = self.eh
        if not e.figur_sichtbar():
            return [Rollen(None, 3.0, schieben=False)]
        return [Mit('eh', Setze(striche=True, neigung=0, pose=Pose(kopf_vorn=True, schreck=1.0, arm_v=-120))),
                Setze(vors_gesicht=True), Warte(0.25), Mit('eh', Setze(striche=False)), Rueckwaerts()]

    def abbeissen(self):
        self.fehlt = 2
        w = math.radians(-90 + 2 * 72 + self.sdreh)
        x = self.sx + math.cos(w) * STERN_R * self.s * 0.8
        y = self.boden - self.kipp() * self.s + math.sin(w) * STERN_R * self.s * 0.8
        self.streue(x, y, 10, KRUEMEL, tempo=120, dauer=0.8, r=(1.5, 3), schwer=True)

    def zeichne_vorn(self, p):
        p.save()
        if self.vors_gesicht:
            q = self.eh.trafo().map(QPointF(16, -80))
            p.translate(q)
            p.scale(self.s * 0.5, self.s * 0.5)
        else:
            p.translate(self.sx, self.boden - self.kipp() * self.s)
            p.rotate(self.sdreh)
            p.scale(self.s, self.s)
        zeichne_zimtstern(p, STERN_R, self.fehlt)
        p.restore()

    def grenzen_extra(self):
        r = STERN_R * self.s * 1.1
        if self.vors_gesicht:
            return self.eh.kasten().adjusted(-r, -r, r, r)
        return QRectF(self.sx - r, self.boden - 2 * r, 2 * r, 2 * r)


class Rueckwaerts(Schritt):
    """Mit dem Stern vor dem Gesicht rückwärts zum nächsten Rand."""

    def beginn(self, sz):
        self.seite = sz.eh.naechster_rand()

    def weiter(self, sz, u, dt):
        e = sz.eh
        e.x += self.seite * sz.tempo * 3.2 * dt
        e.phase += sz.tempo * 3.2 * dt / (e.s * 30)
        e.pose = Pose(bein_v=-30 * math.sin(e.phase), arm_v=-120, kopf_vorn=True, schreck=1.0)
        sz.sx = e.x

    def fertig(self, sz, u):
        return not sz.grenzen().intersects(sz.geo)
