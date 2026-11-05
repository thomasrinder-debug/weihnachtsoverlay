import math

from zeichnen.figur import Pose
from zeichnen.grundlagen import blinzeln
from zeichnen.labor import tafel_flaeche, zeichne_schwamm
from zeichnen.labor_c import STAUB, schiefer_pfad, zeichne_anschriebe, zeichne_tafel_c

from .basis import Erschrecke, Jeweils, Schaue, Setze, Springe, Stehe, Tu, Wandel
from .professor import HaareHoch, Schreibe, TafelSzene, Zurueck

REIHEN = (-178, -157, -134, -112)


class Schwamm(TafelSzene):
    """Statt der Rechnung wischt der Schwamm die ganze Tafelfläche weg, bis nur der Rahmen steht.
    Satt stößt er eine Kreidestaubwolke aus."""
    name, titel, reihenfolge = 'schwamm', 'Hungriger Schwamm', 79

    def vorbereiten(self):
        self.tafel_vorbereiten(0.2)
        self.loecher = []
        self.flaeche = True
        self.schwamm_da = True
        self.schwamm_gr = 1.0
        self.kauen = 0.0
        self.rahmen_vorn = False
        # beide Teilchenlisten gleich anmelden: streue() prüft mit ==, leere Listen gälten sonst als schon da
        self.teilchen = [self.wolke, self.splitter]
        self.a = self.schreib('9-3=6', -64, -180, 28)

    # -- Zeichnen

    def zeichne_tafel(self, p):
        p.save()
        p.translate(self.tafel_x, self.boden)
        p.scale(self.s, self.s)
        zeichne_tafel_c(p, wisch=self.wisch, kreide=self.kreide_da, schwamm=self.schwamm_da,
                        loecher=self.loecher, flaeche=self.flaeche)
        if self.flaeche:
            zeichne_anschriebe(p, self.anschriebe, clip=schiefer_pfad(tafel_flaeche(), self.loecher))
        p.restore()

    def zeichne_requisiten(self, p):
        if not self.rahmen_vorn:
            self.zeichne_tafel(p)

    def zeichne_davor(self, p):
        if self.rahmen_vorn:
            self.zeichne_tafel(p)
        ort, self.schwamm_ort = self.schwamm_ort, None
        super().zeichne_davor(p)
        self.schwamm_ort = ort
        if self.schwamm_ort and self.zeige_figur:
            g = self.schwamm_gr
            kau = 1 + 0.12 * math.sin(self.t * 22) * self.kauen
            p.save()
            p.translate(*self.schwamm_ort)
            p.scale(self.s * g * (2 - kau), self.s * g * kau)
            zeichne_schwamm(p, 0, 5)
            p.restore()

    # -- Ablauf

    def ablauf(self):
        self.x = self.aussen(-self.richtung)
        s = self.s

        def schwamm_weg(sz, v):
            """Ort des Schwamms auf der Fläche (Tafel-Einheiten), v 0..1 über alle Reihen."""
            n = len(REIHEN)
            k = min(n - 1, int(v * n))
            w = v * n - k
            x = 66 - 132 * w if k % 2 == 0 else -66 + 132 * w
            y = REIHEN[k] + 3 * math.sin(v * 80)
            return x, y

        def fressen(dauer, v0, v1, ziehen=False):
            def f(sz, u, dt):
                v = v0 + (v1 - v0) * min(1.0, u / dauer)
                lx, ly = schwamm_weg(sz, v)
                if not sz.loecher or math.hypot(lx - sz.loecher[-1][0], ly - sz.loecher[-1][1]) > 5:
                    sz.loecher.append((lx, ly, 15))
                    if len(sz.loecher) % 3 == 0:
                        sz.streue(*sz.welt(lx, ly), 2, STAUB, tempo=40, dauer=0.5, r=(2, 4), schwer=True)
                wx, wy = sz.welt(lx, ly)
                sz.schwamm_ort = (wx, wy + 5 * s)
                sz.schwamm_gr = 1.0 + 1.0 * v
                sz.kauen = 1.0
                ziel = wx - sz.richtung * 62 * s
                sz.x += max(-1.0, min(1.0, (ziel - sz.x) / (s * 4))) * sz.tempo * 0.7 * dt
                sz.pose = Pose(arm_v=sz.arm_zu(wx, wy) + (6 * math.sin(u * 30) if ziehen else 0),
                               schreck=0.5 if ziehen else 0.0, sorge=0.9 if ziehen else 0.2, blick_y=-0.3,
                               mund_offen=ziehen, bein_v=-12 if ziehen else 0, bein_h=12 if ziehen else 0)
            return JeweilsDt(dauer, f)

        def aufnehmen(sz, u):
            f = tafel_flaeche()
            wx, wy = sz.welt(f.right() - 26, f.bottom() + 5)
            sz.schwamm_da = False
            sz.schwamm_ort = (wx, wy)
            sz.pose = Pose(arm_v=sz.arm_zu(wx, wy - 4 * s), blick_y=0.5)

        def aufstossen(sz, u):
            g = 2.0
            if u < 0.35:
                sz.schwamm_gr = g + 0.35 * math.sin(u / 0.35 * math.pi / 2)
            else:
                sz.schwamm_gr = g + 0.35 * max(0.0, 1 - (u - 0.35) / 0.2)
            if u >= 0.35 and not getattr(sz, 'gerulpst', False):
                sz.gerulpst = True
                x, y = sz.schwamm_ort
                sz.streue(x, y - 6 * s, 50, STAUB, tempo=210, dauer=1.4, r=(10, 22), richtung=-math.pi / 2,
                          streuung=1.2)
            sz.kauen = 0.0
            sz.pose = Pose(arm_v=-80, schreck=0.6 if u > 0.35 else 0.0, sorge=0.6, blick_y=-0.1)

        def zurueckhalten(sz, u):
            sz.pose = Pose(arm_v=-80 + 3 * math.sin(u * 20), sorge=0.7, blick_y=-0.1, auge_zu=blinzeln(sz.t))

        return [
            *self.an_tafel(),
            Stehe(0.3),
            Setze(kreide_da=False),
            Schreibe(self.a, 2.4),
            Setze(kreide_ort=None),
            Stehe(0.6, lambda sz, u: Pose(blick_y=-0.2, sorge=0.3, auge_zu=blinzeln(sz.t))),
            Jeweils(0.5, aufnehmen),
            fressen(0.6, 0.0, 0.08),
            Stehe(0.8, lambda sz, u: Pose(arm_v=sz.arm_zu(*sz.schwamm_ort), schreck=0.8, sorge=0.8, blick_y=-0.3)),
            Schaue(0.8),
            Setze(richtung=-1),
            fressen(3.4, 0.08, 1.0, ziehen=True),
            Setze(flaeche=False, loecher=[], kauen=0.0),
            Jeweils(0.5, zurueckhalten),
            Jeweils(1.0, aufstossen),
            Stehe(1.0, lambda sz, u: Pose(kopf_vorn=True, sorge=0.8, arm_v=-80, auge_zu=0.5 < u < 0.62)),
            Stehe(0.8, lambda sz, u: Pose(arm_v=-80, blick_y=-0.1, sorge=0.5, auge_zu=blinzeln(sz.t))),
            Setze(schwamm_ort=None, schwamm_da=True),
            Zurueck(30, 0.4),
            Stehe(0.9, lambda sz, u: Pose(kopf_vorn=True, arm_v=-20, arm_h=20, hub=-3 * abs(math.sin(u * 6)),
                                          sorge=0.4, auge_zu=True)),
            *self.tafel_abgang(),
        ]

    def schreck_ablauf(self):
        """Er springt durch den leeren Rahmen, dann versinkt alles."""
        self.kreide_ort = self.schwamm_ort = None
        self.nebenbei.clear()
        tief = 330 * self.s
        if not self.figur_sichtbar():
            self.zeige_figur = False
            return [Wandel(0.45, senke=tief)] + self._ende()
        return [HaareHoch(1.0), Erschrecke(0.25, 40), Setze(rahmen_vorn=True),
                Springe(nach=lambda sz: (sz.tafel_x, sz.boden), dauer=0.45, hoehe=50),
                Wandel(0.45, y=lambda sz: sz.y + tief, senke=tief),
                Tu(lambda sz: setattr(sz, 'zeige_figur', False))] + self._ende()


class JeweilsDt(Jeweils):
    """Wie Jeweils, aber funktion(szene, u, dt)."""

    def weiter(self, sz, u, dt):
        self.funktion(sz, u, dt)
