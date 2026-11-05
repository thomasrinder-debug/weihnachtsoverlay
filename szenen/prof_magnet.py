import math
import random

from PyQt6.QtCore import QPointF, QRectF
from PyQt6.QtGui import QColor, QPainterPath

from zeichnen.figur import Pose
from zeichnen.figuren import WichtelSteif
from zeichnen.grundlagen import KEIN_PINSEL, KEIN_STIFT, WEISS, blinzeln, glatt, stift
from zeichnen.labor_b import hebel_knauf, zeichne_schwanenhals, zeichne_hufeisen, zeichne_schaltkasten

from .basis import Erschrecke, Falle, Gehe, Jeweils, Mit, Nebenbei, Renne, Setze, Stehe, Tu, Wandel, Warte, WarteBis
from .professor import FUNKEN, HaareHoch, ProfSzene, denk_pose, triumph_pose, ziehen

HOEHE = 248          # Ständer
ARM = 70             # Ausleger
POL = 170            # Höhe der Polenden über dem Boden
SPITZE = 132         # Mützenspitze des Wichtels (gerade) über seinen Füßen
FELD = [QColor(170, 225, 255), WEISS]


class Magnet(ProfSzene):
    """Ein Riesenmagnet am Ständer zieht die ewig abgeknickte Mützenspitze des Wichtels
    kerzengerade. Magnet aus, die Spitze knickt; der Wichtel bettelt, der Professor legt
    den Hebel kräftig um, und der ganze Wichtel fliegt hoch und klebt am Magneten.
    Der Professor zieht Ständer, Pult und glücklichen Wichtel hinaus."""
    name, titel, reihenfolge = 'magnet', 'Magnetkraft', 66
    mitnehmen = ()

    def vorbereiten(self):
        r, s = self.richtung, self.s
        self.px = self.vom_rand(0.13)
        self.box_x = self.px + r * 62 * s
        self.post_x = self.px + r * 112 * s
        self.hebel = 0.0
        self.an = 0.0
        self.klebt = False
        self.zittern = 0.0
        self.w_idle, self.w_t0, self.w_da = None, 0.0, False
        self.w = self.dazu('w', WichtelSteif, groesse=0.65, knick=1.0)
        self.w.x = self.aussen(-r) - r * 60 * s
        self.w.tempo = self.tempo * 0.8

    def magnet_x(self):
        return self.post_x + self._r0 * ARM * self.s

    def leerlauf(self, fn):
        def f(sz):
            sz.w_idle, sz.w_t0 = fn, sz.t
        return Tu(f)

    def ablauf(self):
        self._r0 = r = self.richtung
        s = self.s
        self.x = self.aussen(-r)
        unter = self.post_x + r * (ARM + 3) * s

        def bettel(d, u):
            return Pose(kopf_vorn=True, arm_v=-150 + 12 * math.sin(u * 14), arm_h=-150 - 12 * math.sin(u * 14),
                        arm_v_x=12, sorge=1.0, mund_offen=(u * 4) % 2 < 1, blick_y=-0.4)

        def traurig(d, u):
            return Pose(kopf_vorn=True, sorge=0.7, blick_y=-0.6, auge_zu=blinzeln(d.t, 1.0))

        def froh(d, u):
            return Pose(kopf_vorn=True, mund_offen=True, arm_v=-140, arm_h=-140, hub=-5 * abs(math.sin(u * 9)),
                        auge_zu=0.5 < u < 0.65)

        def haengt(d, u):
            pendel = 22 * math.sin(u * 9)
            return Pose(kopf_vorn=True, auge_zu=blinzeln(d.t), mund_offen=(u * 4) % 2 < 1.4,
                        arm_v=-150 + pendel, arm_h=-150 - pendel, bein_v=-25 + pendel, bein_h=25 - pendel)

        return [
            Nebenbei(Warte(0.9), Mit('w', Gehe(bis=unter)), Mit('w', Setze(richtung=-r)),
                     self.leerlauf(traurig), Setze(w_da=True)),
            Gehe(bis=self.px),
            Setze(richtung=r),
            Stehe(0.6, lambda sz, u: Pose(auge_zu=blinzeln(sz.t))),
            Stehe(1.0, denk_pose),
            WarteBis(lambda sz: sz.w_da),
            Stehe(0.5, lambda sz, u: Pose(kopf_vorn=True, auge_zu=blinzeln(sz.t), arm_v=-110, arm_v_x=14)),
            Jeweils(0.45, self.hebel_zu(1.0)),
            Tu(lambda sz: sz.anschalten()),
            Mit('w', Wandel(0.35, knick=0.0)),
            Tu(lambda sz: sz.funkeln(8)),
            self.leerlauf(froh),
            Stehe(1.6, triumph_pose),
            Jeweils(0.35, self.hebel_zu(0.0)),
            Setze(an=0.0),
            self.leerlauf(None),
            Mit('w', Wandel(0.06, knick=1.0)),
            Mit('w', Stehe(0.7, lambda d, u: Pose(kopf_vorn=True, sorge=1.0, blick_y=-0.9))),
            self.leerlauf(bettel),
            Warte(1.2),
            Stehe(0.8, lambda sz, u: Pose(kopf_vorn=True, auge_zu=u > 0.3, arm_v=-20, arm_h=20)),
            Jeweils(0.25, self.hebel_zu(1.0, kraft=True)),
            Tu(lambda sz: sz.anschalten()),
            self.leerlauf(None),
            Setze(an=1.7),
            Mit('w', Wandel(0.12, knick=0.0)),
            Mit('w', Setze(pose=Pose(kopf_vorn=True, schreck=0.8, arm_v=-170, arm_h=-170))),
            Mit('w', Wandel(0.3, y=lambda d: d.sz.boden - (POL - SPITZE - 3) * d.sz.s)),
            Tu(lambda sz: sz.ankleben()),
            self.leerlauf(haengt),
            Stehe(0.6, lambda sz, u: Pose(kopf_vorn=True, schreck=0.4, sorge=0.5)),
            Stehe(1.2, lambda sz, u: Pose(kopf_vorn=True, arm_v=-60, arm_h=-50, arm_v_x=14,
                                          hub=-3 * abs(math.sin(u * 4)), sorge=0.4)),
            Setze(mitnehmen=('box_x', 'post_x')),
            Gehe(bis=self.aussen(-r) - r * 330 * s, haltung=ziehen),
        ]

    # -- Handlung

    def hebel_welt(self):
        hx, hy = hebel_knauf(self.hebel)
        return self.box_x + self._r0 * hx * self.s, self.boden + hy * self.s

    def hebel_zu(self, ziel, kraft=False):
        start = {}

        def f(sz, u):
            if 'h' not in start:
                start['h'] = sz.hebel
            dauer = 0.25 if kraft else (0.45 if ziel > 0.5 else 0.35)
            k = glatt(u / dauer)
            sz.hebel = start['h'] + (ziel - start['h']) * k
            sz.pose = Pose(arm_v=sz.arm_zu(*sz.hebel_welt()), arm_h=-20 if kraft else 10, blick_y=0.3,
                           bein_v=-16 if kraft else 0, bein_h=12 if kraft else 0, sorge=0.3 if kraft else 0,
                           auge_zu=kraft and u > 0.1)
            if kraft:
                sz.hopp = 6 * sz.s * math.sin(math.pi * min(1.0, u / dauer))
        return f

    def anschalten(self):
        self.an = 1.0
        self.zittern = 0.4

    def funkeln(self, n):
        x, y = self.magnet_x(), self.boden - POL * self.s
        self.streue(x, y, n, FELD, tempo=110, dauer=0.5, r=(3, 5), art='stern')

    def ankleben(self):
        self.klebt = True
        self.zittern = 0.6
        self.hopp = 0.0
        x, y = self.magnet_x(), self.boden - POL * self.s
        self.streue(x, y, 12, FUNKEN, tempo=180, dauer=0.5, r=(3, 6), art='stern')

    def weiter(self, dt):
        super().weiter(dt)
        self.zittern = max(0.0, self.zittern - dt)
        if self.w_idle and not self.erschreckt:
            self.w.pose = self.w_idle(self.w, self.t - self.w_t0)
        if self.klebt and not self.erschreckt:
            self.w.x = self.magnet_x() - self._r0 * 1 * self.s + self.wackel()
        if self.an and random.random() < 0.08 * self.an and not self.weg_ist:
            self.funkeln(1)

    def wackel(self):
        return math.sin(self.t * 60) * 2.5 * self.s * self.zittern

    # -- Zeichnen

    def zeichne_requisiten(self, p):
        r, s = self._r0, self.s
        # Kabel vom Pult zum Ständer
        p.setPen(stift(QColor('#3A3A3A'), 2.2 * s))
        p.setBrush(KEIN_PINSEL)
        k = QPainterPath()
        k.moveTo(self.box_x + r * 4 * s, self.boden - 60 * s)
        k.cubicTo(self.box_x + r * 20 * s, self.boden - 2 * s, self.post_x - r * 30 * s, self.boden - 2 * s,
                  self.post_x - r * 4 * s, self.boden - 40 * s)
        k.lineTo(self.post_x - r * 4 * s, self.boden - (HOEHE - 4) * s)
        p.drawPath(k)
        p.setPen(KEIN_STIFT)
        p.save()
        p.translate(self.post_x, self.boden)
        p.scale(r * s, s)
        zeichne_schwanenhals(p, HOEHE, ARM)
        p.restore()
        p.save()
        p.translate(self.magnet_x() + self.wackel(), self.boden - (HOEHE - 16) * s)
        p.scale(r * s, s)
        zeichne_hufeisen(p, min(1.0, self.an), self.t)
        p.restore()
        p.save()
        p.translate(self.box_x, self.boden)
        p.scale(r * s, s)
        zeichne_schaltkasten(p, self.hebel, self.an, self.t)
        p.restore()

    def zeichne_davor(self, p):
        if self.an > 1.2 and not self.weg_ist:
            s = self.s
            x, y = self.magnet_x(), self.boden - POL * s
            p.setPen(stift(QColor(200, 240, 255, 200), 1.6 * s))
            for k in range(4):
                a = self.t * 8 + k * 1.6
                p.drawLine(QPointF(x + math.cos(a) * 30 * s, y + math.sin(a) * 10 * s),
                           QPointF(x + math.cos(a) * 38 * s, y + math.sin(a) * 14 * s))
            p.setPen(KEIN_STIFT)

    def requisiten_kasten(self):
        s, r = self.s, self._r0
        xs = [self.box_x - r * 34 * s, self.box_x + r * 22 * s, self.post_x - r * 34 * s,
              self.magnet_x() + r * 50 * s]
        top = self.boden - (HOEHE + 12) * s
        return QRectF(min(xs), top, max(xs) - min(xs), self.boden - top + 4 * s)

    # -- Schreck

    def schreck_ablauf(self):
        w = self.w
        klebte = self.klebt
        self.klebt = False
        self.an = 0.0
        self.hopp = 0.0
        self._vorher()
        neu = []
        if w.zeige_figur:
            if klebte:
                neu.append(Nebenbei(Mit('w', Setze(striche=True, knick=1.0)),
                                    Mit('w', Falle(lambda d: d.y >= d.sz.boden)),
                                    Mit('w', Setze(y=self.boden)),
                                    Mit('w', Erschrecke(0.25, 30)), Mit('w', Renne(zum='rand', tempo=4.0))))
            else:
                neu.append(Nebenbei(Mit('w', Erschrecke(0.35, 40)), Mit('w', Renne(zum='rand', tempo=4.0))))
        if not self.figur_sichtbar():
            self.zeige_figur = False
            return neu + self._ende()
        return neu + [HaareHoch(1.0), Erschrecke(0.35, 50), Renne(zum='rand', tempo=4.0)] + self._ende()
