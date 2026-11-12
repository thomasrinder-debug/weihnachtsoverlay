"""Gemeinsames für die Osterszenen: Ostereier, die hüpfen, fliegen und kullern,
und die Winkekatze mit ihrer Winkepfote."""
import math

from PyQt6.QtCore import QRectF

from zeichnen.figur import Pose
from zeichnen.figuren import Winkekatze
from zeichnen.requisiten import zeichne_osterei

from .basis import Mit, Nebenbei, Setze, Szene, Wandel


class Ei:
    """Ein Osterei in Pixeln: (x, y) ist die Mitte, r die halbe Breite."""

    def __init__(self, x, y, r, farbe, muster=0):
        self.x, self.y, self.r = x, y, r
        self.farbe, self.muster = farbe, muster
        self.dreh = 0.0
        self.bemalt = 4.0
        self.sichtbar = True
        self.bahn = None
        self.flucht = 0.0          # Pixel je Sekunde, hüpft davon

    def bogen(self, t, x1, y1, dauer, hoehe, dreh=360.0, weg=False):
        """Fliegt im Bogen nach (x1, y1); weg=True: verschwindet dort (etwa im Sack)."""
        self.bahn = (t, self.x, self.y, x1, y1, dauer, hoehe, self.dreh, dreh, weg)

    def schritt(self, t, dt, boden):
        if self.bahn:
            t0, x0, y0, x1, y1, dauer, hoehe, d0, dreh, weg = self.bahn
            f = min(1.0, (t - t0) / dauer)
            self.x = x0 + (x1 - x0) * f
            self.y = y0 + (y1 - y0) * f - hoehe * 4 * f * (1 - f)
            self.dreh = d0 + dreh * f
            if f >= 1.0:
                self.bahn = None
                if weg:
                    self.sichtbar = False
        elif self.flucht:
            self.x += self.flucht * dt
            self.y = boden - self.r - abs(math.sin(t * 9)) * self.r * 2.2
            self.dreh = math.sin(t * 9) * 25

    def zeichne(self, p):
        if self.sichtbar:
            zeichne_osterei(p, self.x, self.y, self.r, self.farbe, self.muster, self.dreh, self.bemalt)

    def kasten(self):
        if not self.sichtbar:
            return QRectF()
        r = self.r * 1.4
        return QRectF(self.x - r, self.y - r, 2 * r, 2 * r)

    def im_bild(self, geo):
        return self.sichtbar and self.kasten().intersects(geo)


class WinkeSzene(Szene):
    """Grundlage für Szenen mit der Winkekatze 'k'. Winken über wmitte (Grad), wamp und wtempo (Hz);
    mit propeller=True dreht sich die Pfote mit pdreh Grad je Sekunde im Kreis."""

    def katze(self, x, groesse=0.6, vorn=True):
        self.k = self.dazu('k', Winkekatze, groesse=groesse, vorn=vorn)
        self.k.x = x
        self.k.wink = 145.0
        self.wmitte, self.wamp, self.wtempo, self.wphase = 145.0, 18.0, 1.0, 0.0
        self.propeller, self.pdreh = False, 0.0
        return self.k

    def winken(self, dt):
        k = self.k
        if self.propeller:
            k.wink += self.pdreh * dt
            k.unschaerfe = min(1.0, self.pdreh / 1400)
        else:
            self.wphase += self.wtempo * dt * 2 * math.pi
            k.wink = self.wmitte + self.wamp * math.sin(self.wphase)
            k.unschaerfe = max(0.0, min(1.0, (self.wtempo - 3.0) / 3.0))

    def weiter(self, dt):
        self.winken(dt)

    def katze_flieht(self, dauer=0.8):
        """Schreck der Winkekatze: Pfote wird zum Propeller, sie fliegt zum nächsten Rand hinaus."""
        k = self.k
        if not (k.zeige_figur and k.figur_sichtbar()):
            k.zeige_figur = False
            return []
        self.propeller, self.pdreh = True, 2200.0
        k.froh = False
        k.neigung = 0.0
        ziel = self.aussen(k.naechster_rand())
        return [Nebenbei(Mit('k', Setze(pose=Pose(kopf_vorn=True, schreck=1.0), striche=True)),
                         Mit('k', Wandel(dauer, x=ziel, hopp=lambda d: 160 * d.s)))]
