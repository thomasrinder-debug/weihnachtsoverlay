import math
import random

from PyQt6.QtCore import QPointF, QRectF
from PyQt6.QtGui import QColor

from zeichnen.figur import Pose, renn_pose, zeichne_bein_ik, zeichne_sack, zeichne_weihnachtsmann
from zeichnen.figuren import Wichtel
from zeichnen.hoersaal import zeichne_handglocke, zeichne_riesenglocke, zeichne_schallringe
from zeichnen.requisiten import zeichne_muetze_lose

from .basis import Ducke, Gehe, Jeweils, Mit, Nebenbei, Renne, Setze, Springe, Stehe, Szene, Tu, Wandel, Warte

WG = 0.8
SCHNARCH = [QColor(255, 255, 255, 170), QColor(225, 235, 250, 150)]
STAUB = [QColor(225, 220, 210, 210), QColor(200, 195, 185, 190)]


def wichtel_hand(d, vorn=True):
    pose = d.pose
    a = math.radians(pose.arm_v if vorn else pose.arm_h)
    x0 = 8 if vorn else -8
    q = d.trafo().map(QPointF(x0 - math.sin(a) * 35, -96 + pose.hub + math.cos(a) * 35))
    return q.x(), q.y()


class HsGlocke(Szene):
    """Vorlesungsende: Der Weihnachtsmann schläft im Sitzen. Der Wichtel bimmelt mit der
    Handglocke, dann direkt am Ohr und wird im Schlaf weggewedelt. Aus dem Sack holt er eine
    Riesenglocke, holt aus: DONG. Der Weihnachtsmann schießt senkrecht hoch, landet rennend,
    schnappt im Vorbeirasen seinen Sack, in dessen Schlaufe der Wichtel hängt, und ist weg.
    Nur die Mütze schwebt zurück, bis sie hinterhergezogen wird."""
    name, titel, reihenfolge = 'hs_glocke', 'Vorlesungsende', 1005

    def vorbereiten(self):
        r, s = self.richtung, self.s
        self.xs = self.vom_rand(random.uniform(0.15, 0.18))
        self.sack_x = None            # Sack am Boden
        self.sitzt = False
        self.schlaeft = False
        self.schnarch_t = 0.0
        self.handglocke = True
        self.schwung = 0.0
        self.riese = 0.0              # 0: keine Riesenglocke, 1: in der Hand
        self.riese_schwung = 0.0
        self.ring = 0.0
        self.ring_x = self.ring_y = 0.0
        self.flucht = False
        self.geschleift = False
        self.muetze = None            # [x, y, dreh] der zurückgelassenen Mütze
        self.w = self.dazu('w', Wichtel, groesse=WG, vorn=True)
        self.w.x = self.aussen(-r) - r * 120 * s

    def ablauf(self):
        r, s = self.richtung, self.s
        w = self.w
        self.x = self.aussen(-r)

        def bimmeln(staerke):
            def pose(d, u):
                d.sz.schwung = math.sin(u * (14 + 10 * staerke)) * (25 + 30 * staerke)
                d.sz.ring = staerke * 0.45 * (0.6 + 0.4 * abs(math.sin(u * 14)))
                d.sz.ring_x, d.sz.ring_y = wichtel_hand(d)
                d.hopp = abs(math.sin(u * 12)) * 16 * staerke * d.s
                return Pose(arm_v=-150 + d.sz.schwung * 0.6, arm_h=-30, mund_offen=staerke > 0.5,
                            kopf_vorn=False, hub=0)
            return pose

        def schlaf(sz, u):
            return sz.schlafpose(u)

        def wedeln(sz, u):
            p = sz.schlafpose(u)
            p.arm_v = -120 + 80 * math.sin(u * 10)
            return p

        return [
            Gehe(bis=self.xs),
            # Hinsetzen, gähnen, einschlafen
            Tu(lambda sz: sz.hinsetzen()),
            Stehe(0.45, lambda sz, u: Pose(sitzt=True, sack=False, mund_offen=True, auge_zu=True, arm_v=-150,
                                           arm_h=-150, kopf_vorn=True)),
            Setze(schlaeft=True),
            Nebenbei(Mit('w', Gehe(bis=self.xs + r * 160 * s, tempo=1.8)), Mit('w', Setze(richtung=-r))),
            Stehe(1.2, schlaf),
            # Versuch 1: bimmeln
            Nebenbei(Mit('w', Stehe(0.8, bimmeln(0.3)))),
            Stehe(0.8, schlaf),
            Setze(ring=0.0, schwung=0.0),
            Stehe(0.2, schlaf),
            # Versuch 2: direkt am Ohr, er wedelt im Schlaf
            Mit('w', Gehe(bis=self.xs + r * 108 * s, tempo=1.2)),
            Nebenbei(Mit('w', Stehe(0.7, bimmeln(1.0))), Mit('w', Ducke(0.25)), Mit('w', Stehe(0.3, Pose(
                arm_v=-160, arm_h=-30, schreck=0.6, sorge=1.0)))),
            Stehe(0.7, schlaf),
            Stehe(0.45, wedeln),
            Setze(ring=0.0, schwung=0.0),
            Stehe(0.25, schlaf),
            # Riesenglocke aus dem Sack
            Mit('w', Setze(richtung=-r)),
            Nebenbei(Mit('w', Gehe(bis=lambda d: d.sz.sack_x + r * 30 * s, tempo=1.5))),
            Stehe(0.65, schlaf),
            Setze(handglocke=False, wackel=1.0),
            Nebenbei(Mit('w', Stehe(0.4, Pose(arm_v=-60, arm_h=-60)))),
            Stehe(0.4, schlaf),
            Setze(wackel=0.0, riese=1.0),
            Mit('w', Setze(richtung=r)),
            Mit('w', Springe(lambda d: (d.sz.sack_x - r * 4 * s, d.sz.boden - 92 * s), 0.4, 50)),
            Mit('w', Setze(pose=Pose(arm_v=-175, arm_h=-175))),
            # Erwartungspause: hoch damit
            Nebenbei(Mit('w', Stehe(0.7, lambda d, u: Pose(arm_v=-175, arm_h=-175, auge_zu=u > 0.3,
                                                           hub=-2, mund_offen=False)))),
            Jeweils(0.7, lambda sz, u: setattr(sz, 'riese_schwung', -25 * min(1.0, u / 0.5))),
            Stehe(0.01, schlaf),
            # DONG
            Tu(lambda sz: sz.dong()),
            Jeweils(0.12, lambda sz, u: setattr(sz, 'riese_schwung', -25 + 70 * u / 0.12)),
            Tu(lambda sz: sz.hochschiessen()),
            Springe(lambda sz: (sz.x, sz.boden), 0.6, 260),
            Stehe(0.3, lambda sz, u: sz.strampeln(u)),
            Setze(flucht=True),
            Renne(zum='rand', tempo=6.5),
            Setze(ring=0.0, flucht=False),
            # Die Mütze schwebt herab und wird hinterhergezogen
            Wandel(0.15, ring=0.0),
            Tu(lambda sz: setattr(sz, 'muetze_ziel', sz.aussen(-r))),
            Warte(0.45),
            Jeweils(0.35, lambda sz, u: sz.muetze_weg(u)),
            Setze(muetze=None),
        ]

    # -- Zustände

    def schlafpose(self, u):
        k = math.sin(self.t * 2.4)
        return Pose(sitzt=True, sack=False, auge_zu=True, mund_offen=k > 0.3, arm_v=-20, arm_h=-10,
                    hub=k * 2, wipp=k * 3)

    def hinsetzen(self):
        self.sitzt = True
        self.sack_x = self.x - self.richtung * 80 * self.s
        self.pose_fest = {'sack': False}

    wackel = 0.0
    muetze_ziel = 0.0

    def dong(self):
        s = self.s
        self.ring = 1.0
        self.ring_x, self.ring_y = self.riese_punkt()
        self.ring_y += 60 * s
        self.streue(self.ring_x, self.ring_y, 10, [QColor('#FFE38F'), QColor('#FFFFFF')], tempo=260, dauer=0.5,
                    r=(3, 7), art='stern')

    def hochschiessen(self):
        s = self.s
        self.sitzt = False
        self.schlaeft = False
        hy = self.boden + 54 * s - 230 * s
        self.muetze = [self.x + self.richtung * 6 * s, hy, 0.0]
        self.pose_fest = {'sack': False, 'muetze': False}
        self.striche = True
        self.streue(self.x, self.boden - 6 * s, 12, STAUB, tempo=200, dauer=0.6, r=(7, 13))

    def strampeln(self, u):
        self.striche = False
        self.richtung = self.naechster_rand()
        p = renn_pose(u * 40)
        p.schreck = 1.0
        p.kopf_vorn = False
        if int(u * 30) % 3 == 0:
            self.streue(self.x - self.richtung * 30 * self.s, self.boden - 6 * self.s, 2, STAUB, tempo=120,
                        dauer=0.4, r=(5, 10))
        return p

    def muetze_weg(self, u):
        if self.muetze:
            self.muetze[0] += (self.muetze_ziel - self.muetze[0]) * min(1.0, u / 0.35) * 0.5
            self.muetze[2] = -20

    def riese_punkt(self):
        w = self.w
        x, y = wichtel_hand(w)
        return x, y

    def weiter(self, dt):
        s, w = self.s, self.w
        self.ring = max(0.0, self.ring - dt * (0.6 if self.ring > 0.5 else 0.0))
        if self.schlaeft and not self.erschreckt:
            self.schnarch_t += dt
            if self.schnarch_t > 1.1:
                self.schnarch_t = 0.0
                x = self.x + self.richtung * 40 * s
                self.streue(x, self.boden - 150 * s, 4, SCHNARCH, tempo=50, dauer=1.0, r=(7, 15),
                            richtung=-math.pi / 2, streuung=0.6)
        if self.muetze and not self.erschreckt:
            if self.muetze[1] < self.boden - 8 * s:
                self.muetze[1] += 120 * s * dt
                self.muetze[0] += math.sin(self.t * 4) * 40 * s * dt
                self.muetze[2] = math.sin(self.t * 4) * 18
        if self.flucht and not self.geschleift and self.sack_x is not None:
            if (self.x - self.sack_x) * self.richtung >= -10 * s:
                self.geschleift = True
                w.y = self.boden
                self.sack_x = None
                self.pose_fest = {'muetze': False}
                self.riese = 0.0
        if self.geschleift and not self.erschreckt:
            # der Wichtel hängt mit einem Stiefel in der Sackschlaufe und flattert hinterher
            w.richtung = self.richtung
            w.neigung = -88 + math.sin(self.t * 30) * 6
            w.x = self.x - self.richtung * 120 * s
            w.y = self.y - 96 * s
            w.hopp = 0.0
            w.pose = Pose(kopf_vorn=True, schreck=0.6, arm_v=-175, arm_h=-170, bein_v=-80, bein_h=10,
                          mund_offen=True)

    # -- Zeichnen

    def zeichne_figur(self, p, zwischen=None):
        if not self.sitzt:
            return super().zeichne_figur(p, zwischen)
        s, r = self.s, self.richtung
        pose = self.pose
        p.save()
        p.translate(self.x, self.boden + 54 * s - self.hopp)
        p.scale(s * r, s)
        zeichne_bein_ik(p, -6, -66, 66, -58, True)
        zeichne_bein_ik(p, 6, -66, 80, -56, False)
        zeichne_weihnachtsmann(p, pose)
        p.restore()

    def zeichne_hinten(self, p):
        s = self.s
        if self.sack_x is not None:
            p.save()
            p.translate(self.sack_x, self.boden)
            p.scale(s * self.richtung, s)
            p.rotate(math.sin(self.t * 30) * 8 * self.wackel)
            zeichne_sack(p, 0, -48, -8, 1.2)
            p.restore()
        if self.ring > 0:
            ph = (self.t * 2.2) % 1.0
            zeichne_schallringe(p, self.ring_x, self.ring_y, 1, self.ring, ph, s, 140)
            zeichne_schallringe(p, self.ring_x, self.ring_y, -1, self.ring, ph, s, 140)

    def zeichne_vorn(self, p):
        s, w = self.s, self.w
        if w.zeige_figur:
            x, y = wichtel_hand(w)
            if self.handglocke:
                p.save()
                p.translate(x, y)
                p.scale(s * 1.2 * w.richtung, s * 1.2)
                zeichne_handglocke(p, self.schwung)
                p.restore()
            elif self.riese > 0:
                p.save()
                p.translate(x, y - 10 * s)
                p.scale(s * 0.95 * w.richtung, s * 0.95)
                zeichne_riesenglocke(p, self.riese_schwung, 0.5)
                p.restore()
        if self.muetze:
            mx, my, dreh = self.muetze
            p.save()
            p.translate(mx, my)
            p.scale(s * self.richtung, s)
            p.rotate(dreh)
            zeichne_muetze_lose(p)
            p.restore()

    def grenzen_extra(self):
        s = self.s
        k = QRectF()
        if self.sitzt:
            k = QRectF(self.x - 130 * s, self.boden - 230 * s, 260 * s, 230 * s)
        if self.sack_x is not None:
            k = k.united(QRectF(self.sack_x - 60 * s, self.boden - 110 * s, 120 * s, 110 * s))
        if self.w.zeige_figur:
            x, y = wichtel_hand(self.w)
            k = k.united(QRectF(x - 70 * s, y - 40 * s, 140 * s, 160 * s))
        if self.ring > 0:
            w = (60 + 300 * self.ring) * s
            k = k.united(QRectF(self.ring_x - w, self.ring_y - w, 2 * w, 2 * w))
        if self.muetze:
            k = k.united(QRectF(self.muetze[0] - 50 * s, self.muetze[1] - 60 * s, 110 * s, 70 * s))
        return k

    def figur_sichtbar(self):
        if self.sitzt:
            return True
        return super().figur_sichtbar()

    def schreck_ablauf(self):
        self.ring = 0.0
        self.schlaeft = self.flucht = False
        self.muetze = None
        if self.geschleift:
            self.w.neigung = 0.0
            self.w.y = self.boden
        self.geschleift = False
        self.riese = 0.0
        self.handglocke = self.w.zeige_figur
        if self.sitzt:
            self.sitzt = False
        self.pose_fest = {}
        self.sack_x = None
        self.w.hopp = 0.0
        return self.schreck_alle()
