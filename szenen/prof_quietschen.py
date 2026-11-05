import math

from zeichnen.figur import Pose
from zeichnen.grundlagen import blinzeln
from zeichnen.labor_c import KatzeKugel, zeichne_anschriebe, zeichne_quietsch, zeichne_tafel_c, zeichne_zacken

from .basis import Gehe, Jeweils, Mit, Nebenbei, Schaue, Setze, Stehe, Tu, WarteNebenbei
from .professor import Schreibe, TafelSzene, Zurueck


class Quietschen(TafelSzene):
    """Die Kreide quietscht: Tafel und Kreide zittern, seine Haare stehen ab, die Katze sträubt
    das Fell. Er hebt die Kreide ab, alles beruhigt sich, nur die Katze bleibt eine Fellkugel."""
    name, titel, reihenfolge = 'quietschen', 'Kreidequietschen', 74

    def vorbereiten(self):
        self.tafel_vorbereiten(0.22)
        self.quietsch = 0.0     # Ziel
        self.katze_los = False
        self.q_zeit = 0.0
        self.q = 0.0            # geglättet
        self.a = self.schreib('1+1=', -64, -178, 28)
        self.b = self.schreib('2', 22, -178, 28)
        k = self.dazu('katze', KatzeKugel, groesse=0.62, sitzt=False, buckel=0.0, kugel=0.0)
        k.tempo = self.tempo * 0.9

    def katze_platz(self):
        return self.tafel_x - 128 * self.s

    def weiter(self, dt):
        super().weiter(dt)
        self.q += (self.quietsch - self.q) * min(1.0, dt * 8)
        if self.erschreckt:
            return
        self.haare = self.q
        k = self.darsteller['katze']
        k.buckel = max(k.buckel, min(1.0, self.q_zeit / 0.6))
        self.q_zeit = self.q_zeit + dt if self.q > 0.8 else 0.0
        if self.q_zeit > 1.2:
            k.kugel = min(1.0, k.kugel + dt * 2.5)

    def zeichne_tafel(self, p):
        p.save()
        z = self.q * 1.6
        p.translate(self.tafel_x + z * math.sin(self.t * 83) * self.s, self.boden + z * math.cos(self.t * 71) * self.s)
        p.scale(self.s, self.s)
        zeichne_tafel_c(p, wisch=self.wisch, kreide=self.kreide_da)
        zeichne_anschriebe(p, self.anschriebe)
        p.restore()

    def zeichne_davor(self, p):
        super().zeichne_davor(p)
        if self.q > 0.05 and self.kreide_ort and self.zeige_figur:
            x, y = self.kreide_ort
            p.save()
            p.translate(x, y)
            p.scale(self.s, self.s)
            zeichne_quietsch(p, 0, 0, self.t, self.q)
            for w in (-115, -75, 75, 115):
                zeichne_zacken(p, 20 * math.cos(math.radians(w)), 20 * math.sin(math.radians(w)), 14, w, self.t)
            p.restore()

    def requisiten_kasten(self):
        return super().requisiten_kasten().adjusted(-4 * self.s, -4 * self.s, 4 * self.s, 0)

    def ablauf(self):
        r = self.richtung
        self.x = self.aussen(-r)
        k = self.darsteller['katze']
        k.x = self.aussen(-r) - r * 90 * self.s

        def hinsetzen(d):
            d.richtung, d.sitzt = 1, True

        def abheben(sz, u):
            sz.pose = Pose(arm_v=-150 + 10 * math.sin(u * 20), arm_v_x=14, sorge=0.6, blick_y=-0.3)
            sz.kreide_ort = sz.hand()

        return [
            Nebenbei(Mit('katze', Gehe(bis=lambda d: d.sz.katze_platz(), tempo=0.9)),
                     Mit('katze', Tu(hinsetzen)),
                     Mit('katze', StehBis(lambda d, u: Pose(kopf_vorn=True, auge_zu=blinzeln(d.t, 0.4)),
                                          lambda d: d.sz.katze_los))),
            *self.an_tafel(),
            Stehe(0.4),
            Setze(kreide_da=False),
            Schreibe(self.a, 2.2),
            Setze(quietsch=1.0),
            Schreibe(self.b, 1.8, bis=0.5),
            Stehe(1.0, lambda sz, u: Pose(arm_v=sz.arm_zu(*sz.kreide_ort) + 3 * math.sin(u * 60), schreck=0.7,
                                          sorge=1.0, blick_y=-0.2)),
            Setze(quietsch=0.0),
            Jeweils(0.6, abheben),
            Setze(kreide_ort=None),
            Stehe(0.8, lambda sz, u: Pose(arm_v=-150, arm_v_x=14, blick_y=-0.5, auge_zu=0.4 < u < 0.52)),
            Setze(richtung=lambda sz: 1 if k.x > sz.x else -1),
            Stehe(1.6, lambda sz, u: Pose(blick_y=0.6, sorge=0.7, arm_v=-30, arm_h=20, mund_offen=u > 0.9)),
            Schaue(1.3),
            Setze(richtung=-1),
            Schreibe(self.b, 1.6),
            Setze(kreide_ort=None),
            Zurueck(40),
            Stehe(0.8, lambda sz, u: Pose(kopf_vorn=True, auge_zu=True, arm_v=-20, arm_h=20)),
            Setze(katze_los=True),
            Nebenbei(Mit('katze', Gehe(bis=lambda d: d.sz.aussen(-r) - r * 60 * d.sz.s, tempo=1.1))),
            *self.tafel_abgang(),
            WarteNebenbei(),
        ]


class StehBis(Stehe):
    def __init__(self, pose, bedingung):
        super().__init__(0, pose)
        self.bedingung = bedingung

    def fertig(self, sz, u):
        return self.bedingung(sz)
