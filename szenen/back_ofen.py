import math

from PyQt6.QtCore import QPointF, QRectF
from PyQt6.QtGui import QColor

from zeichnen.baeckerei import zeichne_ofen
from zeichnen.figur import Pose
from zeichnen.figuren import Lebkuchenmann
from zeichnen.grundlagen import blinzeln

from .back_bausteine import figur_trafo, hand, publikum
from .basis import (Erschrecke, Gehe, Jeweils, Mit, Nebenbei, Renne, Setze, Springe, Stehe, Szene, Tu, Wandel,
                    WarteNebenbei)

DAMPF = [QColor('#F4E9D8'), QColor('#E2CFB2'), QColor('#FFFFFF')]


class BackOfen(Szene):
    """Aus dem Backofen springt ein Lebkuchenmann und rennt gegen seinen Stiefel; er wirft ihn
    zurück. Dann hüpfen zwei heraus, er fängt beide und stopft sie hinein, lehnt sich zufrieden
    an die Ofentür. Der Ofen zittert, die Tür fliegt auf, und heraus steigt ein riesiger
    Lebkuchenmann, der sich zu ihm herunterbeugt und den Mund aufmacht. Er flieht, der Riese
    grinst ins Publikum und zwängt sich zurück in den Ofen."""
    name, titel, reihenfolge = 'back_ofen', 'Ofenfrisch', 804

    def vorbereiten(self):
        r = self.richtung
        self.x = self.aussen(-r)
        self.ox = self.vom_rand(0.05)
        self.x0 = self.vom_rand(0.16)
        self.pose_fest = {'sack': False}
        self.tuer = 0.0
        self.wackel = 0.0
        self.halt = {}               # Darsteller in der Hand: name -> 'vorn' / 'hinten'
        for name in ('k1', 'k2'):
            k = self.dazu(name, Lebkuchenmann, groesse=0.45)
            k.zeige_figur = False
            k.x, k.y = self.ox, self.boden
        self.riese = self.dazu('riese', Lebkuchenmann, groesse=2.3)
        self.riese.zeige_figur = False

    def tuer_punkt(self):
        return self.ox, self.boden - 40 * self.s

    # -- kleine Bausteine

    def heraus(self, name, weit):
        r, s = self.richtung, self.s
        return [Mit(name, Setze(zeige_figur=True, x=self.ox, y=self.boden - 30 * s, richtung=r)),
                Mit(name, Springe(lambda d: (d.sz.ox + r * weit * s, d.boden), 0.35, 50))]

    def hinein(self, name):
        return [Tu(lambda sz: sz.halt.pop(name, None)),
                Mit(name, Springe(lambda d: d.sz.tuer_punkt(), 0.35, 70)),
                Mit(name, Setze(zeige_figur=False))]

    def ablauf(self):
        r, s = self.richtung, self.s
        laufen = lambda name, tempo=1.6: Mit(name, Gehe(dauer=5, tempo=tempo))  # noqa: E731

        def wackeln(staerke):
            return Tu(lambda sz: setattr(sz, 'wackel', staerke))

        def zufrieden(sz, u):
            sz.neigung = -10
            sz.pose = Pose(arm_v=-35, arm_h=-40, arm_v_x=14, auge_zu=u < 0.9, sorge=0.9 * max(0.0, u - 0.9),
                           blick_x=-1 if u > 0.9 else 0, kopf_vorn=u > 1.3)
            sz.wackel = min(1.0, u / 1.6)

        def aufbeugen(d, u):
            d.neigung = 14 * min(1.0, u / 0.4)
            d.pose = Pose(mund_offen=u > 0.3, blick_y=0.6, arm_v=-60, arm_h=-30)

        return [
            Nebenbei(Stehe(1.3), wackeln(0.4)),
            Gehe(bis=self.x0, tempo=1.4),
            Setze(richtung=-r),
            Wandel(0.12, tuer=1.0), wackeln(0.0),
            *self.heraus('k1', 40),
            Nebenbei(Mit('k1', Gehe(bis=lambda d: d.sz.x - r * 38 * s, tempo=1.8))),
            Stehe(0.35, lambda sz, u: Pose(kopf_vorn=True, schreck=0.5, blick_y=0.6)),
            Mit('k1', Setze(striche=True, pose=Pose(schreck=1.0, kopf_vorn=True))),
            Mit('k1', Springe(lambda d: (d.x - r * 22 * s, d.boden), 0.25, 20)),
            Mit('k1', Setze(striche=False)),
            Stehe(0.3, Pose(arm_v=-25, arm_v_x=14, blick_y=0.6)),
            Tu(lambda sz: sz.halt.__setitem__('k1', 'vorn')),
            Stehe(0.35, lambda sz, u: Pose(arm_v=-25 - 120 * min(1.0, u / 0.3), arm_v_x=14)),
            *self.hinein('k1'),
            Wandel(0.1, tuer=0.0),
            Wandel(0.1, tuer=1.0),
            *self.heraus('k1', 30), *self.heraus('k2', 55),
            Nebenbei(laufen('k1', 1.7)), Nebenbei(laufen('k2', 1.2)),
            Springe(lambda sz: (sz.x - r * 34 * s, sz.boden), 0.35, 40),
            Tu(lambda sz: sz.fangen()),
            Stehe(0.35, Pose(arm_v=-80, arm_h=-80, arm_v_x=14, mund_offen=True)),
            Gehe(bis=lambda sz: sz.ox + r * 70 * s, tempo=0.8,
                 haltung=lambda p, sz: Pose(bein_v=p.bein_v, bein_h=p.bein_h, hub=p.hub, arm_v=-80, arm_h=-80,
                                            arm_v_x=14)),
            Stehe(0.2, Pose(arm_v=-140, arm_h=-130, arm_v_x=14)),
            Nebenbei(*self.hinein('k2')),
            *self.hinein('k1'),
            Wandel(0.1, tuer=0.0),
            Setze(richtung=r, x=lambda sz: sz.ox + r * 50 * s),
            Jeweils(1.2, zufrieden),
            Setze(neigung=0.0, wackel=0.0),
            Wandel(0.08, tuer=1.0),
            Tu(lambda sz: sz.knall()),
            Mit('riese', Springe(lambda d: (d.sz.ox + r * 70 * s, d.boden), 0.3, 30)),
            Springe(lambda sz: (sz.ox + r * 250 * s, sz.boden), 0.45, 60),
            Setze(richtung=-r),
            Nebenbei(Mit('riese', Jeweils(1.0, aufbeugen))),
            Stehe(0.7, lambda sz, u: Pose(blick_y=-1.0, schreck=min(1.0, u / 0.6), sorge=0.8, arm_v=-20,
                                         arm_v_x=14)),
            publikum(0.5, sorge=1.0, schreck=0.5),
            Setze(striche=True),
            Springe(lambda sz: (sz.ox - r * 30 * s, sz.boden), 0.75, 520),
            Setze(striche=False),
            Nebenbei(Mit('riese', Setze(neigung=0.0, richtung=-r)),
                     Mit('riese', Stehe(0.2, lambda d, u: Pose(blick_y=-0.5, schreck=0.6))),
                     Mit('riese', Stehe(0.8, lambda d, u: Pose(kopf_vorn=True, auge_zu=blinzeln(d.t)))),
                     Mit('riese', Springe(lambda d: d.sz.tuer_punkt(), 0.4, 60)),
                     Mit('riese', Setze(zeige_figur=False)),
                     Tu(lambda sz: setattr(sz, 'tuer', 0.0))),
            Renne(zum='rand', tempo=3.4),
            WarteNebenbei(),
        ]

    def schreck_ablauf(self):
        self.halt.clear()
        self.neigung = 0.0
        for k in (self.darsteller['k1'], self.darsteller['k2']):
            k.y = self.boden
        return self.schreck_alle()

    def fangen(self):
        self.nebenbei.clear()
        self.halt = {'k1': 'vorn', 'k2': 'hinten'}

    def knall(self):
        s = self.s
        x, y = self.tuer_punkt()
        self.streue(x, y, 40, DAMPF, tempo=260, dauer=1.3, r=(16, 40))
        rz = self.riese
        rz.zeige_figur, rz.x, rz.y, rz.richtung = True, self.ox, self.boden - 20 * s, self.richtung
        rz.pose = Pose(schreck=0.0, arm_v=-120, arm_h=-110)

    def weiter(self, dt):
        for name, wo in self.halt.items():
            k = self.darsteller[name]
            if wo == 'vorn':
                x, y = hand(self)
            else:
                w = math.radians(self.pose.arm_h)
                q = figur_trafo(self).map(QPointF(-10 - math.sin(w) * 56, -140 + math.cos(w) * 56))
                x, y = q.x(), q.y()
            k.x, k.y = x, y + 40 * self.s
            k.richtung = self.richtung
            k.pose = Pose(kopf_vorn=True, schreck=1.0, bein_v=math.sin(self.t * 30) * 30,
                          bein_h=-math.sin(self.t * 30) * 30, arm_v=-120, arm_h=-110)

    def zeichne_hinten(self, p):
        p.save()
        p.translate(self.ox, self.boden)
        p.scale(self.s, self.s)
        zeichne_ofen(p, self.tuer, self.wackel, self.t)
        p.restore()

    def grenzen_extra(self):
        s = self.s
        return QRectF(self.ox - 60 * s, self.boden - 120 * s, 120 * s, 120 * s)
