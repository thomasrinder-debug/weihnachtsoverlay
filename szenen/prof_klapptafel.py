import math

from PyQt6.QtCore import QPointF
from PyQt6.QtGui import QTransform

from zeichnen.figur import Pose
from zeichnen.grundlagen import blinzeln
from zeichnen.labor import zeichne_kreide
from zeichnen.labor_c import STAUB, zeichne_anschriebe, zeichne_tafel_c

from .basis import Erschrecke, Gehe, Jeweils, Schaue, Setze, Stehe, Tu, Wandel
from .professor import FUNKEN, HaareHoch, Schreibe, TafelSzene

FUSS = 57


class Klapptafel(TafelSzene):
    """Die Kreide rollt ihm weg, er bückt sich, und die Tafel klappt um, genau auf seinen Kopf.
    Im Kreidestaub bleibt der Abdruck seiner Frisur; er richtet seine Haare passend dazu."""
    name, titel, reihenfolge = 'klapptafel', 'Klapptafel', 76

    def vorbereiten(self):
        self.tafel_vorbereiten(0.2)
        self.kipp = 0.0
        self.tafel_vorn = False     # beim Umklappen liegt die Tafel vor ihm
        self.abdruck = 0.0
        self.boden_kreide = None      # (x, winkel) der heruntergefallenen Kreide
        self.a = self.schreib('6/2=3', -66, -186, 26)

    def tafel_trafo(self):
        tr = QTransform()
        tr.translate(self.tafel_x, self.boden)
        tr.scale(self.s, self.s)
        tr.translate(FUSS, 0)
        tr.rotate(self.kipp)
        tr.translate(-FUSS, 0)
        return tr

    def zeichne_tafel(self, p):
        p.save()
        p.setTransform(self.tafel_trafo(), True)
        zeichne_tafel_c(p, wisch=self.wisch, kreide=self.kreide_da, staub=0.5, abdruck=self.abdruck)
        zeichne_anschriebe(p, self.anschriebe)
        p.restore()

    def zeichne_requisiten(self, p):
        if not self.tafel_vorn:
            self.zeichne_tafel(p)

    def zeichne_davor(self, p):
        if self.boden_kreide:
            x, w = self.boden_kreide
            p.save()
            p.translate(x, self.boden - 2.4 * self.s)
            p.scale(self.s, self.s)
            zeichne_kreide(p, 0, 0, w, 10)
            p.restore()
        if self.tafel_vorn:
            self.zeichne_tafel(p)
        super().zeichne_davor(p)

    def requisiten_kasten(self):
        k = super().requisiten_kasten()
        tr = QTransform().translate(self.tafel_x + FUSS * self.s, self.boden).rotate(self.kipp)
        return tr.mapRect(k.translated(-self.tafel_x - FUSS * self.s, -self.boden)).adjusted(0, 0, 40 * self.s, 0)

    def ablauf(self):
        self.x = self.aussen(-self.richtung)
        s = self.s

        def fallen_lassen(sz, u):
            # Kreide rutscht aus der Hand, fällt und rollt nach rechts weg
            x0, y0 = sz.hand()
            if u < 0.3:
                sz.kreide_ort = (x0 + 10 * s * u, y0 + (sz.boden - y0) * (u / 0.3) ** 2)
            else:
                sz.kreide_ort = None
                v = min(1.0, (u - 0.3) / 1.1)
                ziel = sz.tafel_x + 160 * s
                sz.boden_kreide = (sz.ziel_kreide0 + (ziel - sz.ziel_kreide0) * (1 - (1 - v) ** 2), (u - 0.3) * 520)
            sz.pose = Pose(arm_v=-40, schreck=0.6 if u < 0.6 else 0.0, sorge=0.6, blick_y=0.7)

        def merke(sz):
            sz.ziel_kreide0 = sz.hand()[0] - 4 * s

        def buecken(sz, u):
            sz.pose = Pose(arm_v=-8 + 6 * math.sin(u * 8), arm_h=10, blick_y=0.9, bein_v=-10, bein_h=8)

        def klappen(sz, u):
            if u < 0.5:
                sz.kipp = 2.5 * math.sin(u * 28) * u
            else:
                sz.tafel_vorn = True
                v = min(1.0, (u - 0.5) / 0.3)
                sz.kipp = 20 * v * v
            if u >= 0.8 and not getattr(sz, 'getroffen', False):
                sz.getroffen = True
                q = sz.trafo().map(QPointF(0, -190))
                sz.streue(q.x(), q.y(), 14, STAUB, tempo=120, dauer=0.8, r=(4, 9))
                sz.streue(q.x(), q.y() - 20 * s, 6, FUNKEN, tempo=110, dauer=0.9, r=(3, 6), art='stern')
            if u >= 0.8:
                sz.stauchen = 0.86 - 0.06 * math.exp(-(u - 0.8) * 8)
            buecken(sz, u)

        def hochdruecken(sz, u):
            f = min(1.0, u / 0.8)
            sz.kipp = 20 * (1 - f * f)
            sz.neigung = 20 * (1 - f)
            sz.stauchen = 0.86 + 0.14 * f
            sz.abdruck = f
            sz.pose = Pose(arm_v=-150, arm_h=-140, arm_v_x=14, sorge=0.8, auge_zu=True)

        def haare_richten(sz, u):
            sz.haare = min(1.0, u / 1.3)
            sz.pose = Pose(kopf_vorn=True, arm_v=-165 + 12 * math.sin(u * 14), arm_h=-160 - 12 * math.sin(u * 14),
                           arm_v_x=10, auge_zu=True, mund_offen=False)

        return [
            *self.an_tafel(),
            Stehe(0.4),
            Setze(kreide_da=False),
            Schreibe(self.a, 2.6),
            Tu(merke),
            Jeweils(1.4, fallen_lassen),
            Stehe(0.4, lambda sz, u: Pose(blick_y=0.7, sorge=0.6, auge_zu=blinzeln(sz.t))),
            Gehe(bis=lambda sz: sz.boden_kreide[0] + 36 * s, tempo=0.6),
            Setze(richtung=-1),
            Wandel(0.35, neigung=22, stauchen=0.86),
            Jeweils(1.1, klappen),
            Setze(kipp=20.0),
            Stehe(1.0, lambda sz, u: Pose(arm_v=-8, arm_h=10, schreck=0.8, sorge=1.0, bein_v=-10, bein_h=8)),
            Setze(boden_kreide=None),
            Jeweils(0.8, hochdruecken),
            Setze(kipp=0.0, neigung=0.0, stauchen=1.0, abdruck=1.0, tafel_vorn=False),
            Stehe(0.6, lambda sz, u: Pose(sorge=0.6, auge_zu=blinzeln(sz.t))),
            Setze(richtung=-1),
            Stehe(1.2, lambda sz, u: Pose(blick_y=-0.4, arm_v=-150, arm_v_x=12, sorge=0.3 + 0.4 * min(1, u))),
            Schaue(0.9),
            Jeweils(1.4, haare_richten),
            Setze(haare=1.0),
            Setze(richtung=-1),
            Stehe(0.6, lambda sz, u: Pose(blick_y=-0.3, auge_zu=blinzeln(sz.t))),
            Stehe(1.3, lambda sz, u: Pose(kopf_vorn=True, auge_zu=True, hub=-4 * abs(math.sin(u * 7)),
                                          arm_v=-20, arm_h=20)),
            *self.tafel_abgang(),
        ]

    def schreck_ablauf(self):
        """Kopf zwischen die Schultern, versinken."""
        self.kreide_ort = None
        self.boden_kreide = None
        self.nebenbei.clear()
        tief = 330 * self.s
        return [HaareHoch(1.0), Erschrecke(0.3, 46), Setze(neigung=0.0),
                Wandel(0.15, stauchen=0.72),
                Wandel(0.45, y=lambda sz: sz.y + tief, senke=tief, kipp=0.0),
                Tu(lambda sz: setattr(sz, 'zeige_figur', False))] + self._ende()

