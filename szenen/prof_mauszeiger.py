import math

from PyQt6.QtCore import QRectF
from PyQt6.QtGui import QColor, QPainterPath

from zeichnen.figur import Pose
from zeichnen.figuren import Katze
from zeichnen.grundlagen import blinzeln, glatt
from zeichnen.labor import zeichne_labortisch, zeichne_maus_geraet, zeichne_monitor
from zeichnen.labor_e import zeichne_mauszeiger

from .basis import Erschrecke, Falle, Gehe, Renne, Jeweils, Mit, Nebenbei, Schaue, Setze, Springe, Stehe, Tu, Warte, WarteNebenbei
from .professor import ziehen
from .prof_laptop import GeraetSzene, Hieb

G = 1.4
TISCH_H = 76
KATZE = 0.62


class Mauszeiger(GeraetSzene):
    """Der Mauszeiger hängt, ein Hieb auf den Monitor, und der Zeiger springt aus dem Bildschirm.
    Die Katze jagt ihn, er huscht zurück in den Schirm, die Katze springt hinterher und steckt
    mit dem Vorderteil im Bildschirm fest und strampelt."""
    name, titel, reihenfolge = 'mauszeiger', 'Mäusejagd', 89

    def vorbereiten(self):
        r = self.seite = self.richtung
        s = self.s
        self.tisch_x = self.vom_rand(0.13)
        self.stand = self.tisch_x - r * 98 * s
        self.zeiger = 'schirm'           # schirm, frei, aus
        self.zx, self.zy = 0.0, -50.0    # auf dem Schirm: Monitor-Einheiten; frei: Weltpunkt
        self.zg = 0.5
        self.beine = 0.0
        self.zphase = 0.0
        self.maus_dx = 0.0
        self.bild_an = 1.0
        self.kaputt = 0.0
        self.steckt = False
        k = self.k = self.dazu('katze', Katze, groesse=KATZE)
        k.sitzt = True
        k.x = self.aussen(-r) - r * 60 * s
        k.tempo = self.tempo * 1.1

    # -- Orte

    def monitor_ort(self):
        return self.tisch_x + self.seite * 14 * self.s + self.zitter(), self.boden - (TISCH_H + 8) * self.s

    def am_monitor(self, lx, ly):
        x, y = self.monitor_ort()
        return x + lx * G * self.s, y + ly * G * self.s

    def schirm_welt(self):
        x0, y0 = self.am_monitor(-27, -72)
        x1, y1 = self.am_monitor(27, -28)
        return QRectF(x0, y0, x1 - x0, y1 - y0)

    def maus_ort(self):
        return self.tisch_x - self.seite * (46 - self.maus_dx) * self.s, self.boden - (TISCH_H + 8) * self.s

    def zeiger_welt(self):
        if self.zeiger == 'schirm':
            return self.am_monitor(self.zx, self.zy)
        return self.zx, self.zy

    def katze_steckt_ort(self):
        """Die Katze taucht von der Seite in den Schirm: Kopf und Vorderbeine drin."""
        q = self.schirm_welt()
        k = self.k
        kopf_x = q.center().x() + self.seite * 20 * self.s
        return kopf_x - k.richtung * 44 * k.s, q.center().y() + 62 * k.s

    def weiter(self, dt):
        super().weiter(dt)
        if self.steckt and not self.erschreckt:
            k = self.k
            k.x, k.y = self.katze_steckt_ort()
            w = math.sin(self.t * 17)
            k.pose = Pose(bein_v=50 * w, bein_h=-50 * w)

    # -- Zeichnen

    def zeichne_requisiten(self, p):
        s = self.s
        p.save()
        p.translate(self.tisch_x, self.boden)
        p.scale(s, s)
        zeichne_labortisch(p, 140, TISCH_H)
        p.restore()
        mx, my = self.maus_ort()
        p.save()
        p.translate(mx, my)
        p.scale(s * 1.3, s * 1.3)
        zeichne_maus_geraet(p, 0, 0)
        p.restore()
        p.save()
        p.translate(*self.monitor_ort())
        p.scale(G * s, G * s)
        zeichne_monitor(p, 0, 0, self.bild_an, self.t, self.kaputt)
        p.restore()
        if self.zeiger == 'schirm':
            x, y = self.zeiger_welt()
            zeichne_mauszeiger(p, x, y, self.zg * G * s)

    def zeichne_davor(self, p):
        s = self.s
        if self.steckt:
            q = self.schirm_welt()
            aussen = QPainterPath()
            aussen.addRect(q.adjusted(-400 * s, -400 * s, 400 * s, 400 * s))
            innen = QPainterPath()
            innen.addRoundedRect(q, 8 * G * s, 8 * G * s)
            k = self.k
            k.zeige_figur = True
            p.save()
            p.setClipPath(aussen.subtracted(innen))
            k.zeichne(p)
            p.restore()
            p.save()                      # der Kopf leuchtet grünlich hinter dem Glas
            p.setClipPath(innen)
            p.setOpacity(0.55)
            k.zeichne(p)
            p.setOpacity(1.0)
            p.setBrush(QColor(90, 230, 150, 90))
            p.drawRect(q)
            p.restore()
            k.zeige_figur = False
            # Wellenring, wo die Katze ins Glas taucht
            p.setPen(QColor(220, 255, 235, 160))
            p.setBrush(QColor(0, 0, 0, 0))
            rx = q.right() if self.seite > 0 else q.left()
            w = 1 + 0.08 * math.sin(self.t * 9)
            p.drawEllipse(QRectF(rx - 6 * s * w, q.center().y() - 20 * s * w, 12 * s * w, 40 * s * w))
            p.setPen(QColor(0, 0, 0, 0))
        if self.zeiger == 'frei':
            zeichne_mauszeiger(p, self.zx, self.zy, self.zg * s * G, 0.0, self.beine, self.zphase)

    def requisiten_kasten(self):
        s = self.s
        k = QRectF(self.tisch_x - 80 * s, self.boden - (TISCH_H + 8 + 82 * G) * s, 160 * s,
                   (TISCH_H + 8 + 82 * G) * s)
        if self.zeiger == 'frei':
            k = k.united(QRectF(self.zx - 10 * s, self.zy - 10 * s, 50 * s, 60 * s))
        if self.steckt:
            k = k.united(self.k.kasten().adjusted(-10 * s, -10 * s, 10 * s, 10 * s))
        return k

    # -- Ablauf

    def ablauf(self):
        r, s = self.richtung, self.s
        self.x = self.aussen(-r)
        k_platz = self.tisch_x + r * 128 * s
        p1 = self.tisch_x + r * 215 * s
        p2 = self.tisch_x - r * 10 * s

        def maus_schieben(sz, u):
            sz.maus_dx = 6 * math.sin(u * 2.4)
            sz.zx = 18 * math.sin(u * 2.4)
            sz.zy = -50 + 10 * math.sin(u * 3.7)
            mx, my = sz.maus_ort()
            sz.pose = Pose(arm_v=sz.arm_zu(mx, my - 4 * s), blick_y=0.1, auge_zu=blinzeln(sz.t))
            kat = sz.k
            kat.pose = Pose(blick_x=0.6 * math.sin(u * 2.4), auge_zu=blinzeln(sz.t, 1.3))

        def ruetteln(sz, u):
            sz.maus_dx = 5 * math.sin(u * 30)
            mx, my = sz.maus_ort()
            sz.pose = Pose(arm_v=sz.arm_zu(mx, my - 4 * s) + 4 * math.sin(u * 30), sorge=0.8, blick_y=0.1)

        def getroffen(sz):
            sz.kaputt = 0.5
            sz.haare = 0.3
            x, y = sz.zeiger_welt()
            sz.zeiger, sz.zx, sz.zy = 'frei', x, y

        def bogen(von, nach, hoehe, g0, g1, beine):
            def f(sz, u, dauer):
                a = glatt(min(1.0, u / dauer))
                x0, y0 = von(sz) if callable(von) else von
                x1, y1 = nach(sz) if callable(nach) else nach
                sz.zx = x0 + (x1 - x0) * a
                sz.zy = y0 + (y1 - y0) * a - hoehe * s * math.sin(a * math.pi)
                sz.zg = g0 + (g1 - g0) * a
                sz.beine = beine
                sz.zphase += 0.5
            return f

        start = {}

        def merken(sz):
            start['p'] = (sz.zx, sz.zy)

        raus = bogen(lambda sz: start['p'], (p1, self.boden - 22 * s), 110, 0.5, 1.5, 0.0)
        flitz = bogen(lambda sz: start['p'], (p2, self.boden - 22 * s), 8, 1.5, 1.5, 1.0)
        rein = bogen(lambda sz: start['p'], lambda sz: sz.am_monitor(4, -54), 70, 1.5, 0.5, 1.0)

        def zurueck_auf_schirm(sz):
            sz.zeiger, sz.zx, sz.zy, sz.zg = 'schirm', 4, -54, 0.5

        def steckt(sz):
            sz.steckt = True
            sz.k.zeige_figur = False
            sz.k.neigung = 12
            sz.wackel = 1.0

        def frech(sz, u):
            q = 14 + 4 * math.sin(u * 5)
            sz.zx = -sz.seite * q
            sz.zy = -40 - 3 * abs(math.sin(u * 7))

        return [
            Nebenbei(Warte(0.4), Mit('katze', Gehe(bis=k_platz)), Mit('katze', Setze(richtung=-r))),
            Gehe(bis=self.stand),
            Setze(neigung=12),
            Jeweils(3.0, maus_schieben),
            Setze(zx=4, zy=-54),
            Jeweils(1.0, ruetteln),
            Setze(neigung=0),
            Schaue(0.8),
            Setze(richtung=r),
            Hieb(lambda sz: sz.am_monitor(0, -78), getroffen),
            Mit('katze', Setze(sitzt=False, richtung=r)),
            Tu(merken),
            Jeweils(0.6, lambda sz, u: raus(sz, u, 0.6)),
            Mit('katze', Stehe(0.5, lambda d, u: Pose(bein_v=-10, bein_h=10, hub=4))),
            Setze(beine=1.0),
            Nebenbei(Mit('katze', Springe(nach=(p1 - r * 40 * s, self.boden), dauer=0.6, hoehe=60))),
            Warte(0.3),
            Tu(merken),
            Jeweils(0.8, lambda sz, u: flitz(sz, u, 0.8)),
            WarteNebenbei(),
            Nebenbei(Mit('katze', Gehe(bis=p2 + r * 120 * s, tempo=2.4))),
            Tu(merken),
            Jeweils(0.6, lambda sz, u: rein(sz, u, 0.6)),
            Tu(zurueck_auf_schirm),
            WarteNebenbei(),
            Mit('katze', Setze(richtung=-r)),
            Mit('katze', Springe(nach=lambda d: d.sz.katze_steckt_ort(), dauer=0.45, hoehe=50)),
            Tu(steckt),
            Stehe(1.2, lambda sz, u: Pose(schreck=0.6, sorge=1.0, arm_v=-60, arm_h=-40)),
            Jeweils(1.8, frech),
            Schaue(1.4),
            Stehe(0.9, lambda sz, u: Pose(kopf_vorn=True, arm_v=-120, arm_h=-120, arm_v_x=16, sorge=0.6,
                                          auge_zu=blinzeln(sz.t))),
            Setze(mitnehmen=('tisch_x',)),
            Gehe(bis=self.aussen(-r) - r * 300 * s, haltung=ziehen),
        ]

    def schreck_ablauf(self):
        if not self.steckt:
            return self.schreck_rennen()
        # die Katze plumpst aus dem Schirm, hüpft und rennt
        self.steckt = False
        k = self.k
        k.zeige_figur, k.neigung = False, 0.0
        neu = self.schreck_rennen()
        k.zeige_figur = True
        return [Nebenbei(Mit('katze', Erschrecke(0.25, 20)), Mit('katze', Falle(lambda d: d.y >= d.sz.boden)),
                         Mit('katze', Setze(y=self.boden)), Mit('katze', Renne(zum='rand')))] + neu
