import math

from PyQt6.QtCore import QRectF

from zeichnen.baeckerei import MEHL, Bestaeubt, zeichne_mehlsack
from zeichnen.figur import Pose
from zeichnen.figuren import Wichtel
from zeichnen.grundlagen import blinzeln

from .back_bausteine import publikum, zittern
from .basis import Gehe, Jeweils, Mit, Setze, Springe, Stehe, Szene, Tu, Wandel, Warte

G = 0.9
WOLKE = [MEHL, MEHL, MEHL.darker(104)]


class BackMehl(Szene):
    """Der Wichtel will einen Mehlsack öffnen, der Knoten hält. Ziehen, mit dem Fuß gegen den Sack
    stemmen, dann ein gewaltiger Ruck: der Knoten gibt nach, er landet auf dem Hosenboden. Stille.
    Der Sack seufzt – und explodiert in einer Mehlwolke. Übrig bleibt ein schneeweißer Wichtel,
    der blinzelt, niest und mit weißen Fußspuren davonstapft."""
    name, titel, reihenfolge = 'back_mehl', 'Mehlsack', 803

    def vorbereiten(self):
        r = self.richtung
        self.zeige_figur = False
        self.w = self.dazu('w', Bestaeubt(Wichtel, augen=[(-6, -126), (12, -126)]), groesse=G, mehl=0.0)
        self.w.richtung = r
        self.sx = self.vom_rand(0.17)
        self.zug = 0.0
        self.offen = False
        self.platt = 0.0
        self.spuren = []
        self.letzte_spur = None

    def stand(self):
        """x des Wichtels, damit seine Hand an der Kordel ist."""
        return self.sx - self.richtung * (21 + 8 + self.zug + 39) * self.s

    def ablauf(self):
        r, s = self.richtung, self.s

        def ziehen(staerke, dauer):
            def f(d, u):
                sz = d.sz
                g = min(1.0, u / 0.3)
                sz.zug = (10 + 12 * staerke) * g + abs(zittern(u, 30, 3 * staerke))
                d.x = sz.stand() - r * math.sin(math.radians(14 * staerke * g)) * 60 * s
                d.neigung = -14 * staerke * g + zittern(u, 35, 2)
                d.pose = Pose(arm_v=-82, arm_h=-78, bein_v=-28 - 22 * (staerke > 1.5), bein_h=22,
                              auge_zu=staerke > 1.5, mund_offen=staerke > 1.5, sorge=0.7, wipp=zittern(u, 30, 3))
            return Jeweils(dauer, f)

        def ruck(d, u):
            d.sz.zug = 0.0
            d.sz.offen = True

        def boom(sz):
            sz.w.mehl = 1.0
            for _ in range(3):
                sz.streue(sz.sx, sz.boden - 70 * s, 26, WOLKE, tempo=330, dauer=1.9, r=(18, 40))
            sz.streue(sz.w.x, sz.boden - 60 * s, 18, WOLKE, tempo=200, dauer=1.6, r=(18, 36))

        def platt(sz, u):
            sz.platt = min(1.0, u / 0.4)

        def niesen(d, u):
            if u < 0.5:
                d.pose = Pose(kopf_vorn=True, auge_zu=True, mund_offen=True, blick_y=-0.6)
                d.neigung = -12 * u / 0.5
            else:
                d.pose = Pose(kopf_vorn=True, auge_zu=True, mund_offen=True, arm_v=-60, arm_h=-50)
                d.neigung = 22
                if d.sz.t - getattr(d.sz, 'nies_t', -9) > 1:
                    d.sz.nies_t = d.sz.t
                    d.sz.streue(d.x, d.boden - 120 * G * s, 20, WOLKE, tempo=180, dauer=1.1, r=(10, 24))

        def sitzen(d, u):
            d.stauchen = 0.8
            d.pose = Pose(bein_v=-80, bein_h=-70, arm_v=-30, arm_h=-20, kopf_vorn=True,
                          schreck=0.4 if u < 0.3 else 0.0, auge_zu=blinzeln(d.t))

        return [
            Mit('w', Gehe(bis=lambda d: d.sz.stand())),
            ziehen_mit(ziehen(1, 1.0)),
            Mit('w', Setze(neigung=0.0)), Setze(zug=0.0),
            Mit('w', Setze(x=lambda d: d.sz.stand())),
            Mit('w', publikum(0.6, sorge=0.6)),
            ziehen_mit(ziehen(2, 1.2)),
            Tu(lambda sz: sz.streue(sz.sx, sz.boden - 100 * s, 5, WOLKE, tempo=50, r=(5, 9))),
            Mit('w', Setze(neigung=0.0)),
            Mit('w', Stehe(0.6, lambda d, u: Pose(arm_v=-150 + 20 * math.sin(u * 10), kopf_vorn=True, sorge=1.0,
                                                 mund_offen=u > 0.3))),
            ziehen_mit(ziehen(2.6, 0.5)),
            Mit('w', Jeweils(0.01, ruck)),
            Mit('w', Springe(lambda d: (d.x - r * 70 * s, d.boden), 0.45, 40)),
            Mit('w', Jeweils(0.9, sitzen)),
            Tu(lambda sz: sz.streue(sz.sx, sz.boden - 85 * s, 4, WOLKE, tempo=40, r=(4, 8))),
            Mit('w', Jeweils(0.7, sitzen)),
            Tu(boom),
            Jeweils(0.4, platt),
            Mit('w', Jeweils(1.1, sitzen)),
            Mit('w', Setze(stauchen=1.0)),
            Mit('w', publikum(0.9)),
            Mit('w', Jeweils(0.8, niesen)),
            Mit('w', Setze(neigung=0.0, richtung=lambda d: d.naechster_rand())),
            Mit('w', Gehe(tempo=0.8)),
            WarteSpuren(),
        ]

    def schreck_ablauf(self):
        self.zug = 0.0
        return [Mit('w', Setze(neigung=0.0, stauchen=1.0))] + self.schreck_alle(weihnachtsmann=False)

    def weiter(self, dt):
        w = self.w
        if w.mehl > 0.5 and w.y >= self.boden - 1:
            if self.letzte_spur is None or abs(w.x - self.letzte_spur) > 34 * self.s:
                self.letzte_spur = w.x
                self.spuren.append(w.x)

    def zeichne_hinten(self, p):
        s = self.s
        p.setBrush(MEHL)
        for i, x in enumerate(self.spuren):
            p.drawEllipse(QRectF(x - 9 * s + (i % 2) * 6 * s, self.boden - 4 * s, 16 * s, 5 * s))
        p.save()
        p.translate(self.sx, self.boden)
        p.scale(s * self.richtung * -1, s)
        zeichne_mehlsack(p, self.offen, self.platt, self.zug)
        p.restore()

    def grenzen_extra(self):
        s = self.s
        k = QRectF(self.sx - 60 * s, self.boden - 120 * s, 120 * s, 120 * s)
        if self.spuren:
            a, b = min(self.spuren), max(self.spuren)
            k = k.united(QRectF(a - 12 * s, self.boden - 6 * s, b - a + 24 * s, 6 * s))
        return k


def ziehen_mit(schritt):
    return Mit('w', schritt)


class WarteSpuren(Warte):
    def __init__(self):
        super().__init__(0.0)
