import math
import random

from PyQt6.QtCore import QRectF

from zeichnen.figur import Pose
from zeichnen.grundlagen import blinzeln, glatt
from zeichnen.requisiten import zeichne_seil

from .basis import Erschrecke, Gehe, Nebenbei, Renne, Schritt, Setze, Stehe, Szene, Wandel


class Klettere(Schritt):
    """Klettert am Seil hinauf bis zur Höhe 'bis' (y der Füße), Tempo aus szene.klettern."""

    def __init__(self, bis):
        self.bis = bis

    def beginn(self, sz):
        self.ziel = self.bis(sz)

    def weiter(self, sz, u, dt):
        sz.y -= sz.klettern * dt
        sz.phase += sz.klettern * dt / (sz.s * 20)
        sz.pose = kletter_pose(sz)

    def fertig(self, sz, u):
        return sz.y <= self.ziel


def kletter_pose(sz):
    sw = math.sin(sz.phase)
    pose = Pose(arm_v=-146 + 8 * sw, arm_v_x=18, arm_h=-158 - 10 * sw, bein_v=-32 - 14 * sw,
                bein_h=-16 + 14 * sw, wipp=math.sin(sz.t * 5) * 3, auge_zu=blinzeln(sz.t))
    if sz.frisch_erschreckt(0.6):
        pose.kopf_vorn, pose.schreck, pose.auge_zu = True, 1.0, False
    return pose


def greif_pose(sz, u):
    f = glatt(u / 0.5)
    return Pose(arm_v=-146 * f, arm_v_x=10 + 8 * f, arm_h=-158 * f, auge_zu=blinzeln(sz.t))


def wink_pose(sz, u):
    return Pose(arm_v=-100 + 28 * math.sin(u * 9), arm_v_x=20, arm_h=-158, bein_v=-32, bein_h=-16,
                wipp=math.sin(sz.t * 5) * 3, mund_offen=u < 1.6 and (u * 5) % 2 < 1, auge_zu=blinzeln(sz.t))


class Seil(Szene):
    """Ein Seil fällt nahe am Seitenrand herab, er klettert hinauf, winkt unterwegs und verschwindet."""
    name, titel, reihenfolge = 'seil', 'Seil', 5

    def vorbereiten(self):
        nah_links = random.random() < 0.5
        abstand = self.geo.width() * random.uniform(0.05, 0.09)
        self.xr = self.geo.left() + abstand if nah_links else self.geo.right() - abstand
        self.richtung = 1 if nah_links else -1
        self.seil_ende = self.oben
        self.am_seil = False
        self.klettern = self.geo.height() / 6.5

    def ablauf(self):
        s = self.s
        self.x = self.aussen(-self.richtung)
        return [Nebenbei(Wandel(1.2, seil_ende=self.boden - 6 * s)),
                Gehe(bis=self.xr - self.richtung * 50 * s),
                Stehe(0.5, greif_pose), Setze(am_seil=True),
                Klettere(bis=lambda sz: sz.oben + sz.geo.height() * 0.6),
                Stehe(3.4, wink_pose),
                Klettere(bis=lambda sz: sz.oben - 10 * sz.s),
                Setze(am_seil=False, zeige_figur=False),
                Wandel(0.9, seil_ende=self.oben - 20 * s)]

    def schreck_ablauf(self):
        hoch = self.oben - 20 * self.s
        if self.am_seil:
            # klettert fünfmal so schnell davon
            self.klettern *= 5
            return [Setze(striche=True), Klettere(bis=lambda sz: sz.oben - 10 * sz.s),
                    Setze(am_seil=False, zeige_figur=False, striche=False), Wandel(0.5, seil_ende=hoch)]
        if not self.zeige_figur:
            return [Wandel(0.5, seil_ende=hoch)]
        # unten: rennt zurück zum Rand, das Seil schnellt nach oben
        self.nebenbei.clear()
        return [Nebenbei(Wandel(0.6, seil_ende=hoch)), Erschrecke(0.3, hoehe=30), Renne(zum='zurueck')]

    def seil_x(self, yy):
        laenge = max(1.0, self.seil_ende - self.oben)
        if self.am_seil:
            pendel = math.sin(self.t * 2.2) * 6 * self.s
        else:
            pendel = math.sin(self.t * 2.4) * 10 * self.s * max(0.0, 1 - self.t / 3)
        return self.xr + pendel * ((yy - self.oben) / laenge) ** 2

    def zeichne_seil(self, p):
        zeichne_seil(p, self.seil_x, self.oben, self.seil_ende, self.s)

    def zeichne_hinten(self, p):
        if not self.am_seil:
            self.zeichne_seil(p)

    def zeichne_figur(self, p, zwischen=None):
        if not self.am_seil:
            return super().zeichne_figur(p)
        # das Seil liegt vor dem Bauch, aber hinter dem vorderen Arm
        welt = p.worldTransform()

        def seil_davor(q):
            q.save()
            q.setWorldTransform(welt)
            self.zeichne_seil(q)
            q.restore()

        super().zeichne_figur(p, seil_davor)

    def grenzen_extra(self):
        s = self.s
        return QRectF(self.xr - 60 * s, self.oben - 30 * s, 120 * s, self.seil_ende - self.oben + 60 * s)
