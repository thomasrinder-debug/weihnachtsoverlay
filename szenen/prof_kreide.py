import math
import random

from PyQt6.QtCore import QPointF, QRectF
from PyQt6.QtGui import QColor

from zeichnen.figur import Pose
from zeichnen.grundlagen import KEIN_STIFT, blinzeln, glatt, stern, stift
from zeichnen.labor import KREIDE, tafel_flaeche
from zeichnen.labor_c import STAUB, haelfte_pfad, riss_punkte, zeichne_dicke_kreide, zeichne_riss, zeichne_tafel_c

from .basis import Ducke, Erschrecke, Gehe, Jeweils, Setze, Stehe, Tu, Wandel, WarteBis
from .professor import FUNKEN, HaareHoch, TafelSzene

FUSS = 57            # äußerer Tafelfuß, Drehpunkt der kippenden Hälften
LANG, DICK = 152, 38  # Riesenkreide: 0,6 H lang, 0,15 H dick
KIPP = 84            # so weit kippen die Tafelhälften
STAND = 127          # Abstand Professor - Tafelmitte


class Kreide(TafelSzene):
    """Die Kreide bricht, die zweite bricht schneller. Er zieht Hand über Hand eine
    Riesenkreide hinten aus dem Kittel, holt aus, ein einziger Strich spaltet die Tafel,
    beide Hälften knallen flach auseinander. Er prüft die heile Kreide, nickt ihr
    anerkennend zu - knack, sie bricht doch und fällt ihm auf den Fuß. Er hüpft davon."""
    name, titel, reihenfolge = 'kreide', 'Unzerbrechliche Kreide', 75

    def vorbereiten(self):
        self.tafel_vorbereiten(0.12)
        self.linien = []          # [x0, y0, x1, y1, anteil, dicke] in Tafel-Einheiten
        self.stuecke = []         # fliegende und liegende Kreidestücke (Welt)
        self.riss = 0.0
        self.kipp = 0.0
        self.riss_pts = riss_punkte(tafel_flaeche(), saat=4)
        self.zug = 0.0            # Riesenkreide hinten aus dem Kittel: 0..1.2
        self.halten = None        # (Spitze, Richtung) der Riesenkreide in der Hand, Welt
        self.glanz = 0.0

    # -- Kreidestücke

    def bruch(self, x, y, n, laenge, dicke, tempo=1.0, nach=None):
        for _ in range(n):
            w = random.uniform(-math.pi * 0.95, -math.pi * 0.05)
            v = random.uniform(120, 260) * tempo * self.s
            vx = math.cos(w) * v if nach is None else nach * random.uniform(40, 120) * self.s
            self.stuecke.append(dict(x=x, y=y, vx=vx, vy=math.sin(w) * v, w=random.uniform(0, 180),
                                     dw=random.uniform(-900, 900), l=laenge, d=dicke, liegt=False))

    def knack(self, x, y, staerke=1.0):
        self.streue(x, y, int(5 + 5 * staerke), FUNKEN + [QColor('#FFFFFF')], tempo=220 * staerke, dauer=0.35,
                    r=(3, 6), art='stern')
        self.streue(x, y, int(6 + 6 * staerke), STAUB, tempo=70, dauer=0.6, r=(3, 7))

    def weiter(self, dt):
        super().weiter(dt)
        s = self.s
        for k in self.stuecke:
            if k['liegt']:
                continue
            k['vy'] += 1500 * s * dt
            k['x'] += k['vx'] * dt
            k['y'] += k['vy'] * dt
            k['w'] += k['dw'] * dt
            unten = self.boden + self.senke - k['d'] * 0.45 * s
            if k['y'] >= unten and k['vy'] > 0:
                k['y'] = unten
                if k['vy'] < 160 * s:
                    k['liegt'], k['w'] = True, round(k['w'] / 180) * 180 + random.uniform(-8, 8)
                else:
                    k['vy'] *= -0.3
                    k['vx'] *= 0.5
                    k['dw'] *= 0.4

    # -- Zeichnen

    def zeichne_flaeche(self, p, mit_riss=True):
        for x0, y0, x1, y1, a, d in self.linien:
            if a <= 0:
                continue
            p.setPen(stift(KREIDE, d))
            p.drawLine(QPointF(x0, y0), QPointF(x0 + (x1 - x0) * a, y0 + (y1 - y0) * a))
        p.setPen(KEIN_STIFT)
        if mit_riss:
            zeichne_riss(p, self.riss_pts, self.riss)

    def zeichne_tafel(self, p):
        p.save()
        p.translate(self.tafel_x, self.boden)
        p.scale(self.s, self.s)
        if self.kipp <= 0:
            zeichne_tafel_c(p, kreide=self.kreide_da)
            self.zeichne_flaeche(p)
        else:
            for seite in (-1, 1):
                p.save()
                p.translate(seite * FUSS, 0)
                p.rotate(seite * KIPP * self.kipp)
                p.translate(-seite * FUSS, 0)
                p.setClipPath(haelfte_pfad(self.riss_pts, seite))
                zeichne_tafel_c(p, kreide=False, schwamm=seite > 0)
                self.zeichne_flaeche(p, False)
                p.restore()
        p.restore()

    def zeichne_requisiten(self, p):
        self.zeichne_tafel(p)
        if 0 < self.zug and self.halten is None and self.zeige_figur:
            # Riesenkreide steckt hinten im Kittel, der Kittel verdeckt das untere Ende
            p.save()
            p.setTransform(self.trafo(), True)
            p.setClipRect(QRectF(-200, -600, 400, 540))
            unten = -175 - (LANG - 25) * self.zug + LANG
            zeichne_dicke_kreide(p, -30, unten - LANG / 2, 80, LANG, DICK)
            p.restore()

    def zeichne_davor(self, p):
        super().zeichne_davor(p)
        s = self.s
        if self.halten and self.zeige_figur:
            (tx, ty), (dx, dy) = self.halten
            p.save()
            p.translate(tx - dx * LANG * s / 2, ty - dy * LANG * s / 2)
            p.scale(s, s)
            zeichne_dicke_kreide(p, 0, 0, math.degrees(math.atan2(dy, dx)), LANG, DICK)
            p.restore()
            if self.glanz > 0:
                p.save()
                p.translate(tx - dx * 18 * s, ty - dy * 18 * s)
                p.scale(s, s)
                p.rotate(self.t * 200)
                p.setPen(KEIN_STIFT)
                p.setBrush(QColor(255, 255, 255, int(240 * self.glanz)))
                stern(p, 0, 0, 16 * self.glanz)
                p.restore()
        for k in self.stuecke:
            p.save()
            p.translate(k['x'], k['y'] + (0 if k['liegt'] else 0))
            p.scale(s, s)
            zeichne_dicke_kreide(p, 0, 0, k['w'], k['l'], k['d'])
            p.restore()

    def requisiten_kasten(self):
        s = self.s
        k = super().requisiten_kasten()
        if self.kipp > 0:
            x0, y0 = self.welt(-FUSS - 215, -40 - 160 * max(0.0, 1 - self.kipp))
            x1, _ = self.welt(FUSS + 215, 0)
            k = k.united(QRectF(x0, y0, x1 - x0, self.boden - y0))
        if self.zug > 0 and self.halten is None:
            k = k.united(self.trafo().mapRect(QRectF(-70, -185 - LANG * self.zug, 80, LANG * self.zug + 40)))
        if self.halten:
            (tx, ty), (dx, dy) = self.halten
            ex, ey = tx - dx * LANG * s, ty - dy * LANG * s
            r = DICK * s
            k = k.united(QRectF(min(tx, ex) - r, min(ty, ey) - r, abs(tx - ex) + 2 * r, abs(ty - ey) + 2 * r))
        for st in self.stuecke:
            r = st['l'] * 0.6 * s
            k = k.united(QRectF(st['x'] - r, st['y'] - r, 2 * r, 2 * r))
        return k

    # -- Ablauf

    def fig(self, fx, fy):
        q = self.trafo().map(QPointF(fx, fy))
        return q.x(), q.y()

    def greife(self, spitze, griff, vorn_griff=None):
        """Hält die Riesenkreide beidhändig: Spitze und Griffpunkt in Welt-Koordinaten."""
        dx, dy = spitze[0] - griff[0], spitze[1] - griff[1]
        n = math.hypot(dx, dy) or 1.0
        self.halten = (spitze, (dx / n, dy / n))
        g2 = (griff[0] - dx / n * 26 * self.s, griff[1] - dy / n * 26 * self.s)
        return dict(arm_v=self.arm_zu(*(vorn_griff or griff)), arm_h=self.arm_zu(*g2, vorn=False))

    def ablauf(self):
        r0, s = self.richtung, self.s
        self.x = self.aussen(-r0)
        px = self.tafel_x + STAND * s

        def strich(dauer, x0, y0, x1, y1):
            linie = [x0, y0, x1, y1, 0.0, 2.6]

            def f(sz, u):
                if not any(l is linie for l in sz.linien):
                    sz.linien.append(linie)
                a = min(1.0, u / dauer)
                linie[4] = a
                wx, wy = sz.welt(x0 + (x1 - x0) * a, y0 + (y1 - y0) * a)
                sz.kreide_ort = (wx, wy)
                sz.pose = Pose(arm_v=sz.arm_zu(wx, wy) + 3 * math.sin(u * 40), blick_y=-0.2,
                               auge_zu=blinzeln(sz.t))
            return Jeweils(dauer, f)

        def bricht(n, staerke):
            def f(sz):
                x, y = sz.kreide_ort
                sz.kreide_ort = None
                sz.knack(x, y, staerke)
                sz.bruch(x, y, n, 9, 6, tempo=staerke)
            return Tu(f)

        def zucken(staerke):
            def f(sz, u):
                g = max(0.0, 1 - u / 0.4)
                sz.hopp = 22 * staerke * s * math.sin(min(1.0, u / 0.25) * math.pi)
                return Pose(arm_v=-150 - 20 * staerke * g + 12 * math.sin(u * 50) * g, arm_v_x=12,
                            schreck=1.0 if u < 0.3 else 0.0, sorge=0.8, blick_y=-0.5,
                            bein_v=-10 * staerke, bein_h=8 * staerke)
            return f

        def tasche(sz, u):
            x, y = sz.fig(-2, -122)
            f = min(1.0, u / 0.15)
            if u > 0.18:
                sz.kreide_ort = sz.hand()
            return Pose(arm_v=-40 + (sz.arm_zu(x, y) + 40) * glatt(f), sorge=0.5, blick_y=0.4)

        # Hand über Hand aus dem Kittel: welche Hand zieht, die andere greift nach
        def ziehen(k):
            def f(sz, u):
                a = glatt(min(1.0, u / 0.32))
                sz.zug = (k + a) / 3
                hoch, tief = -215, -172
                ziehend = tief + (hoch - tief) * a
                wartend = hoch + (tief - hoch) * a
                v, h = (ziehend, wartend) if k % 2 == 0 else (wartend, ziehend)
                sz.hopp = 4 * s * math.sin(a * math.pi)
                return Pose(arm_v=v, arm_h=h, arm_v_x=4, blick_y=-0.9, mund_offen=a > 0.5,
                            sorge=0.2 * k, hub=-3 * a)
            return f

        def plopp(sz, u):
            # Die Kreide schnellt heraus, er fängt sie quer vor der Brust
            f = glatt(min(1.0, u / 0.3))
            sp = sz.fig(-40 + 150 * f, -330 + 40 * f)
            gr = sz.fig(-20 + 60 * f, -230 + 40 * f)
            arme = sz.greife(sp, gr)
            return Pose(arm_v_x=12, blick_y=-0.6 + 0.6 * f, mund_offen=True, **arme)

        def stolz(sz, u):
            sz.glanz = math.sin(min(1.0, u / 0.4) * math.pi)
            sp = sz.fig(110, -290)
            arme = sz.greife(sp, sz.fig(40, -190))
            return Pose(arm_v_x=12, blick_y=-0.5, mund_offen=False, auge_zu=0.25 < u < 0.4, **arme)

        def ausholen(sz, u):
            sz.glanz = 0.0
            f = glatt(min(1.0, u / 0.28))
            sp = sz.fig(110 - 140 * f, -290 - 8 * f)
            gr = sz.fig(40 - 38 * f, -190 - 10 * f)
            arme = sz.greife(sp, gr)
            return Pose(arm_v_x=12, blick_y=-0.6, sorge=0.0, mund_offen=True, bein_v=-14 * f, bein_h=10 * f,
                        **arme)

        dicklinie = [0, -194, 0, -94, 0.0, 9.0]

        def hauen(sz, u):
            # 0,08 s herab bis zur Oberkante, dann ein Strich bis ganz unten, kurz halten
            ox, oy = sz.welt(0, -194)
            if u < 0.08:
                f = u / 0.08
                a0 = sz.fig(-30, -298)
                sp = (a0[0] + (ox - a0[0]) * f, a0[1] + (oy - a0[1]) * f)
            else:
                if not any(l is dicklinie for l in sz.linien):
                    sz.linien.append(dicklinie)
                    sz.streue(ox, oy, 8, STAUB, tempo=90, dauer=0.5, r=(3, 7))
                a = min(1.0, (u - 0.08) / 0.14)
                dicklinie[4] = a
                sp = sz.welt(0, -194 + 100 * a)
            gr = sz.fig(48, -150)
            arme = sz.greife(sp, gr)
            return Pose(arm_v_x=12, blick_y=0.3, mund_offen=True, bein_v=-20, bein_h=14, hub=4, **arme)

        def reissen(sz, u):
            sz.riss = min(1.0, u / 0.12)
            sp = sz.welt(0, -94)
            arme = sz.greife(sp, sz.fig(48, -150))
            return Pose(arm_v_x=12, schreck=0.6, mund_offen=True, bein_v=-20, bein_h=14, hub=4, **arme)

        def kippen(sz, u):
            f = min(1.0, u / 0.5)
            sz.kipp = f * f
            if u >= 0.5:
                v = u - 0.5
                sz.kipp = 1 - 0.07 * abs(math.sin(v * 14)) * math.exp(-v * 7)
                if not getattr(sz, 'aufgeschlagen', False):
                    sz.aufgeschlagen = True
                    for seite in (-1, 1):
                        for k in range(5):
                            x, y = sz.welt(seite * (FUSS + 40 + k * 40), -6)
                            sz.streue(x, y, 3, STAUB, tempo=120, dauer=0.7, r=(6, 12),
                                      richtung=-math.pi / 2, streuung=1.3)
            sz.hopp = 34 * s * math.sin(min(1.0, max(0.0, u - 0.4) / 0.35) * math.pi)
            sp = sz.fig(110, -150 - 40 * min(1.0, u / 0.3))
            arme = sz.greife(sp, sz.fig(36, -160))
            return Pose(arm_v_x=12, kopf_vorn=u > 0.45, schreck=1.0, sorge=1.0, bein_v=-16, bein_h=16, **arme)

        def pruefen(sz, u):
            # Kreide vor die Brille, drehen, anerkennend nicken
            f = glatt(min(1.0, u / 0.3))
            dreh = 8 * math.sin(u * 7) if u < 0.8 else 0.0
            sp = sz.fig(95 + 30 * f, -160 - 40 * f + dreh)
            arme = sz.greife(sp, sz.fig(25 + 10 * f, -165 - 10 * f))
            nick = 5 * max(0.0, math.sin((u - 0.8) * 14)) if 0.8 < u < 1.25 else 0.0
            return Pose(arm_v_x=12, blick_y=0.2 - nick * 0.1, auge_zu=nick > 2.5 or blinzeln(sz.t),
                        hub=nick, sorge=0.3 if u < 0.8 else 0.0, mund_offen=False)

        def zerbrechen(sz):
            (tx, ty), (dx, dy) = sz.halten
            mx, my = tx - dx * LANG * s / 2, ty - dy * LANG * s / 2
            w = math.degrees(math.atan2(dy, dx))
            sz.knack(mx, my, 1.6)
            fx, _ = sz.fig(22, 0)
            for k, seite in ((0, 1), (1, -1)):
                h = LANG / 4 * s
                x, y = mx + seite * dx * h, my + seite * dy * h
                sz.stuecke.append(dict(x=x, y=y, vx=(fx - x) / 0.45, vy=-60 * s, w=w, dw=seite * 160,
                                       l=LANG / 2, d=DICK, liegt=False))
            sz.halten = None

        def fallen(sz, u):
            return Pose(arm_v=-60, arm_h=-50, arm_v_x=12, schreck=1.0, sorge=0.6, blick_y=0.8)

        def autsch(sz, u):
            sz.hopp = 40 * s * abs(math.sin(u * math.pi / 0.32))
            return Pose(kopf_vorn=u > 0.5, bein_v=-75, bein_h=6, arm_v=-10, arm_h=-30, arm_v_x=16,
                        schreck=1.0 if u < 0.7 else 0.0, mund_offen=True, sorge=1.0,
                        auge_zu=u > 0.7 and int(u * 6) % 2 == 0)

        ziel_aussen = self.aussen(1 if self.tafel_x > self.geo.center().x() else -1)

        def weghuepfen(sz, u, dt):
            sz.richtung = 1 if ziel_aussen > sz.x else -1
            sz.x += sz.richtung * 340 * s * dt
            sz.hopp = 40 * s * abs(math.sin(u * math.pi / 0.32))
            sz.pose = Pose(bein_v=-75, bein_h=6, arm_v=-10, arm_h=-30, arm_v_x=16, sorge=1.0, mund_offen=True,
                           auge_zu=int(u * 6) % 2 == 0)

        def weg_im_staub(sz):
            sz.weg(STAUB)

        return [
            Gehe(bis=px, tempo=1.8),
            Setze(richtung=-1),
            Setze(kreide_da=False),
            strich(0.4, 30, -170, -12, -162),
            bricht(2, 0.8),
            Stehe(0.35, zucken(0.6)),
            Jeweils(0.25, lambda sz, u: setattr(sz, 'pose', tasche(sz, u))),
            strich(0.12, 30, -150, 22, -148),
            bricht(5, 1.4),
            HaareHoch(0.4),
            Stehe(0.35, zucken(1.0)),
            Setze(hopp=0.0),
            Stehe(0.35, lambda sz, u: Pose(kopf_vorn=True, sorge=0.0, blick_y=0.1, auge_zu=0.1 < u < 0.3)),
            *[Stehe(0.32, ziehen(k)) for k in range(3)],
            Setze(hopp=0.0),
            Stehe(0.3, plopp),
            Setze(zug=0.0),
            Stehe(0.45, stolz),
            Stehe(0.28, ausholen),
            Stehe(0.3, lambda sz, u: ausholen(sz, 0.28)),
            Stehe(0.24, hauen),
            Stehe(0.12, reissen),
            Stehe(0.9, kippen),
            Setze(hopp=0.0, kipp=1.0),
            Stehe(1.15, pruefen),
            Tu(zerbrechen),
            Stehe(0.45, fallen),
            Tu(lambda sz: sz.streue(*sz.fig(22, -4), 10, STAUB, tempo=110, dauer=0.5, r=(4, 9))),
            HaareHoch(0.8),
            Stehe(1.0, autsch),
            Huepfe(weghuepfen),
            Setze(hopp=0.0),
            Tu(weg_im_staub),
            Setze(zeige_figur=False),
            WarteBis(lambda sz: not sz.wolke and not sz.splitter),
        ]

    def schreck_ablauf(self):
        """Er duckt sich, alles versinkt."""
        self.kreide_ort = None
        self.halten = None
        self.zug = 0.0
        self.nebenbei.clear()
        self.halt = self.halt_h = None
        self.hopp = 0.0
        tief = 330 * self.s
        vorher = [HaareHoch(1.0), Erschrecke(0.3, 46), Ducke(0.2)] if self.figur_sichtbar() else []
        return vorher + [Wandel(0.45, y=lambda sz: sz.y + tief, senke=tief),
                         Tu(lambda sz: setattr(sz, 'zeige_figur', False))] + self._ende()


class Huepfe(Jeweils):
    """Ruft funktion(szene, u, dt) auf, bis er aus dem Bild ist."""

    def __init__(self, funktion):
        super().__init__(0.0, funktion)

    def weiter(self, sz, u, dt):
        self.funktion(sz, u, dt)

    def fertig(self, sz, u):
        return u > 0.2 and not sz.figur_sichtbar()
