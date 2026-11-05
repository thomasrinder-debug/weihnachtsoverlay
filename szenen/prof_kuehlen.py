import math
import random
from dataclasses import replace

from PyQt6.QtCore import QRectF
from PyQt6.QtGui import QColor

from zeichnen.figur import Pose
from zeichnen.figuren import Pinguin
from zeichnen.grundlagen import WEISS, blinzeln, glatt
from zeichnen.labor import zeichne_monitor
from zeichnen.labor_e import zeichne_eisblock

from .basis import Erschrecke, Falle, Gehe, Jeweils, Mit, Nebenbei, Renne, Rutsche, Setze, Springe, Stehe, \
    Tu, Wandel, Warte, WarteNebenbei
from .geraet import GeraetSzene, Solange, nackte_hand, qualm, zeichne_handschuh_leer, zeichne_wolke
from .professor import RAUCH, HaareHoch, Publikumsblick

G = 1.7
MON_H = 78 * G
EIS_B, EIS_H = 156, 168
EIS = [QColor('#CFEFFF'), QColor('#9FD6F5'), WEISS]
FROST = [QColor('#E8F8FF'), QColor('#B8E4FA'), WEISS]


class Kuehlen(GeraetSzene):
    """Der Monitor qualmt in einer dicken Wolke. Der Professor wedelt, erst mit einer Hand,
    dann mit beiden, die Wolke wird nur größer. Der Pinguin hüpft auf den Monitor: Qualm weg.
    Der Professor legt die Hand auf den Monitor und lässt sich feiern, da friert alles
    samt seinem Handschuh ein. Er zieht, zerrt, schlüpft heraus und fliegt auf den Rücken.
    Der Pinguin rodelt mit dem Eisblock davon, der Professor pustet in die bloße Hand und folgt."""
    name, titel, reihenfolge = 'kuehlen', 'Eiskalt gekühlt', 90

    def vorbereiten(self):
        r = self.seite = self.richtung
        s = self.s
        self.mon_x = self.vom_rand(0.1)
        self.eis_x = self.mon_x + r * 10 * s
        self.stand = self.mon_x + r * 98 * s
        self.qualm_w = 0.0       # 0..2: Qualmwolke über dem Monitor
        self.raucht = 0.0
        self.kaputt = 0.3
        self.eis = 0.0
        self.handschuh = None    # Punkt des eingefrorenen Handschuhs, relativ zum Monitor
        self.nackt = False
        pg = self.pg = self.dazu('pingu', Pinguin, groesse=0.56)
        pg.x = self.aussen(-r) - r * 30 * s
        pg.tempo = self.tempo * 0.9

    def weiter(self, dt):
        super().weiter(dt)
        if self.raucht and not self.erschreckt:
            qualm(self, self.mon_x, self.boden - (MON_H + 4) * self.s, self.raucht, 1.3)

    # -- Orte

    def oben(self):
        return self.boden - (EIS_H if self.eis > 0.5 else MON_H) * self.s

    def ecke(self):
        """Obere Monitorecke zum Professor hin, wo er die Hand auflegt."""
        return self.mon_x + self.seite * 44 * self.s, self.boden - (MON_H - 2) * self.s

    def wolke_mitte(self):
        r = 34 + 34 * self.qualm_w
        return self.mon_x + self.seite * 8 * self.s, self.boden - (MON_H + r * 0.55) * self.s, r * self.s

    # -- Zeichnen

    def zeichne_requisiten(self, p):
        s = self.s
        p.save()
        p.translate(self.mon_x + self.zitter(), self.boden)
        p.scale(G * s, G * s)
        zeichne_monitor(p, 0, 0, 0.7 if self.qualm_w <= 0 else 0.35, self.t, self.kaputt,
                        flackern=self.qualm_w > 0)
        p.restore()
        if self.eis > 0:
            p.save()
            p.translate(self.eis_x, self.boden)
            p.scale(s, s)
            zeichne_eisblock(p, 0, 0, EIS_B, EIS_H, self.eis, -self.seite, self.t)
            p.restore()
        if self.handschuh and self.nackt:
            dx, dy, w = self.handschuh
            p.setOpacity(0.85)
            zeichne_handschuh_leer(p, self.mon_x + dx, self.boden + dy, s * 1.3, w)
            p.setOpacity(1.0)

    def zeichne_davor(self, p):
        if self.qualm_w > 0:
            x, y, r = self.wolke_mitte()
            zeichne_wolke(p, x, y, r, self.t, saat=3)
        if self.nackt and self.zeige_figur:
            nackte_hand(p, self)

    def requisiten_kasten(self):
        s = self.s
        b = EIS_B / 2 + EIS_H
        k = QRectF(self.mon_x - b * s, self.boden - (EIS_H + 12) * s, 2 * b * s, (EIS_H + 12) * s)
        if self.qualm_w > 0:
            x, y, r = self.wolke_mitte()
            k = k.united(QRectF(x - r * 1.9, y - r * 1.5, r * 3.8, r * 3.0))
        return k

    # -- Ablauf

    def ablauf(self):
        r, s = self.richtung, self.s
        self.x = self.aussen(-r)
        pg = self.pg
        start = {}

        def wedeln(beide, w0, w1, dauer):
            def f(sz, u):
                sz.qualm_w = w0 + (w1 - w0) * min(1.0, u / dauer)
                w = math.sin(u * (22 if beide else 16))
                wx, wy, wr = sz.wolke_mitte()
                if beide:
                    sz.neigung = 8
                    sz.pose = Pose(arm_v=-125 + 45 * w, arm_h=-120 - 45 * w, arm_v_x=16, schreck=0.5, sorge=1.0,
                                   mund_offen=(u * 5) % 1 < 0.5, auge_zu=u > 0.45, bein_v=-14, bein_h=12)
                    sz.russ = min(0.45, u * 0.6)
                    if random.random() < 0.12:
                        mx, my = sz.mund()
                        sz.streue(mx, my, 2, RAUCH, tempo=60, dauer=0.6, r=(4, 8))
                else:
                    sz.pose = Pose(arm_v=-115 + 35 * w, arm_v_x=16, sorge=0.6, blick_y=-0.3,
                                   auge_zu=blinzeln(sz.t))
            return f

        def zisch(sz):
            x, y, rr = sz.wolke_mitte()
            sz.qualm_w, sz.raucht, sz.neigung = 0.0, 0.0, 0.0
            sz.streue(x, y, 22, RAUCH, tempo=160, dauer=0.7, r=(8, 16))
            sz.streue(sz.mon_x, sz.boden - MON_H * s, 12, EIS, tempo=200, dauer=0.6, r=(3, 6), art='stern')

        def staunen(sz, u):
            return Pose(arm_v=-150, arm_h=-130, arm_v_x=16, schreck=0.4, auge_zu=0.5 < u < 0.65, kopf_vorn=u > 0.2,
                        mund_offen=True)

        def auflegen(sz, u):
            sz.pose = Pose(arm_v=sz.arm_zu(*sz.ecke()), arm_h=-140, kopf_vorn=True, bein_v=-10, bein_h=10,
                           wipp=2 * math.sin(u * 6), auge_zu=0.45 < u < 0.6, mund_offen=u < 0.35)
            pg.pose = Pose(blick_x=0.4 * r, auge_zu=blinzeln(sz.t, 0.4))

        def pause(sz, u):
            sz.pose = Pose(arm_v=sz.arm_zu(*sz.ecke()), arm_h=-140, kopf_vorn=True, bein_v=-10, bein_h=10)
            pg.stauchen = 1 - 0.12 * math.sin(min(1.0, u / 0.3) * math.pi)
            pg.pose = Pose(kopf_vorn=True, mund_offen=True, auge_zu=True)
            if random.random() < 0.25:
                sz.streue(sz.mon_x + random.uniform(-40, 40) * s, sz.boden - random.uniform(10, 90) * s, 1, FROST,
                          tempo=30, dauer=0.5, r=(3, 5), art='stern')

        def frieren(sz):
            ex, ey = sz.ecke()
            sz.handschuh = (ex - sz.mon_x, ey - sz.boden, 0.0)
            sz.haare, sz.striche = 1.0, True
            sz.streue(sz.eis_x, sz.boden - 80 * s, 24, EIS, tempo=260, dauer=0.8, r=(3, 7), art='stern')

        def eiswelle(sz, u):
            sz.eis = min(1.0, u / 0.3)
            pg.y = sz.boden - max(MON_H, EIS_H * glatt(sz.eis)) * s
            sz.pose = Pose(arm_v=sz.arm_zu(*sz.ecke()), arm_h=-30, schreck=1.0, sorge=1.0, kopf_vorn=True,
                           bein_v=-8, bein_h=8)

        def ziehen(staerke, dauer):
            def f(sz, u):
                v = min(1.0, u / dauer)
                ruck = math.sin(v * math.pi)
                sz.x = sz.stand
                sz.neigung = -(10 + 20 * staerke) * ruck
                gx, gy = sz.ecke()
                zwei = staerke > 0.4
                sz.pose = Pose(arm_v=sz.arm_zu(gx, gy), arm_h=sz.arm_zu(gx, gy, False) if zwei else -40,
                               bein_v=-34 * ruck, bein_h=24 * ruck, sorge=1.0, mund_offen=ruck > 0.5,
                               auge_zu=ruck > 0.6, schreck=0.3)
                hx, _ = sz.hand(True)
                sz.x = sz.stand + max(-18 * s, min(18 * s, gx - hx))
                sz.wackel = max(sz.wackel, 0.5 * ruck * staerke)
            return f

        def frei(sz):
            sz.nackt, sz.striche = True, False
            gx, gy = sz.ecke()
            sz.streue(gx, gy, 14, EIS, tempo=220, dauer=0.6, r=(3, 6), art='stern')

        def rueckwaerts(sz, u):
            f = min(1.0, u / 0.4)
            if 'x0' not in start:
                start['x0'] = sz.x
            sz.x = start['x0'] + r * 70 * s * (1 - (1 - f) ** 2)
            sz.neigung = -88 * f ** 1.5
            sz.hopp = 26 * s * math.sin(f * math.pi)
            sz.pose = Pose(arm_v=-100, arm_h=-130, kopf_vorn=True, schreck=1.0, bein_v=-40, bein_h=-10,
                           mund_offen=True)

        def liegen(sz, u):
            return Pose(arm_v=-150 + 15 * math.sin(u * 14), arm_h=-20, kopf_vorn=True, auge_zu=u < 0.2,
                        bein_v=-30, bein_h=-10, sorge=0.6)

        def aufsitzen(sz, u):
            f = glatt(min(1.0, u / 0.35))
            sz.neigung = -88 * (1 - f)
            sz.pose = Pose(arm_v=-100, arm_h=-20, sorge=0.8, blick_y=0.2)

        def anpusten(sz, u):
            mx, my = sz.mund()
            sz.pose = Pose(arm_v=sz.arm_zu(mx, my + 8 * s), arm_v_x=16, kopf_vorn=False,
                           mund_offen=(u * 3) % 1 < 0.4, auge_zu=True, sorge=0.8)
            if (u * 3) % 1 < 0.06:
                hx, hy = sz.hand()
                sz.streue(hx, hy, 3, FROST, tempo=50, dauer=0.5, r=(3, 6))

        def rodeln(sz, u):
            if 'x' not in start:
                start['x'] = sz.mon_x
                start['e'] = sz.eis_x
            v = sz.tempo * 1.35 * glatt(min(1.0, u / 0.4))
            start['w'] = start.get('w', 0.0) + v / 60
            d = -r * start['w']
            sz.mon_x, sz.eis_x = start['x'] + d, start['e'] + d
            pg.x = sz.eis_x
            pg.y = sz.boden - EIS_H * s
            pg.neigung = -10
            pg.pose = Pose(arm_v=-150, arm_h=-150, mund_offen=True, bein_v=-20, bein_h=20)
            if random.random() < 0.4:
                sz.streue(sz.eis_x - r * EIS_B / 2 * s, sz.boden, 1, EIS, tempo=60, dauer=0.5, r=(3, 5), art='stern')

        def folgen(pose, sz):
            mx, my = sz.mund()
            return replace(pose, arm_v=sz.arm_zu(mx, my + 8 * s), arm_v_x=16, mund_offen=(sz.t * 3) % 1 < 0.4,
                           sorge=0.6)

        return [
            Nebenbei(Wandel(1.0, qualm_w=1.0, raucht=0.6)),
            Nebenbei(Warte(1.0), Mit('pingu', Gehe(bis=self.mon_x - r * 82 * s, tempo=1.0))),
            Gehe(bis=self.stand, tempo=2.2),
            Setze(richtung=-r),
            Jeweils(0.7, wedeln(False, 1.0, 1.35, 0.7)),
            Jeweils(0.9, wedeln(True, 1.35, 2.1, 0.9)),
            WarteNebenbei(),
            Mit('pingu', Setze(richtung=r)),
            Nebenbei(Mit('pingu', Springe(nach=(self.mon_x, self.boden - MON_H * s), dauer=0.45, hoehe=70)),
                     Jeweils(0.45, wedeln(True, 2.1, 2.2, 0.45))),
            WarteNebenbei(),
            Tu(zisch),
            Mit('pingu', Wandel(0.12, stauchen=0.8)),
            Mit('pingu', Wandel(0.15, stauchen=1.0)),
            Stehe(0.4, staunen),
            Jeweils(0.8, auflegen),
            Jeweils(0.3, pause),
            Tu(frieren),
            Jeweils(0.35, eiswelle),
            Setze(striche=False),
            Jeweils(0.5, ziehen(0.2, 0.5)),
            Jeweils(0.45, ziehen(0.6, 0.45)),
            Jeweils(0.35, ziehen(1.0, 0.7)),
            Tu(frei),
            Jeweils(0.4, rueckwaerts),
            Setze(hopp=0.0),
            Stehe(0.5, liegen),
            Jeweils(0.35, aufsitzen),
            Setze(neigung=0.0),
            Jeweils(0.7, anpusten),
            Publikumsblick(0.8, husten=False),
            Mit('pingu', Setze(richtung=-r)),
            Nebenbei(Solange(rodeln, lambda sz: (sz.eis_x - sz.aussen(-r)) * -r > 0)),
            Warte(0.35),
            Gehe(tempo=1.2, haltung=folgen),
            WarteNebenbei(),
        ]

    def schreck_ablauf(self):
        self._vorher()
        s = self.s
        self.qualm_w = 0.0
        neu = []
        pg = self.pg
        if pg.zeige_figur:
            neu.append(Nebenbei(Mit('pingu', Erschrecke(0.25, 26)),
                                Mit('pingu', Falle(lambda d: d.y >= d.sz.boden)),
                                Mit('pingu', Setze(y=self.boden, neigung=0)),
                                Mit('pingu', Rutsche(zum='rand', tempo=4.0, hoehe=14))))
        self.neigung, self.hopp = 0.0, 0.0
        if not self.figur_sichtbar():
            self.zeige_figur = False
            return neu + self._ende()
        self.streue(self.mon_x, self.boden - 70 * s, 18, EIS, tempo=160, dauer=0.7, r=(3, 7), art='stern')
        return neu + [HaareHoch(1.0), Erschrecke(0.3, 46), Renne(zum='rand', tempo=4.5)] + self._ende()
