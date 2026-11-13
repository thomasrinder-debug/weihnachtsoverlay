import math

from PyQt6.QtCore import QPointF, QRectF

from zeichnen.figur import Pose, zeichne_sack
from zeichnen.figuren import Wichtel
from zeichnen.hoersaal import (zeichne_beamer, zeichne_lichtkegel, zeichne_projektion, zeichne_sack_mit_beinen,
                               zeichne_schatten)

from .basis import Gehe, Jeweils, Mit, Nebenbei, Setze, Springe, Stehe, Szene, Tu, Wandel, WarteBis
from .hs_basis import Publikumsblick

PROJ_B, PROJ_H = 240, 440       # Projektionsfläche am Rand in Einheiten
SCHATTEN = 1.9                  # Vergrößerung des Schattens


class HsBeamer(Szene):
    """Ein Wichtel stellt einen Minibeamer auf, sein Schatten an der Seitenwand ist riesig.
    Hasenohren, dann ein Geweih. Der Weihnachtsmann kommt, sieht das Schattenmonster und
    erstarrt, nur die Knie schlottern. Der Wichtel macht Buh, der Schatten wächst, der
    Weihnachtsmann hechtet kopfüber in seinen Sack, der strampelnd davonhüpft."""
    name, titel, reihenfolge = 'hs_beamer', 'Schattenmonster', 1001

    def vorbereiten(self):
        r, s = self.richtung, self.s
        self.e = -r                                            # Rand mit der Projektion
        self.ex = self.geo.left() if self.e < 0 else self.geo.right()
        self.bx = self.vom_rand(0.24)
        self.licht = 0.0
        self.ohren = self.geweih = self.krallen = 0.0
        self.sgross = SCHATTEN
        self.traegt = True
        self.sack = None             # (x, Bauch) des Sacks am Boden
        self.strampeln = 0.0
        self.w = self.dazu('w', Wichtel, groesse=0.62)
        self.w.x = self.aussen(self.e)
        self.w.richtung = r
        self.zeige_figur = False
        self.x = self.aussen(self.e)

    def ablauf(self):
        r, e, s = self.richtung, self.e, self.s
        w = self.w
        wx = self.bx + e * 70 * s
        self.xm = self.ex + r * 330 * s

        def spiel(art):
            def pose(d, u):
                return Pose(arm_v=-172 + 8 * math.sin(u * 9), arm_h=-168 - 8 * math.sin(u * 9), kopf_vorn=False,
                            mund_offen=u % 0.6 < 0.3, hub=-abs(math.sin(u * 6)) * 3)
            return pose

        def schlottern(sz, u):
            k = math.sin(u * 40) * 9
            return Pose(kopf_vorn=True, schreck=0.7, sorge=1.0, blick_y=-0.9, blick_x=0.6 * e * 0,
                        arm_v=20, arm_h=-20, bein_v=-6 + k, bein_h=6 - k, auge_zu=False)

        return [
            Mit('w', Gehe(bis=self.bx, tempo=1.9)),
            Setze(traegt=False),
            Mit('w', Setze(richtung=e)),
            Mit('w', Stehe(0.25, Pose(arm_v=-40, arm_h=-30, auge_zu=True))),
            Wandel(0.25, licht=1.0),
            Mit('w', Gehe(bis=wx, tempo=0.6)),
            Mit('w', Stehe(0.35, lambda d, u: Pose(kopf_vorn=True, schreck=0.3, mund_offen=True,
                                                    blick_x=e))),
            # Versuch 1: Hasenohren
            Nebenbei(Mit('w', Stehe(1.0, spiel('ohren')))),
            Wandel(0.25, ohren=1.0),
            Jeweils(0.75, lambda sz, u: setattr(sz, 'ohren', 0.8 + 0.2 * math.sin(u * 12))),
            # Versuch 2: Geweih, dabei kommt der Weihnachtsmann
            Setze(zeige_figur=True),
            Nebenbei(Gehe(bis=self.xm, tempo=1.3), Setze(richtung=e),
                     Stehe(0.35, Pose(blick_y=-0.8, auge_zu=False, arm_v=10))),
            Wandel(0.25, ohren=0.0, geweih=1.0),
            Nebenbei(Mit('w', Stehe(1.3, spiel('geweih')))),
            Jeweils(1.3, lambda sz, u: setattr(sz, 'geweih', 0.85 + 0.15 * math.sin(u * 8))),
            WarteBis(lambda sz: not sz.nebenbei),
            # Erwartungspause: er erstarrt, nur die Knie schlottern
            Stehe(0.25, Pose(kopf_vorn=True, schreck=1.0, sorge=1.0, blick_y=-1.0)),
            Stehe(1.0, schlottern),
            # Knall: Buh!
            Mit('w', Setze(pose=Pose(arm_v=-140, arm_h=-140, mund_offen=True))),
            Mit('w', Setze(hopp=lambda d: 14 * d.s)),
            Wandel(0.12, geweih=0.0, krallen=1.0, sgross=SCHATTEN * 1.3),
            Mit('w', Setze(hopp=0.0)),
            Tu(lambda sz: sz.sack_ab()),
            Springe(lambda sz: (sz.sack[0], sz.boden - 90 * s), 0.55, 210),
            Tu(lambda sz: sz.hinein()),
            Wandel(0.15, krallen=0.4, sgross=SCHATTEN),
            Jeweils(0.5, lambda sz, u: setattr(sz, 'strampeln', 1.0)),
            # Der Sack hüpft strampelnd davon
            Nebenbei(Mit('w', Setze(richtung=e)), Mit('w', Stehe(0.6, Pose(arm_v=-140, arm_h=-140)))),
            Jeweils(1.3, lambda sz, u: sz.sack_huepft(u)),
            Setze(sack=None),
            Wandel(0.15, krallen=0.0),
            # Reaktion: der Wichtel dreht sich um, unschuldiger Blick
            Mit('w', Publikumsblick(0.8)),
            Wandel(0.2, licht=0.0),
            Setze(traegt=True),
            Mit('w', Gehe(bis=None, tempo=2.0)),
        ]

    def sack_ab(self):
        self.sack = [self.x + self.e * 70 * self.s, 1.0]
        self.pose_fest = {'sack': False}
        self.striche = False

    def hinein(self):
        self.zeige_figur = False
        self.y = self.boden
        self.neigung = 0.0
        self.sack[1] = 1.35

    def sack_huepft(self, u):
        if self.sack:
            self.sack[0] += self.e * self.tempo * 2.2 / 60
            self.strampeln = 1.0

    def weiter(self, dt):
        if self.aktuell.__class__ is Springe and self.zeige_figur and self.sack:
            u = self.t - self.tz
            self.neigung = min(1.0, u / 0.5) * 180 * 1
        if self.sack and not self.zeige_figur:
            u = (self.t * 3.2) % 1.0
            self.sack_hopp = math.sin(u * math.pi) * 22 * self.s if self.strampeln else 0.0

    sack_hopp = 0.0

    def wichtel_hand(self):
        w = self.w
        return w.x + w.richtung * 30 * w.s, w.y - 64 * w.s

    def lichtquelle(self):
        if self.traegt:
            x, y = self.wichtel_hand()
            return x, y, self.w.richtung, 0.6
        return self.bx, self.boden, self.e, 0.8

    def zeichne_hinten(self, p):
        s, e = self.s, self.e
        x, y, rb, g = self.lichtquelle()
        ox, oy = x + rb * 31 * s * g, y - 23 * s * g
        rand = self.ex - e * 10 * s
        rechteck = self.projektion()
        zeichne_projektion(p, rechteck, self.licht)
        zeichne_lichtkegel(p, QPointF(ox, oy), QPointF(rand, rechteck.top()), QPointF(rand, rechteck.bottom()),
                           self.licht)
        if self.licht > 0.3 and self.w.zeige_figur:
            p.save()
            p.translate(rechteck.center().x(), self.boden - 26 * s)
            g = self.sgross * (self.licht - 0.3) / 0.7
            p.scale(s * g * -e, s * g)
            p.setOpacity(min(1.0, (self.licht - 0.3) / 0.5))
            zeichne_schatten(p, self.ohren, self.geweih, self.krallen, self.t)
            p.restore()

    def projektion(self):
        s, e = self.s, self.e
        x0 = self.ex if e < 0 else self.ex - PROJ_B * s
        return QRectF(x0, self.boden - PROJ_H * s, PROJ_B * s, (PROJ_H - 14) * s)

    def zeichne_vorn(self, p):
        s = self.s
        x, y, rb, g = self.lichtquelle()
        if self.w.zeige_figur or not self.traegt:
            p.save()
            p.translate(x, y + (8 * s if self.traegt else 0))
            p.scale(s * g * rb, s * g)
            zeichne_beamer(p, self.licht > 0.5)
            p.restore()
        if self.sack:
            sx, bauch = self.sack
            p.save()
            p.translate(sx, self.boden - self.sack_hopp)
            p.scale(s * self.e, s)
            if bauch > 1.0:
                zeichne_sack_mit_beinen(p, self.strampeln, self.t, 1.0)
            else:
                zeichne_sack(p, 0, -48, -8, 1.25)
            p.restore()

    def grenzen_extra(self):
        s = self.s
        k = QRectF()
        if self.licht > 0:
            x, y, rb, g = self.lichtquelle()
            k = self.projektion().united(QRectF(x - 40 * s, y - 60 * s, 80 * s, 70 * s))
            k = k.adjusted(0, -120 * s, 0, 0)
        if self.w.zeige_figur:
            x, y, rb, g = self.lichtquelle()
            k = k.united(QRectF(x - 40 * s, y - 60 * s, 80 * s, 70 * s))
        if self.sack:
            k = k.united(QRectF(self.sack[0] - 90 * s, self.boden - 250 * s, 180 * s, 250 * s))
        return k

    def figur_sichtbar(self):
        return super().figur_sichtbar() and self.zeige_figur

    def schreck_ablauf(self):
        self.pose_fest = {}
        self.neigung = 0.0
        self.ohren = self.geweih = self.krallen = 0.0
        if not self.zeige_figur and self.sack:
            self.sack = None
        self.licht = 0.0
        self.traegt = True
        self.w.hopp = 0.0
        return self.schreck_alle()

