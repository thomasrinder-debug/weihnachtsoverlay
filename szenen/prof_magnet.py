import math
import random

from PyQt6.QtCore import QPointF, QRectF
from PyQt6.QtGui import QColor, QPainterPath

from zeichnen.figur import Pose
from zeichnen.figuren import WichtelSteif
from zeichnen.grundlagen import KEIN_PINSEL, KEIN_STIFT, WEISS, blinzeln, glatt, stift
from zeichnen.labor_b import hebel_knauf, zeichne_hufeisen, zeichne_schaltkasten, zeichne_schwanenhals

from .basis import Gehe, Jeweils, Mit, Nebenbei, Setze, Stehe, Tu
from .professor import FUNKEN, STAUB, ProfSzene, Publikumsblick, triumph_pose

G = 1.5              # Magnet vergrößert
POL = 186            # Polenden über dem Boden
HOEHE = POL + 62 * G + 16   # Ständer
ARM = 84             # Ausleger
FELD = [QColor(170, 225, 255), WEISS]
KOPF_PROF = (4, -205)
RUECKEN_W = (-24, -80)      # Rücken des Wichtels in seinen Einheiten


def anheften(fig, lokal, ziel):
    """Verschiebt eine Figur (x, hopp), bis ihr Punkt lokal am Weltpunkt ziel liegt."""
    q = fig.trafo().map(QPointF(*lokal))
    fig.x += ziel[0] - q.x()
    fig.hopp -= ziel[1] - q.y()


class Solange(Jeweils):
    """Ruft funktion(szene, u) in jedem Bild auf, bis bis(szene) wahr ist (höchstens 5 s)."""

    def __init__(self, funktion, bis):
        super().__init__(5.0, funktion)
        self.bis = bis

    def fertig(self, sz, u):
        return u > 5.0 or self.bis(sz)


class Magnet(ProfSzene):
    """Ein Riesenmagnet am Laborständer. Hebel ein Drittel: die Mütze des Wichtels steht
    stramm und zieht ihn lang. Zwei Drittel: Zehenspitzen, dann schwebt er strampelnd.
    Erwartungspause, Hebel ganz: der Wichtel schnellt hoch und klebt waagerecht am Magneten.
    Triumph-Pose, da zieht der Magnet an der Brille: der Professor rutscht, kämpft und fliegt
    kopfvoran hinterher. Beide kleben, der Wichtel winkt begeistert, Publikumsblick, und der
    Ständer rollt mit beiden auf seinen Rädchen aus dem Bild, das Pult am Kabel hinterher."""
    name, titel, reihenfolge = 'magnet', 'Magnetkraft', 66
    mitnehmen = ()

    def vorbereiten(self):
        self._r0 = r = self.richtung
        s = self.s
        self.post_x = self.vom_rand(0.07)
        self.box_x = self.post_x + r * (ARM + 100) * s
        self.hebel = 0.0
        self.an = 0.0
        self.w_klebt = False
        self.p_klebt = False
        self.zug = 0.0               # Feldlinien zur Brille
        self.zittern = 0.0
        self.roll_v = 0.0
        self.box_dreh = 0.0
        self.w = self.dazu('w', WichtelSteif, groesse=0.65, knick=1.0)
        self.w.x = self.magnet_x()
        self.w.richtung = r

    def magnet_x(self):
        return self.post_x + self._r0 * ARM * self.s

    def pol_y(self):
        return self.boden - POL * self.s

    def hebel_welt(self):
        hx, hy = hebel_knauf(self.hebel)
        return self.box_x - self._r0 * hx * self.s, self.boden + hy * self.s

    def wackel(self):
        return math.sin(self.t * 60) * 3 * self.s * self.zittern

    # -- Ablauf

    def ablauf(self):
        self._r0 = r = self.richtung
        s = self.s
        self.x = self.aussen(-r)
        stand = self.box_x + r * 50 * s
        merk = {}

        def hebel(ziel, dauer, kraft=False):
            def f(sz, u):
                if ('h', ziel) not in merk:
                    merk[('h', ziel)] = sz.hebel
                h0 = merk[('h', ziel)]
                k = glatt(u / dauer)
                sz.hebel = h0 + (ziel - h0) * k
                sz.pose = Pose(arm_v=sz.arm_zu(*sz.hebel_welt()), arm_h=-60 if kraft else 10, blick_y=0.3,
                               bein_v=-20 if kraft else 0, bein_h=14 if kraft else 0, auge_zu=kraft,
                               mund_offen=kraft)
                if kraft:
                    sz.hopp = 14 * s * math.sin(math.pi * min(1.0, u / dauer))
            return f

        def ausholen(sz, u):
            sz.hopp = 0.0
            return Pose(kopf_vorn=True, arm_v=-160, arm_h=-150, arm_v_x=14, bein_v=-10, bein_h=10,
                           mund_offen=True, blick_y=-0.2, wipp=3)

        def lang(sz, u):
            """Stufe 1: Mütze stramm, zieht den Wichtel lang, er hält sie fest."""
            d = sz.w
            k = glatt(u / 0.25)
            d.knick = 1 - k
            d.stauchen = 1 + 0.18 * k + 0.02 * math.sin(u * 30)
            d.pose = Pose(kopf_vorn=True, arm_v=-170 * k, arm_h=-165 * k, arm_v_x=6, sorge=1.0,
                          mund_offen=True, blick_y=-0.8)
            sz.pose = Pose(arm_v=sz.arm_zu(*sz.hebel_welt()), blick_x=-0.5, auge_zu=blinzeln(sz.t))

        def schweben(sz, u):
            """Stufe 2: Zehenspitzen, dann schweben, strampeln."""
            d = sz.w
            d.knick = 0.0
            d.stauchen = 1.2 + 0.02 * math.sin(u * 30)
            hoch = 8 * min(1.0, u / 0.2) + 48 * glatt((u - 0.35) / 0.4)
            d.hopp = (hoch + 3 * math.sin(u * 9)) * s
            b = 32 * math.sin(u * 16) * glatt((u - 0.35) / 0.2)
            d.pose = Pose(kopf_vorn=True, arm_v=-170, arm_h=-165, arm_v_x=6, sorge=1.0, mund_offen=True,
                          bein_v=b, bein_h=-b, blick_y=-0.2)
            sz.pose = Pose(arm_v=sz.arm_zu(*sz.hebel_welt()), kopf_vorn=u > 0.6, mund_offen=u > 0.6,
                           auge_zu=blinzeln(sz.t))

        def hochschnellen(sz, u):
            d = sz.w
            if 'w0' not in merk:
                merk['w0'] = (d.x, d.hopp)
            x0, h0 = merk['w0']
            k = min(1.0, u / 0.16) ** 2
            d.stauchen = 1.2 + (1 - 1.2) * k
            d.neigung = 90 * k
            d.pose = Pose(kopf_vorn=True, schreck=1.0, arm_v=-170, arm_h=-170, bein_v=-10, bein_h=10)
            d.x, d.hopp = x0, h0
            q = d.trafo().map(QPointF(*RUECKEN_W))
            zx, zy = sz.magnet_x(), sz.pol_y() + 2 * s
            d.x = x0 + (zx - q.x()) * k
            d.hopp = h0 - (zy - q.y()) * k

        def zerren(sz, u):
            """Die Brille zieht ihn zum Magneten: er stemmt sich dagegen und rutscht."""
            k = glatt(u / 0.15)
            sz.brille = 1.0
            sz.zug = 1.0
            sz.neigung = 26 * k + 4 * math.sin(u * 30)
            sz.x -= r * 30 * s * (1 / 60) * (1 + 2 * u) * k
            b = 20 * math.sin(u * 28)
            sz.pose = Pose(kopf_vorn=True, schreck=1.0, arm_v=60 + 40 * math.sin(u * 20),
                           arm_h=70 - 40 * math.sin(u * 20), bein_v=24 + b, bein_h=40 - b, sorge=1.0)
            if random.random() < 0.5:
                sz.streue(sz.x, sz.boden - 3 * s, 1, STAUB, tempo=70, dauer=0.5, r=(4, 8),
                          richtung=-math.pi / 2 + r * 0.8, streuung=0.5)

        def fliegen(sz, u):
            if 'p0' not in merk:
                merk['p0'] = (sz.x, sz.hopp, sz.neigung)
            x0, h0, n0 = merk['p0']
            k = min(1.0, u / 0.2) ** 1.5
            sz.neigung = n0 + (90 - n0) * k
            sz.pose = Pose(kopf_vorn=True, schreck=1.0, arm_v=40, arm_h=50, bein_v=10, bein_h=-10)
            sz.x, sz.hopp = x0, h0
            q = sz.trafo().map(QPointF(*KOPF_PROF))
            zx, zy = sz.kopf_ziel()
            sz.x = x0 + (zx - q.x()) * k
            sz.hopp = h0 - (zy - q.y()) * k

        def winken(d, u):
            a = 35 * math.sin(u * 16)
            return Pose(kopf_vorn=True, mund_offen=True, arm_v=-95 + a, arm_h=-80 - a, arm_v_x=6,
                        bein_v=-20 + 15 * math.sin(u * 7), bein_h=20 - 15 * math.sin(u * 7),
                        auge_zu=0.4 < u % 1.2 < 0.5)

        def kleben(sz, u):
            sz.pose = Pose(kopf_vorn=True, arm_v=-90 + 4 * math.sin(u * 5), arm_h=-80, bein_v=2, bein_h=-2,
                           auge_zu=0.3 < u < 0.45 or 0.85 < u < 1.0, sorge=0.2)

        def rollen(sz, u):
            if u < 0.35:
                sz.post_off = -r * 8 * s * math.sin(u * 30) * (1 - u / 0.35)
            else:
                sz.roll_v += 1500 * s * (1 / 60)
                sz.post_x -= r * sz.roll_v * (1 / 60)
                sz.post_off = 0.0
            ziel = sz.post_x + r * (ARM + 100) * s
            if (sz.box_x - ziel) * r > 0 and u > 0.5:
                sz.box_x += (ziel - sz.box_x) * 0.25
                sz.box_dreh = min(1.0, sz.box_dreh + 0.08)
            if u > 0.35 and random.random() < 0.6:
                sz.streue(sz.post_x, sz.boden - 3 * s, 1, FUNKEN, tempo=90, dauer=0.35, r=(2, 4), art='stern',
                          richtung=-math.pi / 2 + r * 0.9, streuung=0.4)
            sz.pose = Pose(kopf_vorn=True, arm_v=-90, arm_h=-80, schreck=0.6 if u > 0.35 else 0.0,
                           mund_offen=u > 0.4)

        def alles_weg(sz):
            k = sz.requisiten_kasten()
            return (not k.intersects(sz.geo) and not sz.figur_sichtbar() and not sz.w.figur_sichtbar())

        return [
            Mit('w', Stehe(0.1, lambda d, u: Pose(auge_zu=blinzeln(d.t)))),
            Nebenbei(Mit('w', Stehe(1.2, lambda d, u: Pose(kopf_vorn=u > 0.5, auge_zu=blinzeln(d.t),
                                                            arm_v=-150 if u > 0.6 else 0, arm_v_x=8)))),
            Gehe(bis=stand, tempo=1.8),
            Setze(richtung=-r),
            Jeweils(0.3, hebel(0.33, 0.3)),
            Setze(an=0.45),
            Tu(lambda sz: sz.funkeln(6)),
            Jeweils(0.75, lang),
            Jeweils(0.25, hebel(0.66, 0.25)),
            Setze(an=0.9),
            Tu(lambda sz: sz.funkeln(8)),
            Jeweils(1.0, schweben),
            Nebenbei(Mit('w', Jeweils(0.9, lambda d, u: setattr(d, 'hopp', d.hopp + 0.15 * s * math.sin(u * 9))))),
            Stehe(0.35, ausholen),
            Jeweils(0.14, hebel(1.0, 0.14, kraft=True)),
            Setze(an=1.8, hopp=0.0),
            Jeweils(0.16, hochschnellen),
            Tu(lambda sz: sz.klonk_w()),
            Nebenbei(Mit('w', Stehe(6.0, winken))),
            Stehe(0.7, lambda sz, u: triumph_pose(sz, u)),
            Tu(lambda sz: sz.zing()),
            Jeweils(0.6, zerren),
            Jeweils(0.2, fliegen),
            Tu(lambda sz: sz.klonk_p()),
            Jeweils(0.35, kleben),
            Publikumsblick(1.1),
            Solange(rollen, alles_weg),
            Tu(lambda sz: sz.nebenbei.clear()),
            Setze(zeige_figur=False),
        ]

    post_off = 0.0

    def kopf_ziel(self):
        return (self.magnet_x() + self._r0 * (30 * G + 36) * self.s,
                self.boden - (POL + 44) * self.s)

    # -- Handlung

    def funkeln(self, n):
        self.streue(self.magnet_x(), self.pol_y(), n, FELD, tempo=110, dauer=0.5, r=(3, 5), art='stern')

    def klonk_w(self):
        self.w_klebt = True
        self.zittern = 0.5
        self.streue(self.magnet_x(), self.pol_y(), 14, FUNKEN, tempo=220, dauer=0.5, r=(3, 6), art='stern')

    def zing(self):
        x, y = self.kopf_oben()
        self.streue(x, y + 30 * self.s, 6, FELD, tempo=140, dauer=0.4, r=(3, 5), art='stern')
        self.haare = 0.6

    def klonk_p(self):
        self.p_klebt = True
        self.zug = 0.0
        self.zittern = 0.7
        self.haare = 1.0
        x, y = self.kopf_ziel()
        self.streue(x, y, 16, FUNKEN, tempo=240, dauer=0.5, r=(3, 6), art='stern')

    def weiter(self, dt):
        super().weiter(dt)
        self.zittern = max(0.0, self.zittern - dt)
        if self.erschreckt:
            return
        if self.w_klebt:
            d = self.w
            d.neigung, d.stauchen, d.knick = 90.0, 1.0, 0.0
            anheften(d, RUECKEN_W, (self.magnet_x() + self.wackel(), self.pol_y() + 2 * self.s))
        if self.p_klebt:
            self.neigung = 90.0
            zx, zy = self.kopf_ziel()
            anheften(self, KOPF_PROF, (zx + self.wackel(), zy))
        if self.an and random.random() < 0.06 * self.an and not self.weg_ist:
            self.funkeln(1)

    # -- Zeichnen

    def zeichne_requisiten(self, p):
        r, s = self._r0, self.s
        px = self.post_x + self.post_off
        # Kabel vom Pult zum Ständer
        p.setPen(stift(QColor('#3A3A3A'), 2.2 * s))
        p.setBrush(KEIN_PINSEL)
        k = QPainterPath()
        k.moveTo(self.box_x - r * 4 * s, self.boden - 60 * s)
        k.cubicTo(self.box_x - r * 20 * s, self.boden - 2 * s, px + r * 30 * s, self.boden - 2 * s,
                  px + r * 4 * s, self.boden - 40 * s)
        k.lineTo(px + r * 4 * s, self.boden - (HOEHE * 0.5) * s)
        p.drawPath(k)
        p.setPen(KEIN_STIFT)
        p.save()
        p.translate(px, self.boden)
        p.scale(r * s, s)
        zeichne_schwanenhals(p, HOEHE, ARM)
        p.restore()
        if not self.w_klebt:
            self.zeichne_magnet(p)
        p.save()
        p.translate(self.box_x, self.boden)
        p.rotate(-r * 25 * self.box_dreh)
        p.scale(-r * s, s)
        zeichne_schaltkasten(p, self.hebel, self.an, self.t)
        p.restore()

    def zeichne_magnet(self, p):
        r, s = self._r0, self.s
        p.save()
        p.translate(self.post_x + self.post_off + r * ARM * s + self.wackel(), self.boden - (HOEHE - 16) * s)
        p.scale(r * s, s)
        zeichne_hufeisen(p, min(1.0, self.an), self.t, G)
        p.restore()

    def zeichne_davor(self, p):
        if self.weg_ist:
            return
        s = self.s
        if self.w_klebt:
            self.zeichne_magnet(p)
        x, y = self.magnet_x(), self.pol_y()
        if self.an > 1.2:
            p.setPen(stift(QColor(200, 240, 255, 200), 1.8 * s))
            for k in range(5):
                a = self.t * 8 + k * 1.3
                p.drawLine(QPointF(x + math.cos(a) * 52 * s, y - 40 * s + math.sin(a) * 30 * s),
                           QPointF(x + math.cos(a) * 64 * s, y - 40 * s + math.sin(a) * 38 * s))
        if self.zug:
            # Feldlinien vom Magneten zur Brille
            hx, hy = self.kopf_oben()
            hy += 40 * s
            mx, my = x + self._r0 * 45 * G * s * 0.66, y - 40 * s
            for k in range(3):
                u = (self.t * 3 + k / 3) % 1
                c = QColor(170, 225, 255, int(230 * (1 - u)))
                p.setPen(stift(c, 2.0 * s))
                p.setBrush(KEIN_PINSEL)
                path = QPainterPath()
                path.moveTo(mx, my)
                path.quadTo((mx + hx) / 2, my - (30 + 30 * k) * s, hx, hy)
                p.drawPath(path)
        p.setPen(KEIN_STIFT)

    def requisiten_kasten(self):
        s, r = self.s, self._r0
        px = self.post_x + self.post_off
        xs = [self.box_x - r * 40 * s, self.box_x + r * 40 * s, px - r * 34 * s,
              self.magnet_x() + r * 80 * s, self.magnet_x() - r * 70 * s]
        top = self.boden - (HOEHE + 20) * s
        return QRectF(min(xs), top, max(xs) - min(xs), self.boden - top + 4 * s)

    # -- Schreck

    def schreck_ablauf(self):
        self.w_klebt = self.p_klebt = False
        self.zug = 0.0
        self.an = 0.0
        self.neigung, self.hopp = 0.0, 0.0
        self.w.neigung, self.w.hopp, self.w.stauchen = 0.0, 0.0, 1.0
        return self.schreck_versinken()
