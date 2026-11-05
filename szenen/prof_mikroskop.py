import math
import random

from PyQt6.QtCore import QPointF, QRectF

from zeichnen.figur import Pose
from zeichnen.grundlagen import blinzeln
from zeichnen.labor import zeichne_labortisch
from zeichnen.labor_b import mikroskop_okular, zeichne_mikroskop

from .basis import Gehe, Jeweils, Kurz, Nebenbei, Setze, Stehe, Wandel, Warte
from .professor import ProfSzene, Zurueck, ziehen

M = 1.4             # Mikroskop größer als der Tisch es vermuten ließe
TISCH = 34


class Mikroskop(ProfSzene):
    """Er stellt das Mikroskop scharf, unter dem Objektiv öffnet sich ein großes Auge.
    Als er näher herangeht, reckt sich das Mikroskop, schaut ihn aus dem Okular an und
    folgt ihm, als er zurückweicht. Gegenseitiges Mustern, das Auge zwinkert, er zwinkert
    verlegen zurück und zieht den Tisch samt neugierigem Mikroskop hinaus."""
    name, titel, reihenfolge = 'mikroskop', 'Gegenbesichtigung', 68

    def vorbereiten(self):
        self.tx = self.vom_rand(random.uniform(0.15, 0.17))
        self.strecke = self.neig = self.auge = self.auge_oben = 0.0
        self.oben_offen = 1.0
        self.knopf = 0.0
        self.blick = (0.0, 0.0)
        self.mustern = False

    def fuss(self):
        return self.tx, self.boden - (TISCH + 8) * self.s

    def okular(self):
        ox, oy = mikroskop_okular(self.strecke, self.neig)
        fx, fy = self.fuss()
        return fx + self._r * ox * M * self.s, fy + (oy - 8) * M * self.s

    def ablauf(self):
        self._r = r = self.richtung
        s = self.s
        self.x = self.aussen(-r)
        stand = self.tx - r * 70 * s

        def fokus(sz, u):
            sz.knopf = math.sin(u * 3) * 0.6
            kx = sz.tx - r * 10 * M * s
            ky = sz.fuss()[1] - 30 * M * s
            sz.pose = Pose(arm_v=sz.arm_zu(kx, ky) + 6 * math.sin(u * 12), blick_y=0.4, auge_zu=0.6 < u < 1.1)

        def schaut_runter(sz, u):
            return Pose(blick_y=0.9, sorge=min(0.6, u), arm_v=-150 if u > 0.6 else -30, arm_v_x=12,
                        auge_zu=blinzeln(sz.t))

        def steif(sz, u):
            return Pose(kopf_vorn=u > 1.2, sorge=1.0, arm_v=-20, arm_h=15, schreck=0.3 if u < 1.2 else 0.0,
                        blick_x=-0.6 if u > 1.2 else 0, auge_zu=blinzeln(sz.t, 0.3))

        return [
            Gehe(bis=stand),
            Setze(richtung=r),
            Stehe(0.5),
            Wandel(0.4, neigung=17),
            Jeweils(1.8, fokus),
            Nebenbei(Wandel(0.5, auge=1.0)),
            Jeweils(0.9, fokus),
            Setze(mustern=True),
            Wandel(0.35, neigung=0),
            Stehe(1.3, schaut_runter),
            Kurz(0.16, auge=0.08),
            Stehe(0.4, schaut_runter),
            Setze(pose=Pose(blick_y=1.0, arm_v=-70, arm_h=-40, sorge=0.3)),
            Wandel(0.5, neigung=22),
            Warte(0.5),
            Wandel(0.2, auge=0.0),
            Wandel(0.3, neigung=0),
            Stehe(0.5, lambda sz, u: Pose(blick_y=0.6, sorge=0.6, arm_v=-150, arm_v_x=12)),
            Wandel(0.45, strecke=1.0),
            Wandel(0.3, auge_oben=1.0),
            Stehe(0.5, lambda sz, u: Pose(blick_y=-0.5, sorge=0.3, arm_v=-150, arm_v_x=12)),
            Setze(pose=Pose(schreck=1.0, arm_v=-100, arm_h=-90, arm_v_x=18), haare=0.6),
            Warte(0.15),
            Nebenbei(Wandel(0.7, strecke=1.4, neig=-42)),
            Zurueck(78, 0.6),
            Setze(brille=0.8),
            Stehe(2.6, steif),
            Kurz(0.25, oben_offen=0.05),
            Stehe(0.5, lambda sz, u: Pose(kopf_vorn=True, sorge=0.6, blick_x=-0.6)),
            Stehe(0.6, lambda sz, u: Pose(kopf_vorn=True, sorge=0.4, auge_zu=0.15 < u < 0.4, mund_offen=u > 0.4,
                                          blick_x=-0.6)),
            Setze(mitnehmen=('tx',)),
            Gehe(bis=self.aussen(-r) - r * 200 * s, haltung=ziehen),
        ]

    def weiter(self, dt):
        super().weiter(dt)
        if not self.mustern or not self.zeige_figur:
            self.blick = (0.0, 0.0)
            return
        r, s = self._r, self.s
        q = self.trafo().map(QPointF(20, -190))
        if self.auge_oben > 0.3:
            ax, ay = self.okular()
            w = math.radians(-self.neig)
        else:
            fx, fy = self.fuss()
            ax, ay = fx + r * 13 * M * s, fy - 44 * M * s
            w = 0.0
        dx, dy = (q.x() - ax) * r, q.y() - ay
        dx, dy = dx * math.cos(w) - dy * math.sin(w), dx * math.sin(w) + dy * math.cos(w)
        n = math.hypot(dx, dy) or 1.0
        mx, my = dx / n, dy / n
        if self.auge_oben > 0.9 and not self.erschreckt:
            my += 0.7 * math.sin(self.t * 2.2)       # mustert ihn von Kopf bis Fuß
        self.blick = (max(-1.0, min(1.0, mx * 1.2)), max(-1.0, min(1.0, my * 1.2)))

    # -- Zeichnen

    def zeichne_requisiten(self, p):
        s, r = self.s, self._r
        p.save()
        p.translate(self.tx, self.boden)
        p.scale(r * s, s)
        zeichne_labortisch(p, b=84, h=TISCH)
        p.restore()
        fx, fy = self.fuss()
        p.save()
        p.translate(fx, fy)
        p.scale(r * s * M, s * M)
        zeichne_mikroskop(p, self.strecke, self.neig, self.auge, self.auge_oben, self.blick, self.knopf,
                          self.oben_offen)
        p.restore()

    def requisiten_kasten(self):
        s, r = self.s, self._r
        ox, oy = self.okular()
        xs = [self.tx - 48 * s, self.tx + 48 * s, self.tx + r * 30 * M * s, ox - 22 * s, ox + 22 * s]
        top = min(oy - 26 * s, self.boden - (TISCH + 8 + 80 * M) * s)
        return QRectF(min(xs), top, max(xs) - min(xs), self.boden - top + 4 * s)

    # -- Schreck

    def schreck_ablauf(self):
        self.mustern = False
        self.auge = self.auge_oben = 0.0
        self.strecke = self.neig = 0.0
        self.neigung = 0.0
        return self.schreck_versinken()
