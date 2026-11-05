import math
import random

from PyQt6.QtCore import QPointF, QRectF
from PyQt6.QtGui import QColor, QPainterPath

from zeichnen.figur import Pose, zeichne_sack, zeichne_weihnachtsmann
from zeichnen.grundlagen import (KEIN_PINSEL, KEIN_STIFT, Teilchen, blinzeln, stift, teilchen_kasten,
                                 teilchen_schritt, zeichne_teilchen)
from zeichnen.requisiten import zeichne_rentier, zeichne_schlitten

from .basis import Kurz, Setze, Szene, Warte, WarteBis


class Schlitten(Szene):
    """Rentiergespann fliegt dicht unter dem oberen Rand in Wellen, mit Sternenstaub."""
    name, titel, reihenfolge = 'schlitten', 'Schlitten', 4
    DAUER = 11.0
    VORN, HINTEN = 440, 130     # Ausdehnung des Gespanns in Einheiten vor/hinter dem Schlitten

    def vorbereiten(self):
        self.zeige_figur = False
        self.f = self.s * 0.7
        # die Mütze streift fast die Kante
        self.h0 = self.geo.top() + 255 * self.f + self.geo.height() * 0.03
        self.flug = 0.0             # Flugzeit
        self.winkel = 0.0
        self.winkt = self.erschrocken = False
        self.aus = False            # Gespann weg, nur noch Funken
        self.funken = []            # hinter dem Gespann, deshalb nicht in self.teilchen
        self.x, self.y = self.pos(0)

    def ablauf(self):
        return [Warte(4.4), Kurz(2.8, winkt=True), WarteBis(lambda sz: sz.flug >= sz.DAUER),
                Setze(aus=True), WarteBis(lambda sz: not sz.funken)]

    def schreck_ablauf(self):
        # nach kurzem Schreck steil nach oben aus dem Bild
        return [Setze(winkt=False, erschrocken=True), Warte(0.7), Setze(erschrocken=False),
                WarteBis(lambda sz: sz.ganz_oben_raus()), Setze(aus=True), WarteBis(lambda sz: not sz.funken)]

    def pos(self, t):
        weg = self.geo.width() + (self.VORN + self.HINTEN) * self.f
        u = t / self.DAUER
        if self.richtung > 0:
            x = self.geo.left() - self.VORN * self.f + weg * u
        else:
            x = self.geo.right() + self.VORN * self.f - weg * u
        y = self.h0 + math.sin(t * 0.9) * self.geo.height() * 0.025
        if self.erschreckt:
            d = max(0.0, self.t - self.te - 0.3)
            x += self.richtung * d * d * self.geo.width() * 0.5
            y -= d * d * self.geo.height() * 1.2
        return x, y

    def welt(self, ux, uy):
        """Punkt im Gespann (Einheiten) → Bildschirm."""
        phi = math.radians(self.winkel * self.richtung)
        sx, sy = ux * self.f * self.richtung, uy * self.f
        return (self.x + sx * math.cos(phi) - sy * math.sin(phi),
                self.y + sx * math.sin(phi) + sy * math.cos(phi))

    def ganz_oben_raus(self):
        return all(self.welt(ux, 20)[1] < self.geo.top() for ux in (-130, self.VORN))

    def weiter(self, dt):
        self.flug += dt
        self.x, self.y = self.pos(self.flug)
        x2, y2 = self.pos(self.flug + 0.05)
        self.winkel = math.degrees(math.atan2(y2 - self.y, abs(x2 - self.x))) * 0.6
        self.phase += dt * 8
        if not self.aus:
            for ux, uy in ((-100, -6), (70, -4)):
                for _ in range(2):
                    x, y = self.welt(ux + random.uniform(-6, 6), uy)
                    farbe = random.choice((QColor(255, 214, 90, 235), QColor(255, 255, 255, 235),
                                           QColor(255, 180, 60, 220)))
                    self.funken.append(Teilchen(x, y, random.uniform(-30, 30) * self.f,
                                                random.uniform(10, 50) * self.f, random.uniform(0.8, 1.5),
                                                random.uniform(3, 7) * self.f, 1 * self.f, farbe, 'stern'))
        teilchen_schritt(self.funken, dt, schwere=30 * self.f)

    def grenzen_extra(self):
        k = teilchen_kasten(self.funken)
        if self.aus:
            return k
        ecken = [self.welt(ux, uy) for ux, uy in ((-130, -300), (self.VORN, -300), (-130, 20), (self.VORN, 20))]
        xs = [e[0] for e in ecken]
        ys = [e[1] for e in ecken]
        return k.united(QRectF(min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys)))

    def zeichne_hinten(self, p):
        zeichne_teilchen(p, self.funken)
        if self.aus:
            return
        p.save()
        p.translate(self.x, self.y)
        p.rotate(self.winkel * self.richtung)
        p.scale(self.f * self.richtung, self.f)
        ph, t = self.phase, self.t
        # Geschirr
        p.setPen(stift(QColor('#5A3A1E'), 3))
        p.drawLine(QPointF(95, -34), QPointF(150, -42 + math.sin(ph + 1.3) * 5))
        p.drawLine(QPointF(235, -42 + math.sin(ph + 1.3) * 5), QPointF(290, -48 + math.sin(ph) * 5))
        p.setPen(KEIN_STIFT)
        for i, (rx, ry) in enumerate(((330, -48), (190, -42))):
            p.save()
            p.translate(rx, ry + math.sin(ph + i * 1.3) * 5)
            zeichne_rentier(p, ph + i * 1.3, t + i * 0.7, i == 0)
            p.restore()
        zeichne_sack(p, -64, -96, -10, 1.35)
        sitz = Pose(sitzt=True, sack=False, arm_v=-62 + math.sin(t * 3) * 6, arm_h=-50 + math.sin(t * 3) * 6,
                    hub=math.sin(ph * 0.5) * 1.5, wipp=math.sin(t * 4) * 4, auge_zu=blinzeln(t))
        if self.winkt:
            sitz.arm_v, sitz.arm_v_x = -125 + 20 * math.sin(t * 9), 26
        if self.erschrocken:
            sitz.kopf_vorn, sitz.schreck, sitz.auge_zu, sitz.wipp, sitz.mund_offen = True, 1.0, False, -6, True
        p.save()
        p.translate(-14, 0)
        zeichne_weihnachtsmann(p, sitz)
        p.restore()
        zeichne_schlitten(p)
        # Zügel von der hinteren Hand zu beiden Rentieren
        zuegel = QPainterPath()
        for kx, ky in ((254, -100 + math.sin(ph + 1.3) * 5), (394, -106 + math.sin(ph) * 5)):
            zuegel.moveTo(18, -104)
            zuegel.quadTo((18 + kx) / 2, ky + 30, kx, ky + 8)
        p.setPen(stift(QColor('#5A3A1E'), 2))
        p.setBrush(KEIN_PINSEL)
        p.drawPath(zuegel)
        p.restore()
