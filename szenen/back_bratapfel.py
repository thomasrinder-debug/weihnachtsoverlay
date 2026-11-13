import math

from PyQt6.QtCore import QRectF
from PyQt6.QtGui import QColor

from zeichnen.baeckerei import HOLZ, HOLZ_DUNKEL, zeichne_bratapfel, zeichne_teller
from zeichnen.figur import Pose
from zeichnen.grundlagen import KEIN_STIFT, blinzeln, linear, radial
from zeichnen.requisiten import zeichne_muetze_lose, zeichne_schneehaufen

from .back_bausteine import Flug, kopf, publikum
from .basis import Gehe, Jeweils, Nebenbei, Setze, Stehe, Szene, Tu, Wandel

DAMPF = [QColor(255, 255, 255, 200), QColor(240, 244, 250, 180)]
HOCKER = 46


class BackBratapfel(Szene):
    """Ein dampfender Bratapfel auf einem Hocker. Er tippt hinein und verbrennt sich den Finger,
    pustet und bekommt den Dampf ins Gesicht. Dann stopft er sich den ganzen Apfel in den Mund,
    kaut selig – und läuft knallrot an, Dampf zischt aus den Ohren, die Mütze fliegt wie ein
    Topfdeckel davon. Er hechtet kopfüber in einen Schneehaufen, es zischt gewaltig, die Mütze
    landet auf seinem Stiefel, und er versinkt im schmelzenden Schnee."""
    name, titel, reihenfolge = 'back_bratapfel', 'Bratapfel', 806

    def vorbereiten(self):
        r = self.richtung
        self.x = self.aussen(-r)
        self.x0 = self.vom_rand(0.14)
        self.hx = self.x0 + r * 82 * self.s
        self.sx = self.vom_rand(0.035)
        self.schnee_h = 84.0
        self.pose_fest = {'sack': False}
        self.apfel = 'teller'          # 'teller', 'flug', None
        self.apfel_xy = [0.0, 0.0, 0.0]
        self.rot = 0.0
        self.dampf_bis = -1.0
        self.muetze = None             # [x, y, winkel] lose Mütze
        self.takt = 0.0
        self.muetze_auf = False

    def apfel_ort(self):
        return self.hx, self.boden - (HOCKER + 3) * self.s

    def ablauf(self):
        r, s = self.richtung, self.s

        def finger(sz, u):
            if u < 0.35:
                sz.pose = Pose(arm_v=-70 + 25 * u / 0.35, arm_v_x=14, blick_y=0.6)
                return
            v = u - 0.35
            sz.striche = v < 0.35
            sz.hopp = math.sin(math.pi * min(1.0, v / 0.3)) * 30 * s if v < 0.3 else 0.0
            sz.pose = Pose(arm_v=-165 + 25 * math.sin(v * 40), arm_v_x=16, kopf_vorn=True, schreck=1.0 if v < 0.4
                           else 0.3, mund_offen=True, bein_v=-20 if v < 0.3 else 0)

        def pusten(sz, u):
            sz.neigung = 12 * min(1.0, u / 0.2)
            sz.pose = Pose(arm_v=-30, arm_v_x=14, mund_offen=True, blick_y=0.6, auge_zu=u > 0.2)
            if u < 0.6 and int(u * 20) != int((u - 1 / 60) * 20):
                x, y = sz.apfel_ort()
                sz.streue(x, y - 40 * s, 3, DAMPF, tempo=90, dauer=0.6, r=(5, 10),
                          richtung=0.0 if r > 0 else math.pi, streuung=0.4)

        def husten(sz, u):
            if u < 0.02:
                x, y = kopf(sz)
                sz.streue(x, y, 18, DAMPF, tempo=90, dauer=0.9, r=(10, 22))
            sz.neigung = -8
            sz.pose = Pose(kopf_vorn=True, auge_zu=True, mund_offen=(u * 8) % 2 < 1, arm_v=-120, arm_v_x=14,
                           sorge=0.8)

        def kauen(sz, u):
            sz.pose = Pose(kopf_vorn=True, auge_zu=True, mund_offen=(u * 6) % 2 < 1, arm_v=-20, arm_v_x=14,
                           wipp=math.sin(u * 12) * 3)

        def gluehen(sz, u):
            sz.rot = min(1.0, u / 0.25)
            sz.hopp = abs(math.sin(u * 9)) * 26 * s
            sz.pose = Pose(kopf_vorn=True, schreck=1.0, mund_offen=True, muetze=False,
                           arm_v=-150 + 30 * math.sin(u * 20), arm_h=-140 - 30 * math.sin(u * 20), arm_v_x=20,
                           bein_v=-25 * math.sin(u * 18), bein_h=25 * math.sin(u * 18))

        def hecht(sz, u):
            f = min(1.0, u / 0.55)
            if u < 0.02:
                sz.x0_, sz.y0_ = sz.x, sz.boden
            x1, y1 = sz.sx, sz.boden - 150 * s
            sz.x = sz.x0_ + (x1 - sz.x0_) * f
            sz.y = sz.y0_ + (y1 - sz.y0_) * f - 160 * s * 4 * f * (1 - f)
            sz.hopp = 0.0
            sz.neigung = 180 * f
            sz.pose = Pose(arm_v=-170, arm_h=-170, bein_v=10, bein_h=-10, mund_offen=True, muetze=False,
                           kopf_vorn=True, schreck=1.0)

        def zischen(sz, u):
            sz.schnee_h = 84 - 26 * min(1.0, u / 1.4)
            sz.rot = max(0.0, 1 - u / 1.0)
            k = math.sin(u * 22) * 30 * max(0.0, 1 - u / 1.2)
            sz.pose = Pose(bein_v=k, bein_h=-k, arm_v=-170, arm_h=-170, muetze=False)
            if int(u * 30) != int((u - 1 / 60) * 30) and u < 1.1:
                sz.streue(sz.sx + math.sin(u * 13) * 30 * s, sz.boden - sz.schnee_h * s, 3, DAMPF, tempo=160,
                          dauer=1.0, r=(10, 24), richtung=-math.pi / 2, streuung=0.6)

        def ziel_stiefel(sz):
            return sz.sx, sz.boden - 150 * s - 8 * s

        return [
            Gehe(bis=self.x0),
            Stehe(0.3, lambda sz, u: Pose(blick_y=0.6, auge_zu=blinzeln(sz.t))),
            Jeweils(1.15, finger),
            Setze(striche=False, hopp=0.0),
            Jeweils(0.8, pusten),
            Jeweils(0.6, husten),
            Setze(neigung=0.0),
            publikum(0.7, sorge=0.5),
            Stehe(0.25, Pose(arm_v=-45, arm_v_x=14, blick_y=0.6, mund_offen=True)),
            Setze(apfel='flug', apfel_xy=lambda sz: [*sz.apfel_ort(), 0.0]),
            Flug('apfel_xy', lambda sz: kopf(sz, 18, -170), 0.3, 50, 360),
            Setze(apfel=None),
            Jeweils(1.0, kauen),
            Setze(pose_fest={'sack': False, 'muetze': False}, muetze=lambda sz: [*kopf(sz, 4, -215), 0.0],
                  dampf_bis=lambda sz: sz.t + 1.6, striche=True),
            Nebenbei(Flug('muetze', ziel_stiefel, 2.4, 420, 720)),
            Jeweils(0.9, gluehen),
            Setze(striche=False, hopp=0.0, richtung=-r),
            Jeweils(0.55, hecht),
            Jeweils(1.6, zischen),
            Setze(muetze_auf=True),
            Stehe(0.4, Pose(muetze=False, arm_v=-170, arm_h=-170)),
            Wandel(0.8, y=lambda sz: sz.boden + 260 * s, schnee_h=20.0),
        ]

    def schreck_ablauf(self):
        if self.neigung > 90:
            return [Wandel(0.5, y=self.boden + 260 * self.s)]
        self.dampf_bis = -1
        return [Setze(neigung=0.0, hopp=0.0, striche=False), *super().schreck_ablauf()]

    def weiter(self, dt):
        if self.muetze_auf and self.muetze:
            self.muetze[0], self.muetze[1] = self.x, self.y - 8 * self.s
        if self.t < self.dampf_bis:
            self.takt += dt
            if self.takt > 0.04:
                self.takt = 0.0
                for z in (-1, 1):
                    x, y = kopf(self, 6 + z * 32, -190)
                    self.streue(x, y, 1, DAMPF, tempo=260, dauer=0.5, r=(5, 12),
                                richtung=math.pi / 2 - z * math.pi / 2 - math.pi / 8 * (1 if z > 0 else -1),
                                streuung=0.25)
        if self.apfel == 'teller' and int(self.t * 6) != int((self.t - dt) * 6):
            x, y = self.apfel_ort()
            self.streue(x, y - 34 * self.s, 1, DAMPF, tempo=30, dauer=1.0, r=(4, 9), richtung=-math.pi / 2,
                        streuung=0.3)

    def zeichne_hinten(self, p):
        s = self.s
        p.save()
        p.translate(self.hx, self.boden)
        p.scale(s, s)
        p.setBrush(linear(-20, 0, 20, 0, HOLZ.lighter(110), HOLZ_DUNKEL))
        for x in (-16, 12):
            p.drawRoundedRect(QRectF(x - 2, -HOCKER + 4, 6, HOCKER - 4), 2, 2)
        p.drawRoundedRect(QRectF(-24, -HOCKER, 48, 7), 3, 3)
        p.translate(0, -HOCKER)
        zeichne_teller(p, 26)
        if self.apfel == 'teller':
            zeichne_bratapfel(p, 22)
        p.restore()

    def zeichne_vorn(self, p):
        s = self.s
        if self.rot > 0 and self.zeige_figur and self.neigung < 90:
            x, y = kopf(self)
            c = QColor(230, 30, 30, int(170 * self.rot))
            c0 = QColor(230, 30, 30, 0)
            p.setPen(KEIN_STIFT)
            p.setBrush(radial(x, y, 34 * s, c, c0))
            p.drawEllipse(QRectF(x - 34 * s, y - 34 * s, 68 * s, 68 * s))
        if self.apfel == 'flug':
            x, y, w = self.apfel_xy
            p.save()
            p.translate(x, y)
            p.rotate(w)
            p.scale(s, s)
            zeichne_bratapfel(p, 22)
            p.restore()
        zeichne_schneehaufen(p, self.sx, self.boden, 150 * s, self.schnee_h * s)
        if self.muetze:
            x, y, w = self.muetze
            p.save()
            p.translate(x, y)
            p.rotate(w)
            p.scale(s, s)
            zeichne_muetze_lose(p)
            p.restore()

    def grenzen_extra(self):
        s = self.s
        k = QRectF(self.hx - 30 * s, self.boden - 100 * s, 60 * s, 100 * s)
        k = k.united(QRectF(self.sx - 80 * s, self.boden - 100 * s, 160 * s, 100 * s))
        if self.muetze:
            k = k.united(QRectF(self.muetze[0] - 60 * s, self.muetze[1] - 70 * s, 120 * s, 100 * s))
        if self.apfel == 'flug':
            k = k.united(QRectF(self.apfel_xy[0] - 30 * s, self.apfel_xy[1] - 50 * s, 60 * s, 60 * s))
        if self.zeige_figur and self.neigung > 90:
            k = k.united(QRectF(self.x - 130 * s, self.y - 30 * s, 260 * s, 300 * s))
        return k
