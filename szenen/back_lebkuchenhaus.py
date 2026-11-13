import math

from PyQt6.QtCore import QRectF

from zeichnen.baeckerei import GUSS, KRUEMEL, zeichne_dachplatte, zeichne_gussklecks, zeichne_lebkuchenplatte
from zeichnen.figur import Pose
from zeichnen.figuren import Wichtel
from zeichnen.grundlagen import ROT, ROT_DUNKEL, blinzeln, kreis, radial

from .back_bausteine import publikum
from .basis import Gehe, Jeweils, Mit, Setze, Stehe, Szene, Tu, Wandel

G = 0.9
B, H = 96, 80                     # Rückwand
DACH = math.hypot(B / 2 + 10, 50)
DACH_W = math.degrees(math.atan2(50, B / 2 + 10))
TUPFER = [(-48, -80), (48, -80), (-48, -40), (48, -40), (-48, -4), (48, -4), (0, -130), (-30, -108), (30, -108)]


class BackLebkuchenhaus(Szene):
    """Der Wichtel setzt das Dach auf sein Lebkuchenhaus, alles klappt flach zusammen. Beim zweiten
    Mal neigen sich die Wände, er hält sie mit ausgebreiteten Armen und kleistert alles mit
    Zuckerguss zu: es steht! Triumph. Zum Schluss setzt er vorsichtig ein Bonbon auf den First,
    das Haus sackt zusammen, und das Dach sitzt ihm als Hut auf dem Kopf."""
    name, titel, reihenfolge = 'back_lebkuchenhaus', 'Lebkuchenhaus', 805

    def vorbereiten(self):
        r = self.richtung
        self.zeige_figur = False
        self.w = self.dazu('w', Wichtel, groesse=G)
        self.w.richtung = r
        self.hx = self.vom_rand(0.15)
        self.aL = self.aR = 0.0      # Neigung der Seitenwände (Grad, nach außen)
        self.fh = 1.0                # Höhe der Rückwand (1 steht, klein: liegt)
        self.dach = 'hand'           # 'hand', 'auf', 'hut'
        self.dy = 0.0                # Dach sinkt um so viel
        self.spreiz = 0.0            # Dachplatten klappen um so viel flacher
        self.guss = 0.0
        self.bonbon = False

    def einsturz(self, dauer=0.3):
        return [Wandel(dauer, aL=88.0, aR=88.0, fh=0.12, dy=H - 8, spreiz=DACH_W),
                Tu(lambda sz: sz.streue(sz.hx, sz.boden - 20 * sz.s, 16, KRUEMEL, tempo=170, r=(2, 4.5),
                                        schwer=True))]

    def ablauf(self):
        r, s = self.richtung, self.s
        tragen = lambda p, d: Pose(bein_v=p.bein_v, bein_h=p.bein_h, hub=p.hub, arm_v=-172, arm_h=-165,  # noqa
                                   auge_zu=p.auge_zu)
        stand = self.hx - r * 92 * s

        def halten(d, u):
            d.pose = Pose(arm_v=-95, arm_h=-80, kopf_vorn=True, sorge=0.6, auge_zu=blinzeln(d.t),
                          bein_v=-15, bein_h=15)

        def kleistern(d, u):
            d.pose = Pose(arm_v=-95 + 25 * math.sin(u * 14), arm_h=-80, kopf_vorn=True, mund_offen=True,
                          auge_zu=(u * 3) % 1 < 0.15)
            d.sz.guss = min(1.0, u / 1.0)

        return [
            Mit('w', Gehe(bis=stand, haltung=tragen)),
            Setze(dach='auf', dy=-24.0),
            Wandel(0.3, dy=0.0),
            Mit('w', Stehe(0.35, Pose(arm_v=-30, arm_h=-20, auge_zu=True))),
            *self.einsturz(),
            Mit('w', Setze(striche=True, pose=Pose(kopf_vorn=True, schreck=1.0, arm_v=-120, arm_h=-110))),
            Mit('w', Stehe(0.3, Pose(kopf_vorn=True, schreck=1.0, arm_v=-120, arm_h=-110))),
            Mit('w', Setze(striche=False)),
            Mit('w', publikum(0.5, sorge=0.7)),
            Mit('w', Stehe(0.3, Pose(arm_v=-150, arm_h=-140, mund_offen=True))),
            Wandel(0.45, aL=0.0, aR=0.0, fh=1.0, dy=0.0, spreiz=0.0),
            Mit('w', Gehe(bis=stand - r * 20 * s, tempo=0.4, haltung=lambda p, d: Pose(
                bein_v=-p.bein_v, bein_h=-p.bein_h, arm_v=-40, arm_h=-30, kopf_vorn=True, sorge=0.5))),
            Wandel(0.6, aL=14.0, aR=14.0, dy=6.0),
            Mit('w', Gehe(bis=self.hx - r * 52 * s, tempo=2.2, haltung=lambda p, d: Pose(
                bein_v=p.bein_v * 1.5, bein_h=p.bein_h * 1.5, arm_v=-100, arm_h=-90, mund_offen=True))),
            Wandel(0.2, aL=0.0, aR=0.0, dy=0.0),
            Mit('w', Jeweils(1.0, kleistern)),
            Mit('w', Gehe(bis=stand, tempo=0.5, haltung=lambda p, d: Pose(
                bein_v=-p.bein_v, bein_h=-p.bein_h, arm_v=-60, arm_h=-50, kopf_vorn=True, sorge=0.3))),
            Mit('w', Stehe(0.6, Pose(arm_v=-160, arm_h=-150, bein_v=-14, bein_h=14, kopf_vorn=True,
                                     mund_offen=True))),
            Mit('w', publikum(0.6)),
            Mit('w', Gehe(bis=self.hx - r * 40 * s, tempo=0.6)),
            Mit('w', Stehe(0.35, lambda d, u: Pose(arm_v=-150, arm_v_x=10, auge_zu=True))),
            Setze(bonbon=True),
            Mit('w', Stehe(0.6, lambda d, u: Pose(arm_v=-150 + 100 * min(1.0, u / 0.3), kopf_vorn=True,
                                                 blick_y=-0.8, sorge=min(1.0, u / 0.4)))),
            Wandel(0.25, aL=-6.0, aR=-6.0, dy=4.0),
            Setze(dach='hut'),
            *self.einsturz(0.2),
            Mit('w', Wandel(0.12, stauchen=0.82)),
            Mit('w', Wandel(0.2, stauchen=1.0)),
            Mit('w', publikum(0.9)),
            Mit('w', Setze(richtung=lambda d: d.naechster_rand())),
            Mit('w', Gehe(tempo=1.0, haltung=lambda p, d: Pose(bein_v=p.bein_v, bein_h=p.bein_h, hub=p.hub,
                                                               arm_v=-90, arm_h=-80))),
        ]

    def schreck_ablauf(self):
        self.guss = min(self.guss, 1.0)
        if self.dach == 'hand':
            self.dach = 'auf'
        return [Mit('w', Setze(stauchen=1.0))] + self.schreck_alle(weihnachtsmann=False)

    # -- Zeichnen

    def zeichne_dach(self, p, dy=0.0, spreiz=0.0, bonbon=False):
        for z in (-1, 1):
            p.save()
            p.translate(z * (B / 2 + 10), -H + dy)
            p.scale(-z, 1)
            p.rotate(-(DACH_W - spreiz))
            zeichne_dachplatte(p, DACH)
            p.restore()
        if bonbon:
            p.setBrush(radial(-2, -H - 56 + dy, 7, ROT.lighter(150), ROT_DUNKEL))
            kreis(p, 0, -H - 54 + dy, 5)

    def zeichne_hinten(self, p):
        s = self.s
        p.save()
        p.translate(self.hx, self.boden)
        p.scale(s, s)
        p.save()
        p.scale(1, self.fh)
        zeichne_lebkuchenplatte(p, B, H, fenster=2, tuer=True)
        p.restore()
        for z, a in ((-1, self.aL), (1, self.aR)):
            p.save()
            p.translate(z * B / 2, 0)
            p.rotate(z * a)
            zeichne_lebkuchenplatte(p, 14, H)
            p.restore()
        if self.dach == 'auf':
            self.zeichne_dach(p, self.dy, self.spreiz, self.bonbon)
        if self.guss > 0:
            n = int(len(TUPFER) * self.guss + 0.5)
            for x, y in TUPFER[:n]:
                if self.fh < 0.5:
                    y = y * 0.12
                p.save()
                p.translate(x, y)
                zeichne_gussklecks(p, 7 * min(1.0, self.guss * 1.5))
                p.setBrush(GUSS)
                p.drawRoundedRect(QRectF(-2.5, 0, 5, 10 * self.guss), 2.5, 2.5)
                p.restore()
        p.restore()

    def zeichne_vorn(self, p):
        w = self.w
        if not w.zeige_figur or self.dach not in ('hand', 'hut'):
            return
        p.save()
        p.setTransform(w.trafo(), True)
        if self.dach == 'hand':
            p.translate(14, -60)
            p.scale(0.8 / G, 0.8 / G)
        else:
            p.translate(4, -34)
            p.scale(1.05 / G, 1.05 / G)
        self.zeichne_dach(p, bonbon=self.dach == 'hut')
        p.restore()

    def grenzen_extra(self):
        s = self.s
        k = QRectF(self.hx - 140 * s, self.boden - 160 * s, 280 * s, 160 * s)
        if self.w.zeige_figur and self.dach in ('hand', 'hut'):
            k = k.united(self.w.kasten().adjusted(-30 * s, -50 * s, 30 * s, 0))
        return k
