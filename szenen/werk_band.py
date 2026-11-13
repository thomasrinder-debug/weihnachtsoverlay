import math
import random

from PyQt6.QtCore import QRectF

from zeichnen.figur import Pose, renn_pose
from zeichnen.figuren import Wichtel, WichtelSteif
from zeichnen.grundlagen import SCHWARZ, WEISS, kreis
from zeichnen.werkstatt import PAKET_FARBEN, zeichne_foerderband, zeichne_kiste, zeichne_paeckchen

from .basis import WarteBis, Jeweils, Mit, Schritt, Setze, Springe, Stehe, Szene, Tu, Wandel, Warte, muetze_richten
from .werk_basis import Blick, schweiss, verpuffen

KB, KH = 96, 72          # Kiste


class Mitgerissen(Schritt):
    """Das Band reißt dem Wichtel die Füße weg: bäuchlings mitgenommen, über die Kante
    und im Bogen in die Kiste."""

    def beginn(self, sz):
        self.flug = None

    def weiter(self, sz, u, dt):
        w, r, s = sz.w, sz.richtung, sz.s
        if self.flug is None:
            w.x += r * sz.v * dt
            w.neigung = min(1.0, u / 0.12) * 85
            w.hopp = min(1.0, u / 0.12) * 14 * s
            w.pose = Pose(kopf_vorn=True, schreck=1.0, mund_offen=True, arm_v=-170, arm_h=-160,
                          bein_v=20, bein_h=35)
            if (w.x - sz.xb) * r >= 0:
                self.flug = (u, w.x, w.y)
            return
        u0, x0, y0 = self.flug
        f = min(1.0, (u - u0) / 0.42)
        w.x = x0 + (sz.kiste_x - x0) * f
        w.y = y0 + (sz.kiste_y - 40 * s - y0) * f - 110 * s * 4 * f * (1 - f)
        w.neigung = 85 + 120 * f
        w.pose = Pose(kopf_vorn=True, schreck=1.0, mund_offen=True, arm_v=-170, arm_h=-160,
                      bein_v=-30 * f, bein_h=40)

    def fertig(self, sz, u):
        return self.flug is not None and u - self.flug[0] >= 0.42


class KisteFaehrt(Schritt):
    """Die Kiste hüpft aufs Band und fährt mit ihm hinaus (oder flieht beim Schreck allein)."""

    def __init__(self, flucht=False):
        self.flucht = flucht

    def beginn(self, sz):
        self.x0, self.y0 = sz.kiste_x, sz.kiste_y
        self.ziel_x = sz.xb - sz.richtung * 70 * sz.s
        self.seite = -1 if sz.kiste_x - sz.geo.left() < sz.geo.right() - sz.kiste_x else 1

    def weiter(self, sz, u, dt):
        s = sz.s
        if self.flucht:
            sz.kiste_x += self.seite * sz.tempo * 3.5 * min(1.0, u * 4) * dt
            sz.kiste_y = sz.boden - abs(math.sin(u * 14)) * 22 * s
            sz.kiste_dreh = math.sin(u * 14) * 8
            return
        if u < 0.45:
            f = u / 0.45
            sz.kiste_x = self.x0 + (self.ziel_x - self.x0) * f
            sz.kiste_y = self.y0 + (sz.band_y - self.y0) * f - 90 * s * 4 * f * (1 - f)
            sz.kiste_dreh = -sz.richtung * 20 * math.sin(math.pi * f)
        else:
            sz.kiste_y = sz.band_y
            sz.kiste_x += sz.richtung * sz.v * dt
            sz.kiste_dreh = math.sin(u * 9) * 3

    def fertig(self, sz, u):
        return not QRectF(sz.kiste_x - 60 * sz.s, sz.kiste_y - 90 * sz.s, 120 * sz.s, 90 * sz.s).intersects(sz.geo)


class Fliessband(Szene):
    """Wichtel am Fließband: die Päckchen kommen immer schneller, er wirft sie hektisch in die Kiste
    hinter sich, dann rennt er auf dem Band zum Schaltkasten und kommt nicht vom Fleck. Das Band
    stoppt, er verschnauft und richtet die Mütze. Dann Vollgas: es reißt ihn von den Füßen und
    schleudert ihn in die Kiste, Deckel zu, nur die Mützenspitze schaut heraus."""
    name, titel, reihenfolge = 'werk_band', 'Fließband im Vollgas', 900

    def vorbereiten(self):
        self.zeige_figur = False
        r, s = self.richtung, self.s
        rand = self.geo.left() if r > 0 else self.geo.right()
        self.xb = self.vom_rand(0.15)
        xa = rand - r * 20 * s
        self.band_links = min(xa, self.xb)
        self.band_l = abs(self.xb - xa) / s
        self.xa = xa
        self.band_y = self.boden - 46 * s
        self.post = self.xb + r * 34 * s
        self.kiste_x, self.kiste_y, self.kiste_dreh = self.xb + r * 112 * s, self.boden, 0.0
        self.deckel, self.drin, self.spaehen = 112.0, False, 0.0
        self.v, self.lauf = 0.0, 0.0
        self.iv, self.naechst, self.fangen = None, 0.0, False
        self.wurf_t = -9.0
        self.pakete, self.stapel = [], 0
        self.weg = False
        self.w = self.dazu('w', WichtelSteif, groesse=0.6, knick=1.0)
        self.w.richtung = r
        self.w.x, self.w.y = rand - r * 60 * s, self.band_y

    # -- Ablauf

    def ablauf(self):
        r, s = self.richtung, self.s

        def arbeiten(sz, u, hektik=0.0):
            w = sz.w
            a = sz.t - sz.wurf_t
            if a < 0.35:
                f = a / 0.35
                w.pose = Pose(arm_v=-60 - 150 * f, arm_h=-50 - 140 * f, arm_v_x=6, kopf_vorn=hektik > 0.5,
                              sorge=hektik, mund_offen=hektik > 0.3, bein_v=-8, bein_h=8)
            else:
                z = math.sin(sz.t * (6 + 20 * hektik))
                w.pose = Pose(arm_v=-55 + 25 * z * hektik, arm_h=-45 - 25 * z * hektik, sorge=hektik,
                              kopf_vorn=hektik > 0.5, schreck=max(0.0, hektik - 0.6),
                              mund_offen=hektik > 0.3, bein_v=-12 * z * hektik, bein_h=12 * z * hektik,
                              auge_zu=hektik < 0.1 and (sz.t % 3.4) < 0.14)
            if hektik > 0.4 and random.random() < 0.08:
                schweiss(sz, w.x, w.y - 115 * s)

        def steigern(sz, u):
            f = u / 2.2
            sz.v = sz.tempo * (0.9 + 1.2 * f * f)
            sz.iv = 0.6 - 0.42 * f
            arbeiten(sz, u, min(1.0, 0.2 + f))

        def laufband(sz, u):
            w = sz.w
            w.phase += 0.5
            w.pose = renn_pose(w.phase)
            w.pose.kopf_vorn = 0.7 < u < 1.0
            w.pose.sorge = 1.0
            w.pose.arm_v = -100 + 15 * math.sin(u * 30)
            w.neigung = 22
            w.x += r * 0.12 * sz.tempo * (1 / 60)
            if random.random() < 0.5:
                sz.streue(w.x + r * 8 * s, sz.band_y - 4 * s, 1, WEISS, tempo=70, dauer=0.4, r=(3, 6),
                          richtung=(0.0 if r > 0 else math.pi), streuung=0.5)
            if random.random() < 0.15:
                schweiss(sz, w.x, w.y - 120 * s)

        def keuchen(sz, u):
            sz.w.pose = Pose(arm_v=-20, arm_h=-15, hub=2 * math.sin(u * 16), mund_offen=(u * 8) % 2 < 1,
                             kopf_vorn=True, sorge=0.6, auge_zu=True)

        def wackeln(sz, u):
            sz.kiste_dreh = 7 * math.sin(u * 32) * max(0.0, 1 - u / 0.6)
            sz.kiste_y = sz.boden - abs(math.sin(u * 16)) * 8 * s * max(0.0, 1 - u / 0.6)

        return [
            Setze(v=self.tempo * 1.5, iv=0.55, naechst=0.2),
            Mitreiten(),
            Setze(v=self.tempo * 0.9),
            Mit('w', Springe(nach=(self.post, self.boden), dauer=0.4, hoehe=40)),
            Mit('w', Setze(richtung=-r, pose=Pose())),
            Setze(iv=0.6, fangen=True),
            Jeweils(1.2, lambda sz, u: arbeiten(sz, u)),
            Jeweils(2.2, steigern),
            Setze(iv=None),
            Jeweils(0.3, lambda sz, u: arbeiten(sz, u, 1.0)),
            Setze(fangen=False),
            Mit('w', Springe(nach=(self.xb - r * 50 * s, self.band_y), dauer=0.45, hoehe=95)),
            Mit('w', Setze(richtung=-r)),
            Jeweils(1.1, laufband),
            Setze(v=0.0),
            Mit('w', Setze(neigung=32, pose=Pose(arm_v=-150, arm_h=-140, mund_offen=True, kopf_vorn=True,
                                                 schreck=0.7))),
            Warte(0.18),
            Mit('w', Wandel(0.15, neigung=0.0)),
            Jeweils(0.3, lambda sz, u: keuchen(sz, u)),
            *muetze_richten('w', 1.2),
            Mit('w', Blick(0.45)),
            Setze(v=self.tempo * 3.2),
            Mitgerissen(),
            Mit('w', Setze(zeige_figur=False)),
            Setze(drin=True),
            Wandel(0.1, deckel=0.0),
            Tu(lambda sz: sz.streue(sz.kiste_x, sz.kiste_y - 70 * s, 8, WEISS, tempo=90, dauer=0.5)),
            Setze(v=0.0),
            Jeweils(0.6, wackeln),
            Wandel(0.2, deckel=22.0),
            Jeweils(0.85, lambda sz, u: setattr(sz, 'spaehen', 1.0 - (0.3 < u < 0.42))),
            Setze(spaehen=0.0),
            Wandel(0.12, deckel=0.0),
            Setze(v=-self.tempo * 3.0),
            KisteFaehrt(),
            Tu(lambda sz: sz.aufraeumen()),
            WarteBis(lambda sz: not sz.wolke),
        ]

    def aufraeumen(self):
        s = self.s
        verpuffen(self, self.band_links + self.band_l * s / 2, self.boden, self.band_l * s, 60 * s, 24)
        self.weg = True
        self.pakete.clear()

    def schreck_ablauf(self):
        self.nebenbei.clear()
        self.iv, self.fangen = None, False
        if self.drin:
            self.deckel = 0.0
            self.spaehen = 0.0
            return [KisteFaehrt(flucht=True)]
        s = self.s
        verpuffen(self, self.band_links + self.band_l * s / 2, self.boden, self.band_l * s, 60 * s, 24)
        verpuffen(self, self.kiste_x, self.boden, KB * s, KH * s, 10)
        self.weg = True
        self.pakete.clear()
        w = self.w
        w.neigung, w.hopp, w.y = 0.0, 0.0, self.boden
        return self.schreck_alle(weihnachtsmann=False)

    # -- Päckchen

    def weiter(self, dt):
        r, s = self.richtung, self.s
        self.lauf += self.v * dt
        if self.weg:
            return
        if self.iv and self.t >= self.naechst:
            self.naechst = self.t + self.iv
            self.pakete.append({'x': self.xa, 'y': self.band_y, 'farbe': random.choice(PAKET_FARBEN),
                                'art': 'band', 'dreh': 0.0})
        for pk in list(self.pakete):
            if pk['art'] == 'band':
                pk['x'] += r * self.v * dt
                if (pk['x'] - self.xb) * r >= -12 * s:
                    frei = self.t - self.wurf_t > 0.3
                    if self.fangen and frei or self.stapel >= 3:
                        if self.fangen and frei:
                            self.wurf_t = self.t
                        ziel = (self.kiste_x, self.kiste_y - KH * s)
                    else:
                        ziel = (self.xb + r * 14 * s, self.boden - self.stapel * 26 * s)
                        self.stapel += 1
                    pk.update(art='flug' if ziel[0] == self.kiste_x else 'fall', t0=self.t,
                              x0=pk['x'], y0=pk['y'], x1=ziel[0], y1=ziel[1],
                              drall=random.uniform(-1, 1) * 300)
            elif pk['art'] in ('flug', 'fall'):
                dauer = 0.45 if pk['art'] == 'flug' else 0.3
                f = min(1.0, (self.t - pk['t0']) / dauer)
                bogen = 120 * s if pk['art'] == 'flug' else 10 * s
                pk['x'] = pk['x0'] + (pk['x1'] - pk['x0']) * f
                pk['y'] = pk['y0'] + (pk['y1'] - pk['y0']) * f - bogen * 4 * f * (1 - f)
                pk['dreh'] = pk['drall'] * f if pk['art'] == 'flug' else r * 8 * f
                if f >= 1:
                    if pk['art'] == 'flug':
                        self.pakete.remove(pk)
                    else:
                        pk['art'] = 'stapel'
            if pk in self.pakete and not QRectF(pk['x'] - 40 * s, pk['y'] - 80 * s, 80 * s, 80 * s).intersects(self.geo) \
                    and pk['art'] == 'band' and (pk['x'] - self.xa) * r > 10 * s:
                self.pakete.remove(pk)

    # -- Zeichnen

    def paket(self, p, pk):
        p.save()
        p.translate(pk['x'], pk['y'])
        p.rotate(pk['dreh'])
        p.scale(self.s, self.s)
        zeichne_paeckchen(p, 30, 24, pk['farbe'])
        p.restore()

    def zeichne_hinten(self, p):
        if self.weg:
            return
        p.save()
        p.translate(self.band_links, self.boden)
        p.scale(self.s, self.s)
        zeichne_foerderband(p, self.band_l, self.lauf / self.s * self.richtung)
        p.restore()
        for pk in self.pakete:
            if pk['art'] in ('band', 'stapel', 'fall'):
                self.paket(p, pk)

    def zeichne_vorn(self, p):
        s, r = self.s, self.richtung
        if not self.weg:
            for pk in self.pakete:
                if pk['art'] == 'flug':
                    self.paket(p, pk)
        if self.weg and not self.drin:
            return
        p.save()
        p.translate(self.kiste_x, self.kiste_y)
        p.rotate(self.kiste_dreh)
        p.scale(-r * s, s)
        zeichne_kiste(p, KB, KH, self.deckel)
        if self.drin:
            p.save()
            p.setClipRect(QRectF(-80, -140, 160, 140 - KH - 7))
            p.scale(0.6, 0.6)
            Wichtel.steife_muetze(p, 6, -(KH + 2) / 0.6 + 26, 1.0)
            p.restore()
        if self.spaehen > 0 and self.deckel > 8:
            for dx in (-16, -4):
                p.setBrush(WEISS)
                kreis(p, 30 + dx, -KH - 6, 4.2)
                p.setBrush(SCHWARZ)
                p.drawEllipse(QRectF(30 + dx - 1.6, -KH - 6 - 3.2 * self.spaehen + 0.8, 3.2, 3.2 * self.spaehen))
        p.restore()

    def grenzen_extra(self):
        s = self.s
        k = QRectF()
        if not self.weg:
            k = QRectF(self.band_links - 4 * s, self.boden - 60 * s, (self.band_l + 8) * s, 64 * s)
            for pk in self.pakete:
                k = k.united(QRectF(pk['x'] - 32 * s, pk['y'] - 70 * s, 64 * s, 76 * s))
        if not self.weg or self.drin:
            k = k.united(QRectF(self.kiste_x - 70 * s, self.kiste_y - 160 * s, 140 * s, 164 * s))
        return k


class Mitreiten(Schritt):
    """Der Wichtel steht mit verschränkten Armen auf dem Band und lässt sich bis ans Ende fahren."""

    def weiter(self, sz, u, dt):
        w = sz.w
        w.x += sz.richtung * sz.v * dt
        w.pose = Pose(arm_v=-25, arm_h=-35, kopf_vorn=u > 0.5, auge_zu=u > 0.5, blick_y=-0.3)

    def fertig(self, sz, u):
        return (sz.w.x - (sz.xb - sz.richtung * 30 * sz.s)) * sz.richtung >= 0
