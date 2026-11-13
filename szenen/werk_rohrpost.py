import math
import random

from PyQt6.QtCore import QRectF
from PyQt6.QtGui import QColor

from zeichnen.figur import Pose
from zeichnen.werkstatt import PAKET_FARBEN, zeichne_kapsel, zeichne_korb, zeichne_rohrpost

from .basis import Gehe, Jeweils, Schritt, Setze, Stehe, Szene, Tu, Warte
from .werk_basis import STAUB, Blick, greife, haenge_an, schweiss, verpuffen, welt

MUND = 140
KB, KH = 92, 54
RIESE = 110
STERNE = (QColor('#FFE38F'), QColor('#FFF4C2'))
G = 1500


class Rohrpost(Szene):
    """Am Rand hängt ein Rohrpostrohr. Kapseln mit Wunschzetteln plumpsen in den Korb, immer
    schneller, eine trifft den Weihnachtsmann am Kopf. Es rumpelt, eine Riesenkapsel steckt im
    Trichter fest. Er zieht, stemmt sich dagegen, hält inne: Schlupp, die Kapsel saust ins Rohr
    und nimmt ihn mit. Eine Beule wandert das Rohr hinauf, Stille, dann schießt er kopfüber in den
    Korb; die Riesenkapsel landet ordentlich auf seinen Stiefelsohlen."""
    name, titel, reihenfolge = 'werk_rohrpost', 'Wunschzettel-Rohrpost', 906

    def vorbereiten(self):
        r, s = self.richtung, self.s
        self.r0 = r
        rand = self.geo.left() if r > 0 else self.geo.right()
        self.xr = rand + r * 24 * s
        self.oben = -(self.boden - self.geo.top()) / s - 5
        self.mx, self.my = self.xr + r * 48 * s, self.boden - MUND * s
        self.xk = self.xr + r * 62 * s
        self.x = self.aussen(-r)
        self.pose_fest = {'sack': False}
        self.kapseln, self.im_korb = [], []
        self.riese = None
        self.beule, self.beule_y, self.wackeln = 0.0, 0.0, 0.0
        self.weg = False

    def griff(self):
        return self.riese['x'] + self.r0 * RIESE / 2 * self.s, self.riese['y']

    def schiesse(self, ziel, dauer=0.45, laenge=34, farbe=None, riese=False):
        zx, zy = ziel
        vx = (zx - self.mx) / dauer
        vy = (zy - self.my - 0.5 * G * self.s * dauer ** 2) / dauer
        k = {'x': self.mx, 'y': self.my, 'vx': vx, 'vy': vy, 'dreh': 0.0, 'vd': self.r0 * 300,
             'laenge': laenge, 'farbe': farbe or random.choice(PAKET_FARBEN), 'rest': dauer, 'ziel': ziel,
             'art': 'riese' if riese else 'korb'}
        self.kapseln.append(k)
        self.streue(self.mx, self.my, 4, STAUB, tempo=60, dauer=0.4, r=(3, 6))
        return k

    def ablauf(self):
        r, s = self.richtung, self.s
        xs = self.xr + r * 200 * s
        korb = (self.xk, self.boden - 30 * s)

        def kopf(sz):
            return welt(sz, 12, -205)

        def nicken(sz, u):
            sz.pose = Pose(sack=False, kopf_vorn=False, blick_y=0.4 + 0.3 * math.sin(u * 10),
                           arm_v=-20, arm_h=-10, auge_zu=(sz.t % 3.4) < 0.14)

        def schuss_kopf(sz):
            k = sz.schiesse(kopf(sz), 0.4)
            k['art'] = 'kopf'

        def getroffen(sz, u):
            f = math.sin(min(1.0, u / 0.5) * math.pi)
            sz.neigung = -14 * f
            sz.pose = Pose(sack=False, kopf_vorn=True, auge_zu=u < 0.6, schreck=0.0, sorge=0.8,
                           arm_v=-170, arm_h=-20, arm_v_x=4, mund_offen=u < 0.3)
            if random.random() < 0.25 and u < 0.6:
                x, y = kopf(sz)
                sz.streue(x + math.cos(sz.t * 9) * 26 * s, y - 10 * s, 1, STERNE, tempo=10, dauer=0.5,
                          r=(4, 7), art='stern')

        def rumpeln(sz, u):
            sz.wackeln = 0.3 + u
            sz.beule = min(1.0, u * 3)
            sz.beule_y = sz.oben + (-MUND - 60 - sz.oben) * (u / 1.2)
            sz.pose = Pose(sack=False, kopf_vorn=u > 0.6, blick_y=-0.8 if u < 0.6 else 0.0, sorge=min(1.0, u),
                           arm_v=-30, arm_h=-20, auge_zu=0.8 < u < 0.9)

        def steckt(sz):
            sz.beule, sz.wackeln = 0.0, 0.4
            sz.riese = {'x': sz.mx + r * 40 * s, 'y': sz.my, 'dreh': 0.0, 'art': 'steckt'}
            sz.streue(sz.mx, sz.my, 10, STAUB, tempo=110, dauer=0.5)

        def zerren(staerke):
            def f(sz, u):
                k = abs(math.sin(u * 7)) * staerke
                sz.pose = Pose(sack=False, arm_h=-80, bein_v=-28 - 50 * (staerke > 1), bein_h=24,
                               kopf_vorn=staerke > 1, sorge=1.0, mund_offen=True, hub=-2 * k)
                greife(sz, *sz.griff(), neigung=-6 - 8 * k)
                sz.riese['x'] = sz.mx + r * (40 + 3 * k) * s
                if staerke > 1 and random.random() < 0.12:
                    schweiss(sz, *kopf(sz))
            return f

        def halten(sz, u):
            sz.pose = Pose(sack=False, arm_h=-80, bein_v=-24, bein_h=24, kopf_vorn=True,
                           auge_zu=0.3 < u < 0.45 or 0.8 < u < 0.95, sorge=0.3)
            greife(sz, *sz.griff(), neigung=-6)

        def eingesaugt(sz, u):
            f = min(1.0, u / 0.4)
            sz.riese['x'] = sz.mx + r * (40 - 380 * f * f) * s
            sz.pose = Pose(sack=False, arm_h=-170, bein_v=30, bein_h=45, kopf_vorn=False, schreck=1.0,
                           mund_offen=True, wipp=10)
            sz.neigung = min(1.0, u / 0.08) * 80
            sz.stauchen = 1.0 + 0.25 * min(1.0, u / 0.1)
            sz.pose.arm_v = -178
            haenge_an(sz, *sz.griff())
            sz.wackeln = 1.0
            if f >= 1:
                sz.zeige_figur = False

        def hinauf(sz, u):
            sz.beule = 1.0
            sz.beule_y = -MUND - 40 + (sz.oben + 40 - (-MUND - 40)) * min(1.0, u / 0.7)
            sz.wackeln = 0.6

        def herab(sz, u):
            sz.beule = 1.0
            sz.beule_y = sz.oben + 40 + (-MUND - 50 - sz.oben - 40) * min(1.0, u / 0.3)
            sz.wackeln = 1.0

        class Hinaus(Schritt):
            dauer = 0.5

            def beginn(self, sz):
                sz.beule = 0.0
                sz.zeige_figur, sz.richtung, sz.stauchen = True, r, 1.0
                sz.hopp = 0.0
                self.x0, self.y0 = sz.mx - r * 230 * s, sz.my + 0 * s
                self.x1, self.y1 = sz.xk, sz.boden - (KH + 64) * s

            def weiter(self, sz, u, dt):
                f = min(1.0, u / self.dauer)
                sz.x = self.x0 + (self.x1 - self.x0) * f
                sz.y = self.y0 + (self.y1 - self.y0) * f - 70 * s * 4 * f * (1 - f)
                sz.neigung = 90 + 90 * f
                sz.pose = Pose(sack=False, arm_v=-178, arm_h=-170, bein_v=-10, bein_h=10, schreck=1.0,
                               mund_offen=True)

            def ende(self, sz):
                sz.streue(sz.xk, sz.boden - KH * s, 14, STAUB, tempo=120, dauer=0.6)
                sz.wackeln = 0.0

        def strampeln(sz, u):
            z = math.sin(u * 22)
            ruhig = sz.riese and sz.riese['art'] == 'liegt'
            sz.pose = Pose(sack=False, arm_v=-178, arm_h=-170, bein_v=-14 + (0 if ruhig else 22 * z),
                           bein_h=14 - (0 if ruhig else 22 * z))

        def riese_raus(sz):
            sz.riese = None
            sz.schiesse((sz.xk, sz.y - 9 * s), 0.5, RIESE, QColor('#D3172E'), riese=True)

        return [
            Gehe(bis=xs, tempo=1.5),
            Setze(richtung=-r),
            Tu(lambda sz: sz.schiesse(korb)),
            Jeweils(0.5, nicken),
            Tu(lambda sz: sz.schiesse((sz.xk - r * 12 * s, korb[1]), 0.35)),
            Jeweils(0.22, nicken),
            Tu(schuss_kopf),
            Jeweils(0.4, lambda sz, u: setattr(sz, 'pose', Pose(sack=False, kopf_vorn=False, blick_y=-0.3,
                                                                arm_v=-30))),
            Jeweils(0.75, getroffen),
            Setze(neigung=0.0),
            Jeweils(1.2, rumpeln),
            Tu(steckt),
            Stehe(0.3, Pose(sack=False, kopf_vorn=True, schreck=1.0, arm_v=-120, arm_h=-110)),
            Gehe(bis=lambda sz: sz.griff()[0] + r * 75 * s, tempo=0.9),
            Setze(richtung=-r),
            Jeweils(0.55, zerren(1.0)),
            Jeweils(0.65, zerren(1.6)),
            Jeweils(0.7, halten),
            Jeweils(0.4, eingesaugt),
            Setze(zeige_figur=False, stauchen=1.0, neigung=0.0),
            Jeweils(0.7, hinauf),
            Setze(beule=0.0, wackeln=0.15),
            Warte(0.55),
            Jeweils(0.3, herab),
            Hinaus(),
            Jeweils(0.35, strampeln),
            Tu(riese_raus),
            Jeweils(1.1, strampeln),
            Tu(lambda sz: sz.aufraeumen()),
            Setze(zeige_figur=False),
            Warte(0.6),
        ]

    def aufraeumen(self):
        s = self.s
        verpuffen(self, self.xk, self.boden, KB * s, KH * s, 10)
        verpuffen(self, self.xr, self.boden, 50 * s, MUND * s, 14)
        self.weg = True
        self.kapseln.clear()
        self.im_korb.clear()
        self.riese = None

    def schreck_ablauf(self):
        self.nebenbei.clear()
        sichtbar = self.zeige_figur and self.figur_sichtbar()
        kopfueber = self.neigung > 60
        self.aufraeumen()
        self.neigung, self.hopp, self.stauchen, self.y = 0.0, 0.0, 1.0, self.boden
        if not sichtbar or kopfueber:
            self.zeige_figur = False
            return [Warte(0.6)]
        return self.schreck_alle()

    def weiter(self, dt):
        s = self.s
        self.wackeln = max(0.0, self.wackeln - dt * 0.4) if self.beule == 0 else self.wackeln
        for k in list(self.kapseln):
            k['vy'] += G * s * dt
            k['x'] += k['vx'] * dt
            k['y'] += k['vy'] * dt
            k['dreh'] += k['vd'] * dt
            k['rest'] -= dt
            if k['art'] == 'abprall':
                if k['y'] > self.boden + 40 * s:
                    self.kapseln.remove(k)
                continue
            if k['rest'] <= 0:
                self.kapseln.remove(k)
                x, y = k['ziel']
                if k['art'] == 'korb':
                    self.im_korb.append((x - self.xk, random.uniform(-25, 25), k['farbe']))
                    self.streue(x, self.boden - KH * s, 3, STAUB, tempo=50, dauer=0.4, r=(3, 6))
                elif k['art'] == 'kopf':
                    k.update(art='abprall', vx=-k['vx'] * 0.4, vy=-260 * s, rest=9)
                    self.kapseln.append(k)
                    self.streue(x, y, 6, STERNE, tempo=120, dauer=0.6, r=(4, 7), art='stern')
                elif k['art'] == 'riese':
                    self.riese = {'x': x, 'y': y, 'dreh': 0.0, 'art': 'liegt'}

    def zeichne_hinten(self, p):
        if self.weg:
            return
        s = self.s
        p.save()
        p.translate(self.xk, self.boden)
        p.scale(s, s)
        zeichne_korb(p, KB, KH, vorn=False)
        for dx, w, farbe in self.im_korb:
            p.save()
            p.translate(dx / s, -KH + 4)
            p.rotate(w)
            zeichne_kapsel(p, 34, farbe)
            p.restore()
        p.restore()
        if self.riese and self.riese['art'] == 'steckt':
            self.kapsel(p, self.riese['x'], self.riese['y'], RIESE, QColor('#D3172E'), 0.0)

    def kapsel(self, p, x, y, laenge, farbe, dreh):
        p.save()
        p.translate(x, y)
        p.scale(self.s, self.s)
        zeichne_kapsel(p, laenge, farbe, dreh)
        p.restore()

    def zeichne_vorn(self, p):
        s, r = self.s, self.r0
        if self.weg:
            for k in self.kapseln:
                self.kapsel(p, k['x'], k['y'], k['laenge'], k['farbe'], k['dreh'])
            return
        for k in self.kapseln:
            self.kapsel(p, k['x'], k['y'], k['laenge'], k['farbe'], k['dreh'])
        p.save()
        p.translate(self.xr, self.boden)
        p.scale(r * s, s)
        zeichne_rohrpost(p, self.oben, MUND, self.beule, self.beule_y, self.wackeln)
        p.restore()
        p.save()
        p.translate(self.xk, self.boden)
        p.scale(s, s)
        zeichne_korb(p, KB, KH)
        p.restore()
        if self.riese and self.riese['art'] == 'liegt':
            self.kapsel(p, self.riese['x'], self.riese['y'], RIESE, QColor('#D3172E'), 0.0)

    def grenzen_extra(self):
        s = self.s
        if self.weg:
            k = QRectF()
        else:
            a, b = sorted((self.xr - 40 * self.r0 * s, self.xk + self.r0 * 60 * s))
            k = QRectF(a, self.geo.top(), b - a, self.boden - self.geo.top())
        for kp in self.kapseln:
            k = k.united(QRectF(kp['x'] - kp['laenge'] * s, kp['y'] - kp['laenge'] * s,
                                2 * kp['laenge'] * s, 2 * kp['laenge'] * s))
        if self.riese:
            k = k.united(QRectF(self.riese['x'] - RIESE * s, self.riese['y'] - 30 * s, 2 * RIESE * s, 60 * s))
        if self.zeige_figur and self.neigung > 20:
            k = k.united(QRectF(self.x - 300 * s, self.y - self.hopp - 300 * s, 600 * s, 600 * s))
        return k
