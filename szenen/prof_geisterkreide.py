import math
import random

from PyQt6.QtGui import QColor

from zeichnen.figur import Pose
from zeichnen.grundlagen import KEIN_STIFT, blinzeln, kreis, radial
from zeichnen.labor import striche_spitze, tafel_flaeche, zeichne_kreide
from zeichnen.labor_c import zeichne_schlaffe_kreide

from .basis import Jeweils, Setze, Stehe, Tu
from .professor import Schreibe, Streiche, TafelSzene, Zurueck, denk_pose

GLANZ = [QColor(220, 240, 255, 220), QColor(255, 255, 255, 200)]


def vortrag(sz, u):
    """Dreht sich zum Publikum und doziert mit erhobenem Zeigefinger."""
    return Pose(kopf_vorn=True, arm_v=-130 + 14 * math.sin(u * 7), arm_v_x=16, mund_offen=(u * 5) % 2 < 1,
                auge_zu=blinzeln(sz.t))


class Geisterkreide(TafelSzene):
    """Dreht er sich zum Publikum, schreibt die Kreide allein 1+1=2. Er fährt herum, sie erstarrt
    und plumpst herunter. Beim zweiten Mal fängt er sie und zwingt sie, aus der 2 eine 3 zu machen;
    danach hängt sie schlaff in seiner Hand."""
    name, titel, reihenfolge = 'geisterkreide', 'Geisterkreide', 80

    def vorbereiten(self):
        self.tafel_vorbereiten(0.2)
        self.geist = None           # Weltpunkt der schwebenden Kreide
        self.geist_winkel = 0.0
        self.zappeln = 0.0
        self.a = self.schreib('1+1=', -64, -178, 28)
        self.zwei = self.schreib('2', 18, -178, 28)
        self.drei = self.schreib('3', 44, -184, 34)

    def ablage(self):
        f = tafel_flaeche()
        return self.welt(f.left() + 21, f.bottom() + 3)

    # -- Zeichnen

    def zeichne_davor(self, p):
        if self.kreide_ort and self.zappeln > 0:
            x, y = self.kreide_ort
            self.kreide_ort = (x + math.sin(self.t * 47) * 3 * self.s * self.zappeln, y)
            super().zeichne_davor(p)
            self.kreide_ort = (x, y)
        else:
            super().zeichne_davor(p)
        if self.geist:
            x, y = self.geist
            p.save()
            p.translate(x, y)
            p.scale(self.s, self.s)
            p.setPen(KEIN_STIFT)
            p.setBrush(radial(0, 0, 22, QColor(210, 235, 255, 150), QColor(210, 235, 255, 0)))
            kreis(p, 0, 0, 22)
            zeichne_kreide(p, 5, -5, self.geist_winkel, 16)
            p.restore()

    # -- Ablauf

    def ablauf(self):
        self.x = self.aussen(-self.richtung)
        s = self.s

        def geist_schreibt(a, dauer, start=None):
            def f(sz, u):
                v = min(1.0, u / dauer)
                a.anteil = v
                lx, ly = striche_spitze(a.striche, v)
                sz.geist = sz.welt(lx, ly)
                sz.geist_winkel = -50 + 12 * math.sin(u * 9)
                if random.random() < 0.15:
                    sz.streue(*sz.geist, 1, GLANZ, tempo=30, dauer=0.5, r=(2, 4), art='stern')
                sz.pose = vortrag(sz, u + (start or 0))
            return Jeweils(dauer, f)

        def schweben(von, nach, dauer, mit_vortrag=True):
            def f(sz, u):
                v = min(1.0, u / dauer)
                (x0, y0), (x1, y1) = von(sz), nach(sz)
                g = v * v * (3 - 2 * v)
                sz.geist = (x0 + (x1 - x0) * g, y0 + (y1 - y0) * g - math.sin(v * math.pi) * 25 * s)
                sz.geist_winkel = -50 * g + 8 * math.sin(u * 7)
                if mit_vortrag:
                    sz.pose = vortrag(sz, u)
            return Jeweils(dauer, f)

        def abheben(sz):
            sz.kreide_da = False
            sz.geist = sz.ablage()

        def herumfahren(sz, u):
            sz.pose = Pose(schreck=0.8, sorge=0.6, arm_v=-60, arm_h=-40, blick_y=-0.3)

        def plumpsen(sz, u):
            x0, y0 = sz.geist_start
            x1, y1 = sz.ablage()
            v = min(1.0, u / 0.45)
            sz.geist = (x0 + (x1 - x0) * v, y0 + (y1 - y0) * v * v)
            sz.geist_winkel = -50 + 50 * v
            sz.pose = Pose(sorge=0.8, blick_y=0.2 + 0.5 * v, arm_v=-60)

        def hingelegt(sz):
            sz.geist = None
            sz.kreide_da = True

        def merke(sz):
            sz.geist_start = sz.geist

        def fangen(sz, u):
            # er schnappt die Kreide aus der Luft
            v = min(1.0, u / 0.25)
            ziel = sz.geist or sz.kreide_ort
            sz.pose = Pose(arm_v=sz.arm_zu(*ziel), schreck=0.6 * (1 - v), sorge=0.5, mund_offen=True)
            if v >= 1 and sz.geist:
                sz.kreide_ort, sz.geist = sz.geist, None
                sz.zappeln = 1.0

        def schlaff(p, hx, hy):
            zeichne_schlaffe_kreide(p, hx + 2, hy + 4, 1.0, 1, 0.0)

        def ansehen(sz, u):
            sz.pose = Pose(arm_v=-125 + 4 * math.sin(u * 3), arm_v_x=16, blick_y=-0.2, sorge=0.2,
                           auge_zu=blinzeln(sz.t))

        mitte = lambda sz: sz.welt(-40, -205)  # noqa: E731
        an_zwei = lambda sz: sz.welt(26, -186)  # noqa: E731
        return [
            *self.an_tafel(),
            Stehe(0.5, lambda sz, u: Pose(auge_zu=blinzeln(sz.t))),
            Jeweils(0.6, vortrag),
            Tu(abheben),
            schweben(lambda sz: sz.ablage(), lambda sz: sz.welt(-60, -178), 0.8),
            geist_schreibt(self.a, 2.2),
            geist_schreibt(self.zwei, 0.6),
            Jeweils(0.3, vortrag),
            Setze(richtung=-1),
            Jeweils(0.5, herumfahren),
            Tu(merke),
            Jeweils(0.5, plumpsen),
            Tu(hingelegt),
            Stehe(0.6, lambda sz, u: Pose(blick_y=0.6, sorge=0.7, auge_zu=0.3 < u < 0.4)),
            Stehe(1.2, denk_pose),
            Stehe(0.6, lambda sz, u: Pose(blick_y=0.6, sorge=0.4, auge_zu=blinzeln(sz.t))),
            # zweiter Versuch: er tut, als würde er sich umdrehen
            Jeweils(0.5, vortrag),
            Tu(abheben),
            schweben(lambda sz: sz.ablage(), an_zwei, 0.7),
            Setze(richtung=-1),
            Jeweils(0.35, fangen),
            Jeweils(0.5, lambda sz, u: setattr(sz, 'pose', Pose(arm_v=sz.arm_zu(*sz.kreide_ort), sorge=0.9,
                                                               blick_y=-0.3, mund_offen=False))),
            Streiche(self.zwei, 0.6),
            Schreibe(self.drei, 1.0),
            Setze(kreide_ort=None, zappeln=0.0, halt=lambda sz: schlaff),
            Zurueck(30, 0.4),
            Jeweils(1.3, ansehen),
            Stehe(1.3, lambda sz, u: Pose(kopf_vorn=True, auge_zu=True, hub=-4 * abs(math.sin(u * 7)),
                                          arm_v=-60, arm_h=20)),
            *self.tafel_abgang(),
        ]

    def schreck_ablauf(self):
        self.kreide_ort = None
        if self.geist:
            self.streue(*self.geist, 6, GLANZ, tempo=80, dauer=0.5, r=(2, 4), art='stern')
        self.geist = None
        return self.schreck_puff()

    def requisiten_kasten(self):
        return super().requisiten_kasten().adjusted(0, -30 * self.s, 0, 0)
