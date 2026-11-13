import math
import random

from PyQt6.QtCore import QRectF

from zeichnen.figur import Pose, geh_pose, renn_pose
from zeichnen.figuren import WichtelSteif
from zeichnen.werkstatt import zeichne_papierbahn, zeichne_papierstaender, zeichne_walze

from .basis import Gehe, Jeweils, Mit, Schritt, Setze, Stehe, Szene, Tu, Warte
from .werk_basis import STAUB, Blick, hand, schweiss, verpuffen

WG = 0.6
ROLLE_Y = 70


class Rueckwaerts(Schritt):
    """Der Wichtel geht rückwärts (Blick zur Rolle) bis x=bis und zieht dabei Papier ab."""

    def __init__(self, bis, tempo=0.6):
        self.bis_v, self.tempo = bis, tempo

    def beginn(self, sz):
        self.bis = self.bis_v(sz) if callable(self.bis_v) else self.bis_v
        self.seite = 1 if self.bis > sz.w.x else -1

    def weiter(self, sz, u, dt):
        w = sz.w
        v = sz.tempo * self.tempo
        w.x += self.seite * v * dt
        w.phase -= v * dt / (38 * w.s)
        w.pose = geh_pose(w.phase, sz.t)
        w.pose.arm_v = -70
        w.pose.blick_y = 0.2
        sz.dreh += self.seite * v * dt / (sz.rr * sz.s) * sz.richtung

    def fertig(self, sz, u):
        if (sz.w.x - self.bis) * self.seite >= 0:
            sz.w.x = self.bis
            return True
        return False


class Papierrolle(Szene):
    """Ein Wichtel zieht Geschenkpapier von einer Rolle mit Feder; beim ersten Zug schnappt das
    Ende zurück. Beim zweiten rennt er mit dem Papier über der Schulter weit weg, die Bahn spannt
    sich, er stemmt sich dagegen, hält inne. Dann schnappt die Rolle zurück, wickelt ihn ein, und
    die dicke Walze mit zwei strampelnden Schnabelschuhen rollt davon."""
    name, titel, reihenfolge = 'werk_papier', 'Rollo-Geschenkpapier', 905

    def vorbereiten(self):
        self.zeige_figur = False
        r, s = self.richtung, self.s
        self.xp = self.vom_rand(0.1)
        self.cy = self.boden - ROLLE_Y * s
        self.rr, self.dreh = 28.0, 0.0
        self.an_hand, self.ende_xy = False, None
        self.walze = None
        self.wackeln = 0.0
        self.weg = False
        self.w = self.dazu('w', WichtelSteif, groesse=WG, knick=1.0)
        self.w.richtung = r
        self.w.x = self.aussen(-r) - r * 30 * s

    def anfang(self):
        r, s = self.richtung, self.s
        return self.xp + r * self.rr * 0.7 * s, self.cy + self.rr * 0.7 * s

    def lappen(self):
        x, y = self.anfang()
        return x + self.richtung * 3 * self.s, y + 16 * self.s

    def ablauf(self):
        r, s = self.richtung, self.s
        greif_x = self.xp + r * 52 * s

        def schnapp(ruck):
            def f(sz, u):
                k = min(1.0, u / 0.18)
                hx, hy = hand(sz.w, True)
                lx, ly = sz.lappen()
                sz.ende_xy = (hx + (lx - hx) * k, hy + (ly - hy) * k)
                sz.dreh -= r * 0.5
                if ruck:
                    sz.w.neigung = 25 * math.sin(min(1.0, u / 0.4) * math.pi)
                    sz.w.pose = Pose(arm_v=-100, arm_h=-60, kopf_vorn=u > 0.25, schreck=0.6, mund_offen=True,
                                     bein_v=-20, bein_h=15)
            return f

        def wegrennen(sz, u):
            w = sz.w
            w.richtung = r
            v = sz.tempo * 1.6 * min(1.0, 0.3 + u * 3)
            w.x += r * v / 60
            w.phase += v / 60 / (30 * w.s)
            w.pose = renn_pose(w.phase)
            w.pose.arm_v = 70
            w.pose.kopf_vorn = False
            w.neigung = 12
            sz.dreh += r * v / 60 / (sz.rr * s)
            sz.rr = max(22.0, sz.rr - 0.06)

        def stemmen(sz, u, pause=False):
            w = sz.w
            z = math.sin(u * 30)
            w.neigung = 32
            if pause:
                w.pose = Pose(arm_v=70, arm_h=50, bein_v=-30, bein_h=30, kopf_vorn=True, sorge=0.7,
                              auge_zu=0.35 < u < 0.5)
                w.neigung = 26
            else:
                w.phase += 0.5
                w.pose = renn_pose(w.phase)
                w.pose.arm_v = 70
                w.pose.sorge = 1.0
                w.pose.mund_offen = True
                w.x -= r * 14 * s / 60
                sz.dreh -= r * 14 / 60 / sz.rr
                if random.random() < 0.4:
                    sz.streue(w.x - r * 6 * s, sz.boden - 2 * s, 1, STAUB, tempo=50, dauer=0.4, r=(3, 6),
                              richtung=-math.pi / 2 - r * 1.2, streuung=0.4)
                if random.random() < 0.12:
                    schweiss(sz, w.x, w.y - 140 * WG * s)

        class Zurueckgerissen(Schritt):
            def beginn(self, sz):
                self.x0 = sz.w.x

            def weiter(self, sz, u, dt):
                w = sz.w
                f = min(1.0, u / 0.32)
                w.x = self.x0 + (sz.xp - self.x0) * f * f
                w.hopp = 40 * s * math.sin(f * math.pi)
                w.neigung = -70 * min(1.0, u / 0.08)
                w.pose = Pose(arm_v=-170, arm_h=-160, bein_v=-60, bein_h=-40, kopf_vorn=True, schreck=1.0,
                              mund_offen=True)
                w.striche = True
                sz.dreh -= r * 0.9

            def fertig(self, sz, u):
                return u >= 0.32

        def einwickeln(sz):
            w = sz.w
            w.zeige_figur, w.striche = False, False
            sz.an_hand, sz.ende_xy = False, None
            sz.walze = {'x': sz.xp, 'y': sz.cy, 'R': 46.0, 'vy': 0.0, 'auf': True}
            sz.wackeln = 1.0
            sz.streue(sz.xp, sz.cy, 10, STAUB, tempo=120, dauer=0.5)

        def strampeln(sz, u):
            sz.walze['dreh_extra'] = math.sin(u * 20) * 0.05

        return [
            Mit('w', Gehe(bis=greif_x, tempo=1.4)),
            Mit('w', Setze(richtung=-r)),
            Mit('w', Stehe(0.25, Pose(arm_v=-80, arm_h=-20, blick_y=0.3))),
            Setze(an_hand=True),
            Rueckwaerts(greif_x + r * 55 * s, 0.7),
            Setze(an_hand=False),
            Jeweils(0.45, schnapp(True)),
            Setze(ende_xy=None),
            Mit('w', Setze(neigung=0.0)),
            Mit('w', Blick(0.6)),
            Mit('w', Gehe(bis=greif_x, tempo=1.0)),
            Mit('w', Setze(richtung=-r)),
            Mit('w', Stehe(0.2, Pose(arm_v=-80, arm_h=-20, blick_y=0.3, kopf_vorn=True, auge_zu=True))),
            Setze(an_hand=True),
            Jeweils(1.0, wegrennen),
            Jeweils(0.9, lambda sz, u: stemmen(sz, u)),
            Jeweils(0.75, lambda sz, u: stemmen(sz, u, pause=True)),
            Zurueckgerissen(),
            Tu(einwickeln),
            Jeweils(0.8, strampeln),
            WalzeRollt(),
            Tu(lambda sz: sz.aufraeumen()),
            Warte(0.6),
        ]

    def aufraeumen(self):
        verpuffen(self, self.xp, self.boden, 60 * self.s, 100 * self.s, 12)
        self.weg = True
        self.an_hand, self.ende_xy = False, None

    def schreck_ablauf(self):
        self.nebenbei.clear()
        neu = []
        if self.walze:
            neu.append(WalzeRollt(4.0))
        w = self.w
        w.neigung, w.hopp, w.striche = 0.0, 0.0, False
        self.aufraeumen()
        if neu:
            return neu + [Warte(0.6)]
        return self.schreck_alle(weihnachtsmann=False)

    def weiter(self, dt):
        self.wackeln = max(0.0, self.wackeln - dt * 1.5)
        if self.an_hand and self.w.zeige_figur:
            self.ende_xy = hand(self.w, True)

    def zeichne_hinten(self, p):
        s, r = self.s, self.richtung
        if self.weg:
            return
        p.save()
        p.translate(self.xp, self.boden)
        p.rotate(math.sin(self.t * 40) * 4 * self.wackeln)
        p.scale(s * r, s)
        zeichne_papierstaender(p, 0 if self.walze and self.walze['auf'] else self.rr, self.dreh * r)
        p.restore()

    def zeichne_vorn(self, p):
        s = self.s
        if not self.weg and not self.walze:
            x0, y0 = self.anfang()
            x1, y1 = self.ende_xy or self.lappen()
            zeichne_papierbahn(p, x0, y0, x1, y1, breite=11 * s, wellen=0.0 if self.an_hand else 2 * s, t=self.t)
        wz = self.walze
        if wz:
            p.save()
            p.translate(wz['x'], wz['y'])
            p.scale(s, s)
            zeichne_walze(p, 0, 0, wz['R'], self.dreh + wz.get('dreh_extra', 0.0), self.t)
            p.restore()

    def grenzen_extra(self):
        s = self.s
        k = QRectF()
        if not self.weg:
            k = QRectF(self.xp - 40 * s, self.boden - 100 * s, 80 * s, 102 * s)
            if not self.walze:
                x0, y0 = self.anfang()
                x1, y1 = self.ende_xy or self.lappen()
                k = k.united(QRectF(min(x0, x1) - 8 * s, min(y0, y1) - 8 * s, abs(x1 - x0) + 16 * s,
                                    abs(y1 - y0) + 16 * s))
        if self.walze:
            R = (self.walze['R'] + 40) * s
            k = k.united(QRectF(self.walze['x'] - R, self.walze['y'] - R, 2 * R, 2 * R))
        return k


class WalzeRollt(Schritt):
    """Die Walze plumpst vom Ständer und rollt zum Rand hinaus."""

    def __init__(self, tempo=2.2):
        self.tempo = tempo

    def beginn(self, sz):
        wz = sz.walze
        self.seite = -1 if wz['x'] - sz.geo.left() < sz.geo.right() - wz['x'] else 1

    def weiter(self, sz, u, dt):
        wz, s = sz.walze, sz.s
        boden = sz.boden - wz['R'] * s
        if wz['y'] < boden or wz['vy'] < 0:
            wz['vy'] += 1600 * s * dt
            wz['y'] += wz['vy'] * dt
            wz['auf'] = False
            if wz['y'] >= boden:
                wz['y'] = boden
                wz['vy'] = -wz['vy'] * 0.35 if wz['vy'] > 200 * s else 0.0
                sz.streue(wz['x'], sz.boden, 6, STAUB, tempo=70, dauer=0.5)
        v = sz.tempo * self.tempo * min(1.0, u * 2)
        wz['x'] += self.seite * v * dt
        sz.dreh += self.seite * v * dt / (wz['R'] * s)

    def fertig(self, sz, u):
        wz, s = sz.walze, sz.s
        R = (wz['R'] + 40) * s
        return not QRectF(wz['x'] - R, wz['y'] - R, 2 * R, 2 * R).intersects(sz.geo)
