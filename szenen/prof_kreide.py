import math
import random

from zeichnen.figur import Pose
from zeichnen.grundlagen import blinzeln
from zeichnen.labor import striche_spitze, tafel_flaeche
from zeichnen.labor_c import (STAUB, haelfte_pfad, riss_punkte, zeichne_anschriebe, zeichne_dicke_kreide, zeichne_riss,
                              zeichne_stummel, zeichne_stummelhaufen, zeichne_tafel_c)

from .basis import Ducke, Erschrecke, Jeweils, Setze, Stehe, Tu, Wandel
from .professor import HaareHoch, Schreibe, TafelSzene, Zurueck, triumph_pose

HAUFEN_X = -4          # Stummelhaufen unter der Schreibstelle (Tafel-Einheiten)
FUSS = 57


class Kreide(TafelSzene):
    """Die Kreide bricht immer wieder, der Stummelhaufen wächst. Er zieht eine armdicke Kreide
    aus dem Kittel; beim ersten Strich bricht die Tafel in zwei Hälften, die Kreide bleibt heil."""
    name, titel, reihenfolge = 'kreide', 'Unzerbrechliche Kreide', 75

    def vorbereiten(self):
        self.tafel_vorbereiten(0.2)
        self.a = self.schreib('3+4=', -64, -178, 28)
        self.b = self.schreib('7', 18, -184, 40)
        self.b.dicke = 7.5
        self.haufen = []        # (x, y, winkel) liegende Stummel
        self.fallend = []       # [x, y, vy, winkel, dreh]
        self.riss = 0.0
        self.spalt = 0.0
        self.riss_pts = riss_punkte(tafel_flaeche(), saat=4)

    # -- Kreide bricht

    def brechen(self, zwei=False):
        if not self.kreide_ort:
            return
        wx, wy = self.kreide_ort
        lx, ly = (wx - self.tafel_x) / self.s, (wy - self.boden) / self.s
        for k in range(3 if zwei else 2):
            self.fallend.append([lx + k * 4, ly, -60.0, random.uniform(0, 180), random.uniform(-500, 500)])
        self.streue(wx, wy, 6, STAUB, tempo=50, dauer=0.5, r=(2, 4))

    def weiter(self, dt):
        super().weiter(dt)
        for f in list(self.fallend):
            f[2] += 900 * dt
            f[1] += f[2] * dt
            f[0] += (HAUFEN_X - f[0]) * min(1.0, dt * 3)
            f[3] += f[4] * dt
            if f[1] >= -3.2:
                nah = sum(1 for x, _, _ in self.haufen if abs(x - f[0]) < 12)
                self.haufen.append((f[0] + random.uniform(-10, 10), -3.2 - 3.6 * nah, random.uniform(-25, 25)))
                self.fallend.remove(f)

    # -- Zeichnen

    def zeichne_tafel(self, p):
        p.save()
        p.translate(self.tafel_x, self.boden)
        p.scale(self.s, self.s)
        if self.spalt <= 0:
            zeichne_tafel_c(p, wisch=self.wisch, kreide=self.kreide_da)
            zeichne_anschriebe(p, self.anschriebe)
            zeichne_riss(p, self.riss_pts, self.riss)
        else:
            for seite in (-1, 1):
                p.save()
                p.translate(seite * FUSS, 0)
                p.rotate(seite * 16 * self.spalt)
                p.translate(-seite * FUSS, 0)
                p.setClipPath(haelfte_pfad(self.riss_pts, seite))
                zeichne_tafel_c(p, wisch=self.wisch, kreide=False, schwamm=seite > 0)
                zeichne_anschriebe(p, self.anschriebe)
                p.restore()
        zeichne_stummelhaufen(p, 0, self.haufen)
        for x, y, _, w, _ in self.fallend:
            zeichne_stummel(p, x, y, w)
        p.restore()

    def requisiten_kasten(self):
        k = super().requisiten_kasten()
        w = 70 * self.s * math.sin(math.radians(16)) * self.spalt * 2.2
        return k.adjusted(-w, 0, w, 0)

    # -- Ablauf

    def ablauf(self):
        self.x = self.aussen(-self.richtung)

        def knack(zwei=False):
            return [Tu(lambda sz: sz.brechen(zwei)),
                    Stehe(0.25, lambda sz, u: Pose(arm_v=-70, schreck=0.8, sorge=0.6)),
                    Setze(kreide_ort=None),
                    Stehe(0.6, lambda sz, u: Pose(arm_v=-110, arm_v_x=14, blick_y=-0.4, sorge=0.9,
                                                  auge_zu=blinzeln(sz.t))),
                    Stehe(0.4, lambda sz, u: Pose(arm_v=15, arm_h=10, blick_y=0.3))]

        def grosse_kreide(p, hx, hy):
            zeichne_dicke_kreide(p, hx + 4, hy + 6, -70)

        def herausziehen(sz, u):
            f = min(1.0, u / 0.9)
            sz.pose = Pose(arm_v=20 - 160 * f * f, arm_v_x=12, blick_y=-0.5 * f, mund_offen=f > 0.8,
                           auge_zu=blinzeln(sz.t))
            sz.halt = grosse_kreide

        def ansetzen(sz, u):
            sz.halt = grosse_kreide
            sz.kreide_ort = None

        def strich(sz, u):
            sz.halt = None
            f = min(1.0, u / 0.5)
            sz.b.anteil = 0.32 * f
            lx, ly = striche_spitze(sz.b.striche, sz.b.anteil)
            wx, wy = sz.welt(lx, ly)
            sz.dicke_ort = (wx, wy)
            sz.pose = Pose(arm_v=sz.arm_zu(wx, wy), blick_y=-0.2, sorge=0.0, mund_offen=True)

        def reissen(sz, u):
            sz.riss = min(1.0, u / 0.2)
            sz.pose = Pose(arm_v=sz.arm_zu(*sz.dicke_ort), schreck=1.0, sorge=0.8)
            if u > 0.2 and sz.spalt == 0:
                sz.streue(*sz.welt(0, -150), 16, STAUB, tempo=110, dauer=0.7, r=(3, 7))
            if u > 0.2:
                g = min(1.0, (u - 0.2) / 0.45)
                sz.spalt = g * g - 0.12 * math.sin(max(0.0, u - 0.65) * 20) * math.exp(-max(0.0, u - 0.65) * 6) * (u > 0.65)

        return [
            *self.an_tafel(),
            Stehe(0.4),
            Setze(kreide_da=False),
            Schreibe(self.a, 0.9, bis=0.3),
            *knack(),
            Schreibe(self.a, 0.8, bis=0.6),
            *knack(True),
            Schreibe(self.a, 0.7, bis=0.85),
            *knack(True),
            Setze(kreide_ort=None),
            Stehe(0.6, lambda sz, u: Pose(blick_y=0.6, sorge=0.7, auge_zu=blinzeln(sz.t))),
            Stehe(0.8, lambda sz, u: Pose(kopf_vorn=True, sorge=0.3, arm_v=15, arm_h=10, blick_x=0.3)),
            Jeweils(0.9, herausziehen),
            Stehe(1.0, lambda sz, u: Pose(kopf_vorn=True, arm_v=-150 + 6 * math.sin(u * 6), arm_v_x=14,
                                          mund_offen=True, auge_zu=0.5 < u < 0.62)),
            Tu(lambda sz: setattr(sz, 'dicke_ort', None)),
            Jeweils(0.5, strich),
            Jeweils(1.1, reissen),
            Setze(spalt=1.0),
            Zurueck(65, 0.5),
            Stehe(0.9, lambda sz, u: Pose(schreck=0.8, sorge=1.0, arm_v=-60, blick_y=0.2)),
            Tu(lambda sz: setattr(sz, 'halt', grosse_kreide)),
            Stehe(0.8, lambda sz, u: Pose(arm_v=-150, arm_v_x=12, blick_y=-0.6, auge_zu=blinzeln(sz.t))),
            Setze(halt=None),
            Zurueck(15, 0.3),
            Setze(halt=lambda sz: grosse_kreide_triumph),
            Stehe(1.5, lambda sz, u: triumph_pose(sz, u)),
            Setze(halt=lambda sz: grosse_kreide),
            *self.tafel_abgang(),
        ]

    def zeichne_davor(self, p):
        super().zeichne_davor(p)
        if getattr(self, 'dicke_ort', None) and self.zeige_figur and self.halt is None:
            p.save()
            p.translate(*self.dicke_ort)
            p.scale(self.s, self.s)
            zeichne_dicke_kreide(p, 12, 24, 65)
            p.restore()

    def schreck_ablauf(self):
        """Er duckt sich, alles versinkt."""
        self.kreide_ort = self.dicke_ort = None
        self.nebenbei.clear()
        self.halt = self.halt_h = None
        self.fallend.clear()
        tief = 330 * self.s
        vorher = [HaareHoch(1.0), Erschrecke(0.3, 46), Ducke(0.2)] if self.figur_sichtbar() else []
        return vorher + [Wandel(0.45, y=lambda sz: sz.y + tief, senke=tief),
                         Tu(lambda sz: setattr(sz, 'zeige_figur', False))] + self._ende()


def grosse_kreide_triumph(p, hx, hy):
    zeichne_dicke_kreide(p, hx, hy - 10, -90)
