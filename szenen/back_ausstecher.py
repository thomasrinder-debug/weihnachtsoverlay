import math

from PyQt6.QtCore import QPointF, QRectF

from zeichnen.baeckerei import KRUEMEL, zeichne_ausstecher, zeichne_teigplatte, zeichne_teigstern
from zeichnen.figur import Pose
from zeichnen.figuren import Wichtel
from zeichnen.grundlagen import blinzeln

from .back_bausteine import publikum
from .basis import Gehe, Jeweils, Mit, Renne, Setze, Springe, Stehe, Szene, Tu, Wandel

R = 42            # Sternradius in Einheiten des Weihnachtsmanns
G = 0.9          # Größe des Wichtels


class BackAusstecher(Szene):
    """Der Wichtel will mit einer großen Sternform Plätzchen ausstechen. Drücken hilft nicht,
    Draufspringen auch nicht, der Teig federt wie ein Trampolin. Beim dritten, gewaltigen Sprung
    schleudert ihn der Teig hoch in die Luft; er landet genau in der Form, sticht sich selbst
    aus und stolziert mit Teigstern und Ausstecher als Ballettröckchen davon."""
    name, titel, reihenfolge = 'back_ausstecher', 'Ausstechform', 801

    def vorbereiten(self):
        r = self.richtung
        self.zeige_figur = False
        self.w = self.dazu('w', Wichtel, groesse=G)
        self.w.richtung = r
        self.tx = self.vom_rand(0.2)
        self.form = 'hand'           # 'hand', 'teig', 'rock'
        self.delle = 0.0             # Einsinken des Teigs (Einheiten)
        self.loch = False
        self.wackel = 0.0

    def auf_form(self):
        return self.boden - (12 + 9 + self.delle * 0.8) * self.s

    def ablauf(self):
        r, s, w = self.richtung, self.s, self.w
        tragen = lambda p, d: Pose(bein_v=p.bein_v, bein_h=p.bein_h, hub=p.hub, arm_v=-172, arm_h=-165,  # noqa
                                   auge_zu=p.auge_zu)

        def druecken(d, u):
            d.pose = Pose(arm_v=-75 + 8 * math.sin(u * 40), arm_h=-70, kopf_vorn=True, sorge=0.8,
                          auge_zu=u > 0.3, bein_v=-20, bein_h=25)
            d.neigung = 18
            d.sz.wackel = math.sin(u * 40)

        def stampfen(d, u):
            f = (u % 0.5) / 0.5
            d.hopp = math.sin(f * math.pi) * 34 * s * (1 + u)
            d.sz.delle = max(0.0, -math.sin(f * math.pi * 2)) * 8 if f > 0.5 else 0.0
            d.y = d.sz.auf_form()
            d.pose = Pose(arm_v=-150, arm_h=-140, bein_v=-25 * math.sin(f * math.pi), bein_h=25,
                          mund_offen=True, kopf_vorn=f > 0.5)

        def ducken(d, u):
            d.stauchen = 1 - 0.22 * min(1.0, u / 0.3)
            d.pose = Pose(arm_v=-20, arm_h=-30, bein_v=-30, bein_h=30, kopf_vorn=True, sorge=0.3,
                          auge_zu=0.45 < u < 0.6, blick_y=0.6)

        def katapult(d, u):
            # 0..0.3 hoch, 0.3..0.55 tief einsinken, dann weit hinauf und zurück
            sz = d.sz
            d.stauchen = 1.0
            if u < 0.35:
                f = u / 0.35
                d.hopp = math.sin(f * math.pi) * 70 * s
                sz.delle = 0.0
            elif u < 0.6:
                f = (u - 0.35) / 0.25
                d.hopp = 0
                sz.delle = math.sin(f * math.pi / 2) * 45
            else:
                f = min(1.0, (u - 0.6) / 1.4)
                sz.delle = 45 * max(0.0, 1 - (u - 0.6) / 0.12) - 8 * math.sin(min(1.0, (u - 0.6) / 0.4) * 9) * \
                    max(0.0, 1 - (u - 0.6) / 0.6)
                d.hopp = 4 * f * (1 - f) * 420 * s
            d.y = sz.auf_form()
            luft = u > 0.6
            d.pose = Pose(arm_v=-160 + (40 * math.sin(u * 25) if luft else 0), arm_h=-150,
                          bein_v=-30 if luft else -10, bein_h=40 if luft else 10, mund_offen=True,
                          kopf_vorn=luft, schreck=1.0 if luft else 0.0)

        def landen(sz):
            sz.form, sz.loch, sz.delle = 'rock', True, 0.0
            sz.w.hopp, sz.w.y = 0.0, sz.boden
            sz.streue(sz.tx, sz.boden - 10 * s, 14, KRUEMEL, tempo=150, r=(2, 4), schwer=True)

        return [
            Mit('w', Gehe(bis=self.tx - r * 75 * s, haltung=tragen)),
            Mit('w', Stehe(0.25, Pose(arm_v=-120, arm_h=-110))),
            Setze(form='teig'),
            Mit('w', Jeweils(1.0, druecken)),
            Mit('w', Setze(neigung=0.0)), Setze(wackel=0.0),
            Mit('w', Stehe(0.4, lambda d, u: Pose(kopf_vorn=True, sorge=0.6, auge_zu=blinzeln(d.t)))),
            Mit('w', Springe(lambda d: (d.sz.tx, d.sz.auf_form()), 0.4, 60)),
            Mit('w', Jeweils(1.0, stampfen)),
            Mit('w', Setze(hopp=0.0)), Setze(delle=0.0),
            Mit('w', Jeweils(0.7, ducken)),
            Mit('w', Jeweils(2.0, katapult)),
            Tu(landen),
            Mit('w', Stehe(0.5, Pose(blick_y=0.9, kopf_vorn=True, schreck=0.6, arm_v=-60, arm_h=-50))),
            Mit('w', publikum(1.1, arm_v=-120, arm_h=-110)),
            Mit('w', Setze(richtung=lambda d: d.naechster_rand())),
            Mit('w', Gehe(tempo=0.9, haltung=lambda p, d: Pose(
                bein_v=p.bein_v * 0.6, bein_h=p.bein_h * 0.6, hub=p.hub, arm_v=-150, arm_h=-140,
                auge_zu=True, wipp=p.wipp))),
        ]

    def schreck_ablauf(self):
        w = self.w
        if self.form == 'hand':
            self.form = 'teig'
        neu = [Setze(delle=0.0, wackel=0.0), Mit('w', Setze(hopp=0.0, neigung=0.0, stauchen=1.0))]
        if w.y < self.boden:
            neu.append(Mit('w', Springe(lambda d: (d.x - d.richtung * 40 * d.sz.s, d.boden), 0.3, 40)))
        return neu + self.schreck_alle(weihnachtsmann=False)

    def mitte_form(self):
        if self.form == 'hand':
            q = self.w.trafo().map(QPointF(12, -134 - R / G))
            return q.x(), q.y()
        return self.tx, self.boden - 12 * self.s - self.delle * self.s * 0.8

    def zeichne_hinten(self, p):
        s = self.s
        p.save()
        p.translate(self.tx, self.boden - 12 * s)
        p.scale(s, s)
        zeichne_teigplatte(p, 220, 12, (0, R) if self.loch else None, self.delle)
        p.restore()
        if self.form == 'teig':
            x, y = self.mitte_form()
            p.save()
            p.translate(x + self.wackel * 1.5 * s, y)
            p.scale(s, s)
            zeichne_ausstecher(p, R, flach=0.4)
            p.restore()

    def zeichne_vorn(self, p):
        if not self.w.zeige_figur:
            return
        if self.form == 'hand':
            x, y = self.mitte_form()
            p.save()
            p.translate(x, y)
            p.scale(self.s, self.s)
            zeichne_ausstecher(p, R)
            p.restore()
        elif self.form == 'rock':
            p.save()
            p.setTransform(self.w.trafo(), True)
            p.translate(0, -48)
            zeichne_teigstern(p, R / G, 0.4)
            zeichne_ausstecher(p, R / G, flach=0.4, rand=7)
            p.restore()

    def grenzen_extra(self):
        s = self.s
        k = QRectF(self.tx - 120 * s, self.boden - 70 * s, 240 * s, 70 * s)
        x, y = self.mitte_form()
        return k.united(QRectF(x - 60 * s, y - 60 * s, 120 * s, 120 * s))
