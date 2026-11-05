"""Grundgerüst der Szenen.

Eine Szene ist eine Liste von Schritten, die nacheinander ablaufen:

    class Spaziergang(Szene):
        name, titel = 'laufen', 'Spaziergang'

        def ablauf(self):
            self.x = self.aussen(-self.richtung)
            return [Gehe(bis=self.vom_rand(0.2)), Schaue(1.9), Erschrecke(), Renne(zum='zurueck')]

Bewegt jemand die Maus oder drückt eine Taste, ersetzt schreck_ablauf() die
restlichen Schritte; ohne eigene Fassung: Schreck und weg zum nächsten Rand.

Zahlen in Schritten dürfen auch Funktionen sein, die erst beim Beginn des
Schritts mit der Szene aufgerufen werden, etwa bis=lambda sz: sz.oben.

Weitere Figuren (Wichtel, Schneemann ...) sind Darsteller: self.dazu('wichtel',
Wichtel, groesse=0.7) in vorbereiten(), dann laufen alle Schritte auch mit
ihnen, etwa Mit('wichtel', Gehe(bis=...)) oder Nebenbei(Mit('wichtel', Renne())).
"""
import math
import random

from PyQt6.QtCore import QPointF, QRectF
from PyQt6.QtGui import QTransform

from zeichnen.figur import Pose, figur, figur_kasten, geh_pose, renn_pose, winke_pose, zeichne_schreckstriche
from zeichnen.grundlagen import (KEIN_STIFT, Teilchen, blinzeln, glatt, teilchen_kasten, teilchen_schritt,
                                 zeichne_teilchen)


def wert(v, sz):
    return v(sz) if callable(v) else v


# ---------------------------------------------------------------- Szene

class Szene:
    name = ''           # Kurzname, z. B. für --sofort
    titel = ''          # Anzeige im Menü
    reihenfolge = 99    # Platz im Menü und bei Strg+Alt+1..9
    braucht = None      # 'taskleiste', 'schreibmarke': Szene spielt mit dem echten Bildschirm
    nur_ausloeser = False   # kommt nicht in der zufälligen Reihe, nur über einen eigenen Auslöser

    def __init__(self, geo, s, daten=None):
        self.geo = geo
        self.daten = daten              # bei 'braucht': Bildausschnitte und Rechtecke, siehe bildanalyse.py
        self.s = s                      # Pixel je Zeichen-Einheit
        self.t = 0.0
        self.fertig = False
        self.erschreckt = False
        self.te = 0.0                   # Zeitpunkt des Schrecks
        self.richtung = random.choice((1, -1))
        self.boden = geo.bottom()
        self.oben = geo.top()
        self.tempo = geo.width() / 9    # Gehtempo in Pixel je Sekunde
        # Zustand der Figur, die Schritte verändern ihn
        self.x, self.y = 0.0, self.boden
        self.hopp = 0.0
        self.neigung = 0.0
        self.stauchen = 1.0
        self.phase = 0.0
        self.pose = Pose()
        self.zeige_figur = True
        self.striche = False
        self.teilchen = []              # Listen mit Funken, Rauch usw.
        self.nebenbei = []              # Schritte, die im Hintergrund weiterlaufen
        self.darsteller = {}            # weitere Figuren, siehe dazu()
        self.wolke, self.splitter = [], []  # Teilchen von streue(), ohne und mit Schwerkraft
        self.vorbereiten()
        self.schritte = list(self.ablauf())
        self.aktuell = None
        self.tz = 0.0
        self.naechster()

    # -- zum Überschreiben

    def vorbereiten(self):
        """Eigenen Zustand anlegen (Orte, Requisiten), bevor ablauf() gefragt wird."""

    def ablauf(self):
        return []

    def schreck_ablauf(self):
        """Neue Schritte nach dem Schreck. None: die Szene hat selbst umgeplant."""
        return [Erschrecke(), Renne(zum='rand')]

    def weiter(self, dt):
        """Wird in jedem Bild nach dem aktuellen Schritt aufgerufen."""

    def zeichne_hinten(self, p):
        pass

    def zeichne_vorn(self, p):
        pass

    def grenzen_extra(self):
        return QRectF()

    def striche_punkt(self):
        return self.x + 6 * self.s * self.richtung, self.y - self.hopp - 262 * self.s

    # -- Hilfen für Szenen

    def dazu(self, name, art, groesse=1.0, vorn=False, **eigen):
        """Neue Figur, vorn=True: vor dem Weihnachtsmann. eigen: Merkmale für die Zeichnung."""
        d = Darsteller(self, art, groesse, vorn, **eigen)
        self.darsteller[name] = d
        return d

    def aussen(self, seite):
        """x knapp außerhalb des Bildes, seite -1 = links, +1 = rechts."""
        rand = 130 * self.s
        return self.geo.left() - rand if seite < 0 else self.geo.right() + rand

    def vom_rand(self, anteil, seite=None):
        """x im Abstand anteil·Breite vom Rand, an dem die Szene beginnt."""
        seite = -self.richtung if seite is None else seite
        if seite < 0:
            return self.geo.left() + self.geo.width() * anteil
        return self.geo.right() - self.geo.width() * anteil

    def naechster_rand(self):
        return -1 if self.x - self.geo.left() < self.geo.right() - self.x else 1

    def streue(self, x, y, anzahl, farbe, tempo=80, dauer=0.8, r=(5, 12), schwer=False, art='rauch',
               richtung=None, streuung=math.pi):
        """Wölkchen (Schnee, Rauch) oder mit schwer=True Splitter (Krümel, Schalen), die herunterfallen.
        Größen in Einheiten, richtung in Bogenmaß (None: rundherum)."""
        liste = self.splitter if schwer else self.wolke
        if liste not in self.teilchen:
            self.teilchen.append(liste)
        s = self.s
        for _ in range(anzahl):
            w = random.uniform(0, 2 * math.pi) if richtung is None else richtung + random.uniform(-1, 1) * streuung
            v = random.uniform(0.4, 1.0) * tempo * s
            c = random.choice(farbe) if isinstance(farbe, (list, tuple)) else farbe
            liste.append(Teilchen(x, y, math.cos(w) * v, math.sin(w) * v, random.uniform(0.6, 1.0) * dauer,
                                  random.uniform(*r) * s, random.uniform(*r) * s * (0.6 if schwer else 1.6),
                                  c, art))

    def schreck_alle(self, weihnachtsmann=True, hoehe=40):
        """Schreck für Szenen mit mehreren Figuren: wer zu sehen ist, hüpft und rennt zum nächsten Rand."""
        self.nebenbei.clear()
        neu = []
        for name, d in self.darsteller.items():
            if d.zeige_figur and d.figur_sichtbar():
                neu.append(Nebenbei(Mit(name, Erschrecke(0.35, hoehe)), Mit(name, Renne(zum='rand'))))
            else:
                d.zeige_figur = False
        if weihnachtsmann and self.zeige_figur and self.figur_sichtbar():
            neu += [Erschrecke(0.35, hoehe), Renne(zum='rand')]
        else:
            self.zeige_figur = False
        return neu + [WarteNebenbei(), WarteBis(lambda sz: not sz.wolke and not sz.splitter)]

    def frisch_erschreckt(self, dauer=0.45):
        return self.erschreckt and self.t - self.te < dauer

    def figur_sichtbar(self):
        return figur_kasten(self.x, self.y - self.hopp, self.s).intersects(self.geo)

    # -- Ablauf

    def naechster(self):
        if not self.schritte:
            self.aktuell, self.fertig = None, True
            return
        self.aktuell = self.schritte.pop(0)
        self.tz = self.t
        self.aktuell.beginn(self)

    def schritt(self, dt):
        self.t += dt
        if self.wolke or self.splitter:
            teilchen_schritt(self.wolke, dt, bremse=2.5)
            teilchen_schritt(self.splitter, dt, schwere=900 * self.s)
        for eintrag in list(self.nebenbei):
            s, t0 = eintrag
            s.weiter(self, self.t - t0, dt)
            if s.fertig(self, self.t - t0):
                self.nebenbei.remove(eintrag)
        d = dt
        for _ in range(50):              # Schritte ohne Dauer gleich im selben Bild erledigen
            if self.fertig or self.aktuell is None:
                break
            u = self.t - self.tz
            self.aktuell.weiter(self, u, d)
            if not self.aktuell.fertig(self, u):
                break
            self.aktuell.ende(self)
            self.naechster()
            d = 0.0
        self.weiter(dt)

    def erschrecken(self):
        """Jemand hat die Maus bewegt oder eine Taste gedrückt."""
        if self.erschreckt or self.fertig:
            return
        self.erschreckt, self.te = True, self.t
        neu = self.schreck_ablauf()
        if neu is not None:
            self.schritte = list(neu)
            self.naechster()

    # -- Zeichnen

    def zeichne_figur(self, p, zwischen=None):
        figur(p, self.x, self.y - self.hopp, self.s, self.richtung, self.pose, zwischen,
              self.stauchen, self.neigung)

    def zeichne(self, p):
        self.zeichne_hinten(p)
        for d in self.darsteller.values():
            if not d.vorn:
                d.zeichne(p)
        if self.zeige_figur:
            self.zeichne_figur(p)
        for d in self.darsteller.values():
            if d.vorn:
                d.zeichne(p)
        self.zeichne_vorn(p)
        if self.striche:
            zeichne_schreckstriche(p, *self.striche_punkt(), self.s)
        for liste in self.teilchen:
            zeichne_teilchen(p, liste)

    def grenzen(self):
        k = QRectF()
        if self.zeige_figur:
            k = figur_kasten(self.x, self.y - self.hopp, self.s).adjusted(0, -30 * self.s, 0, 0)
        k = k.united(self.grenzen_extra())
        for d in self.darsteller.values():
            if d.zeige_figur:
                k = k.united(d.kasten())
        for liste in self.teilchen:
            k = k.united(teilchen_kasten(liste))
        return k


# ---------------------------------------------------------------- Weitere Figuren

class Darsteller:
    """Eine weitere Figur mit denselben Eigenschaften wie die Szene (x, y, richtung,
    pose, hopp, neigung, stauchen ...), deshalb laufen alle Schritte auch mit ihr.
    Was sie nicht selbst hat (t, geo, oben, boden ...), holt sie von der Szene.

    art: Klasse aus zeichnen/figuren.py mit KASTEN (Umriss in Einheiten, Fuß im
    Ursprung, Blick nach rechts), KOPF (Punkt über dem Kopf) und zeichne(p, d)."""

    def __init__(self, sz, art, groesse, vorn, **eigen):
        self.sz = sz
        self.art = art
        self.s = sz.s * groesse
        self.vorn = vorn
        self.x, self.y = sz.aussen(-sz.richtung), sz.boden
        self.richtung = sz.richtung
        self.tempo = sz.tempo
        self.hopp = self.neigung = self.phase = 0.0
        self.stauchen = 1.0
        self.pose = Pose()
        self.zeige_figur = True
        self.striche = False
        for k, v in eigen.items():
            setattr(self, k, v)

    def __getattr__(self, name):
        return getattr(self.sz, name)

    def trafo(self):
        tr = QTransform()
        tr.translate(self.x, self.y - self.hopp)
        tr.rotate(self.neigung * self.richtung)
        tr.scale(self.s * self.richtung * (2 - self.stauchen), self.s * self.stauchen)
        return tr

    def zeichne(self, p):
        if not self.zeige_figur:
            return
        p.save()
        p.setTransform(self.trafo(), True)
        p.setPen(KEIN_STIFT)
        self.art.zeichne(p, self)
        p.restore()
        if self.striche:
            zeichne_schreckstriche(p, *self.striche_punkt(), self.sz.s)

    def striche_punkt(self):
        q = self.trafo().map(QPointF(*self.art.KOPF))
        return q.x(), q.y()

    def kasten(self):
        k = self.trafo().mapRect(self.art.KASTEN)
        return k.adjusted(0, -30 * self.sz.s if self.striche else 0, 0, 0)

    def figur_sichtbar(self):
        return self.kasten().intersects(self.geo)

    def naechster_rand(self):
        return -1 if self.x - self.geo.left() < self.geo.right() - self.x else 1


# ---------------------------------------------------------------- Allgemeine Schritte

class Schritt:
    dauer = 0.0

    def beginn(self, sz):
        pass

    def weiter(self, sz, u, dt):
        """u: Sekunden seit Beginn des Schritts."""

    def fertig(self, sz, u):
        return u >= self.dauer

    def ende(self, sz):
        pass


class Warte(Schritt):
    def __init__(self, dauer):
        self.dauer_v = dauer

    def beginn(self, sz):
        self.dauer = wert(self.dauer_v, sz)


class WarteBis(Schritt):
    def __init__(self, bedingung):
        self.bedingung = bedingung

    def fertig(self, sz, u):
        return self.bedingung(sz)


class Setze(Schritt):
    """Setzt Eigenschaften der Szene sofort, z. B. Setze(zeige_figur=False)."""

    def __init__(self, **werte):
        self.werte = werte

    def beginn(self, sz):
        for k, v in self.werte.items():
            setattr(sz, k, wert(v, sz))


class Kurz(Schritt):
    """Setzt Eigenschaften für eine Weile und stellt sie danach zurück, z. B. Kurz(0.15, zu=True)."""

    def __init__(self, dauer, **werte):
        self.dauer, self.werte = dauer, werte

    def beginn(self, sz):
        self.vorher = {k: getattr(sz, k) for k in self.werte}
        for k, v in self.werte.items():
            setattr(sz, k, wert(v, sz))

    def ende(self, sz):
        for k, v in self.vorher.items():
            setattr(sz, k, v)


class Wandel(Schritt):
    """Überblendet Eigenschaften weich zu Zielwerten, z. B. Wandel(1.2, h=0.88)."""

    def __init__(self, dauer, **ziele):
        self.dauer, self.ziele = dauer, ziele

    def beginn(self, sz):
        self.von = {k: getattr(sz, k) for k in self.ziele}
        self.nach = {k: wert(v, sz) for k, v in self.ziele.items()}

    def weiter(self, sz, u, dt):
        f = glatt(u / self.dauer) if self.dauer > 0 else 1.0
        for k in self.ziele:
            setattr(sz, k, self.von[k] + (self.nach[k] - self.von[k]) * f)


class Tu(Schritt):
    """Ruft einmal eine Funktion mit der Szene auf."""

    def __init__(self, funktion):
        self.funktion = funktion

    def beginn(self, sz):
        self.funktion(sz)


class Jeweils(Schritt):
    """Ruft eine Weile in jedem Bild funktion(szene, u) auf."""

    def __init__(self, dauer, funktion):
        self.dauer, self.funktion = dauer, funktion

    def weiter(self, sz, u, dt):
        self.funktion(sz, u)


class Folge(Schritt):
    """Mehrere Schritte nacheinander als ein Schritt (für Nebenbei)."""

    def __init__(self, *schritte):
        self.liste = list(schritte)

    def beginn(self, sz):
        self.rest = list(self.liste)
        self.aktiv, self.t0 = None, 0.0
        self.weiter_zum_naechsten(sz, 0.0)

    def weiter_zum_naechsten(self, sz, u):
        self.aktiv = self.rest.pop(0) if self.rest else None
        self.t0 = u
        if self.aktiv:
            self.aktiv.beginn(sz)

    def weiter(self, sz, u, dt):
        while self.aktiv:
            self.aktiv.weiter(sz, u - self.t0, dt)
            if not self.aktiv.fertig(sz, u - self.t0):
                return
            self.aktiv.ende(sz)
            self.weiter_zum_naechsten(sz, u)

    def fertig(self, sz, u):
        return self.aktiv is None


class Mit(Schritt):
    """Führt einen Schritt mit einem Darsteller aus statt mit dem Weihnachtsmann."""

    def __init__(self, wer, schritt):
        self.wer, self.schritt = wer, schritt

    def beginn(self, sz):
        self.d = sz.darsteller[self.wer]
        self.schritt.beginn(self.d)

    def weiter(self, sz, u, dt):
        self.schritt.weiter(self.d, u, dt)

    def fertig(self, sz, u):
        return self.schritt.fertig(self.d, u)

    def ende(self, sz):
        self.schritt.ende(self.d)


class WarteNebenbei(Schritt):
    """Wartet, bis alles im Hintergrund fertig ist, etwa bis alle Figuren weg sind."""

    def fertig(self, sz, u):
        return not sz.nebenbei


class Nebenbei(Schritt):
    """Startet Schritte im Hintergrund und geht sofort weiter, z. B. damit
    ein Seil herabfällt, während er läuft."""

    def __init__(self, *schritte):
        self.folge = Folge(*schritte)

    def beginn(self, sz):
        self.folge.beginn(sz)
        sz.nebenbei.append((self.folge, sz.t))


# ---------------------------------------------------------------- Schritte der Figur

class Gehe(Schritt):
    """Geht bis zum x-Wert 'bis' (None: aus dem Bild hinaus) oder eine feste 'dauer' lang."""
    pose_fn = staticmethod(geh_pose)
    neigung_v = 0.0
    schrittlaenge = 38

    def __init__(self, bis=None, tempo=1.0, dauer=None, haltung=None, neigung=None):
        """haltung(pose, szene) darf die Gangart abwandeln, etwa einen Arm hochhalten."""
        self.bis_v, self.tempo, self.dauer_v = bis, tempo, dauer
        self.haltung = haltung
        if neigung is not None:
            self.neigung_v = neigung

    def beginn(self, sz):
        self.ziel = wert(self.bis_v, sz)
        if self.ziel is not None and abs(self.ziel - sz.x) > 0.5:
            sz.richtung = 1 if self.ziel > sz.x else -1
        sz.neigung = self.neigung_v

    def v(self, sz, u):
        return sz.tempo * wert(self.tempo, sz)

    def weiter(self, sz, u, dt):
        v = self.v(sz, u)
        sz.x += sz.richtung * v * dt
        sz.phase += v * dt / (sz.s * self.schrittlaenge)
        if self.pose_fn:
            sz.pose = self.pose_fn(sz.phase, sz.t)
            if self.haltung:
                sz.pose = self.haltung(sz.pose, sz)

    def fertig(self, sz, u):
        if self.dauer_v is not None:
            return u >= self.dauer_v
        if self.ziel is None:
            return u > 0.1 and not sz.figur_sichtbar()
        if (sz.x - self.ziel) * sz.richtung >= 0:
            sz.x = self.ziel
            return True
        return False

    def ende(self, sz):
        sz.neigung = 0.0


class Renne(Gehe):
    """Rennt aus dem Bild: zum='rand' (nächster Rand), 'zurueck' oder 'weiter'."""
    pose_fn = staticmethod(lambda phase, t: renn_pose(phase))
    neigung_v = 10.0
    schrittlaenge = 30

    def __init__(self, zum='rand', tempo=3.6, haltung=None, neigung=None):
        super().__init__(None, tempo, haltung=haltung, neigung=neigung)
        self.zum = zum

    def beginn(self, sz):
        if self.zum == 'rand':
            sz.richtung = sz.naechster_rand()
        elif self.zum == 'zurueck':
            sz.richtung = -sz.richtung
        super().beginn(sz)

    def v(self, sz, u):
        return super().v(sz, u) * glatt(u / 0.25 + 0.2)


class Stehe(Schritt):
    """Steht still; pose ist eine Pose oder eine Funktion (szene, u) -> Pose."""

    def __init__(self, dauer, pose=None):
        self.dauer, self.pose = dauer, pose

    def weiter(self, sz, u, dt):
        if self.pose is None:
            sz.pose = Pose(auge_zu=blinzeln(sz.t))
        else:
            sz.pose = self.pose(sz, u) if callable(self.pose) else self.pose


class Schaue(Stehe):
    """Dreht den Kopf zu den Zuschauern, blinzelt, wird langsam unruhig."""

    def __init__(self, dauer):
        super().__init__(dauer, self.pose_zu)

    @staticmethod
    def pose_zu(sz, u):
        if u < 0.35:
            return Pose(auge_zu=blinzeln(sz.t))
        return Pose(kopf_vorn=True, blick_y=0.25, auge_zu=0.9 < u < 1.05,
                    sorge=min(1.0, (u - 0.35) / 1.2) * 0.6)


class Winke(Stehe):
    def __init__(self, dauer):
        super().__init__(dauer, lambda sz, u: winke_pose(u, sz.t))


class Erschrecke(Schritt):
    """Großer Schreck: Hüpfer, große Augen, Schreckstriche."""

    def __init__(self, dauer=0.35, hoehe=48):
        self.dauer, self.hoehe = dauer, hoehe

    def beginn(self, sz):
        sz.striche, sz.neigung = True, 0.0

    def weiter(self, sz, u, dt):
        sz.hopp = math.sin(math.pi * min(1.0, u / self.dauer)) * self.hoehe * sz.s
        sz.pose = Pose(kopf_vorn=True, schreck=1.0, sorge=0.4, arm_v=-115, arm_h=-100, arm_v_x=20,
                       bein_v=-18, bein_h=18, wipp=-6)

    def ende(self, sz):
        sz.hopp, sz.striche = 0.0, False


class Ducke(Schritt):
    def __init__(self, dauer=0.3):
        self.dauer = dauer

    def weiter(self, sz, u, dt):
        sz.pose = Pose(arm_v=40, arm_h=35, bein_v=-8, bein_h=8, hub=4)
        sz.stauchen = 1 - 0.14 * math.sin(min(1.0, u / self.dauer) * math.pi / 2)

    def ende(self, sz):
        sz.stauchen = 1.0


class Springe(Schritt):
    """Sprung im Bogen zum Punkt nach=(x, y), Scheitel 'hoehe' Einheiten über der Verbindungslinie."""

    def __init__(self, nach, dauer=0.95, hoehe=170):
        self.nach_v, self.dauer_v, self.hoehe = nach, dauer, hoehe

    def beginn(self, sz):
        self.x0, self.y0 = sz.x, sz.y
        self.x1, self.y1 = wert(self.nach_v, sz)
        self.dauer = wert(self.dauer_v, sz)

    def weiter(self, sz, u, dt):
        f = min(1.0, u / self.dauer)
        sz.x = self.x0 + (self.x1 - self.x0) * f
        sz.y = self.y0 + (self.y1 - self.y0) * f - self.hoehe * sz.s * 4 * f * (1 - f)
        sz.stauchen = 1 + 0.08 * math.sin(u / 0.25 * math.pi) if u < 0.25 else 1.0
        sz.pose = Pose(arm_v=-132, arm_h=-122, arm_v_x=24, bein_v=-38, bein_h=30, mund_offen=True, wipp=-6)

    def ende(self, sz):
        sz.stauchen = 1.0


class Falle(Schritt):
    """Fällt senkrecht, bis bis(szene) wahr ist."""

    def __init__(self, bis):
        self.bis = bis

    def beginn(self, sz):
        self.v = 120 * sz.s

    def weiter(self, sz, u, dt):
        self.v += 1400 * sz.s * dt
        sz.y += self.v * dt
        sz.pose = Pose(arm_v=-138, arm_h=-128, arm_v_x=24, bein_v=-6, bein_h=6, mund_offen=True, wipp=8)

    def fertig(self, sz, u):
        return self.bis(sz)


class Gleite(Schritt):
    """Gleitet in 'dauer' Sekunden nach x=bis und wird dabei langsamer (Rutschen, Schlittern)."""

    def __init__(self, bis, dauer, pose=None):
        self.bis_v, self.dauer, self.pose = bis, dauer, pose

    def beginn(self, sz):
        self.x0, self.x1 = sz.x, wert(self.bis_v, sz)

    def weiter(self, sz, u, dt):
        f = min(1.0, u / self.dauer)
        sz.x = self.x0 + (self.x1 - self.x0) * (1 - (1 - f) ** 2)
        if self.pose is not None:
            sz.pose = self.pose(sz, u) if callable(self.pose) else self.pose


class Rutsche(Renne):
    """Saust auf dem Bauch (neigung 80) oder Rücken (-95) aus dem Bild, hoehe hebt den Körper an."""

    def __init__(self, zum='rand', tempo=3.6, neigung=80, hoehe=30, pose=None):
        super().__init__(zum, tempo, neigung=neigung)
        self.hoehe = hoehe
        self.pose = pose or Pose(arm_v=-170, arm_h=-170, bein_v=10, bein_h=20, mund_offen=True)
        self.pose_fn = None

    def beginn(self, sz):
        super().beginn(sz)
        sz.hopp = self.hoehe * sz.s

    def v(self, sz, u):
        return sz.tempo * wert(self.tempo, sz)

    def weiter(self, sz, u, dt):
        super().weiter(sz, u, dt)
        sz.pose = self.pose(sz, u) if callable(self.pose) else self.pose

    def ende(self, sz):
        super().ende(sz)
        sz.hopp = 0.0


def muetze_richten(wer, dauer=1.6):
    """Running Gag: der Wichtel richtet seine abgeknickte Mützenspitze würdevoll gerade,
    sie knickt sofort wieder ab. Schritte für die Schrittliste."""
    return [Mit(wer, Stehe(0.35, lambda d, u: Pose(arm_v=-175 * min(1.0, u / 0.3), arm_v_x=6, kopf_vorn=True))),
            Mit(wer, Wandel(0.3, knick=0.0)),
            Mit(wer, Stehe(0.25, Pose(kopf_vorn=True, auge_zu=True))),
            Mit(wer, Stehe(dauer - 1.2, Pose(kopf_vorn=True, auge_zu=True, mund_offen=False))),
            Mit(wer, Wandel(0.06, knick=1.0)),
            Mit(wer, Stehe(0.24, Pose(kopf_vorn=True, sorge=1.0, blick_y=-0.8)))]
