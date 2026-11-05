import math
import random
from dataclasses import replace

from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import QColor, QPainterPath

from zeichnen.figur import Pose
from zeichnen.grundlagen import KEIN_PINSEL, KEIN_STIFT, blinzeln, glatt, stift
from zeichnen.labor import KREIDE, tafel_flaeche, zeichne_schwamm
from zeichnen.labor_c import STAUB, schiefer_pfad, zeichne_tafel_c
from zeichnen.professor import Professor

from .basis import Erschrecke, Gehe, Jeweils, Renne, Setze, Stehe, Tu, Wandel, WarteBis
from .professor import HaareHoch, Publikumsblick, TafelSzene, Umkippen

GROSS = 1.8          # Schwamm in der Hand, größer als auf der Ablage
STAND = 118          # Abstand Professor - Tafelmitte
REIHEN = (-180, -160, -140, -120, -104)


class Schwamm(TafelSzene):
    """Er wischt einen Kreidekringel weg, beim nächsten Wischen ist die Tafelfläche selbst
    weg, ein Loch bis zum Hintergrund. Er wischt ungläubig weiter, bis nur der Rahmen steht,
    stützt sich ab und fällt durch den leeren Rahmen. Wieder auf den Beinen tupft er sich
    die Stirn - die halbe Mütze ist weg. Publikumsblick. In Panik schrubbt er nach und
    radiert sich bis auf die Beine aus, die allein davonlaufen."""
    name, titel, reihenfolge = 'schwamm', 'Radikaler Schwamm', 79

    def vorbereiten(self):
        self.tafel_vorbereiten(0.12)
        self.loecher = []
        self.flaeche = True
        self.kringel = 1.0          # Deckkraft des Kreidekringels
        self.rahmen_vorn = False
        self.radiert = []           # weggewischte Stellen an ihm selbst (Figur-Einheiten)
        self.rest = None            # alles oberhalb dieser Figur-Höhe ist weg
        self.fall = None            # [x, y, vy] des fallenden Schwamms
        # beide Teilchenlisten gleich anmelden: streue() prüft mit ==, leere Listen gälten sonst als schon da
        self.teilchen = [self.wolke, self.splitter]

    # -- Hilfen

    def fig(self, fx, fy):
        q = self.trafo().map(QPointF(fx, fy))
        return q.x(), q.y()

    def in_fig(self, x, y):
        q = self.trafo().inverted()[0].map(QPointF(x, y))
        return q.x(), q.y()

    def weiter(self, dt):
        super().weiter(dt)
        if self.fall:
            self.fall[2] += 1500 * self.s * dt
            self.fall[1] = min(self.boden - 4 * self.s, self.fall[1] + self.fall[2] * dt)

    # -- Zeichnen

    def zeichne_tafel(self, p):
        p.save()
        p.translate(self.tafel_x, self.boden)
        p.scale(self.s, self.s)
        zeichne_tafel_c(p, wisch=self.wisch, kreide=self.kreide_da, schwamm=False, loecher=self.loecher,
                        flaeche=self.flaeche)
        if self.flaeche and self.kringel > 0:
            p.save()
            p.setClipPath(schiefer_pfad(tafel_flaeche(), self.loecher))
            pfad = QPainterPath()
            pfad.moveTo(-52, -150)
            for k in range(1, 41):
                u = k / 40
                pfad.lineTo(-52 + 100 * u, -150 + 18 * math.sin(u * math.pi * 3) - 10 * math.sin(u * 17))
            farbe = QColor(KREIDE)
            farbe.setAlphaF(farbe.alphaF() * self.kringel)
            p.setPen(stift(farbe, 4.5))
            p.setBrush(KEIN_PINSEL)
            p.drawPath(pfad)
            p.setPen(KEIN_STIFT)
            p.restore()
        p.restore()

    def zeichne_requisiten(self, p):
        if not self.rahmen_vorn:
            self.zeichne_tafel(p)

    def zeichne_figur(self, p, zwischen=None):
        p.save()
        p.setTransform(self.trafo(), True)
        p.setPen(KEIN_STIFT)
        if self.radiert or self.rest is not None:
            weg = QPainterPath()
            weg.setFillRule(Qt.FillRule.WindingFill)
            for x, y, r in self.radiert:
                weg.addEllipse(QPointF(x, y), r, r * 0.8)
            if self.rest is not None:
                weg.addRect(QRectF(-300, -500, 600, 500 + self.rest))
            bleibt = QPainterPath()
            bleibt.addRect(QRectF(-300, -500, 600, 600))
            p.setClipPath(bleibt.subtracted(weg))
        Professor.zeichne(p, self)
        p.restore()

    def zeichne_davor(self, p):
        if self.rahmen_vorn:
            self.zeichne_tafel(p)
        ort = self.schwamm_ort or (self.fall and self.fall[:2])
        if ort:
            p.save()
            p.translate(*ort)
            p.scale(self.s * GROSS, self.s * GROSS)
            zeichne_schwamm(p, 0, 5)
            p.restore()

    def requisiten_kasten(self):
        k = super().requisiten_kasten()
        ort = self.schwamm_ort or (self.fall and self.fall[:2])
        if ort:
            r = 26 * GROSS * self.s
            k = k.united(QRectF(ort[0] - r, ort[1] - r, 2 * r, 2 * r))
        return k

    # -- Ablauf

    def ablauf(self):
        r0, s = self.richtung, self.s
        self.x = self.aussen(-r0)
        px = self.tafel_x + STAND * s

        def wischen(sz, lx, ly, heftig=0.0, u=0.0):
            wx, wy = sz.welt(lx, ly)
            sz.schwamm_ort = (wx, wy)
            ziel = min(px, wx + 82 * s)
            sz.x += max(-1.0, min(1.0, (ziel - sz.x) / (s * 4))) * sz.tempo * (1.2 + heftig) / 60
            sz.pose = Pose(arm_v=sz.arm_zu(wx, wy) + heftig * 6 * math.sin(u * 40),
                           arm_h=-40 - 40 * heftig, blick_y=-0.3, mund_offen=heftig > 0.5,
                           sorge=0.9 * heftig, schreck=0.3 * heftig, hub=heftig * 2 * math.sin(u * 30),
                           auge_zu=blinzeln(sz.t) and heftig == 0)

        def kringel_weg(sz, u):
            f = min(1.0, u / 0.6)
            lx = -48 + 96 * f
            ly = -150 + 14 * math.sin(u * 26)
            sz.kringel = 1 - f
            if random.random() < 0.4:
                sz.wisch.append((lx, ly, random.uniform(7, 11)))
                sz.streue(*sz.welt(lx, ly), 1, STAUB, tempo=30, dauer=0.5, r=(3, 6))
            wischen(sz, lx, ly)

        def nicken(sz, u):
            n = 4 * max(0.0, math.sin(u * 25))
            wx, wy = sz.welt(48, -150)
            sz.schwamm_ort = (wx, wy)
            return Pose(arm_v=sz.arm_zu(wx, wy), hub=n, auge_zu=True, blick_y=-0.3)

        def loch_wischen(sz, lx, ly, r):
            if not sz.loecher or math.hypot(lx - sz.loecher[-1][0], ly - sz.loecher[-1][1]) > r * 0.35:
                sz.loecher.append((lx, ly, r))
                if random.random() < 0.5:
                    sz.streue(*sz.welt(lx, ly), 2, STAUB, tempo=50, dauer=0.5, r=(2, 5), schwer=True)

        def zweiter_strich(sz, u):
            f = glatt(min(1.0, u / 0.5))
            lx = 52 - 80 * f
            ly = -165 + 6 * math.sin(f * 9)
            loch_wischen(sz, lx, ly, 17)
            wischen(sz, lx, ly)

        def starren(sz, u):
            sz.schwamm_ort = sz.welt(-28, -165)
            return Pose(arm_v=sz.arm_zu(*sz.schwamm_ort), schreck=1.0, sorge=0.6, blick_y=-0.3)

        def tasten(sz, u):
            # mit dem Schwamm durchs Loch stochern, ungläubig
            lx = -6 + 16 * math.sin(u * 13)
            ly = -166 + 5 * math.cos(u * 17)
            wischen(sz, lx, ly)
            return Pose(arm_v=sz.arm_zu(*sz.schwamm_ort), sorge=1.0, blick_y=-0.2, auge_zu=0.3 < u < 0.4)

        def bahn(v):
            n = len(REIHEN)
            k = min(n - 1, int(v * n))
            w = v * n - k
            x = 64 - 128 * w if k % 2 == 0 else -64 + 128 * w
            return x, REIHEN[k]

        def wie_wild(sz, u):
            v = min(1.0, u / 1.0)
            lx, ly = bahn(v)
            loch_wischen(sz, lx, ly, 23)
            wischen(sz, lx, ly, heftig=1.0, u=u)

        def leer(sz):
            sz.flaeche, sz.loecher = False, []
            k = sz.requisiten_kasten()
            for _ in range(10):
                sz.streue(random.uniform(k.left(), k.right()), random.uniform(k.top(), k.top() + 60 * s), 1,
                          STAUB, tempo=40, dauer=0.6, r=(4, 8))

        def zurueck_zu(ziel):
            def f(sz, u):
                sz.x += (ziel - sz.x) * min(1.0, 12 / 60)
                b = 16 * math.sin(u * 18)
                sz.schwamm_ort = sz.hand()
                sz.pose = Pose(bein_v=b, bein_h=-b, arm_v=-70, arm_h=20, sorge=0.6, auge_zu=blinzeln(sz.t))
            return f

        def abstuetzen(sz, u):
            # will sich an die Tafel lehnen, stützt ins Leere
            sz.schwamm_ort = None
            f = glatt(min(1.0, u / 0.3))
            return Pose(arm_v=-90 + 10 * f, arm_h=-60, kopf_vorn=False, blick_y=0.2, wipp=-3,
                        auge_zu=blinzeln(sz.t))

        def aufstehen(sz, u):
            f = glatt(min(1.0, u / 0.4))
            sz.neigung = 88 * (1 - f)
            return Pose(kopf_vorn=f > 0.9, arm_v=-8, arm_h=8, auge_zu=f < 0.9)

        def stirn(sz, u):
            # erleichtert die Stirn abtupfen, quer über Mütze und Haar
            f = min(1.0, u / 0.5)
            ziel = sz.fig(44 - 34 * f, -215 - 6 * math.sin(u * 30))
            pose = Pose(arm_v=sz.arm_zu(*ziel), arm_v_x=14, auge_zu=True, mund_offen=f > 0.3, blick_y=-0.4)
            sz.pose = pose
            hx, hy = sz.hand()
            sz.schwamm_ort = (hx, hy - 8 * s)
            if f > 0.05:
                fx, fy = sz.in_fig(hx, hy)
                sz.radiert.append((fx + 6, fy - 24, 21))
            return pose

        def panik(sz, u):
            f = min(1.0, u / 0.55)
            ziel = sz.fig(14 + 40 * math.sin(u * 32), -215 + 150 * f)
            pose = Pose(arm_v=sz.arm_zu(*ziel), arm_h=-100, schreck=1.0, sorge=1.0,
                        bein_v=-8 * math.sin(u * 30), bein_h=8 * math.sin(u * 30))
            sz.pose = pose
            hx, hy = sz.hand()
            sz.schwamm_ort = (hx, hy)
            fx, fy = sz.in_fig(hx, hy)
            sz.radiert.append((fx, fy - 10, 34))
            sz.rest = min(-120, -215 + 150 * f - 25)
            return pose

        def loslassen(sz):
            x, y = sz.schwamm_ort
            sz.schwamm_ort = None
            sz.fall = [x, y, -100 * s]
            sz.rest = -64

        def beine(sz, u):
            w = 10 * math.sin(u * 26) if u > 0.35 else 0.0
            return Pose(bein_v=w, bein_h=-w)

        def ende(sz):
            sz.weg(STAUB)

        return [
            Setze(schwamm_ort=lambda sz: sz.hand()),
            *self.herein(px),
            Setze(richtung=-1),
            Jeweils(0.6, kringel_weg),
            Stehe(0.25, nicken),
            Jeweils(0.5, zweiter_strich),
            Stehe(0.4, starren),
            Stehe(0.6, tasten),
            Stehe(0.35, lambda sz, u: Pose(kopf_vorn=True, sorge=0.8, blick_y=0.1, auge_zu=0.15 < u < 0.3,
                                           arm_v=-50)),
            Tu(lambda sz: setattr(sz, 'schwamm_ort', sz.welt(48, -180))),
            Jeweils(1.0, wie_wild),
            Tu(leer),
            Stehe(0.35, lambda sz, u: Pose(arm_v=-70, sorge=0.5, blick_y=-0.2, auge_zu=0.1 < u < 0.25)),
            Jeweils(0.35, zurueck_zu(px)),
            Stehe(0.3, abstuetzen),
            Setze(rahmen_vorn=True),
            Umkippen(0.45, nach=1),
            Stehe(0.4, lambda sz, u: Pose(arm_v=-8, arm_h=8, auge_zu=True)),
            Stehe(0.4, aufstehen),
            Setze(neigung=0.0, rahmen_vorn=False),
            Stehe(0.5, stirn),
            Setze(schwamm_ort=None),
            Publikumsblick(1.0, husten=False),
            HaareHoch(0.6),
            Stehe(0.55, panik),
            Tu(loslassen),
            Stehe(0.6, beine),
            Renne(zum='rand', tempo=3.0),
            Tu(ende),
            WarteBis(lambda sz: not sz.wolke and not sz.splitter),
        ]

    def herein(self, px):
        return [Gehe(bis=px, tempo=1.8, haltung=lambda pose, sz: _mit_schwamm(pose, sz))]

    def schreck_ablauf(self):
        """Hüpfer mit Schwamm, dann versinkt alles."""
        self.kreide_ort = self.schwamm_ort = None
        self.fall = None
        self.nebenbei.clear()
        tief = 330 * self.s
        if not self.figur_sichtbar():
            self.zeige_figur = False
            return [Wandel(0.45, senke=tief)] + self._ende()
        return [HaareHoch(1.0), Erschrecke(0.3, 46), Setze(neigung=0.0),
                Wandel(0.45, y=lambda sz: sz.y + tief, senke=tief),
                Tu(lambda sz: setattr(sz, 'zeige_figur', False))] + self._ende()


def _mit_schwamm(pose, sz):
    pose = replace(pose, arm_v=-70)
    sz.pose = pose
    sz.schwamm_ort = sz.hand()
    return pose
