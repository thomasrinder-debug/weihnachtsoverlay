import math

from PyQt6.QtGui import QTransform

from zeichnen.figur import Pose
from zeichnen.figuren import WichtelSteif
from zeichnen.grundlagen import blinzeln
from zeichnen.labor_c import tafel_beine, zeichne_anschriebe, zeichne_tafel_c

from .basis import Gehe, Jeweils, Mit, Nebenbei, Setze, Stehe, WarteNebenbei
from .professor import Schreibe, TafelSzene, Zurueck

MITTE = (0, -144)       # Drehpunkt der Tafelfläche


def umkippen(a, ziel, dauer):
    """Die Null fällt um: erst zögernd, dann schnell, federt nach."""
    def f(sz, u):
        if u < 0.35:
            a.dreh = ziel * 0.04 * math.sin(u * 30)
        else:
            v = min(1.0, (u - 0.35) / (dauer - 0.55))
            nach = 0.08 * math.sin(max(0.0, u - dauer + 0.2) * 25) * (v >= 1)
            a.dreh = ziel * (v * v - nach)
    return Jeweils(dauer, f)


class Null(TafelSzene):
    """Eine große Null kippt immer wieder zur Seite, er richtet sie zweimal auf. Der Wichtel
    dreht schließlich die ganze Tafel um eine Vierteldrehung, und der Professor nickt zufrieden."""
    name, titel, reihenfolge = 'null', 'Schiefe Null', 78

    def vorbereiten(self):
        self.tafel_vorbereiten(0.22)
        self.tafel_dreh = 0.0
        self.a = self.schreib('1-1=', -66, -176, 30)
        self.n = self.schreib('0', 30, -186, 40)
        w = self.dazu('wichtel', WichtelSteif, groesse=0.62, knick=1.0)
        w.tempo = self.tempo * 0.9

    def tafel_trafo(self):
        tr = QTransform()
        tr.translate(self.tafel_x, self.boden)
        tr.scale(self.s, self.s)
        return tr

    def zeichne_tafel(self, p):
        p.save()
        p.setTransform(self.tafel_trafo(), True)
        tafel_beine(p)
        p.translate(*MITTE)
        p.rotate(self.tafel_dreh)
        p.translate(-MITTE[0], -MITTE[1])
        zeichne_tafel_c(p, wisch=self.wisch, kreide=self.kreide_da, beine=False)
        zeichne_anschriebe(p, self.anschriebe)
        p.restore()

    def requisiten_kasten(self):
        k = super().requisiten_kasten()
        tr = QTransform()
        mx, my = self.welt(*MITTE)
        tr.translate(mx, my)
        tr.rotate(self.tafel_dreh)
        tr.translate(-mx, -my)
        return k.united(tr.mapRect(k))

    def null_oben(self):
        """Weltpunkt oben an der Null (zum Aufrichten mit dem Finger)."""
        a = self.n
        mx, my = a.x + a.breite() / 2, a.y + a.hoehe / 2
        w = math.radians(a.dreh)
        lx, ly = mx + math.sin(w) * a.hoehe * 0.5, my - math.cos(w) * a.hoehe * 0.5
        return self.welt(lx, ly)

    def ablauf(self):
        r = self.richtung
        s = self.s
        self.x = self.aussen(-r)
        wi = self.darsteller['wichtel']
        wi.x = self.aussen(-r) - r * 80 * s

        def aufrichten(dauer, wut=0.0):
            def f(sz, u):
                v = min(1.0, u / dauer)
                sz.n.dreh = -90 * (1 - v) ** 2
                px, py = sz.null_oben()
                sz.pose = Pose(arm_v=sz.arm_zu(px, py), sorge=0.4 + wut * 0.6, blick_y=-0.3,
                               mund_offen=wut > 0 and (u * 8) % 2 < 1)
            return Jeweils(dauer + 0.15, f)

        def drehen(d, u):
            # Wichtel stemmt die linke Kante hoch, die Tafel dreht sich eine Vierteldrehung
            v = min(1.0, u / 1.1)
            d.sz.tafel_dreh = 90 * (v * v * (3 - 2 * v)) + 6 * math.sin(max(0.0, u - 1.1) * 18) * math.exp(
                -max(0.0, u - 1.1) * 5)
            d.hopp = 10 * d.sz.s * math.sin(min(1.0, u / 0.6) * math.pi)
            d.pose = Pose(arm_v=-170, arm_h=-165, arm_v_x=8, mund_offen=True, bein_v=-14, bein_h=10)

        links = lambda d: d.sz.tafel_x - 108 * d.sz.s  # noqa: E731
        return [
            *self.an_tafel(),
            Stehe(0.3),
            Setze(kreide_da=False),
            Schreibe(self.a, 1.5),
            Schreibe(self.n, 0.9),
            Setze(kreide_ort=None),
            Zurueck(40),
            Stehe(0.4, lambda sz, u: Pose(kopf_vorn=True, auge_zu=blinzeln(sz.t), arm_v=-20, arm_h=20)),
            umkippen(self.n, -90, 1.0),
            Stehe(0.6, lambda sz, u: Pose(schreck=0.5, sorge=0.8, blick_y=-0.2)),
            Gehe(bis=lambda sz: sz.tafel_x + 108 * sz.s, tempo=0.6),
            Setze(richtung=-1),
            aufrichten(0.6),
            Zurueck(30, 0.4),
            Stehe(0.6, lambda sz, u: Pose(blick_y=-0.2, sorge=0.5, auge_zu=0.3 < u < 0.4)),
            umkippen(self.n, -90, 0.8),
            Stehe(0.3, lambda sz, u: Pose(schreck=0.7, sorge=1.0)),
            Gehe(bis=lambda sz: sz.tafel_x + 108 * sz.s, tempo=0.8),
            Setze(richtung=-1),
            aufrichten(0.4, wut=1.0),
            Stehe(0.5, lambda sz, u: Pose(arm_v=sz.arm_zu(*sz.null_oben()), sorge=1.0, blick_y=-0.3)),
            Zurueck(30, 0.4),
            umkippen(self.n, -90, 0.7),
            Stehe(0.7, lambda sz, u: Pose(kopf_vorn=True, sorge=1.0, arm_v=10, arm_h=-10, hub=2)),
            # der Wichtel hilft
            Mit('wichtel', Gehe(bis=links, tempo=1.0)),
            Mit('wichtel', Setze(richtung=1)),
            Mit('wichtel', Stehe(0.6, lambda d, u: Pose(blick_y=-0.6, auge_zu=blinzeln(d.t),
                                                       arm_v=-150 + 8 * math.sin(u * 6), arm_v_x=8))),
            Mit('wichtel', Stehe(0.3, Pose(kopf_vorn=True, mund_offen=True, arm_v=-120, arm_v_x=14))),
            Mit('wichtel', Jeweils(1.7, drehen)),
            Setze(tafel_dreh=90.0),
            Mit('wichtel', Setze(hopp=0.0)),
            Nebenbei(Mit('wichtel', Stehe(1.4, lambda d, u: Pose(kopf_vorn=True, auge_zu=True, arm_v=-20, arm_h=20,
                                                                hub=-3 * abs(math.sin(u * 7)))))),
            Stehe(0.5, lambda sz, u: Pose(blick_y=-0.4, auge_zu=blinzeln(sz.t))),
            Stehe(1.4, lambda sz, u: Pose(kopf_vorn=True, auge_zu=True, hub=-4 * abs(math.sin(u * 7)),
                                          arm_v=-20, arm_h=20)),
            WarteNebenbei(),
            Nebenbei(Mit('wichtel', Gehe(bis=lambda d: d.sz.aussen(-r) - r * 40 * d.sz.s, tempo=1.0))),
            *self.tafel_abgang(),
            WarteNebenbei(),
        ]

    def schreck_ablauf(self):
        self.kreide_ort = None
        self.darsteller['wichtel'].hopp = 0.0
        return self.schreck_versinken()
