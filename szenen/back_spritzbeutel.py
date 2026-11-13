import math

from PyQt6.QtCore import QPointF, QRectF

from zeichnen.baeckerei import GUSS, zeichne_gussklecks, zeichne_riesenkeks, zeichne_sahnehaube, zeichne_spritzbeutel
from zeichnen.figur import Pose
from zeichnen.figuren import augen
from zeichnen.grundlagen import ROT, ROT_DUNKEL, blinzeln, kreis, radial, stift

from .back_bausteine import figur_trafo, hand, kopf, publikum, zittern
from .basis import Erschrecke, Gehe, Gleite, Jeweils, Renne, Setze, Stehe, Szene, Wandel


class BackSpritzbeutel(Szene):
    """Er will einen Riesenkeks verzieren, aber aus dem Spritzbeutel kommt nichts. Drücken,
    Pressen mit ganzer Kraft, Schütteln: ein einziger Tupfer. Er hält sich die Tülle vors Auge,
    der Beutel bläht sich still auf, und dann sitzt ihm eine Zuckergusstorte auf dem Kopf.
    Zwei Augen blinzeln heraus, die Kirsche landet obendrauf, er tastet sich hinaus."""
    name, titel, reihenfolge = 'back_spritzbeutel', 'Spritzbeutel', 802

    def vorbereiten(self):
        r = self.richtung
        self.x = self.aussen(-r)
        self.x0 = self.vom_rand(0.13)
        self.kx = self.x0 + r * 105 * self.s
        self.pose_fest = {'sack': False}
        self.druck = 0.0
        self.leer = 0.0
        self.beutel_w = -35.0        # Neigung des Beutels (Grad), 0: Tülle nach unten
        self.haube = 0.0            # 0..1 Gussberg auf dem Kopf
        self.strahl = False
        self.kirsche = None         # Höhe über der Haube (Einheiten) beim Herabfallen
        self.tupfer = None          # [x, y, vy]
        self.liegt = None           # Beutel am Boden [x, y, winkel]

    def ablauf(self):
        r, s = self.richtung, self.s
        halten = lambda p, sz: Pose(bein_v=p.bein_v, bein_h=p.bein_h, hub=p.hub, arm_v=-62,  # noqa: E731
                                    arm_v_x=14, auge_zu=p.auge_zu)

        def druecken(staerke):
            def f(sz, u):
                sz.druck = 0.5 * staerke + 0.5 * staerke * abs(math.sin(u * 9))
                sz.neigung = 6 * staerke
                sz.stauchen = 1 - 0.03 * staerke * abs(zittern(u, 30))
                sz.pose = Pose(arm_v=-62 + zittern(u, 45, 4 * staerke), arm_v_x=14, auge_zu=staerke > 1,
                               mund_offen=staerke > 1, sorge=0.6, wipp=zittern(u, 40, 2 * staerke))
            return Jeweils(1.0 if staerke < 2 else 1.1, f)

        def schuetteln(sz, u):
            sz.pose = Pose(arm_v=-90 + 45 * math.sin(u * 22), arm_v_x=14, mund_offen=True, sorge=0.8)
            sz.beutel_w = -20 + 25 * math.sin(u * 22)

        def drehen(sz, u):
            f = min(1.0, u / 0.4)
            sz.beutel_w = -20 + (140 + 20) * f
            sz.pose = Pose(arm_v=-62 - 50 * f, arm_v_x=14, blick_x=0.3, blick_y=0.3)

        def spaehen(sz, u):
            sz.druck = min(1.6, u / 1.0 * 1.6)
            sz.pose = Pose(arm_v=-112, arm_v_x=14, blick_x=0.3, blick_y=0.3, auge_zu=0.3 < u < 0.42)

        def platsch(sz, u):
            sz.haube = min(1.0, u / 0.15)
            sz.leer = min(1.0, u / 0.2)
            sz.druck = 0.0
            sz.pose = Pose(arm_v=-140, arm_h=-120, arm_v_x=14, muetze=False, bein_v=-20, bein_h=20)

        def kirsche(sz, u):
            sz.kirsche = max(0.0, 220 * (1 - u / 0.45) ** 2) if u < 0.45 else 0.0

        return [
            Gehe(bis=self.x0, haltung=halten),
            druecken(1),
            Stehe(0.4, lambda sz, u: Pose(arm_v=-62, arm_v_x=14, blick_y=0.6, sorge=0.4,
                                         auge_zu=blinzeln(sz.t))),
            druecken(2.2),
            Setze(tupfer=lambda sz: list(sz.tuelle()) + [0.0], neigung=0.0, stauchen=1.0, druck=0.0),
            Stehe(0.5, lambda sz, u: Pose(arm_v=-62, arm_v_x=14, kopf_vorn=True, sorge=1.0)),
            Jeweils(0.7, schuetteln),
            Jeweils(0.4, drehen),
            Jeweils(1.0, spaehen),
            Setze(strahl=True),
            Jeweils(0.12, lambda sz, u: None),
            Setze(strahl=False, pose_fest={'sack': False, 'muetze': False}),
            Jeweils(0.2, platsch),
            Gleite(lambda sz: sz.x - r * 22 * s, 0.35, lambda sz, u: Pose(arm_v=-140, arm_h=-120, arm_v_x=14,
                                                                          bein_v=-20, bein_h=20)),
            Setze(liegt=lambda sz: sz.beutel_los()),
            Stehe(0.5, Pose(kopf_vorn=True, arm_v=-20, arm_h=-20, schreck=0.0)),
            Jeweils(0.5, kirsche),
            publikum(1.1),
            Setze(richtung=lambda sz: sz.naechster_rand()),
            Gehe(tempo=0.7, haltung=lambda p, sz: Pose(bein_v=p.bein_v * 0.6, bein_h=p.bein_h * 0.6, hub=p.hub,
                                                       arm_v=-95 + 10 * math.sin(sz.t * 6), arm_h=-80,
                                                       arm_v_x=14, kopf_vorn=True)),
        ]

    def schreck_ablauf(self):
        self.strahl, self.druck = False, 0.0
        if self.liegt is None:
            self.liegt = self.beutel_los()
        return [Setze(neigung=0.0, stauchen=1.0), Erschrecke(), Renne(zum='rand')]

    def beutel_los(self):
        x, _ = hand(self)
        return [x, self.boden - 8 * self.s, 90.0 * self.richtung]

    def tuelle(self):
        x, y = hand(self)
        w = math.radians(self.beutel_w * self.richtung)
        return x - math.sin(w) * 34 * self.s, y + math.cos(w) * 34 * self.s

    def weiter(self, dt):
        if self.tupfer:
            t = self.tupfer
            t[2] += 1400 * self.s * dt
            t[1] = min(self.boden - 3 * self.s, t[1] + t[2] * dt)

    def zeichne_hinten(self, p):
        s = self.s
        p.save()
        p.translate(self.kx, self.boden)
        p.scale(s, s)
        zeichne_riesenkeks(p, 46, 0.3)
        p.restore()
        if self.tupfer:
            p.save()
            p.translate(self.tupfer[0], self.tupfer[1])
            p.scale(s, s)
            zeichne_gussklecks(p, 4.5)
            p.restore()

    def zeichne_vorn(self, p):
        s, r = self.s, self.richtung
        if self.liegt is not None:
            x, y, w = self.liegt
            p.save()
            p.translate(x, y)
            p.rotate(w)
            p.scale(s, s)
            zeichne_spritzbeutel(p, 0, 1.0)
            p.restore()
        elif self.zeige_figur:
            x, y = hand(self)
            p.save()
            p.translate(x, y)
            p.rotate(self.beutel_w * r)
            p.scale(s * 1.25, s * 1.25)
            p.translate(0, 28)
            zeichne_spritzbeutel(p, self.druck, self.leer)
            p.restore()
        if self.strahl:
            hx, hy = kopf(self)
            tx, ty = self.tuelle()
            p.setPen(stift(GUSS, 12 * s))
            p.drawLine(QPointF(tx, ty), QPointF(hx, hy))
            p.setPen(stift(GUSS, 0))
        if self.haube > 0 and self.zeige_figur:
            p.save()
            p.setTransform(figur_trafo(self), True)
            p.translate(6, -142 + self.pose.hub)
            g = 1.15 * self.haube
            zeichne_sahnehaube(p, g, kirsche=False)
            if self.haube >= 1:
                pose = Pose(auge_zu=self.pose.auge_zu or blinzeln(self.t, 0.4), kopf_vorn=True)
                augen(p, (-9, 9), -38, 5, 6, pose, (0.0, 0.1), 0.6)
                if self.kirsche is not None:
                    ky = -100 - self.kirsche
                    p.setBrush(radial(1, ky - 3, 9, ROT.lighter(150), ROT_DUNKEL))
                    kreis(p, 3, ky, 8)
            p.restore()

    def grenzen_extra(self):
        s = self.s
        k = QRectF(self.kx - 50 * s, self.boden - 100 * s, 100 * s, 100 * s)
        x, y = hand(self) if self.liegt is None else self.liegt[:2]
        k = k.united(QRectF(x - 70 * s, y - 90 * s, 140 * s, 180 * s))
        if self.haube > 0:
            hx, hy = kopf(self)
            k = k.united(QRectF(hx - 60 * s, hy - 120 * s - (self.kirsche or 0) * s, 120 * s,
                                180 * s + (self.kirsche or 0) * s))
        if self.tupfer:
            k = k.united(QRectF(self.tupfer[0] - 10 * s, self.tupfer[1] - 10 * s, 20 * s, 20 * s))
        return k
