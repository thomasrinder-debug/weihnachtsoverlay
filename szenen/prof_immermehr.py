import math

from PyQt6.QtCore import QRectF
from PyQt6.QtGui import QColor

from zeichnen.figur import Pose
from zeichnen.grundlagen import blinzeln
from zeichnen.labor import BREITE, KREIDE, TAFEL_B, kreide_striche, striche_spitze, tafel_flaeche, zeichne_striche
from zeichnen.labor_c import zeichne_tafel_c

from .basis import Erschrecke, Jeweils, Schaue, Setze, Springe, Stehe, Tu, Wandel
from .professor import FUNKEN, HaareHoch, TafelSzene, Zurueck, triumph_pose

HOEHE = 28
OBEN = -170
PAARE = 10
ENGE = 0.45           # stärker als auf die Hälfte lassen sich die Zeichen nicht zusammendrücken
GLANZ = [QColor(255, 255, 255, 230), QColor(220, 240, 255, 220)]


class Zeichen:
    def __init__(self, ch):
        self.ch = ch
        self.anteil = 0.0
        self.striche = kreide_striche(ch, 0, 0, HOEHE)
        self.breite = BREITE.get(ch, 0.72) * HOEHE


class Immermehr(TafelSzene):
    """Hinter eine 1 setzt er ein Plus, sofort erscheint eine weitere 1. Begeistert setzt er Plus
    um Plus, bis die gedrängten Einsen den Rahmen auseinanderdrücken."""
    name, titel, reihenfolge = 'immermehr', 'Immer mehr', 81

    def vorbereiten(self):
        self.tafel_vorbereiten(0.2)
        self.zeichen = []
        self.knall = 0.0          # 0..1 Seitenleisten fliegen weg
        self.tafel_vorn = False
        self.druck = 0.0

    # -- Lage der Zeichen

    def lage(self):
        """(Tafelbreite, Stauchung, x-Anfang) aus der Summe der Zeichenbreiten."""
        w = sum(z.breite for z in self.zeichen) or 1
        platz = TAFEL_B - 14
        k = max(ENGE, min(1.0, platz / w))
        b = max(TAFEL_B, w * k + 14)
        return b, k, -b / 2 + 7

    def spitze(self):
        """Weltpunkt der Kreide: am Ende des letzten Zeichens."""
        b, k, x = self.lage()
        for z in self.zeichen[:-1]:
            x += z.breite * k
        if not self.zeichen:
            return self.welt(x, OBEN)
        z = self.zeichen[-1]
        lx, ly = striche_spitze(z.striche, z.anteil)
        return self.welt(x + lx * k, OBEN + ly)

    def seiten(self, b):
        aus = (b - TAFEL_B) / 2
        if aus <= 0 and self.knall <= 0:
            return None
        w = self.knall
        fall = 260 * w * w
        z = self.druck * 1.2 * math.sin(self.t * 70)
        return ((-aus * 0.1 - 70 * w + z, fall, -aus * 0.7 - 110 * w), (aus * 0.1 + 70 * w - z, fall, aus * 0.7 + 110 * w))

    # -- Zeichnen

    def zeichne_tafel(self, p):
        b, k, x = self.lage()
        p.save()
        p.translate(self.tafel_x, self.boden)
        p.scale(self.s, self.s)
        zeichne_tafel_c(p, b=b, wisch=self.wisch, kreide=self.kreide_da, seiten=self.seiten(b), leiste=TAFEL_B - 4)
        for z in self.zeichen:
            if z.anteil > 0:
                p.save()
                p.translate(x, OBEN)
                p.scale(k, 1)
                zeichne_striche(p, z.striche, z.anteil, KREIDE, 2.4)
                p.restore()
            x += z.breite * k
        p.restore()

    def zeichne_requisiten(self, p):
        if not self.tafel_vorn:
            self.zeichne_tafel(p)

    def zeichne_davor(self, p):
        if self.tafel_vorn:
            self.zeichne_tafel(p)
        super().zeichne_davor(p)

    def requisiten_kasten(self):
        b, _, _ = self.lage()
        f = tafel_flaeche(b=b)
        x0, y0 = self.welt(f.left() - 230 * self.knall - 42, f.top() - 16)
        x1, _ = self.welt(f.right() + 230 * self.knall + 42, 0)
        return QRectF(x0, y0, x1 - x0, self.boden - y0 + 2 * self.s)

    # -- Ablauf

    def ablauf(self):
        self.x = self.aussen(-self.richtung)
        s = self.s

        def neues(ch):
            return Tu(lambda sz: sz.zeichen.append(Zeichen(ch)))

        def schreiben(dauer, eifer=0.0):
            def f(sz, u, dt):
                z = sz.zeichen[-1]
                z.anteil = min(1.0, u / dauer)
                wx, wy = sz.spitze()
                sz.kreide_ort = (wx, wy)
                ziel = wx - sz.richtung * 58 * s
                schritt = max(-1.0, min(1.0, (ziel - sz.x) / (s * 4))) * sz.tempo * 0.6 * dt
                sz.x += schritt
                sz.phase += abs(schritt) / (s * 38)
                bein = 14 * math.sin(sz.phase) if abs(schritt) > 0.05 * s else 0
                sz.pose = Pose(arm_v=sz.arm_zu(wx, wy) + 4 * math.sin(u * 30), bein_v=-bein, bein_h=bein,
                               blick_y=-0.3, mund_offen=eifer > 0.5, auge_zu=blinzeln(sz.t), hub=-2 * eifer *
                               abs(math.sin(u * 12)))
            return JeweilsDt(dauer, f)

        def plopp(sz, u):
            z = sz.zeichen[-1]
            z.anteil = min(1.0, u / 0.12)
            if not getattr(z, 'funkelt', False):
                z.funkelt = True
                b, k, x = sz.lage()
                for y in sz.zeichen[:-1]:
                    x += y.breite * k
                sz.streue(*sz.welt(x + z.breite * k / 2, OBEN + HOEHE / 2), 5, GLANZ, tempo=70, dauer=0.5,
                          r=(2, 4), art='stern')

        schritte = [*self.an_tafel(), Stehe(0.3), Setze(kreide_da=False),
                    neues('1'), schreiben(0.6), Stehe(0.3, lambda sz, u: Pose(arm_v=-50, auge_zu=blinzeln(sz.t))),
                    neues('+'), schreiben(0.6), neues('1'), Jeweils(0.25, plopp),
                    Stehe(0.5, lambda sz, u: Pose(arm_v=-50, schreck=0.5, blick_y=-0.3)),
                    Schaue(1.0),
                    Setze(richtung=-1),
                    neues('+'), schreiben(0.5), neues('1'), Jeweils(0.25, plopp),
                    Stehe(0.6, lambda sz, u: Pose(kopf_vorn=True, mund_offen=True, arm_v=-60, arm_h=-40,
                                                  hub=-4 * abs(math.sin(u * 10)))),
                    Setze(richtung=-1)]
        dauer = 0.42
        for i in range(PAARE - 2):
            eifer = min(1.0, i / 3)
            schritte += [neues('+'), schreiben(dauer, eifer), neues('1'), Jeweils(0.18, plopp)]
            dauer = max(0.22, dauer * 0.85)

        def knallen(sz, u):
            v = min(1.0, u / 0.7)
            sz.knall = v
            if not getattr(sz, 'geknallt', False):
                sz.geknallt = True
                for seite in (-1, 1):
                    b, _, _ = sz.lage()
                    sz.streue(*sz.welt(seite * b / 2, -144), 8, FUNKEN, tempo=160, dauer=0.5, r=(3, 6),
                              art='stern')
            sz.pose = Pose(schreck=1.0, sorge=0.8, arm_v=-115, arm_h=-100, arm_v_x=20)

        schritte += [
            Setze(kreide_ort=None),
            Zurueck(45, 0.4),
            Setze(druck=1.0),
            Stehe(0.8, lambda sz, u: Pose(arm_v=-60, arm_h=-40, sorge=0.3 + 0.5 * u, blick_y=-0.2,
                                          auge_zu=blinzeln(sz.t))),
            Setze(druck=0.0),
            Jeweils(0.7, knallen),
            Setze(knall=1.0),
            Zurueck(15, 0.3),
            Stehe(1.0, lambda sz, u: Pose(blick_y=-0.2, sorge=0.8, auge_zu=0.5 < u < 0.6)),
            Schaue(0.8),
            Stehe(1.3, triumph_pose),
            *self.tafel_abgang(),
        ]
        return schritte

    def schreck_ablauf(self):
        """Er springt hinter die Tafel, dann versinkt alles."""
        self.kreide_ort = None
        self.nebenbei.clear()
        tief = 330 * self.s
        if not self.figur_sichtbar():
            self.zeige_figur = False
            return [Wandel(0.45, senke=tief)] + self._ende()
        return [HaareHoch(1.0), Erschrecke(0.25, 40), Setze(tafel_vorn=True),
                Springe(nach=lambda sz: (sz.tafel_x, sz.boden), dauer=0.45, hoehe=45),
                Wandel(0.45, y=lambda sz: sz.y + tief, senke=tief),
                Tu(lambda sz: setattr(sz, 'zeige_figur', False))] + self._ende()


class JeweilsDt(Jeweils):
    """Wie Jeweils, aber funktion(szene, u, dt)."""

    def weiter(self, sz, u, dt):
        self.funktion(sz, u, dt)
