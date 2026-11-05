import math

from PyQt6.QtCore import QRectF

from zeichnen.figur import Pose
from zeichnen.grundlagen import blinzeln
from zeichnen.requisiten import zeichne_fahrrad

from .basis import Gehe, Nebenbei, Setze, Szene, Wandel


class Fahre(Gehe):
    """Wie Gehe, aber ohne Beinarbeit: die Phase zählt hier die Radumdrehung."""
    pose_fn = None
    schrittlaenge = 32


class Fahrrad(Szene):
    """Radelt am unteren Rand entlang, schaut kurz herüber, klingelt und macht einen Wheelie."""
    name, titel, reihenfolge = 'fahrrad', 'Fahrrad', 3

    def vorbereiten(self):
        self.zeige_figur = False
        self.tempo = self.geo.width() / 8
        self.schaut = self.klingel = self.erschrocken = False
        self.wheelie = 0.0

    def ablauf(self):
        self.x = self.aussen(-self.richtung)
        bei = self.vom_rand
        return [Fahre(bis=bei(0.33)), Setze(schaut=True), Fahre(bis=bei(0.37)), Setze(klingel=True),
                Fahre(bis=bei(0.44)), Setze(klingel=False), Fahre(bis=bei(0.49)), Setze(schaut=False),
                Fahre(bis=bei(0.62)), Nebenbei(Wandel(0.55, wheelie=16), Wandel(0.6, wheelie=0)),
                Fahre()]

    def schreck_ablauf(self):
        # wendet zum näheren Rand und tritt nach kurzem Schreck voll in die Pedale
        self.nebenbei.clear()
        return [Setze(richtung=lambda sz: sz.naechster_rand(), erschrocken=True, schaut=False,
                      klingel=False, wheelie=0.0, striche=True),
                Fahre(dauer=0.3), Fahre(dauer=0.2, tempo=2.5), Setze(erschrocken=False, striche=False),
                Fahre(tempo=4)]

    def figur_sichtbar(self):
        return self.grenzen_extra().intersects(self.geo)

    def striche_punkt(self):
        return self.x - 8 * self.s * self.richtung, self.boden - 292 * self.s

    def grenzen_extra(self):
        s = self.s
        return QRectF(self.x - 145 * s, self.boden - 310 * s, 290 * s, 315 * s)

    def zeichne_vorn(self, p):
        s, t = self.s, self.t
        rad = self.phase
        kurbel = rad * 0.6
        pose = Pose(sitzt=True, sack=False, arm_v=-41, arm_h=-46, hub=math.sin(kurbel * 2) * 1.2,
                    wipp=math.sin(t * 7) * 3, auge_zu=blinzeln(t) and not self.erschrocken,
                    kopf_vorn=self.schaut or self.erschrocken, blick_y=0.25,
                    mund_offen=self.wheelie > 4 or self.erschreckt,
                    schreck=1.0 if self.erschrocken else 0.0)
        p.save()
        p.translate(self.x, self.boden)
        p.scale(s * self.richtung, s)
        if self.wheelie:
            p.translate(-60, 0)
            p.rotate(-self.wheelie)
            p.translate(60, 0)
        zeichne_fahrrad(p, rad, kurbel, t, pose, self.klingel)
        p.restore()
