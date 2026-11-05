import math
import random

from PyQt6.QtCore import QPointF, QRectF
from PyQt6.QtGui import QColor

from zeichnen.grundlagen import GOLD, GOLD_HELL, KEIN_STIFT, bildstueck, glatt, kreis, radial

from .basis import Jeweils, Setze, Szene, Tu, Wandel, Warte


class Scherbe:
    __slots__ = ('stueck', 'x', 'y', 'vx', 'vy', 'w', 'vw', 'alter')

    def __init__(self, stueck, x, y, vx, vy, vw):
        self.stueck, self.x, self.y, self.vx, self.vy = stueck, x, y, vx, vy
        self.w, self.vw, self.alter = 0.0, vw, 0.0


class Taskleiste(Szene):
    """Ein Symbol in der Taskleiste fängt an zu zappeln, wird mit jedem Anfall größer,
    glüht, platzt in Scherben, Funken und Rauch und taucht danach wieder an seinem Platz
    auf, mit einem kleinen Nachzittern. Das echte Symbol bleibt unberührt: die Szene deckt
    es mit einem Flicken ab und spielt mit einer Kopie aus dem Bildschirmfoto."""
    name, titel, reihenfolge = 'taskleiste', 'Platzendes Taskleistensymbol', 60
    braucht = 'taskleiste'

    def vorbereiten(self):
        self.zeige_figur = False
        d = self.daten
        self.r = d['rechteck']
        self.einheit = self.r.height()               # Größe des Symbols in Pixeln
        self.zx = self.zy = self.winkel = 0.0
        self.groesse = 1.0
        self.gluehen = 0.0
        self.ganz = True                             # Kopie sichtbar
        self.scherben = []
        self.blitz = 0.0
        self.zittern = 0.0                           # Stärke des Zappelns, Pixel
        self.tempo_z = 30.0                          # Zappeln je Sekunde (Kreisfrequenz)

    def ablauf(self):
        return [
            Warte(0.8),
            self.zappeln(1.0, 0.10, 26),
            Warte(0.6),
            self.zappeln(1.1, 0.14, 32), *self.wachsen(1.3),
            Warte(0.4),
            self.zappeln(1.2, 0.18, 38), *self.wachsen(1.7),
            Warte(0.3),
            self.zappeln(0.9, 0.24, 46), *self.wachsen(2.2),
            Wandel(1.1, gluehen=1.0, zittern=lambda sz: sz.einheit * 0.2),
            Jeweils(0.35, lambda sz, u: setattr(sz, 'groesse', 2.2 + 0.5 * glatt(u / 0.35))),
            Tu(Taskleiste.platzen),
            Warte(0.5),
            Wandel(0.5, blitz=0.0),
            Warte(1.2),
            Setze(groesse=0.0, ganz=True, gluehen=0.0, zittern=0.0, zx=0.0, zy=0.0, winkel=0.0),
            Jeweils(0.55, lambda sz, u: setattr(sz, 'groesse', self.federnd(u / 0.55))),
            Setze(groesse=1.0, tempo_z=50.0),
            Setze(zittern=lambda sz: sz.einheit * 0.08),
            Wandel(0.8, zittern=0.0),
            Warte(0.3),
        ]

    @staticmethod
    def federnd(u):
        u = min(1.0, u)
        return 1 - math.exp(-6 * u) * math.cos(9 * u)

    def zappeln(self, dauer, staerke, tempo):
        def f(sz, u):
            huelle = math.sin(math.pi * min(1.0, u / dauer))
            sz.zittern = staerke * sz.einheit * huelle
            sz.tempo_z = tempo
        return Jeweils(dauer, f)

    def wachsen(self, ziel):
        """Ruckartig größer, mit kurzem Überschwingen."""
        def f(sz, u):
            von = sz._von
            sz.groesse = von + (ziel - von) * Taskleiste.federnd(u / 0.35)
        return [Tu(lambda sz: setattr(sz, '_von', sz.groesse)), Jeweils(0.35, f)]

    def platzen(self):
        s = self.s
        self.ganz = False
        self.blitz = 1.0
        mx, my = self.mitte()
        n = 4
        w, h = self.r.width() / n, self.r.height() / n
        for i in range(n):
            for j in range(n):
                stueck = QRectF(self.r.x() + i * w, self.r.y() + j * h, w, h)
                ox = (i + 0.5 - n / 2) * w * self.groesse
                oy = (j + 0.5 - n / 2) * h * self.groesse
                a = math.atan2(oy - 0.6 * h, ox) + random.uniform(-0.4, 0.4)
                v = random.uniform(220, 520) * s
                self.scherben.append(Scherbe(stueck, mx + ox, my + oy, math.cos(a) * v,
                                             math.sin(a) * v - 260 * s, random.uniform(-720, 720)))
        self.streue(mx, my, 26, [GOLD_HELL, GOLD, QColor('#FFF6D0')], tempo=420, dauer=0.9, r=(4, 8), art='stern')
        self.streue(mx, my, 14, [QColor(120, 120, 120, 170), QColor(80, 80, 80, 150)], tempo=120, dauer=1.6,
                    r=(10, 22))

    def mitte(self):
        """Mitte der Kopie: wächst nach oben aus der Taskleiste heraus."""
        c = self.r.center()
        return c.x() + self.zx, c.y() + self.zy - (self.groesse - 1) * self.r.height() * 0.55

    def striche_punkt(self):
        mx, my = self.mitte()
        return mx, my - self.einheit * max(self.groesse, 0.5) * 0.5

    def schreck_ablauf(self):
        self.nebenbei.clear()
        if self.ganz:
            von = self.groesse

            def huepf(sz, u):
                f = min(1.0, u / 0.45)
                sz.zy = -math.sin(math.pi * f) * sz.einheit * 1.2
                sz.groesse = von + (1.0 - von) * glatt(f)
                sz.zittern = 0.0
                sz.winkel = 0.0
            return [Setze(striche=True, gluehen=0.0), Jeweils(0.45, huepf), Setze(striche=False, zy=0.0), Warte(0.15)]
        return [Wandel(0.15, blitz=0.0), Setze(ganz=True, groesse=0.0, gluehen=0.0, zittern=0.0, striche=True),
                Jeweils(0.35, lambda sz, u: setattr(sz, 'groesse', self.federnd(u / 0.35))),
                Setze(groesse=1.0, striche=False), Warte(0.1)]

    def weiter(self, dt):
        t = self.t
        if self.zittern > 0:
            self.zx = math.sin(t * self.tempo_z) * self.zittern
            self.zy = -abs(math.sin(t * self.tempo_z * 0.5)) * self.zittern * 0.5 if not self.erschreckt else self.zy
            self.winkel = math.sin(t * self.tempo_z * 0.8 + 1) * self.zittern / self.einheit * 60
        elif not self.erschreckt:
            self.zx = self.zy = self.winkel = 0.0
        if self.erschreckt and self.scherben:
            for sch in self.scherben:
                sch.alter = max(sch.alter, 1.3)
        schwere = 1100 * self.s
        boden = self.geo.bottom() + 40 * self.s
        for sch in self.scherben:
            sch.alter += dt
            sch.x += sch.vx * dt
            sch.y += sch.vy * dt
            sch.vy += schwere * dt
            sch.w += sch.vw * dt
        self.scherben = [sch for sch in self.scherben if sch.alter < 1.6 and sch.y < boden]
        if self.erschreckt:
            self.wolke.clear()
            self.splitter.clear()

    def zeichne_hinten(self, p):
        d = self.daten
        p.drawImage(self.r, d['flicken'])
        if self.blitz > 0:
            mx, my = self.mitte()
            r = self.einheit * (1.5 + 2.5 * (1 - self.blitz))
            p.setPen(KEIN_STIFT)
            p.setBrush(radial(mx, my, r, QColor(255, 250, 220, int(230 * self.blitz)), QColor(255, 200, 80, 0)))
            kreis(p, mx, my, r)

    def zeichne_vorn(self, p):
        d = self.daten
        mx, my = self.mitte()
        if self.ganz and self.groesse > 0.01:
            if self.gluehen > 0:
                r = self.einheit * self.groesse * 0.9
                p.setPen(KEIN_STIFT)
                p.setBrush(radial(mx, my, r, QColor(255, 120, 60, int(150 * self.gluehen)), QColor(255, 60, 0, 0)))
                kreis(p, mx, my, r)
            bildstueck(p, d['symbol'], self.r, self.r, QPointF(mx, my), self.winkel, self.groesse)
            if self.gluehen > 0:
                # rot glühend, pulsierend
                puls = 0.5 + 0.5 * math.sin(self.t * 24)
                p.save()
                p.translate(mx, my)
                p.scale(self.groesse, self.groesse)
                p.rotate(self.winkel)
                p.setPen(KEIN_STIFT)
                p.setBrush(QColor(255, 70, 40, int(110 * self.gluehen * (0.6 + 0.4 * puls))))
                w, h = self.r.width(), self.r.height()
                p.drawRoundedRect(QRectF(-w * 0.36, -h * 0.36, w * 0.72, h * 0.72), w * 0.15, h * 0.15)
                p.restore()
        for sch in self.scherben:
            bildstueck(p, d['symbol'], self.r, sch.stueck, QPointF(sch.x, sch.y), sch.w, self.groesse * 0.9,
                       1 - glatt((sch.alter - 1.0) / 0.6))

    def grenzen(self):
        mx, my = self.mitte()
        r = self.einheit * max(self.groesse, 1.0) * 0.9 + 4
        k = QRectF(mx - r, my - r - (30 * self.s if self.striche else 0), 2 * r, 2 * r + (30 * self.s if self.striche else 0))
        k = k.united(self.r)
        if self.blitz > 0:
            k = k.united(QRectF(mx - 4.2 * self.einheit, my - 4.2 * self.einheit, 8.4 * self.einheit, 8.4 * self.einheit))
        for sch in self.scherben:
            e = self.einheit * 0.6
            k = k.united(QRectF(sch.x - e, sch.y - e, 2 * e, 2 * e))
        return k.united(super().grenzen())
