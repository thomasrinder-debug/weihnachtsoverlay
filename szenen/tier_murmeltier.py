import math

from PyQt6.QtCore import QPointF, QRectF
from PyQt6.QtGui import QColor

from zeichnen.figur import Pose
from zeichnen.grundlagen import KEIN_PINSEL, KEIN_STIFT, stift
from zeichnen.tiere import Murmeltier, zeichne_schneedecke, zeichne_stiefel

from .basis import (Erschrecke, Gehe, Hoppel, Jeweils, Mit, Nebenbei, Renne, Setze, Springe, Stehe, Szene, Tu,
                    Wandel, Warte, WarteNebenbei)
from .tier_gemeinsam import Flug, figur_mit_beinen, publikumsblick, puff

DECKE_B, DECKE_H = 170, 72


class Winterschlaf(Szene):
    """Ein Murmeltier schnarcht unter seiner Schneedecke. Er tippt es an, rüttelt, stemmt
    schließlich die Füße in den Schnee und reißt die Decke weg. Das Murmeltier richtet sich
    langsam auf, er beugt sich neugierig vor – Pause – und es pfeift ihm einen Warnpfiff ins
    Gesicht, der ihn rückwärts aus den Stiefeln bläst. Das Murmeltier nimmt die leeren Stiefel als
    Kopfkissen; die Decke kommt von draußen zurückgeflogen."""
    name, titel, reihenfolge = 'tier_murmeltier', 'Winterschlaf', 770

    def vorbereiten(self):
        r = self.richtung
        self.x = self.aussen(-r)
        self.mx = self.vom_rand(0.2)
        self.zug = 0.0
        self.wackel = 0.0
        self.deck = 0.0
        self.decke_hoch = 0.0
        self.decke_x = self.mx + self.richtung * 42 * self.s
        self.socken = False
        self.stiefel = None          # (x) stehen gelassene Stiefel
        self.ringe = -1.0            # Zeit seit dem Pfiff
        self.m = self.dazu('m', Murmeltier, schlaf=1.0, pfiff=0.0, recken=0.0)
        self.m.x, self.m.richtung = self.mx, -r
        self.schnarch = 0.0

    def zeichne_figur(self, p, zwischen=None):
        figur_mit_beinen(self, p, stiefel=not self.socken)

    def weiter(self, dt):
        m = self.m
        if m.schlaf > 0.5 and m.zeige_figur:
            self.schnarch += dt
            if self.schnarch > 1.1:
                self.schnarch = 0.0
                kx = m.x + m.richtung * 56 * m.s
                self.streue(kx, self.boden - 40 * m.s, 2, QColor(255, 255, 255, 200), tempo=25, dauer=1.2,
                            r=(3, 7), richtung=-math.pi / 2, streuung=0.4)
        if self.ringe >= 0:
            self.ringe += dt

    def ablauf(self):
        r, s = self.richtung, self.s
        steh = self.mx - r * 150 * s
        tippen = lambda sz, u: Pose(arm_v=-60 + 25 * abs(math.sin(u * 9)), arm_v_x=24, blick_y=0.7, hub=3)  # noqa: E731
        ziehen = lambda sz, u: Pose(arm_v=-82 + 4 * math.sin(u * 40), arm_h=-78, arm_v_x=26, bein_v=-28,  # noqa: E731
                                    bein_h=14, mund_offen=True, sorge=1.0)
        return [
            Wandel(0.3, deck=1.0),
            Gehe(bis=steh, tempo=1.0),
            Stehe(0.3, Pose(blick_y=0.8)),
            # 1. antippen
            Stehe(0.6, tippen),
            Stehe(0.4, lambda sz, u: Pose(kopf_vorn=True, blick_x=-r * 0.6, sorge=0.5)),
            # 2. rütteln
            Jeweils(0.7, lambda sz, u: (setattr(sz, 'wackel', math.sin(u * 40) * 6),
                                        setattr(sz, 'pose', Pose(arm_v=-75, arm_h=-70, arm_v_x=24,
                                                                 hub=2 * math.sin(u * 40), mund_offen=True)))),
            Setze(wackel=0.0),
            Stehe(0.35, Pose(blick_y=0.8, sorge=0.8)),
            # 3. Decke wegziehen
            Setze(neigung=-14.0),
            Nebenbei(Wandel(1.0, zug=35.0)),
            Stehe(1.0, ziehen),
            Wandel(0.12, zug=200.0, deck=0.0),
            Tu(lambda sz: puff(sz, sz.decke_x, sz.boden - 40 * sz.s, 18, 150)),
            Setze(neigung=0.0),
            Springe((steh - r * 30 * s, self.boden), 0.3, 25),
            Stehe(0.35, Pose(kopf_vorn=True, schreck=0.3)),
            # es wacht auf, er beugt sich vor
            Mit('m', Setze(schlaf=0.0, pose=Pose(auge_zu=True))),
            Mit('m', Wandel(0.5, recken=24.0)),
            Gehe(bis=steh + r * 10 * s, tempo=0.5),
            Setze(neigung=14.0, pose=Pose(blick_y=0.3)),
            Stehe(0.55, Pose(blick_y=0.3)),
            # der Pfiff
            Mit('m', Setze(pose=Pose())),
            Mit('m', Wandel(0.08, pfiff=1.0, recken=40.0)),
            Setze(ringe=0.0, neigung=0.0, stiefel=lambda sz: sz.x, socken=True,
                  pose=Pose(sitzt=True, schreck=1.0, arm_v=-150, arm_h=-140)),
            Flug((self.aussen(-r), self.boden - 120 * s), 0.7, hoehe=90, neigung=-200,
                 pose=Pose(sitzt=True, schreck=1.0, arm_v=-150, arm_h=-140)),
            Setze(zeige_figur=False),
            Mit('m', Wandel(0.2, pfiff=0.0, recken=24.0)),
            Mit('m', Stehe(0.8, lambda d, u: Pose(auge_zu=0.3 < u < 0.42 or 0.55 < u < 0.67))),
            # Stiefel als Kopfkissen
            Mit('m', Setze(recken=0.0)),
            Mit('m', Hoppel(bis=lambda d: self.stiefel + r * 55 * s, tempo=0.45, hoehe=8)),
            Mit('m', Setze(richtung=-r, schlaf=1.0)),
            Warte(0.6),
            Setze(decke_x=self.aussen(-r), decke_hoch=180.0, zug=0.0),
            Wandel(0.01, deck=1.0),
            Wandel(0.55, decke_x=lambda sz: sz.m.x + r * 42 * s, decke_hoch=0.0),
            Tu(lambda sz: puff(sz, sz.m.x, sz.boden - 20 * sz.s, 16, 140)),
            Warte(0.9),
            Wandel(0.4, deck=0.0),
        ]

    def schreck_ablauf(self):
        self.nebenbei.clear()
        self.ringe = -1.0
        m = self.m
        neu = []
        if m.figur_sichtbar():
            m.schlaf, m.pfiff, m.recken = 0.0, 0.0, 0.0
            neu.append(Nebenbei(Mit('m', Setze(pose=Pose(schreck=1.0), richtung=m.naechster_rand())),
                                Mit('m', Hoppel(tempo=3.4, hoehe=20))))
        else:
            m.zeige_figur = False
        neu.append(Nebenbei(Wandel(0.3, deck=0.0)))
        if self.zeige_figur and self.figur_sichtbar():
            self.neigung, self.y, self.socken = 0.0, self.boden, False
            return neu + [Erschrecke(0.35, 40), Renne(zum='rand'), WarteNebenbei()]
        self.zeige_figur = False
        return neu + [Setze(stiefel=None), WarteNebenbei()]

    # -- Zeichnen

    def zeichne_hinten(self, p):
        if self.stiefel is not None and self.m.schlaf < 0.5:
            self._stiefel(p, self.stiefel)

    def _stiefel(self, p, x):
        p.save()
        p.translate(x, self.boden)
        p.scale(self.s * self.richtung, self.s)
        p.setPen(KEIN_STIFT)
        zeichne_stiefel(p, 0, 0)
        p.restore()

    def zeichne_vorn(self, p):
        m = self.m
        if self.stiefel is not None and m.schlaf > 0.5:
            p.save()
            p.translate(m.x + m.richtung * 66 * m.s, self.boden)
            p.rotate(-90 * m.richtung)
            p.scale(self.s * 0.9, self.s * 0.9)
            p.setPen(KEIN_STIFT)
            zeichne_stiefel(p, 0, 0)
            p.restore()
        if self.deck > 0:
            p.save()
            p.setOpacity(self.deck)
            p.translate(self.decke_x + math.sin(self.t * 30) * 0 + self.wackel * self.s, self.boden - self.decke_hoch * self.s)
            p.scale(self.s * -self.richtung, self.s)
            p.setPen(KEIN_STIFT)
            zeichne_schneedecke(p, DECKE_B, DECKE_H, self.zug)
            p.restore()
        if 0 <= self.ringe < 0.9:
            mund = QPointF(m.x, self.boden - (150 + 40) * m.s)
            p.save()
            p.setBrush(KEIN_PINSEL)
            for i in range(4):
                u = self.ringe * 1.4 - i * 0.18
                if u <= 0 or u > 1:
                    continue
                rad = (30 + 220 * u) * self.s
                p.setPen(stift(QColor(255, 255, 255, int(230 * (1 - u))), (5 - 3 * u) * self.s * 1.4))
                start = 180 - 35 if self.richtung > 0 else -35
                p.drawArc(QRectF(mund.x() - rad, mund.y() - rad, 2 * rad, 2 * rad), int(start * 16), 70 * 16)
            p.restore()

    def grenzen_extra(self):
        s = self.s
        k = QRectF(self.decke_x - 110 * s, self.boden - (DECKE_H + self.decke_hoch + 20) * s,
                   220 * s, (DECKE_H + self.decke_hoch + 20) * s)
        if self.zug:
            k = k.united(k.translated(-self.richtung * self.zug * s, 0))
        if self.stiefel is not None:
            k = k.united(QRectF(min(self.stiefel, self.m.x) - 120 * s, self.boden - 70 * s,
                                abs(self.stiefel - self.m.x) + 240 * s, 70 * s))
        if 0 <= self.ringe < 0.9:
            m = self.m
            rad = 260 * s
            k = k.united(QRectF(m.x - rad, self.boden - 190 * s - rad, 2 * rad, 2 * rad))
        return k
