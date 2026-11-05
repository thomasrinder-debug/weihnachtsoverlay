import math
import random

from PyQt6.QtCore import QPointF, QRectF
from PyQt6.QtGui import QColor, QPainterPath

from zeichnen.figur import Pose
from zeichnen.figuren import Pinguin
from zeichnen.grundlagen import (KEIN_PINSEL, KEIN_STIFT, ROT, WEISS, blinzeln, kreis, linear, radial, stift)

from .basis import Gehe, Jeweils, Mit, Schritt, Setze, Stehe, Szene, Tu, Wandel, Warte

FISCH = QColor('#7FB8E0')
GLITZER = [WEISS, QColor('#CDEBFF')]


class Fang(Schritt):
    """Etwas fliegt in hohem Bogen aus dem Eisloch zu ziel(szene)."""

    def __init__(self, was, ziel, dauer=0.8, hoehe=160):
        self.was, self.ziel, self.dauer, self.hoehe = was, ziel, dauer, hoehe

    def beginn(self, sz):
        sz.fang = [self.was, sz.lx, sz.boden, 0.0]
        self.x0, self.y0 = sz.lx, sz.boden

    def weiter(self, sz, u, dt):
        x1, y1 = self.ziel(sz)
        f = min(1.0, u / self.dauer)
        sz.fang[1] = self.x0 + (x1 - self.x0) * f
        sz.fang[2] = self.y0 + (y1 - self.y0) * f - self.hoehe * sz.s * 4 * f * (1 - f)
        sz.fang[3] += 500 * dt


class PinguinAngeln(Szene):
    """Ein Pinguin angelt am Eisloch. Zuerst zieht er eine Ringelsocke heraus und wirft sie
    verdutzt weg, dann springt ihm ein Fisch auf den Kopf. Er schnappt ihn sich glücklich
    und watschelt satt davon."""
    name, titel, reihenfolge = 'angeln', 'Pinguin angelt', 45

    def vorbereiten(self):
        self.zeige_figur = False
        r = self.richtung
        self.pg = self.dazu('pg', Pinguin, groesse=0.8, vorn=True)
        self.pg.richtung = r
        self.lx = self.vom_rand(random.uniform(0.17, 0.2))     # Eisloch
        self.loch = 0.0
        self.rute = False
        self.zupfen = 0.0
        self.fang = None        # ['socke'|'fisch', x, y, drehung]

    def ablauf(self):
        r, s = self.richtung, self.s
        sitzen = lambda d, u: Pose(arm_v=-70, arm_h=10, bein_v=-60, bein_h=-50, auge_zu=blinzeln(d.t))  # noqa: E731
        return [
            Wandel(0.5, loch=1.0),
            Mit('pg', Gehe(bis=self.lx - r * 70 * s, tempo=0.5)),
            Mit('pg', Setze(hopp=lambda d: -14 * d.s)),
            Setze(rute=True),
            Mit('pg', Stehe(1.6, sitzen)),
            Jeweils(0.6, lambda sz, u: setattr(sz, 'zupfen', math.sin(u * 30))),
            Setze(zupfen=0.0),
            Mit('pg', Stehe(0.3, Pose(arm_v=-150, arm_h=10, bein_v=-60, bein_h=-50, kopf_vorn=True,
                                      mund_offen=True))),
            Fang('socke', lambda sz: (sz.lx - r * 40 * s, sz.boden - 150 * s), 0.6, 80),
            Mit('pg', Stehe(1.2, lambda d, u: Pose(arm_v=-150, arm_h=10, bein_v=-60, bein_h=-50, kopf_vorn=True,
                                                   sorge=1.0, blick_y=-1, blick_x=-0.5,
                                                   auge_zu=0.6 < u < 0.72))),
            Fang('socke', lambda sz: (sz.aussen(r), sz.boden - 300 * s), 0.9, 120),
            Setze(fang=None),
            Mit('pg', Stehe(1.4, sitzen)),
            Jeweils(0.8, lambda sz, u: setattr(sz, 'zupfen', math.sin(u * 40))),
            Setze(zupfen=0.0),
            Fang('fisch', lambda sz: sz.kopf(), 0.6, 120),
            Mit('pg', Stehe(1.0, lambda d, u: Pose(arm_v=-70, arm_h=10, bein_v=-60, bein_h=-50, kopf_vorn=True,
                                                   schreck=0.5, blick_y=-1))),
            Setze(fang=None, rute=False),
            Mit('pg', Stehe(1.0, lambda d, u: Pose(bein_v=-60, bein_h=-50, auge_zu=True,
                                                   mund_offen=(u * 6) % 2 < 1))),
            Mit('pg', Setze(hopp=0.0)),
            Mit('pg', Stehe(0.6, Pose(kopf_vorn=True, auge_zu=True, arm_v=-60, arm_h=-60))),
            Mit('pg', Gehe(bis=self.aussen(-r), tempo=0.6)),
            Wandel(0.4, loch=0.0),
        ]

    def schreck_ablauf(self):
        self.nebenbei.clear()
        self.fang = None
        pg = self.pg
        if not pg.figur_sichtbar():
            return [Wandel(0.3, loch=0.0)]
        # Kopfsprung ins Eisloch
        return [Setze(rute=False), Mit('pg', Setze(hopp=0.0, striche=True,
                                                    pose=Pose(kopf_vorn=True, schreck=1.0, arm_v=-150, arm_h=-150))),
                Warte(0.2), Mit('pg', Setze(striche=False)),
                Mit('pg', Wandel(0.25, x=lambda d: d.sz.lx, neigung=180, hopp=lambda d: 60 * d.s)),
                Mit('pg', Wandel(0.35, hopp=lambda d: -200 * d.s)), Mit('pg', Setze(zeige_figur=False)),
                Tu(lambda sz: sz.streue(sz.lx, sz.boden - 6 * sz.s, 14, GLITZER, tempo=160, dauer=0.5, r=(3, 6))),
                Wandel(0.3, loch=0.0)]

    def kopf(self):
        q = self.pg.trafo().map(QPointF(0, -140))
        return q.x(), q.y()

    def spitze(self):
        q = self.pg.trafo().map(QPointF(40, -150))
        return q.x(), q.y()

    def zeichne_hinten(self, p):
        s = self.s
        if self.loch > 0:
            p.setBrush(linear(0, self.boden - 12 * s, 0, self.boden, QColor('#E9F4FF'), QColor('#B8D3EE')))
            p.drawEllipse(QRectF(self.lx - 46 * s * self.loch, self.boden - 12 * s, 92 * s * self.loch, 16 * s))
            p.setBrush(linear(0, self.boden - 8 * s, 0, self.boden, QColor('#1C3A5E'), QColor('#0B1A2E')))
            p.drawEllipse(QRectF(self.lx - 30 * s * self.loch, self.boden - 8 * s, 60 * s * self.loch, 10 * s))

    def zeichne_vorn(self, p):
        s = self.s
        if self.rute and self.pg.zeige_figur:
            hx, hy = self.pg.trafo().map(QPointF(6, -60)).x(), self.pg.trafo().map(QPointF(6, -60)).y()
            sx, sy = self.spitze()
            p.setPen(stift(QColor('#6B4423'), 3 * s))
            p.drawLine(QPointF(hx, hy), QPointF(sx, sy))
            p.setPen(stift(QColor(255, 255, 255, 170), 1 * s))
            ende = (self.fang[1], self.fang[2]) if self.fang else (self.lx, self.boden - 4 * s + self.zupfen * 4 * s)
            schnur = QPainterPath()
            schnur.moveTo(sx, sy)
            schnur.quadTo(sx + (ende[0] - sx) * 0.6, sy + 30 * s, *ende)
            p.setBrush(KEIN_PINSEL)
            p.drawPath(schnur)
            p.setPen(KEIN_STIFT)
            if not self.fang:
                p.setBrush(ROT)
                kreis(p, self.lx, self.boden - 6 * s + self.zupfen * 4 * s, 3.5 * s)
        if self.fang:
            was, x, y, dreh = self.fang
            p.save()
            p.translate(x, y)
            p.rotate(dreh)
            p.scale(s, s)
            if was == 'socke':
                socke = QPainterPath()
                socke.moveTo(-6, -18)
                socke.lineTo(6, -18)
                socke.lineTo(6, 4)
                socke.quadTo(18, 6, 16, 14)
                socke.lineTo(-6, 14)
                socke.closeSubpath()
                p.setBrush(QColor('#E8E8EE'))
                p.drawPath(socke)
                p.setBrush(QColor('#2A6FD6'))
                for k in range(3):
                    p.drawRect(QRectF(-6, -16 + k * 9, 12, 4))
            else:
                p.rotate(math.sin(self.t * 25) * 20)
                p.setBrush(radial(-4, -2, 16, FISCH.lighter(130), FISCH.darker(130)))
                p.drawEllipse(QRectF(-14, -7, 26, 14))
                schwanz = QPainterPath()
                schwanz.moveTo(-12, 0)
                schwanz.lineTo(-22, -8)
                schwanz.lineTo(-22, 8)
                schwanz.closeSubpath()
                p.drawPath(schwanz)
                p.setBrush(WEISS)
                kreis(p, 6, -2, 2.5)
                p.setBrush(QColor('#1F1F1F'))
                kreis(p, 6.6, -2, 1.2)
            p.restore()

    def grenzen_extra(self):
        s = self.s
        k = QRectF(self.lx - 120 * s, self.boden - 200 * s, 240 * s, 200 * s)
        if self.fang:
            k = k.united(QRectF(self.fang[1] - 30 * s, self.fang[2] - 30 * s, 60 * s, 60 * s))
        return k
