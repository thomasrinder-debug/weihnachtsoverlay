import math

from PyQt6.QtCore import QPointF
from PyQt6.QtGui import QColor, QTransform

from zeichnen.figur import Pose
from zeichnen.grundlagen import KEIN_STIFT, blinzeln, kreis, radial
from zeichnen.labor import KREIDE
from zeichnen.labor_c import zeichne_anschriebe, zeichne_tafel_c

from .basis import Erschrecke, Gehe, Jeweils, Setze, Stehe, Tu
from .professor import HaareHoch, Schreibe, TafelSzene, Zurueck, schreib_stehe

TEXT = '1+2+3+4+5+6+7+8+9+'
DREHPUNKT = 57          # rechter Fuß der Tafel


class Endlos(TafelSzene):
    """Die Formel wird zum Rand hin immer kleiner, zum Schluss ein dicker Punkt in der Ecke.
    Er tritt zufrieden zurück, und die Tafel kippt unter dem Gewicht des Punkts zur Seite."""
    name, titel, reihenfolge = 'endlos', 'Endlosformel', 73

    def vorbereiten(self):
        self.tafel_vorbereiten(0.2)
        self.kipp = 0.0
        self.rollo = 0.0
        self.punkt_r = 0.0
        self.zeichen = []
        x, h = -68.0, 30.0
        for ch in TEXT:
            yb = -160 + (x + 68) / 136 * 50
            a = self.schreib(ch, x, yb - h, h)
            self.zeichen.append(a)
            x += a.breite()
            h *= 0.88
            if x > 56:
                break
        self.punkt = (64.0, -106.0)

    # -- Zeichnen: Tafel kippt um ihren rechten Fuß, beim Schreck rollt sie sich ein

    def tafel_trafo(self):
        tr = QTransform()
        tr.translate(self.tafel_x, self.boden)
        tr.scale(self.s, self.s * (1 - self.rollo))
        tr.translate(DREHPUNKT, 0)
        tr.rotate(self.kipp)
        tr.translate(-DREHPUNKT, 0)
        return tr

    def zeichne_tafel(self, p):
        p.save()
        p.setTransform(self.tafel_trafo(), True)
        zeichne_tafel_c(p, wisch=self.wisch, kreide=self.kreide_da)
        zeichne_anschriebe(p, self.anschriebe)
        if self.punkt_r > 0:
            p.setPen(KEIN_STIFT)
            x, y = self.punkt
            p.setBrush(radial(x - 1, y - 1, self.punkt_r * 1.3, QColor('#FFFFFF'), KREIDE))
            kreis(p, x, y, self.punkt_r)
        p.restore()

    def requisiten_kasten(self):
        k = super().requisiten_kasten()
        tr = QTransform().translate(self.tafel_x, self.boden)
        tr = tr.scale(1, 1 - self.rollo)
        tr.translate(DREHPUNKT * self.s, 0)
        tr.rotate(self.kipp)
        tr.translate(-DREHPUNKT * self.s, 0)
        return tr.mapRect(k.translated(-self.tafel_x, -self.boden)).adjusted(-4 * self.s, 0, 4 * self.s, 0)

    def punkt_welt(self):
        q = self.tafel_trafo().map(QPointF(*self.punkt))
        return q.x(), q.y()

    # -- Ablauf

    def ablauf(self):
        self.x = self.aussen(-self.richtung)

        def setzen(sz, u):
            # Punkt mit Nachdruck: zweimal draufdrücken
            sz.punkt_r = 7.5 * min(1.0, u / 0.5)
            px, py = sz.punkt_welt()
            stoss = 6 * abs(math.sin(u * 9))
            sz.kreide_ort = (px + stoss * sz.s, py)
            sz.pose = Pose(arm_v=sz.arm_zu(px + stoss * sz.s, py), blick_y=0.3, sorge=0.2,
                           auge_zu=blinzeln(sz.t))

        def kippen(sz, u):
            # langsam anfangen, dann fallen, gegen den Boden federn
            if u < 0.5:
                sz.kipp = 3 * math.sin(u * 30) * u
            else:
                v = min(1.0, (u - 0.5) / 0.55)
                sz.kipp = 24 * v * v - (4 * math.sin((u - 1.05) * 18) * math.exp(-(u - 1.05) * 5) if v >= 1 else 0)
            sz.pose = Pose(kopf_vorn=u < 0.5, arm_v=-128 if u < 0.6 else -60, arm_h=-128 if u < 0.6 else -40,
                           arm_v_x=14, bein_v=-14, bein_h=14, schreck=0.0 if u < 0.6 else 0.6,
                           sorge=0.0 if u < 0.6 else 0.8, mund_offen=u < 0.4)

        def aufrichten(sz, u):
            f = min(1.0, u / 0.7)
            sz.kipp = 24 * (1 - f) ** 2 - 5 * math.sin(f * math.pi) * (f > 0.6)
            sz.punkt_r = 7.5 * max(0.0, 1 - u / 0.3)

        def wegwischen(sz, u):
            px, py = sz.punkt_welt()
            sz.pose = Pose(arm_v=sz.arm_zu(px + 4 * math.sin(u * 25) * sz.s, py), blick_y=0.3, sorge=0.5)

        schreiben = [Schreibe(a, 0.15 + 0.022 * a.hoehe, abstand=58) for a in self.zeichen]
        return [
            *self.an_tafel(),
            Stehe(0.3),
            Setze(kreide_da=False),
            *schreiben,
            schreib_stehe(0.4, lambda sz, u: sz.punkt_welt()),
            Jeweils(0.8, setzen),
            Setze(kreide_ort=None),
            Zurueck(60),
            Stehe(0.3),
            Jeweils(1.9, kippen),
            Setze(kipp=24),
            Stehe(1.1, lambda sz, u: Pose(kopf_vorn=True, sorge=0.8, blick_x=math.sin(u * 3) * 0.6,
                                          auge_zu=0.6 < u < 0.7)),
            Stehe(0.8, lambda sz, u: Pose(arm_v=-150, arm_v_x=12, blick_y=-0.6, sorge=0.6)),
            Gehe(bis=lambda sz: sz.punkt_welt()[0] + 55 * sz.s, tempo=0.6),
            Setze(richtung=-1),
            Jeweils(0.5, wegwischen),
            Jeweils(0.9, lambda sz, u: (aufrichten(sz, u), wegwischen(sz, u + 0.5))),
            Setze(kipp=0.0, punkt_r=0.0),
            Zurueck(30, 0.4),
            Stehe(1.3, lambda sz, u: Pose(kopf_vorn=True, auge_zu=True, hub=-4 * abs(math.sin(u * 7)),
                                          arm_v=-20, arm_h=20)),
            *self.tafel_abgang(),
        ]

    def schreck_ablauf(self):
        """Er packt die Tafel oben und zieht sie wie ein Rollo mit sich hinunter."""
        self.kreide_ort = self.schwamm_ort = None
        self.nebenbei.clear()
        tief = 330 * self.s

        def ziehen(sz, u):
            f = min(1.0, u / 0.5)
            sz.rollo = f * f
            sz.y = sz.boden + tief * f * f
            sz.pose = Pose(arm_v=-170, arm_h=-160, arm_v_x=16, schreck=1.0, sorge=1.0, mund_offen=True)

        return [HaareHoch(1.0), Erschrecke(0.3, 46), Jeweils(0.5, ziehen),
                Tu(lambda sz: setattr(sz, 'zeige_figur', False)), Setze(weg_ist=True)] + self._ende()
