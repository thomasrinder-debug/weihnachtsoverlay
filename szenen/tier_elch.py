import math

from PyQt6.QtCore import QRectF

from zeichnen.figur import Pose
from zeichnen.grundlagen import blinzeln
from zeichnen.tiere import Elch, Rotkehlchen, Schneeeule, elch_geweih_punkt, elch_punkt

from .basis import Gehe, Jeweils, Mit, Nebenbei, Schritt, Setze, Stehe, Szene, Tu, Wandel, Warte, WarteNebenbei
from .tier_gemeinsam import FEDERN, Flug, publikumsblick, puff, sterne

ELCH_G, EULE_G, VOGEL_G = 0.72, 0.62, 1.1


def wegfliegen(sz, name, dauer=0.7):
    """Ein Vogel flattert schräg nach oben zum nächsten Seitenrand hinaus."""
    d = sz.darsteller[name]
    seite = d.naechster_rand()
    return Mit(name, Folge2(Setze(fliegt=True, richtung=seite),
                            Flug(lambda w: (sz.aussen(seite), w.y - 260 * sz.s), dauer, hoehe=0)))


class Folge2(Schritt):
    """Wie Folge, aber für Mit: führt Schritte mit dem Darsteller nacheinander aus."""

    def __init__(self, *schritte):
        from .basis import Folge
        self.f = Folge(*schritte)

    def beginn(self, sz):
        self.f.beginn(sz)

    def weiter(self, sz, u, dt):
        self.f.weiter(sz, u, dt)

    def fertig(self, sz, u):
        return self.f.fertig(sz, u)


class AufPlatz(Schritt):
    """Hält einen Vogel auf einem beweglichen Sitzplatz (Funktion szene -> QPointF)."""

    def __init__(self, name, platz, dauer=None):
        self.name, self.platz, self.dauer_v = name, platz, dauer

    def weiter(self, sz, u, dt):
        q = self.platz(sz)
        d = sz.darsteller[self.name]
        d.x, d.y = q.x(), q.y()


class Untermieter(Szene):
    """Ein Elch mit mächtigem Geweih bleibt stehen. Ein Rotkehlchen landet darauf, er nickt ein
    wenig ein. Dann plumpst eine dicke Schneeeule dazu: Er stemmt sich breitbeinig dagegen und
    hält stand. Als das Rotkehlchen auf dem Kopf der Eule einmal hüpft, kippt der Elch kopfüber
    auf sein Geweih, die Beine in der Luft. Die Eule landet seelenruhig auf seinem Hinterteil."""
    name, titel, reihenfolge = 'tier_elch', 'Elch mit Untermieter', 710

    def vorbereiten(self):
        self.zeige_figur = False
        r = self.richtung
        self.ex = self.vom_rand(0.11)
        self.e = self.dazu('e', Elch, groesse=ELCH_G, spreiz=0.0, nicken=0.0, kipp=0.0, drehpunkt=(30, -104))
        self.o = self.dazu('o', Schneeeule, groesse=EULE_G, fluegel=0.0, flattern=0.0, zerzaust=0.0, muede=0.0,
                           fliegt=False)
        self.v = self.dazu('v', Rotkehlchen, groesse=VOGEL_G, plustern=1.0, fluegel=0.0, zittern=0.0, fliegt=False)
        self.o.x, self.o.y = self.aussen(-r), self.boden - 520 * self.s
        self.v.x, self.v.y = self.aussen(-r), self.boden - 420 * self.s
        self.halten = {}

    # -- Sitzplätze

    def geweih(self, sz=None):
        return elch_geweih_punkt(self.e)

    def eulenkopf(self, sz=None):
        o = self.o
        return o.trafo().map(__import__('PyQt6.QtCore', fromlist=['QPointF']).QPointF(0, -128))

    def hinterteil(self, sz=None):
        return elch_punkt(self.e, -16, -118)

    def weiter(self, dt):
        for name, platz in self.halten.items():
            d = self.darsteller[name]
            q = platz()
            d.x, d.y = q.x(), q.y()
        for d in (self.o, self.v):
            if d.fliegt:
                if d is self.o:
                    d.fluegel, d.flattern = 0.7, 40 * math.sin(self.t * 28)
                else:
                    d.fluegel = -60 + 50 * math.sin(self.t * 40)
            elif d is self.o:
                d.fluegel, d.flattern = 0.0, 0.0
            else:
                d.fluegel = 0.0

    def sitz(self, name, platz):
        def f(sz):
            sz.halten[name] = platz
            sz.darsteller[name].fliegt = False
        return Tu(f)

    def los(self, name):
        def f(sz):
            sz.halten.pop(name, None)
        return Tu(f)

    def ablauf(self):
        r, s = self.richtung, self.s
        e_pose = lambda **k: (lambda d, u: Pose(auge_zu=blinzeln(d.t), **k))  # noqa: E731
        return [
            Mit('e', Gehe(bis=self.ex, tempo=1.1)),
            Mit('e', Setze(pose=Pose())),
            # Rotkehlchen landet
            Mit('v', Setze(fliegt=True, richtung=r)),
            Mit('v', Flug(lambda d: (self.geweih().x(), self.geweih().y()), 0.7, hoehe=60)),
            self.sitz('v', self.geweih),
            Mit('e', Wandel(0.12, nicken=14.0)),
            Mit('e', Wandel(0.25, nicken=9.0)),
            Mit('e', Stehe(0.6, e_pose(blick_y=-1.0, sorge=0.6))),
            # Die Eule plumpst dazu
            Mit('o', Setze(fliegt=True, richtung=r)),
            Mit('o', Flug(lambda d: (self.geweih().x() - r * 10 * s, self.geweih().y()), 0.75, hoehe=90)),
            Mit('o', Setze(fliegt=False)),
            Tu(lambda sz: sz.halten.update(o=sz.geweih)),
            Tu(lambda sz: sz.halten.update(v=sz.eulenkopf)),
            Tu(lambda sz: puff(sz, sz.geweih().x(), sz.geweih().y(), 8, 80)),
            Mit('e', Wandel(0.14, nicken=42.0, spreiz=0.5)),
            Mit('e', Setze(pose=Pose(schreck=0.8))),
            Mit('e', Stehe(0.35, Pose(schreck=0.8))),
            # Er stemmt sich dagegen und hält stand
            Mit('e', Wandel(0.9, nicken=22.0, spreiz=1.0)),
            Mit('e', Stehe(0.5, e_pose(sorge=0.2))),
            Mit('o', Setze(muede=0.5)),
            Mit('e', Stehe(0.6, e_pose(blick_x=-1.0, blick_y=0.2))),
            # Das Rotkehlchen hüpft einmal
            self.los('v'),
            Mit('v', Flug(lambda d: (d.x, d.y), 0.3, hoehe=28)),
            Mit('e', Setze(pose=Pose(schreck=1.0))),
            Mit('e', Wandel(0.25, nicken=72.0, spreiz=0.4)),
            self.los('o'),
            Mit('o', Setze(fliegt=True, muede=0.0)),
            Tu(lambda sz: sz.halten.update(v=sz.eulenkopf)),
            Mit('e', Wandel(0.45, kipp=180.0, spreiz=0.0)),
            Tu(lambda sz: puff(sz, sz.e.x, sz.boden, 22, 200)),
            Tu(lambda sz: sz.streue(sz.o.x, sz.o.y - 50 * sz.s, 6, FEDERN, tempo=90, dauer=0.9, r=(3, 6))),
            Nebenbei(Mit('e', Jeweils(2.4, lambda d, u: setattr(d, 'pose', Pose(
                bein_v=25 * math.sin(u * 14), bein_h=-25 * math.sin(u * 14 + 1), schreck=0.3))))),
            Mit('o', Flug(lambda d: (self.hinterteil().x(), self.hinterteil().y()), 0.55, hoehe=40)),
            Tu(lambda sz: sz.halten.update(o=sz.hinterteil)),
            Mit('o', Setze(fliegt=False, muede=0.5)),
            Warte(0.3),
            Mit('o', Stehe(1.1, lambda d, u: Pose(auge_zu=0.4 < u < 0.52))),
            # Abflug, der Elch plumpst zurück
            self.los('o'), self.los('v'),
            Nebenbei(wegfliegen(self, 'o', 0.8)),
            Nebenbei(wegfliegen(self, 'v', 0.6)),
            Mit('e', Wandel(0.5, kipp=360.0, nicken=30.0)),
            Mit('e', Setze(kipp=0.0)),
            Tu(lambda sz: sterne(sz, sz.geweih().x(), sz.geweih().y() - 20 * sz.s)),
            Tu(lambda sz: puff(sz, sz.e.x, sz.boden, 14, 160)),
            Mit('e', Wandel(0.5, nicken=0.0)),
            Mit('e', Stehe(0.7, Pose(auge_zu=True, sorge=1.0))),
            Mit('e', Gehe(bis=self.aussen(-r), tempo=1.5)),
            WarteNebenbei(),
        ]

    def schreck_ablauf(self):
        self.halten.clear()
        self.nebenbei.clear()
        e = self.e
        e.kipp = e.nicken = e.spreiz = 0.0
        neu = []
        for name in ('o', 'v'):
            d = self.darsteller[name]
            if d.figur_sichtbar():
                d.muede = 0.0 if name == 'o' else d.plustern
                neu.append(Nebenbei(wegfliegen(self, name, 0.5)))
            else:
                d.zeige_figur = False
        if e.figur_sichtbar():
            from .basis import Erschrecke, Renne
            neu.append(Nebenbei(Mit('e', Erschrecke(0.3, 40)), Mit('e', Renne(zum='rand'))))
        else:
            e.zeige_figur = False
        return neu + [WarteNebenbei(), Warte(0.01)]

    def grenzen_extra(self):
        e = self.e
        if not e.zeige_figur or not e.kipp:
            return QRectF()
        k = Elch.KASTEN
        pkt = [elch_punkt(e, x, y) for x, y in ((k.left(), k.top()), (k.right(), k.top()),
                                                   (k.left(), k.bottom()), (k.right(), k.bottom()))]
        xs, ys = [q.x() for q in pkt], [q.y() for q in pkt]
        return QRectF(min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys))
