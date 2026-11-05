import math
import random

from PyQt6.QtCore import QPointF, QRectF
from PyQt6.QtGui import QPainterPath

from zeichnen.figur import Pose
from zeichnen.figuren import GRAU, Katze
from zeichnen.grundlagen import bildstueck, blinzeln, glatt, zeichne_teilchen

from .basis import Gehe, Jeweils, Mit, Renne, Setze, Stehe, Szene, Tu, Wandel, Warte


class Buchstabe:
    """Ein Stück der Zeile (meist ein Buchstabe), das hüpfen, kippen und den Platz wechseln kann."""

    def __init__(self, rechteck):
        self.heim = rechteck
        self.platz = rechteck.center().x()      # Ziel-Mitte, ändert sich beim Vertauschen
        self.x = self.platz
        self.dy = self.vy = 0.0
        self.w = self.vw = 0.0


class Tippkatze(Szene):
    """Kurz nach dem Tippen: Zwischen zwei Wörtern öffnet sich ein Spalt, eine graue Katze
    schaut neugierig heraus, klettert auf die Zeile und trampelt darauf herum. Die
    Buchstaben hüpfen, kippen und vertauschen sich. Zum Schluss rutscht alles an seinen
    Platz, und die Katze verschwindet wieder im Spalt. Der echte Text bleibt unberührt:
    die Szene deckt die Zeile ab und spielt mit einer Kopie aus dem Bildschirmfoto."""
    name, titel, reihenfolge = 'tippkatze', 'Katze im getippten Text', 61
    braucht = 'schreibmarke'
    nur_ausloeser = True

    def vorbereiten(self):
        self.zeige_figur = False
        d = self.daten
        self.z = d['rechteck']
        self.h = h = self.z.height()
        self.buchstaben = [Buchstabe(r) for r in d['stuecke']]
        self.zeile_an = True
        self.spalt = 0.0
        self.auf = 0.0                       # wie weit die Katze aus dem Spalt schaut
        self.klemme = True
        sc = min(2.9 * h / 132, self.s * 0.7)
        self.sc = sc
        self.k = self.dazu('k', Katze, groesse=sc / self.s, fell=GRAU, sitzt=True)
        self.k.tempo = 3.2 * h
        self.k.richtung = random.choice((1, -1))
        self.spalt_x = self.waehle_spalt()
        self.k.x = self.spalt_x - 16 * sc * self.k.richtung
        self.k.y = self.z.bottom() + 140 * sc
        self.k.pose = Pose(kopf_vorn=True)
        oben, unten = d.get('tinte', (self.z.top(), self.z.bottom()))
        self.boden = oben + 0.3 * (unten - oben)      # Pfoten stehen auf den Buchstaben
        self.links = self.z.left() + 0.5 * h
        self.rechts = self.z.right() - 0.5 * h
        self.letzte_phase = 0

    def waehle_spalt(self):
        """x zwischen zwei Wörtern, möglichst in der Mitte der Zeile."""
        b = self.buchstaben
        mitte = self.z.center().x()
        beste, wert_b = None, None
        for a, c in zip(b, b[1:]):
            luecke = c.heim.left() - a.heim.right()
            x = (a.heim.right() + c.heim.left()) / 2
            w = luecke - abs(x - mitte) / (self.z.width() + 1) * self.h
            if wert_b is None or w > wert_b:
                beste, wert_b = x, w
        return beste if beste is not None else mitte

    # -- Ablauf

    def ablauf(self):
        h, sc, k = self.h, self.sc, self.k
        unten = self.z.bottom() + 140 * sc
        guck = self.z.bottom() + 52 * sc

        def schaue(sz, u):
            k.pose = Pose(kopf_vorn=True, blick_x=math.sin(u * 2.4) * 0.9, blick_y=-0.3 + 0.3 * math.sin(u * 1.3),
                          auge_zu=blinzeln(sz.t), sitzt=True)

        def ohren_zucken(sz, u):
            k.pose = Pose(kopf_vorn=True, blick_x=0.0, blick_y=0.6, auge_zu=0.3 < u < 0.42, sitzt=True)

        return [
            Warte(0.3),
            Wandel(0.5, spalt=1.0),
            Mit('k', Wandel(0.9, y=guck)),
            Jeweils(1.8, schaue),
            Jeweils(0.7, ohren_zucken),
            Mit('k', Setze(sitzt=False)),
            *self.hopser(lambda sz: k.x + k.richtung * 1.2 * h, lambda sz: self.boden, 0.5, 70, klemme_aus=True),
            Wandel(0.4, spalt=0.0),
            Mit('k', Stehe(0.5, lambda d, u: Pose(blick_y=0.8, auge_zu=blinzeln(d.t)))),
            Mit('k', Gehe(bis=self.links)),
            Mit('k', Stehe(0.4, Pose(blick_y=0.8))),
            Mit('k', Gehe(bis=lambda sz: min(self.rechts, k.x + 4 * h))),
            *self.sprung_auf_der_stelle(),
            Mit('k', Gehe(bis=self.rechts)),
            *self.treteln(1.4),
            Mit('k', Gehe(bis=lambda sz: (self.links + self.rechts) / 2)),
            *self.sprung_auf_der_stelle(),
            Mit('k', Stehe(1.2, lambda d, u: Pose(kopf_vorn=True, auge_zu=0.2 < u < 0.9))),
            Tu(Tippkatze.aufraeumen),
            Mit('k', Stehe(0.9, lambda d, u: Pose(kopf_vorn=True, blick_y=0.8, sorge=0.3))),
            Wandel(0.4, spalt=1.0),
            *self.hopser(lambda sz: self.spalt_x - 16 * sc * k.richtung, lambda sz: guck, 0.5, 50),
            Mit('k', Setze(sitzt=True, pose=Pose(kopf_vorn=True))),
            Mit('k', Wandel(0.5, y=unten)),
            Mit('k', Setze(zeige_figur=False)),
            Wandel(0.4, spalt=0.0),
            Warte(0.5),
            Tu(Tippkatze.alles_heim),
        ]

    def hopser(self, x, y, dauer, hoehe, klemme_aus=False):
        """Sprung der Katze im Bogen, auch in den Spalt hinein oder heraus."""
        k = self.k
        start = {}

        def anfang(sz):
            start['x'], start['y'] = k.x, k.y
            start['zx'], start['zy'] = x(sz), y(sz)
            if start['zx'] != k.x:
                k.richtung = 1 if start['zx'] > k.x else -1

        def flug(sz, u):
            f = min(1.0, u / dauer)
            k.x = start['x'] + (start['zx'] - start['x']) * f
            k.y = start['y'] + (start['zy'] - start['y']) * f - hoehe * k.s * 4 * f * (1 - f)
            k.pose = Pose(bein_v=-40, bein_h=35)
            if klemme_aus and k.y < self.z.top() + 0.3 * self.h:
                sz.klemme = False
            if not klemme_aus and f > 0.6:
                sz.klemme = True
        return [Tu(anfang), Jeweils(dauer, flug), Tu(lambda sz: self.stampfe(2.0, 1.6) if klemme_aus else None)]

    def sprung_auf_der_stelle(self):
        k = self.k

        def duck(sz, u):
            k.stauchen = 1 - 0.18 * glatt(u / 0.35)
            k.pose = Pose(blick_y=0.8)

        def hoch(sz, u):
            f = min(1.0, u / 0.45)
            k.stauchen = 1.0
            k.hopp = math.sin(math.pi * f) * 70 * k.s
            k.pose = Pose(bein_v=-35, bein_h=30, mund_offen=True)
        return [Jeweils(0.35, duck), Jeweils(0.45, hoch), Mit('k', Setze(hopp=0.0)),
                Tu(lambda sz: sz.stampfe(2.2, 2.2, tauschen=3)),
                Mit('k', Stehe(0.5, Pose(kopf_vorn=True, mund_offen=True)))]

    def treteln(self, dauer):
        """Milchtritt: abwechselnd mit den Vorderpfoten auf die Buchstaben drücken."""
        k = self.k
        zuletzt = [0]

        def f(sz, u):
            n = int(u * 7)
            k.pose = Pose(bein_v=12 * (1 if n % 2 else -1), bein_h=0, auge_zu=True)
            if n != zuletzt[0]:
                zuletzt[0] = n
                pfote = k.x + k.richtung * (26 + (12 if n % 2 else -14)) * k.s
                sz.tritt(pfote, 0.5)
        return [Jeweils(dauer, f)]

    # -- Buchstaben

    def unter(self, x):
        for b in self.buchstaben:
            if abs(b.x - x) <= b.heim.width() / 2 + 1:
                return b
        return None

    def tritt(self, x, staerke, tauschen=0.25):
        b = self.unter(x)
        if not b:
            return
        b.vy -= staerke * 20 * self.h
        b.vw += random.uniform(-1, 1) * 260 * staerke
        if random.random() < tauschen:
            i = self.buchstaben.index(b)
            j = i + random.choice((-1, 1))
            if 0 <= j < len(self.buchstaben):
                c = self.buchstaben[j]
                b.platz, c.platz = c.platz, b.platz
                c.vy -= staerke * 14 * self.h

    def stampfe(self, breite, staerke, tauschen=1):
        """Kräftige Landung: alles in der Nähe hüpft, ein paar Buchstaben tauschen die Plätze."""
        x = self.k.x
        for b in self.buchstaben:
            n = abs(b.x - x) / self.h
            if n < breite:
                b.vy -= staerke * (1 - n / breite) * 16 * self.h
                b.vw += random.uniform(-1, 1) * 320 * staerke * (1 - n / breite)
        nahe = [i for i, b in enumerate(self.buchstaben[:-1]) if abs(b.x - x) < breite * self.h]
        for _ in range(tauschen):
            if nahe:
                i = random.choice(nahe)
                a, c = self.buchstaben[i], self.buchstaben[i + 1]
                a.platz, c.platz = c.platz, a.platz

    def aufraeumen(self):
        for b in self.buchstaben:
            if abs(b.platz - b.heim.center().x()) > 0.5:
                b.vy -= 5 * self.h
            b.platz = b.heim.center().x()

    def alles_heim(self):
        for b in self.buchstaben:
            b.platz = b.x = b.heim.center().x()
            b.dy = b.vy = b.w = b.vw = 0.0

    def ziel(self, b):
        if self.spalt <= 0:
            return b.platz
        seite = -1 if b.heim.center().x() < self.spalt_x else 1
        return b.platz + seite * self.spalt * 0.75 * self.h

    # -- Schreck

    def schreck_ablauf(self):
        self.nebenbei.clear()
        k = self.k
        self.zeile_an = False            # es wird wieder getippt: echter Text sofort sichtbar
        if not k.zeige_figur:
            return [Warte(0.05)]
        if self.klemme:
            # schaut nur aus dem Spalt: abtauchen
            return [Mit('k', Setze(striche=True, pose=Pose(kopf_vorn=True, schreck=1.0, sitzt=True))),
                    Mit('k', Wandel(0.3, y=self.z.bottom() + 40 * self.sc)), Mit('k', Setze(zeige_figur=False,
                                                                                        striche=False))]
        k.sitzt = False
        k.tempo = self.tempo
        self.klemme = False
        return [Mit('k', Setze(buckel=1.0, striche=True, hopp=0.0, stauchen=1.0,
                               pose=Pose(kopf_vorn=True, schreck=1.0))),
                Mit('k', Jeweils(0.3, lambda d, u: setattr(d, 'hopp', math.sin(math.pi * u / 0.3) * 40 * d.s))),
                Mit('k', Setze(striche=False, hopp=0.0)),
                Mit('k', Renne(zum='rand', tempo=4.5))]

    # -- je Bild

    def weiter(self, dt):
        h = self.h
        k = self.k
        if self.zeile_an:
            for b in self.buchstaben:
                b.x += (self.ziel(b) - b.x) * min(1.0, dt * 9)
                b.vy += (-b.dy * 260 - b.vy * 14) * dt
                b.dy += b.vy * dt
                b.dy = max(-2.5 * h, min(0.25 * h, b.dy))
                b.vw += (-b.w * 160 - b.vw * 9) * dt
                b.w += b.vw * dt
            # Pfoten drücken die Buchstaben ein wenig ein; jeder Schritt tritt einen an
            if k.zeige_figur and not self.klemme and k.hopp == 0:
                schritt = int(k.phase / math.pi)
                if schritt != self.letzte_phase:
                    self.letzte_phase = schritt
                    vorn = schritt % 2 == 0
                    pfote = k.x + k.richtung * (30 if vorn else -22) * k.s
                    self.tritt(pfote, 0.45)
                for b in self.buchstaben:
                    if abs(b.x - k.x) < 40 * k.s:
                        b.dy = max(b.dy, 0.06 * h)

    # -- Zeichnen

    def klemmpfad(self):
        z, g = self.z, self.geo
        pfad = QPainterPath()
        pfad.addRect(QRectF(g.left(), g.top(), g.width(), z.top() - g.top()))
        w = max(0.0, self.spalt) * 0.75 * self.h
        pfad.addRect(QRectF(self.spalt_x - w, z.top() - 1, 2 * w, z.height() + 1))
        return pfad

    def zeichne(self, p):
        d = self.daten
        if self.zeile_an:
            p.drawImage(self.z, d['flicken'])
            for b in self.buchstaben:
                bildstueck(p, d['zeile'], self.z, b.heim, QPointF(b.x, b.heim.bottom() + b.dy), b.w, unten=True)
        p.save()
        if self.klemme:
            p.setClipPath(self.klemmpfad())
        self.k.zeichne(p)
        p.restore()
        for liste in self.teilchen:
            zeichne_teilchen(p, liste)

    def grenzen_extra(self):
        k = self.z.adjusted(-1.5 * self.h, -3 * self.h, 1.5 * self.h, 0.5 * self.h)
        return k if self.zeile_an else QRectF()
