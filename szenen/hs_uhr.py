import math

from PyQt6.QtCore import QRectF
from PyQt6.QtGui import QColor

from zeichnen.figur import Pose
from zeichnen.grundlagen import blinzeln, kreis
from zeichnen.hoersaal import figur_trafo, zeichne_bart_lang, zeichne_schallringe, zeichne_wanduhr

from .basis import Gehe, Jeweils, Nebenbei, Setze, Stehe, Szene, Tu, Wandel
from .hs_basis import Plumps, Publikumsblick

R = 62                       # Radius der Uhr in Einheiten
STAUB = [QColor(225, 220, 210, 210), QColor(200, 195, 185, 190)]


class HsUhr(Szene):
    """Die Uhr an der Wand steht kurz vor Schluss, der Sekundenzeiger zuckt nur hin und her.
    Antippen: sie wackelt. Draufhauen: der Minutenzeiger klappt herunter. Er springt hoch und
    dreht ihn mit Schwung auf Schluss, Triumph. Stille. Dann rast die Uhr los, die Zeiger
    werden zur Scheibe, und sein Bart wächst im Zeitraffer bis auf den Boden. Er dreht sich
    zum Gehen, tritt auf den Bart und schlägt der Länge nach hin."""
    name, titel, reihenfolge = 'hs_uhr', 'Die Uhr steht', 1006

    def vorbereiten(self):
        r, s = self.richtung, self.s
        e = -r
        rand = self.geo.left() if e < 0 else self.geo.right()
        self.ux = rand - e * (R + 40) * s
        self.uy = self.boden - 300 * s
        self.ein = 0.0
        self.minute, self.stunde, self.sekunde = 330.0, 357.0, 0.0
        self.zittern = 0.0
        self.wackel = 0.0           # Amplitude, klingt ab
        self.haengt = False         # Minutenzeiger baumelt
        self.rast = 0.0             # 0..1: Uhr rast
        self.bart = 0.0
        self.ring = 0.0
        self.t_haengt = 0.0

    def ablauf(self):
        r, s = self.richtung, self.s
        self.x = self.aussen(-r)
        xu = self.ux + r * 112 * s

        def guckt(sz, u):
            return Pose(blick_y=-1.0, blick_x=-1, auge_zu=blinzeln(sz.t), arm_v=10)

        def hops(hoehe, dauer, schlag):
            def f(sz, u):
                k = min(1.0, u / dauer)
                sz.hopp = math.sin(k * math.pi) * hoehe * s
                return Pose(arm_v=-170 if k < 0.6 else -120, arm_v_x=16, mund_offen=schlag, bein_v=-20 * k,
                            bein_h=20 * k, blick_y=-1)
            return f

        def triumph(sz, u):
            return Pose(kopf_vorn=True, arm_v=-150, arm_h=-150, arm_v_x=14, bein_v=-14, bein_h=14,
                        mund_offen=u < 0.4, auge_zu=0.5 < u < 0.62)

        def schaut_runter(sz, u):
            return Pose(kopf_vorn=True, arm_v=-150 + 100 * min(1.0, u / 0.4), arm_h=-150 + 100 * min(1.0, u / 0.4),
                        schreck=min(1.0, u * 2), sorge=1.0, blick_y=1.0, bein_v=-14, bein_h=14)

        return [
            Wandel(0.3, ein=1.0),
            Gehe(bis=xu),
            Setze(richtung=-r),
            Stehe(0.6, guckt),
            # Versuch 1: antippen
            Setze(richtung=-r),
            Stehe(0.4, hops(40, 0.4, False)),
            Tu(lambda sz: sz.stoss(8)),
            Stehe(0.6, guckt),
            # Versuch 2: draufhauen, der Minutenzeiger klappt herunter
            Stehe(0.45, hops(70, 0.45, True)),
            Tu(lambda sz: sz.stoss(22)),
            Setze(haengt=True, t_haengt=lambda sz: sz.t),
            Stehe(0.6, lambda sz, u: Pose(blick_y=-1.0, blick_x=-1, sorge=1.0, arm_v=20, arm_h=-20)),
            # Versuch 3: mit Schwung auf Schluss gedreht
            Stehe(0.55, hops(95, 0.55, True)),
            Setze(haengt=False),
            Jeweils(0.5, lambda sz, u: sz.drehen(u)),
            Setze(minute=360.0, stunde=360.0),
            Stehe(0.7, triumph),
            # Erwartungspause: Stille
            Stehe(0.45, Pose(kopf_vorn=True, arm_v=-150, arm_h=-150, auge_zu=True, bein_v=-14, bein_h=14)),
            # Knall: die Uhr rast, der Bart wächst
            Wandel(0.2, rast=1.0),
            Nebenbei(Wandel(1.2, bart=1.0)),
            Stehe(1.25, schaut_runter),
            Wandel(0.15, rast=0.0),
            Stehe(0.35, Pose(kopf_vorn=True, schreck=1.0, sorge=1.0, blick_y=1.0, arm_v=20, arm_h=-20)),
            # Er will gehen und tritt auf den Bart
            Setze(richtung=r),
            Gehe(dauer=0.3, tempo=0.5),
            Tu(lambda sz: setattr(sz, 'striche', True)),
            Plumps(80, 0.3, 40, Pose(arm_v=-170, arm_h=-170, schreck=1.0, mund_offen=True, bein_v=10, bein_h=-30)),
            Tu(lambda sz: sz.platsch()),
            Setze(ring=0.35),
            Stehe(0.7, Pose(arm_v=-170, arm_h=-170, auge_zu=True, bein_v=10, bein_h=-30)),
            Setze(ring=0.0),
            Wandel(0.35, neigung=0.0, hopp=0.0),
            Publikumsblick(0.6, sorge=0.6),
            Setze(richtung=-r),
            Gehe(bis=None, tempo=1.3),
            Wandel(0.3, ein=0.0),
        ]

    def stoss(self, staerke):
        self.wackel = staerke

    def drehen(self, u):
        f = min(1.0, u / 0.5)
        self.minute = 180 + (540 - 180) * (1 - (1 - f) ** 2)
        self.stunde = 357 + 3 * f

    def platsch(self):
        s = self.s
        x = self.x + self.richtung * 150 * s
        self.streue(x, self.boden - 6 * s, 14, STAUB, tempo=180, dauer=0.6, r=(7, 14))

    def weiter(self, dt):
        t = self.t
        self.wackel *= max(0.0, 1 - 3 * dt)
        self.zittern = math.sin(t * 22) * self.wackel + math.sin(t * 70) * 3 * self.rast
        if self.rast > 0:
            self.minute += 2600 * self.rast * dt
            self.stunde += 220 * self.rast * dt
            self.sekunde += 9000 * self.rast * dt
        else:
            # der Sekundenzeiger zuckt nur hin und her
            if not self.erschreckt:
                self.sekunde = 6 if (t % 1.0) < 0.5 else 0
        if self.haengt:
            self.minute = 180 + math.sin(t * 6) * 25 * math.exp(-0.5 * max(0.0, t - self.t_haengt)) \
                if hasattr(self, 't_haengt') else 180
            if not hasattr(self, 't_haengt'):
                self.t_haengt = t

    def zeichne_hinten(self, p):
        if self.ein <= 0:
            return
        s = self.s
        p.save()
        p.translate(self.ux, self.uy + (1 - self.ein) * -260 * s)
        p.scale(s, s)
        p.setPen(QColor(90, 70, 50))
        p.drawLine(0, -R - 4, 0, -R - 40)
        p.setPen(QColor(0, 0, 0, 0))
        zeichne_wanduhr(p, R, self.minute, self.stunde, self.sekunde, self.zittern)
        if self.rast > 0.2:
            # Bewegungsunschärfe der rasenden Zeiger
            p.setBrush(QColor(40, 40, 40, int(70 * self.rast)))
            kreis(p, 0, 0, R * 0.74)
        p.restore()
        if self.ring > 0:
            zeichne_schallringe(p, self.ux, self.uy, self.richtung, self.ring, (self.t * 1.8) % 1.0, s, 90)

    def zeichne_vorn(self, p):
        if self.bart <= 0 or not self.zeige_figur:
            return
        p.save()
        p.setTransform(figur_trafo(self), True)
        if self.pose.kopf_vorn:
            p.translate(-14, 0)
        zeichne_bart_lang(p, self.bart, 0.0, self.t)
        p.restore()

    def grenzen_extra(self):
        s = self.s
        k = QRectF(self.ux - (R + 20) * s, self.uy - (R + 50) * s - (1 - self.ein) * 260 * s,
                   2 * (R + 20) * s, 2 * (R + 30) * s + 20 * s)
        if self.bart > 0:
            k = k.united(figur_trafo(self).mapRect(QRectF(-20, -150, 260, 160)))
        if self.ring > 0:
            w = (60 + 300 * self.ring) * s
            k = k.united(QRectF(self.ux - w, self.uy - w, 2 * w, 2 * w))
        if abs(self.neigung) > 1:
            k = k.united(QRectF(self.x - 350 * s, self.boden - 300 * s, 700 * s, 300 * s))
        return k

    def schreck_ablauf(self):
        self.rast = 0.0
        self.ring = 0.0
        self.neigung, self.hopp = 0.0, 0.0
        return [Setze(striche=False), *super().schreck_ablauf(), Wandel(0.25, ein=0.0)]

