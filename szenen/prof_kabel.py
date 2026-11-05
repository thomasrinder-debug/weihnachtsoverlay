import math
from dataclasses import replace

from PyQt6.QtCore import QPointF, QRectF
from PyQt6.QtGui import QColor, QTransform

from zeichnen.figur import Pose
from zeichnen.grundlagen import GOLD_HELL, KEIN_PINSEL, KEIN_STIFT, blinzeln, glatt, stern, stift
from zeichnen.labor_d import kabel_linie, wicklung_punkt, zeichne_knaeuel, zeichne_stecker, zeichne_wicklung
from zeichnen.professor import professor_trafo

from .basis import Erschrecke, Gehe, Jeweils, Schritt, Setze, Stehe, Tu, Wandel
from .professor import FUNKEN, STAUB, HaareHoch, ProfSzene, Publikumsblick, Zurueck

KN = 2.3                  # Kabelknäuel, vergrößert
BEINE, BAUCH, ARME = 3 / 8, 6 / 8, 1.0   # Wickelstand nach jeder Drehung
VERZUG = 0.24             # so viel später hüpft der Stecker hinterher


class Drehe(Schritt):
    """Dreht sich um die eigene Achse (Breite der Figur folgt dem Kosinus) und wickelt sich
    dabei ein. abklingen: wird langsamer (Kreisel), rueck: andersherum."""

    def __init__(self, dauer, runden, wickel_bis=None, menge_bis=None, wirbel=0.5, abklingen=False, rueck=False,
                 weg=0.0):
        self.dauer, self.runden = dauer, runden
        self.wickel_bis, self.menge_bis, self.wirbel = wickel_bis, menge_bis, wirbel
        self.abklingen, self.rueck, self.weg = abklingen, rueck, weg

    def beginn(self, sz):
        self.r0, self.w0, self.m0, self.x0 = sz.richtung, sz.wickel, sz.menge, sz.x

    def weiter(self, sz, u, dt):
        f = min(1.0, u / self.dauer)
        g = 1 - (1 - f) ** 2 if self.abklingen else f
        phi = 2 * math.pi * self.runden * g * (-1 if self.rueck else 1)
        c = math.cos(phi)
        sz.richtung = self.r0 if c >= 0 else -self.r0
        sz.dreh_x = 0.35 + 0.65 * abs(c)
        vorn = abs(c) < 0.6 and math.sin(phi) * (-1 if self.rueck else 1) > 0
        if self.wickel_bis is not None:
            sz.wickel = self.w0 + (self.wickel_bis - self.w0) * f
        if self.menge_bis is not None:
            sz.menge = self.m0 + (self.menge_bis - self.m0) * f
        sz.wirbel = self.wirbel * (1 - f if self.abklingen else 1)
        sz.hopp = abs(math.sin(phi)) * 6 * sz.s
        if self.weg:
            sz.x = self.x0 + sz.rand * self.weg * sz.s * glatt(f * 1.4)
        sz.pose = Pose(kopf_vorn=vorn, arm_v=-150 + 40 * math.sin(u * 17), arm_h=-140 + 40 * math.cos(u * 15),
                       arm_v_x=16, sorge=0.7, mund_offen=True, blick_y=0.3, wipp=8 * math.sin(phi))

    def ende(self, sz):
        sz.richtung, sz.dreh_x, sz.hopp, sz.wirbel = self.r0, 1.0, 0.0, 0.0


class Huepfe(Schritt):
    """Hüpft mit zusammengebundenen Beinen zum nächsten Rand hinaus, der Stecker hüpft hinterher."""

    def __init__(self, tempo=1.0, hoehe=34, takt=0.42):
        self.tempo, self.hoehe, self.takt = tempo, hoehe, takt

    def beginn(self, sz):
        sz.richtung = sz.naechster_rand()
        sz.neigung, sz.dreh_x = 0.0, 1.0
        if sz.stecker:
            sz.stecker['folgt'] = sz.stecker['x'] - sz.x

    def weiter(self, sz, u, dt):
        ph = (u / self.takt) % 1
        luft = 0.15 < ph
        if luft:
            sz.x += sz.richtung * self.tempo * sz.tempo * dt / 0.85
            sz.hopp = math.sin(math.pi * (ph - 0.15) / 0.85) * self.hoehe * sz.s
            sz.stauchen = 1.0
        else:
            sz.hopp = 0.0
            sz.stauchen = 1 - 0.14 * math.sin(math.pi * ph / 0.15)
        sz.pose = Pose(kopf_vorn=False, sorge=0.2, mund_offen=False, auge_zu=True, blick_y=-0.5,
                       wipp=5 * math.sin(u * 12))

    def fertig(self, sz, u):
        if u < 0.1 or sz.figur_sichtbar():
            return False
        st = sz.stecker
        return sz.weg_ist or not st or not sz.geo.adjusted(-30 * sz.s, 0, 30 * sz.s, 0).contains(
            QPointF(st['x'], sz.boden - 10))

    def ende(self, sz):
        sz.hopp, sz.stauchen = 0.0, 1.0
        sz.zeige_figur = False


class Kabel(ProfSzene):
    """Er zieht am Kabelsalat, erst mit einer Hand, dann mit beiden, nichts rührt sich.
    Also dreht er sich, immer hektischer, und wickelt dabei Beine, Bauch und Arme ein.
    Letzter Ruck nach hinten: der Knäuel gibt nach, das straffe Kabel wirbelt ihn wie
    einen Kreisel zurück. Er taumelt, blickt ins Publikum, hebt würdevoll das Kinn und
    kann doch nur mit gefesselten Beinen hinaushüpfen, der Stecker hüpft hinterher."""
    name, titel, reihenfolge = 'kabel', 'Kabelsalat', 86

    def vorbereiten(self):
        self.rand = -self.richtung
        self.kx = self.vom_rand(0.14)
        self.menge = 1.0
        self.wickel = 0.0
        self.eng = 0.0
        self.haelt = False
        self.straff = 0.0
        self.wackel = 0.0
        self.knaeuel_hopp = 0.0
        self.dreh_x = 1.0
        self.wirbel = 0.0
        self.sterne = 0.0
        self.stecker = None
        self.spur = []

    def trafo(self):
        return QTransform.fromScale(self.dreh_x, 1) * professor_trafo(
            self.x, self.y - self.hopp, self.s, self.richtung, self.stauchen, self.neigung)

    def weiter(self, dt):
        super().weiter(dt)
        if self.wickel >= BEINE - 0.01:
            self.pose = replace(self.pose, bein_v=0, bein_h=0)
        if self.wickel >= ARME - 0.01:
            self.pose = replace(self.pose, arm_v=-4, arm_h=5, arm_v_x=10)
        self.spur.append((self.t, self.x, self.hopp))
        while len(self.spur) > 2 and self.spur[1][0] < self.t - VERZUG:
            self.spur.pop(0)
        st = self.stecker
        if not st:
            return
        if 'folgt' in st:
            _, x, h = self.spur[0]
            st['x'] = x + st['folgt']
            st['y'] = self.boden - 5 * self.s - h * 0.8
            st['dreh'] = 180 * (self.richtung < 0) - self.richtung * 25 * h / max(1.0, 34 * self.s)
        elif st['fliegt']:
            st['vy'] += 1500 * self.s * dt
            st['x'] += st['vx'] * dt
            st['y'] += st['vy'] * dt
            st['dreh'] += 1000 * dt
            if st['y'] >= self.boden - 5 * self.s and st['vy'] > 0:
                st['y'], st['fliegt'] = self.boden - 5 * self.s, False
                st['dreh'] = 0 if self.rand < 0 else 180
                self.streue(st['x'], self.boden - 4 * self.s, 4, STAUB, tempo=60, dauer=0.4, r=(3, 6))

    # -- Punkte

    def knaeuel_punkt(self):
        return self.kx + self.rand * 30 * self.s, self.boden - 22 * KN * self.s * (0.35 + 0.65 * self.menge)

    def koerper_punkt(self):
        rx, y = wicklung_punkt(self.wickel)
        q = self.trafo().map(QPointF(-rx, y))
        return q.x(), q.y()

    # -- Zeichnen

    def zeichne_requisiten(self, p):
        s = self.s
        p.save()
        p.translate(self.kx, self.boden - self.knaeuel_hopp)
        if self.wackel:
            p.rotate(self.wackel * 6 * math.sin(self.t * 40))
        p.scale(s * KN * self.rand, s * KN)
        zeichne_knaeuel(p, 0, 0, self.menge, self.t, breite=2.8)
        if not self.haelt and self.wickel == 0 and self.menge > 0.5:
            kabel_linie(p, [(14, -6), (26, -2), (38, -1.5)], 2.8)
        p.restore()

    def zeichne_davor(self, p):
        if not self.zeige_figur:
            return
        s = self.s
        b = 6.5 * s
        kx, ky = self.knaeuel_punkt()
        if self.stecker:
            st = self.stecker
            bx, by = self.koerper_punkt()
            mx = (bx + st['x']) / 2
            kabel_linie(p, [(bx, by), (mx, max(by, st['y']) + 6 * s), (st['x'], st['y'])], b)
            p.save()
            p.translate(st['x'], st['y'])
            p.scale(s * 1.8, s * 1.8)
            zeichne_stecker(p, 0, 0, st['dreh'])
            p.restore()
        elif self.menge > 0.03 and (self.haelt or self.wickel > 0):
            ex, ey = self.koerper_punkt() if self.wickel > 0 else self.hand()
            durch = 26 * (1 - self.straff) * s
            kabel_linie(p, [(kx, ky), ((kx + ex) / 2, max(ky, ey) + durch), (ex, ey)], b)

    def zeichne_vorn(self, p):
        s = self.s
        if self.zeige_figur and self.wickel > 0:
            p.save()
            p.setTransform(self.trafo(), True)
            zeichne_wicklung(p, self.wickel, self.eng, vorn=True)
            p.restore()
        super().zeichne_vorn(p)
        if not self.zeige_figur:
            return
        if self.wirbel > 0.02:
            p.setBrush(KEIN_PINSEL)
            p.setPen(stift(QColor(255, 255, 255, int(220 * self.wirbel)), 3.2 * s))
            for k, hy in enumerate((40, 110, 185)):
                r = QRectF(self.x - 62 * s, self.y - self.hopp - (hy + 12) * s, 124 * s, 24 * s)
                start = (self.t * 900 * (1 if self.rand > 0 else -1) + k * 120) % 360
                p.drawArc(r, int(start * 16), int(130 * 16))
                p.drawArc(r, int((start + 180) * 16), int(70 * 16))
            p.setPen(KEIN_STIFT)
        if self.sterne > 0.02:
            x, y = self.kopf_oben()
            p.setPen(KEIN_STIFT)
            for k in range(3):
                w = self.t * 7 + k * 2.1
                c = QColor(GOLD_HELL)
                c.setAlphaF(self.sterne)
                p.setBrush(c)
                stern(p, x + math.cos(w) * 38 * s, y + 12 * s + math.sin(w) * 10 * s, 11 * s)

    def zeichne_hinten(self, p):
        super().zeichne_hinten(p)
        if self.zeige_figur and self.wickel > 0:
            p.save()
            p.setTransform(self.trafo(), True)
            zeichne_wicklung(p, self.wickel, self.eng, vorn=False)
            p.restore()

    def requisiten_kasten(self):
        s = self.s
        k = QRectF(self.kx - 45 * KN * s, self.boden - 50 * KN * s - self.knaeuel_hopp, 90 * KN * s,
                   50 * KN * s + self.knaeuel_hopp)
        if self.zeige_figur:
            f = self.figur_kasten()
            k = k.united(QRectF(self.x - 70 * s, f.top() - 20 * s, 140 * s, self.boden - f.top() + 20 * s))
            if self.haelt:
                hx, hy = self.hand()
                k = k.united(QRectF(hx - 12 * s, hy - 12 * s, 24 * s, 24 * s))
        if self.stecker:
            st = self.stecker
            k = k.united(QRectF(st['x'] - 40 * s, st['y'] - 40 * s, 80 * s, 50 * s))
        return k

    # -- Ablauf

    def reisst(self, sz):
        """Der Knäuel gibt schlagartig nach, der Stecker fliegt heraus."""
        s = self.s
        self.straff, self.wackel = 0.0, 0.0
        self.streue(self.kx, self.boden - 30 * s, 16, STAUB, tempo=180, dauer=0.7, r=(6, 13))
        self.streue(self.kx, self.boden - 40 * s, 8, FUNKEN, tempo=220, dauer=0.5, r=(3, 6), art='stern')
        self.menge = 0.0
        self.stecker = dict(x=self.kx, y=self.boden - 30 * s, vx=-self.rand * 60 * s, vy=-620 * s, dreh=0,
                            fliegt=True)

    def ablauf(self):
        r, s = self.rand, self.s
        self.x = self.aussen(r)
        px = self.kx + r * 112 * s
        knaeuel = lambda sz: sz.knaeuel_punkt()

        def greifen(sz, u):
            return Pose(arm_v=sz.arm_zu(sz.kx + r * 52 * s, sz.boden - 6 * s), hub=8 * min(1, u * 4), blick_y=0.9)

        def zerre_hand(sz, u):
            sz.neigung = -14 * abs(math.sin(u * 11))
            sz.wackel = 0.4
            sz.pose = Pose(arm_v=sz.arm_zu(*knaeuel(sz)) - 25, arm_h=20, arm_v_x=16, bein_v=-14, bein_h=10,
                           sorge=0.3, blick_y=0.5, mund_offen=u > 0.3)

        def zerre_beide(sz, u):
            sz.neigung = -26 + 4 * math.sin(u * 34)
            sz.wackel = 1.0
            sz.pose = Pose(arm_v=sz.arm_zu(*knaeuel(sz)) - 15, arm_h=sz.arm_zu(*knaeuel(sz), vorn=False) - 15,
                           arm_v_x=18, bein_v=-30, bein_h=20, sorge=0.0, blick_y=0.4, mund_offen=True,
                           auge_zu=u > 0.3)

        def anhalten(sz, u):
            return Pose(kopf_vorn=0.1 < u < 0.3, blick_y=0.6, sorge=0.5, arm_v=-60, arm_h=-40)

        def gespannt(sz, u):
            return Pose(blick_y=0.6, sorge=0.6, kopf_vorn=False, auge_zu=False)

        def taumeln(sz, u):
            sz.sterne = 1.0
            sz.neigung = 13 * math.sin(u * 8) * (1 - 0.4 * u)
            sz.stauchen = 1 - 0.04 * abs(math.sin(u * 8))
            sz.pose = Pose(kopf_vorn=True, auge_zu=(u * 5) % 1 < 0.35, mund_offen=True, sorge=0.6,
                           blick_x=math.sin(u * 14), wipp=6 * math.sin(u * 8))

        def wuerde(sz, u):
            return Pose(kopf_vorn=False, auge_zu=True, blick_y=-0.6, hub=-3 * min(1, u * 4))

        return [
            Gehe(bis=px, tempo=1.8),
            Setze(richtung=-r),
            Stehe(0.3, greifen),
            Setze(haelt=True),
            Zurueck(30, 0.3),
            Setze(straff=1.0),
            Jeweils(0.6, zerre_hand),
            Setze(neigung=0.0, wackel=0.0),
            Stehe(0.15),
            Jeweils(0.75, zerre_beide),
            Setze(neigung=0.0, wackel=0.0, straff=0.0),
            Stehe(0.4, anhalten),
            Drehe(0.9, 1, BEINE, 0.75, wirbel=0.3),
            Drehe(0.65, 1, BAUCH, 0.5, wirbel=0.6),
            Drehe(0.45, 1, ARME, 0.35, wirbel=1.0),
            Setze(eng=1.0, straff=0.6),
            Stehe(0.35, gespannt),
            Setze(straff=1.0, wackel=0.8),
            Wandel(0.25, neigung=-28),
            Stehe(0.1, lambda sz, u: Pose(auge_zu=True, mund_offen=True, sorge=0.2)),
            Tu(self.reisst),
            Setze(neigung=0.0),
            Drehe(1.1, 4, wirbel=1.0, abklingen=True, rueck=True, weg=55),
            Jeweils(0.9, taumeln),
            Setze(neigung=0.0, stauchen=1.0),
            Wandel(0.3, sterne=0.0),
            Publikumsblick(1.0, husten=False),
            Stehe(0.45, wuerde),
            Huepfe(tempo=0.9),
        ]

    def schreck_ablauf(self):
        self._vorher()
        self.haelt = False
        self.sterne = self.wirbel = 0.0
        self.dreh_x = 1.0
        if not self.zeige_figur or not self.figur_sichtbar():
            self.zeige_figur = False
            return self._ende()
        return [Setze(neigung=0.0, hopp=0.0, stauchen=1.0), Wandel(0.15, wickel=1.0, eng=1.0),
                HaareHoch(1.0), Erschrecke(0.3, 50),
                Huepfe(tempo=3.6, hoehe=40, takt=0.3)] + self._ende()
