import math
from dataclasses import replace

from PyQt6.QtCore import QRectF

from zeichnen.figur import Pose, renn_pose
from zeichnen.grundlagen import WEISS, blinzeln
from zeichnen.requisiten import zeichne_muetze_lose

from .basis import Gehe, Hoppel, Mit, Nebenbei, Schritt, Setze, Stehe, Tu, Wandel, Warte, WarteBis
from .ostern import WinkeSzene


class Gezogen(Schritt):
    """Er rennt auf der Stelle davon und wird trotzdem rückwärts zu ziel(szene) gezogen."""

    def __init__(self, dauer, ziel):
        self.dauer, self.ziel = dauer, ziel

    def beginn(self, sz):
        self.x0, self.x1 = sz.x, self.ziel(sz)
        sz.neigung = 16

    def weiter(self, sz, u, dt):
        f = min(1.0, u / self.dauer)
        sz.x = self.x0 + (self.x1 - self.x0) * f * f
        sz.phase += dt * 22
        sz.pose = replace(renn_pose(sz.phase), sorge=1.0)
        if int(u * 12) != int((u - dt) * 12):
            sz.streue(sz.x, sz.boden - 4 * sz.s, 2, WEISS, tempo=50, dauer=0.5, r=(3, 6))

    def ende(self, sz):
        sz.neigung = 0.0


class Herbeiwinken(WinkeSzene):
    """Der Weihnachtsmann spaziert an einer Winkekatze vorbei. Sie winkt ihn herbei, er schüttelt
    den Kopf und will weiter, doch ihr Winken zieht ihn rückwärts heran, während seine Beine
    vergeblich davonrennen. Dann ein kurzer Wisch mit der Pfote nach oben: er schießt senkrecht
    aus dem Bild, die Mütze segelt herab und landet auf der Katze."""
    name, titel, reihenfolge = 'herbeiwinken', 'Herbeigewinkt', 92

    def vorbereiten(self):
        r = self.richtung
        k = self.katze(self.aussen(-r))
        k.richtung = r
        self.x = self.aussen(-r)
        self.flugmuetze = None          # [x, y, dreh, Startzeit] der fallenden Mütze

    def ablauf(self):
        r, s = self.richtung, self.s
        kx = self.vom_rand(0.07)
        k = lambda d, u: Pose(kopf_vorn=True, auge_zu=blinzeln(d.t))  # noqa: E731
        return [
            Nebenbei(Mit('k', Hoppel(bis=kx, tempo=0.6, hoehe=16)),
                     Mit('k', Setze(richtung=r, pose=Pose(kopf_vorn=True))),
                     Mit('k', Stehe(30, k))),
            Warte(0.6),
            Gehe(bis=self.vom_rand(0.27)),
            Wandel(0.3, wmitte=170.0, wamp=35.0, wtempo=2.4),
            Stehe(0.3, Pose(blick_x=0.0)),
            Setze(richtung=-r),
            Stehe(0.7, lambda sz, u: Pose(blick_y=0.3, sorge=0.3, auge_zu=blinzeln(sz.t))),
            Stehe(0.6, lambda sz, u: Pose(kopf_vorn=True, auge_zu=True, blick_x=math.sin(u * 14))),
            Setze(richtung=r),
            Gehe(bis=self.vom_rand(0.3), tempo=0.6),
            Wandel(0.2, wtempo=4.0, wamp=45.0),
            Gezogen(1.8, lambda sz: sz.k.x + r * 85 * s),
            Wandel(0.25, wtempo=1.0, wamp=0.0),
            Stehe(0.5, Pose(kopf_vorn=True, schreck=0.6, sorge=1.0)),
            Setze(richtung=-r),
            Stehe(0.4, Pose(blick_y=0.4, sorge=0.6)),
            Stehe(0.8, lambda sz, u: Pose(kopf_vorn=True, sorge=0.8, auge_zu=0.3 < u < 0.42)),
            Wandel(0.35, wmitte=270.0),
            Mit('k', Setze(froh=True)),
            Wandel(0.12, wmitte=150.0),
            Tu(lambda sz: sz.abschuss()),
            Abschuss(),
            Setze(zeige_figur=False),
            WarteBis(lambda sz: sz.flugmuetze is None),
            Mit('k', Setze(muetze=True)),
            Wandel(0.3, wmitte=145.0, wamp=14.0, wtempo=1.4),
            Warte(0.8),
            Tu(lambda sz: sz.nebenbei.clear()),
            Mit('k', Hoppel(bis=lambda d: d.sz.aussen(-r), tempo=0.5, hoehe=16)),
        ]

    def abschuss(self):
        s = self.s
        self.pose_fest = {'muetze': False}
        self.flugmuetze = [self.x + self.richtung * 4 * s, self.y - 232 * s, 0.0, self.t]
        self.streue(self.x, self.boden - 6 * s, 14, WEISS, tempo=140, dauer=0.7, r=(4, 10))

    def weiter(self, dt):
        super().weiter(dt)
        m = self.flugmuetze
        if m:
            k = self.k
            ziel = k.y - 150 * k.s
            alt = self.t - m[3]
            if alt < 0.5:
                m[1] -= 160 * self.s * dt * (1 - alt / 0.5)
            else:
                m[1] += 120 * self.s * dt
            m[0] += (k.x + 2 * k.s * k.richtung - m[0]) * min(1.0, dt * 1.6) + math.sin(self.t * 4) * 30 * self.s * dt
            m[2] = math.sin(self.t * 4) * 20
            if alt > 0.5 and m[1] >= ziel:
                self.flugmuetze = None

    def zeichne_vorn(self, p):
        m = self.flugmuetze
        if m:
            k = self.k
            p.save()
            p.translate(m[0], m[1])
            p.rotate(m[2])
            p.scale(k.s * k.richtung, k.s)
            zeichne_muetze_lose(p)
            p.restore()

    def grenzen_extra(self):
        m = self.flugmuetze
        if not m:
            return QRectF()
        s = self.s
        return QRectF(m[0] - 60 * s, m[1] - 60 * s, 120 * s, 80 * s)

    def schreck_ablauf(self):
        self.flugmuetze = None
        neu = self.katze_flieht()
        return neu + self.schreck_alle(hoehe=40, ausser=('k',))


class Abschuss(Schritt):
    """Schießt senkrecht nach oben aus dem Bild."""

    def beginn(self, sz):
        self.v = 900 * sz.s

    def weiter(self, sz, u, dt):
        self.v += 1800 * sz.s * dt
        sz.y -= self.v * dt
        sz.pose = Pose(arm_v=-170, arm_h=-165, arm_v_x=16, bein_v=8, bein_h=-8, schreck=1.0, mund_offen=True,
                       kopf_vorn=True)

    def fertig(self, sz, u):
        return sz.y < sz.oben - 40 * sz.s

