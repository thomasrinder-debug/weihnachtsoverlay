import math
import random

from PyQt6.QtCore import QPointF, QRectF
from PyQt6.QtGui import QTransform

from zeichnen.figur import (zeichne_faeustling_vorn, zeichne_kopf_vorn, zeichne_schreckstriche,
                            zeichne_tropfen, segment)
from zeichnen.grundlagen import KEIN_STIFT, ROT_DUNKEL, ROT_HELL, radial

from .basis import Jeweils, Kurz, Setze, Szene, Wandel, Warte


class Spaehen(Szene):
    """Zieht sich am Rand ins Bild, mustert die Zuschauer, erschrickt und duckt
    sich weg. Beim zweiten Mal lugt er zitternd hervor und winkt schüchtern.
    Unten und oben (kopfüber) schaut er über die Kante, seitlich um sie herum."""
    name, titel, reihenfolge = 'spaehen', 'Spähen', 2

    def vorbereiten(self):
        self.zeige_figur = False
        self.sc = self.s * 1.3
        # Zustand des Kopfes, die Schritte überblenden ihn
        self.h = 0.0            # wie weit er herausschaut, 0 = ganz hinter dem Rand
        self.hand = 0.0         # Fäustlinge an der Kante
        self.bx = self.by = 0.0  # Blickrichtung
        self.schreck = self.sorge = self.zittern = self.winken = 0.0
        self.zu = self.tropfen = self.striche_kopf = False
        erst = self.zufallsort()
        zweit = self.zufallsort()
        while zweit[2] == erst[2]:
            zweit = self.zufallsort()
        self.orte = (erst, zweit)
        self.ort = erst

    def ablauf(self):
        erst, zweit = self.orte
        umschauen = Jeweils(1.6, lambda sz, u: setattr(sz, 'bx', math.sin(u / 1.6 * 2 * math.pi)))
        return [
            # neugierig
            Wandel(0.6, hand=1), Wandel(1.2, h=0.88), umschauen, Setze(bx=0.0, by=0.3),
            Warte(0.5), Kurz(0.15, zu=True), Wandel(0.8, h=1.1),
            # Huch!
            Setze(schreck=1.0, striche_kopf=True, zittern=1.5, by=0.0), Warte(0.25), Setze(zittern=0.0),
            Wandel(0.18, h=0.0), Wandel(0.2, hand=0.0), Setze(striche_kopf=False), Warte(1.3),
            # vorsichtig an anderer Stelle
            Setze(ort=zweit, schreck=0.0, sorge=0.8, zittern=0.7, by=0.25),
            Wandel(0.5, hand=1), Wandel(1.5, h=0.86), Setze(tropfen=True), Warte(0.6),
            Kurz(0.15, zu=True), Warte(0.65), Kurz(0.15, zu=True), Warte(0.3),
            Wandel(0.3, winken=1), Warte(1.1), Wandel(0.25, winken=0), Wandel(0.25, h=0), Wandel(0.25, hand=0),
        ]

    def schreck_ablauf(self):
        if self.hand <= 0 and self.h <= 0:
            return []
        self.nebenbei.clear()
        return [Setze(schreck=1.0, sorge=0.3, zu=False, winken=0.0, tropfen=False, bx=0.0, by=0.0,
                      striche_kopf=True, zittern=1.8),
                Wandel(0.1, h=lambda sz: sz.h + 0.08), Warte(0.12), Setze(zittern=0.0),
                Wandel(0.12, h=0.0), Wandel(0.12, hand=0.0), Warte(0.15)]

    def zufallsort(self):
        g = self.geo
        rand = random.choice(('unten', 'oben', 'links', 'rechts'))
        if rand in ('unten', 'oben'):
            y = g.bottom() if rand == 'unten' else g.top()
            return g.left() + g.width() * random.uniform(0.15, 0.85), y, rand
        y = g.top() + g.height() * random.uniform(0.3, 0.75)
        return (g.left() if rand == 'links' else g.right()), y, rand

    def trafo(self):
        """Örtliches System mit dem Rand als Nulllinie: unten geht es nach -y ins
        Bild, oben hängt er kopfüber herunter, seitlich geht es nach -x."""
        x, y, rand = self.ort
        tr = QTransform()
        tr.translate(x, y)
        if rand == 'oben':
            tr.rotate(180)
        tr.scale(self.sc * (-1 if rand == 'links' else 1), self.sc)
        return tr

    def grenzen_extra(self):
        if self.hand <= 0 and self.h <= 0:
            return QRectF()
        waagerecht = self.ort[2] in ('unten', 'oben')
        lokal = QRectF(-110, -175, 220, 185) if waagerecht else QRectF(-175, -115, 185, 230)
        return self.trafo().mapRect(lokal)

    def zeichne_vorn(self, p):
        if self.hand <= 0 and self.h <= 0:
            return
        t = self.t
        p.save()
        p.setTransform(self.trafo(), True)
        p.setPen(KEIN_STIFT)
        tief = 84 - 100 * self.h            # Kopfmitte, positiv = noch hinter dem Rand
        zit = math.sin(t * 40) * self.zittern
        greif = -2 + 18 * (1 - self.hand)
        kopf = ((self.bx, self.by), self.schreck, self.sorge, self.zu, math.sin(t * 3) * 2)
        if self.ort[2] in ('unten', 'oben'):
            p.setClipRect(QRectF(-200, -400, 400, 400))
            p.setBrush(radial(zit - 10, tief + 50, 60, ROT_HELL, ROT_DUNKEL))
            p.drawEllipse(QPointF(zit, tief + 66), 48, 34)
            zeichne_kopf_vorn(p, zit, tief, *kopf)
            if self.tropfen:
                zeichne_tropfen(p, zit + 27, tief - 18 + (t * 9) % 12)
            zeichne_faeustling_vorn(p, -50 + zit * 0.5, greif)
            wx = 50 + zit * 0.5 + math.sin(t * 10) * 5 * self.winken
            wy = greif - 34 * self.winken
            if self.winken > 0:
                segment(p, wx, wy + 8, 52, 20, 16, ROT_HELL, ROT_DUNKEL)
            zeichne_faeustling_vorn(p, wx, wy)
            striche = (zit, tief - 76)
        else:
            # seitlich: Kopf bleibt aufrecht und neigt sich um die Kante
            p.setClipRect(QRectF(-400, -300, 400, 600))
            p.setBrush(radial(tief + 50, zit - 10, 60, ROT_HELL, ROT_DUNKEL))
            p.drawEllipse(QPointF(tief + 70, zit + 40), 36, 52)
            p.save()
            p.translate(tief, zit)
            p.rotate(-14)
            zeichne_kopf_vorn(p, 0, 0, *kopf)
            if self.tropfen:
                zeichne_tropfen(p, -27, -18 + (t * 9) % 12)
            p.restore()
            for y, winkt in ((-52, False), (58, True)):
                p.save()
                gx, gy = greif + zit * 0.5, y
                if winkt and self.winken > 0:
                    gx -= 30 * self.winken
                    gy -= 22 * self.winken - math.sin(t * 10) * 5 * self.winken
                    segment(p, gx + 8, gy, 20, y, 16, ROT_HELL, ROT_DUNKEL)
                p.translate(gx, gy)
                p.rotate(90)
                zeichne_faeustling_vorn(p, 0, 0)
                p.restore()
            striche = (tief - 18, zit - 74)
        p.setClipping(False)
        if self.striche_kopf:
            zeichne_schreckstriche(p, *striche, 1.0)
        p.restore()
