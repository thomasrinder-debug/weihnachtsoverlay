"""Tafel-Varianten und Kreide-Requisiten für die Tafel-Szenen des Professors
(Endlosformel, Kreidequietschen, Unzerbrechliche Kreide, Klapptafel, Schiefe Null,
Hungriger Schwamm, Geisterkreide, Immer mehr).

Alle in Zeichen-Einheiten, Boden der Tafel mittig im Ursprung, wie in labor.py.
"""
import math
import random

from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import QColor, QPainterPath

from .grundlagen import *  # noqa: F401,F403  Farben und Hilfen
from .labor import (HOLZ, HOLZ_DUNKEL, KREIDE, SCHIEFER, SCHIEFER_DUNKEL, TAFEL_B, TAFEL_H, TAFEL_UNTEN,
                    tafel_flaeche, zeichne_schwamm)

KREIDE_HELL = QColor('#F7F4EA')
STAUB = [QColor(240, 240, 232, 200), QColor(225, 228, 222, 180), QColor(250, 250, 245, 220)]


def tafel_beine(p, b=TAFEL_B, h=TAFEL_H, unten=TAFEL_UNTEN, welche=(-1, 1), querholz=True, kurz=False):
    """Holzständer der Tafel; welche: (-1,) nur linkes, (1,) nur rechtes Bein; kurz: enden an der Ablage."""
    p.setPen(KEIN_STIFT)
    f = tafel_flaeche(b, h, unten)
    oben = f.bottom() + 6 if kurz else f.top() - 10
    for seite in welche:
        x0, x1 = seite * b * 0.38, seite * b * (0.3 + 0.08 * (1 - oben / (f.top() - 10)) if kurz else 0.3)
        p.setBrush(linear(x0 - 4, 0, x0 + 4, 0, HOLZ, HOLZ_DUNKEL))
        pfad = QPainterPath()
        pfad.moveTo(x0 - 3.5, 0)
        pfad.lineTo(x1 - 3, oben)
        pfad.lineTo(x1 + 3, oben)
        pfad.lineTo(x0 + 3.5, 0)
        pfad.closeSubpath()
        p.drawPath(pfad)
    if querholz:
        p.setBrush(HOLZ_DUNKEL)
        p.drawRect(QRectF(-b * 0.36, -24, b * 0.72, 4))


def schiefer_pfad(f, loecher=()):
    """Schreibfläche ohne die weggefressenen Stellen (loecher: Liste (x, y, r))."""
    pfad = QPainterPath()
    pfad.addRect(f)
    if loecher:
        weg = QPainterPath()
        weg.setFillRule(Qt.FillRule.WindingFill)
        for x, y, r in loecher:
            weg.addEllipse(QPointF(x, y), r, r * 0.85)
        pfad = pfad.subtracted(weg)
    return pfad


def zeichne_tafel_c(p, b=TAFEL_B, h=TAFEL_H, unten=TAFEL_UNTEN, wisch=(), kreide=True, schwamm=True, beine=True,
                    loecher=(), flaeche=True, rahmen=True, seiten=None, abdruck=0.0, staub=0.0, leiste=None):
    """Tafel wie in labor.py, aber zerlegbar:
    loecher   weggefressene Stellen der Schieferfläche (Hungriger Schwamm)
    flaeche   False: nur noch der leere Rahmen
    seiten    ((dx, dy, dreh), (dx, dy, dreh)) für linke und rechte Rahmenleiste: lose, verschoben
              und gedreht (Immer mehr); None: Rahmen am Stück
    leiste    Länge der Ober- und Unterleiste bei losen Seiten (None: ganze Breite)
    abdruck   0..1 Frisur-Abdruck im Kreidestaub (Klapptafel)
    staub     0..1 Kreidestaub-Schleier auf der Fläche
    """
    p.setPen(KEIN_STIFT)
    f = tafel_flaeche(b, h, unten)
    if beine:
        tafel_beine(p, b, h, unten, kurz=not flaeche)
    if rahmen and seiten is None:
        p.setBrush(linear(0, f.top() - 6, 0, f.bottom() + 6, HOLZ.lighter(115), HOLZ_DUNKEL))
        pfad = QPainterPath()
        pfad.addRoundedRect(f.adjusted(-6, -6, 6, 6), 3, 3)
        p.drawPath(pfad.subtracted(schiefer_pfad(f)))
        p.setBrush(QColor(40, 25, 10, 90))
        p.drawPath(schiefer_pfad(f.adjusted(-1, -1, 1, 1)).subtracted(schiefer_pfad(f)))
    elif rahmen:
        # Ober- und Unterleiste fest, Seitenleisten lose
        lb = f.width() - 4 if leiste is None else leiste
        p.setBrush(linear(0, f.top() - 6, 0, f.top(), HOLZ.lighter(120), HOLZ))
        p.drawRoundedRect(QRectF(f.center().x() - lb / 2, f.top() - 6, lb, 6), 2, 2)
        p.setBrush(linear(0, f.bottom(), 0, f.bottom() + 6, HOLZ, HOLZ_DUNKEL))
        p.drawRoundedRect(QRectF(f.center().x() - lb / 2, f.bottom(), lb, 6), 2, 2)
    if flaeche:
        pfad = schiefer_pfad(f, loecher)
        p.setBrush(linear(f.left(), f.top(), f.right(), f.bottom(), SCHIEFER.lighter(115), SCHIEFER_DUNKEL))
        p.drawPath(pfad)
        p.save()
        p.setClipPath(pfad)
        p.setBrush(QColor(255, 255, 255, 14))
        for k in range(4):
            p.drawEllipse(QPointF(f.left() + (0.2 + 0.2 * k) * f.width(),
                                  f.top() + (0.3 + 0.13 * (k % 3)) * f.height()), 18, 7)
        for x, y, r in wisch:
            p.setBrush(radial(x, y, r, QColor(220, 230, 225, 70), QColor(220, 230, 225, 0)))
            p.drawEllipse(QPointF(x, y), r * 1.4, r)
        if staub > 0:
            p.setBrush(QColor(230, 235, 228, int(70 * staub)))
            p.drawRect(f)
        if abdruck > 0:
            zeichne_frisur_abdruck(p, f.right() - 30, f.bottom() - 24, abdruck)
        p.restore()
    if rahmen and seiten is not None:
        for (dx, dy, dreh), x in zip(seiten, (f.left() - 3, f.right() + 3)):
            p.save()
            # Drehpunkt unten: die Leiste klappt oben nach außen weg
            p.translate(x + dx, f.bottom() + 6 + dy)
            p.rotate(dreh)
            p.setBrush(linear(-3, 0, 3, 0, HOLZ.lighter(115), HOLZ_DUNKEL))
            p.drawRoundedRect(QRectF(-3.5, -f.height() - 12, 7, f.height() + 12), 2.5, 2.5)
            p.setBrush(QColor(60, 40, 20, 160))
            kreis(p, 0, -f.height() - 8, 1.2)
            kreis(p, 0, -4, 1.2)
            p.restore()
    # Ablage mit Kreide und Schwamm
    p.setBrush(linear(0, f.bottom() + 4, 0, f.bottom() + 11, HOLZ.lighter(120), HOLZ_DUNKEL))
    p.drawRoundedRect(QRectF(f.left() - 4, f.bottom() + 5, f.width() + 8, 6), 2, 2)
    if kreide:
        p.setBrush(KREIDE_HELL)
        p.drawRoundedRect(QRectF(f.left() + 14, f.bottom() + 1, 14, 4.5), 2, 2)
    if schwamm:
        zeichne_schwamm(p, f.right() - 26, f.bottom() + 5)


def zeichne_frisur_abdruck(p, x, y, staerke=1.0):
    """Abdruck einer wirren Frisur im Kreidestaub: Kopfrund mit strahlenförmigen Büscheln."""
    a = int(150 * staerke)
    p.setPen(KEIN_STIFT)
    p.setBrush(radial(x, y, 30, QColor(235, 238, 230, a), QColor(235, 238, 230, 0)))
    p.drawEllipse(QPointF(x, y), 30, 26)
    farbe = QColor(240, 242, 236, int(200 * staerke))
    zufall = random.Random(7)
    for k in range(13):
        w = math.radians(-170 + k * 160 / 12)
        l = zufall.uniform(16, 26)
        bx, by = x + math.cos(w) * 11, y + math.sin(w) * 9
        sx, sy = x + math.cos(w) * (11 + l), y + math.sin(w) * (9 + l)
        pfad = QPainterPath()
        n = QPointF(-math.sin(w) * 3.5, math.cos(w) * 3.5)
        pfad.moveTo(bx + n.x(), by + n.y())
        pfad.quadTo(bx + (sx - bx) * 0.5 + n.x() * 0.4, by + (sy - by) * 0.5 + n.y() * 0.4 + 2, sx, sy)
        pfad.quadTo(bx + (sx - bx) * 0.5 - n.x() * 0.4, by + (sy - by) * 0.5 - n.y() * 0.4, bx - n.x(), by - n.y())
        pfad.closeSubpath()
        p.setBrush(farbe)
        p.drawPath(pfad)
    # Mützenzipfel und Brillengläser als blanke Stellen
    p.setBrush(QColor(47, 74, 62, int(220 * staerke)))
    p.drawEllipse(QPointF(x - 6, y + 6), 4.5, 4.5)
    p.drawEllipse(QPointF(x + 6, y + 6), 4.5, 4.5)


# ---------------------------------------------------------------- Kreide

def zeichne_dicke_kreide(p, x, y, winkel=0.0, laenge=58, dicke=15):
    """Armdicke Kreide mit runden Enden und Glanz, Mitte bei (x, y)."""
    p.setPen(KEIN_STIFT)
    p.save()
    p.translate(x, y)
    p.rotate(winkel)
    r = QRectF(-laenge / 2, -dicke / 2, laenge, dicke)
    p.setPen(stift(QColor('#8A8270'), 1.6))
    p.setBrush(linear(0, -dicke / 2, 0, dicke / 2, QColor('#FFFFFF'), QColor('#CFCBBE')))
    p.drawRoundedRect(r, dicke / 2.2, dicke / 2.2)
    p.setPen(KEIN_STIFT)
    p.setBrush(QColor(255, 255, 255, 170))
    p.drawRoundedRect(QRectF(-laenge / 2 + 5, -dicke / 2 + 2, laenge - 12, dicke * 0.22), 1.5, 1.5)
    p.setBrush(QColor(180, 175, 160, 120))
    p.drawEllipse(QPointF(laenge / 2 - dicke * 0.3, 0), dicke * 0.22, dicke * 0.42)
    p.restore()


def zeichne_stummel(p, x, y, winkel=0.0, laenge=13):
    p.save()
    p.translate(x, y)
    p.rotate(winkel)
    p.setPen(stift(QColor('#9A9484'), 0.8))
    p.setBrush(KREIDE_HELL)
    p.drawRoundedRect(QRectF(-laenge / 2, -3.3, laenge, 6.6), 2.5, 2.5)
    p.setPen(KEIN_STIFT)
    p.restore()


def zeichne_stummelhaufen(p, x, stummel):
    """Haufen abgebrochener Kreidestücke am Boden; stummel: Liste (dx, dy, winkel)."""
    p.setPen(KEIN_STIFT)
    if stummel:
        n = len(stummel)
        p.setBrush(radial(x, -1, 10 + n, QColor(240, 240, 232, 120), QColor(240, 240, 232, 0)))
        p.drawEllipse(QPointF(x, -1), 10 + n * 1.5, 3 + n * 0.3)
    for dx, dy, w in stummel:
        zeichne_stummel(p, x + dx, dy, w)


def zeichne_schlaffe_kreide(p, x, y, schlaff=1.0, richtung=1, t=0.0):
    """Kreide, die wie erschöpft durchhängt (Geisterkreide): Griff bei (x, y)."""
    p.setPen(KEIN_STIFT)
    p.save()
    p.translate(x, y)
    p.scale(richtung * 1.7, 1.7)
    pendel = math.sin(t * 2.2) * 4 * schlaff
    knick = 75 * schlaff
    pfad = QPainterPath()
    l = 13
    pts = []
    for k in range(7):
        u = k / 6
        w = math.radians(-20 + (knick + pendel) * u * u)
        pts.append((math.cos(w) * l * u, math.sin(w) * l * u + 2 * schlaff * u))
    links = [(px, py - 2.3) for px, py in pts]
    rechts = [(px, py + 2.3) for px, py in pts]
    pfad.moveTo(*links[0])
    for q in links[1:]:
        pfad.lineTo(*q)
    pfad.quadTo(pts[-1][0] + 3, pts[-1][1], *rechts[-1])
    for q in reversed(rechts[:-1]):
        pfad.lineTo(*q)
    pfad.closeSubpath()
    p.setPen(stift(QColor('#8A8270'), 0.7))
    p.setBrush(KREIDE_HELL)
    p.drawPath(pfad)
    p.setPen(KEIN_STIFT)
    p.setBrush(QColor(0, 0, 0, 30))
    for q in rechts[1:-1]:
        kreis(p, q[0], q[1] - 0.6, 0.9)
    p.restore()


def zeichne_quietsch(p, x, y, t, staerke=1.0):
    """Zitternde Bögen um die Kreidespitze: hier quietscht es."""
    if staerke <= 0:
        return
    p.setBrush(KEIN_PINSEL)
    for k in range(3):
        r = 8 + k * 6 + 2 * math.sin(t * 40 + k)
        a = int(220 * staerke * (1 - k * 0.25))
        p.setPen(stift(QColor(255, 250, 220, a), 2.2))
        for mitte in (-45, 135):
            p.drawArc(QRectF(x - r, y - r, 2 * r, 2 * r), int((mitte - 28) * 16), int(56 * 16))
    p.setPen(KEIN_STIFT)


def zeichne_zacken(p, x, y, laenge, winkel, t, farbe=QColor(255, 250, 220, 220)):
    """Kurzer Zickzack-Strich (Zittern, Vibration)."""
    p.save()
    p.translate(x, y)
    p.rotate(winkel)
    pfad = QPainterPath()
    pfad.moveTo(0, 0)
    n = 5
    for k in range(1, n + 1):
        pfad.lineTo(laenge * k / n, (2.4 if k % 2 else -2.4) * (1 + 0.3 * math.sin(t * 50)))
    p.setPen(stift(farbe, 2.0))
    p.setBrush(KEIN_PINSEL)
    p.drawPath(pfad)
    p.setPen(KEIN_STIFT)
    p.restore()


# ---------------------------------------------------------------- Riss

def riss_punkte(f, saat=5, n=9):
    """Gezackte Linie von oben nach unten durch die Tafelmitte (Tafel-Einheiten)."""
    zufall = random.Random(saat)
    pts = []
    for k in range(n + 1):
        y = f.top() - 8 + (f.height() + 16) * k / n
        x = f.center().x() + (0 if k in (0, n) else zufall.uniform(-7, 7))
        pts.append((x, y))
    return pts


def haelfte_pfad(punkte, seite, weit=300):
    """Fläche links (seite -1) oder rechts (seite 1) der Risslinie, nach unten bis zum Boden."""
    pfad = QPainterPath()
    pfad.moveTo(punkte[0][0], -weit)
    for q in punkte:
        pfad.lineTo(*q)
    pfad.lineTo(punkte[-1][0], 10)
    pfad.lineTo(seite * weit, 10)
    pfad.lineTo(seite * weit, -weit)
    pfad.closeSubpath()
    return pfad


def zeichne_riss(p, punkte, anteil):
    """Wachsender Riss (dunkler Spalt mit hellem Rand)."""
    if anteil <= 0:
        return
    n = max(1, int(len(punkte) * anteil))
    pfad = QPainterPath()
    pfad.moveTo(*punkte[0])
    for q in punkte[1:n + 1]:
        pfad.lineTo(*q)
    p.setBrush(KEIN_PINSEL)
    p.setPen(stift(QColor(230, 220, 200, 200), 3.2))
    p.drawPath(pfad)
    p.setPen(stift(QColor(15, 20, 15), 1.8))
    p.drawPath(pfad)
    p.setPen(KEIN_STIFT)


# ---------------------------------------------------------------- Fellkugel

def zeichne_fellkugel(p, r, t, hell, dunkel, bauch, sorge=1.0):
    """Katze als gesträubte Fellkugel (Fuß im Ursprung, Blick nach rechts): Stacheln, Ohren,
    große Augen und ein senkrecht abstehender Schwanz."""
    p.setPen(KEIN_STIFT)
    cy = -r - 2
    # Schwanz wie eine Flaschenbürste
    p.save()
    p.translate(-r * 0.7, cy - r * 0.3)
    p.rotate(-25 + 3 * math.sin(t * 30))
    for k in range(9):
        y = -k * r * 0.12
        l = r * 0.32 * (1 - k / 14)
        p.setBrush(hell if k % 2 else dunkel)
        p.drawEllipse(QPointF(0, y), l * 0.7, l * 0.5)
    p.restore()
    # Stacheln
    zufall = random.Random(11)
    for k in range(34):
        w = 2 * math.pi * k / 34 + zufall.uniform(-0.05, 0.05)
        l = r * zufall.uniform(1.18, 1.42) * (1 + 0.04 * math.sin(t * 45 + k))
        pfad = QPainterPath()
        b = 0.12
        pfad.moveTo(math.cos(w - b) * r * 0.9, cy + math.sin(w - b) * r * 0.9)
        pfad.lineTo(math.cos(w) * l, cy + math.sin(w) * l)
        pfad.lineTo(math.cos(w + b) * r * 0.9, cy + math.sin(w + b) * r * 0.9)
        pfad.closeSubpath()
        p.setBrush(dunkel if k % 3 == 0 else hell)
        p.drawPath(pfad)
    p.setBrush(radial(-r * 0.3, cy - r * 0.35, r * 1.3, hell.lighter(115), dunkel))
    kreis(p, 0, cy, r)
    # Streifen
    p.setBrush(QColor(dunkel.red(), dunkel.green(), dunkel.blue(), 150))
    for k in range(3):
        p.save()
        p.translate(-r * 0.15 + k * r * 0.18, cy - r * 0.78)
        p.rotate(-12 + k * 12)
        p.drawRoundedRect(QRectF(-2, 0, 4, r * 0.32), 2, 2)
        p.restore()
    # Pfötchen
    p.setBrush(bauch)
    for dx in (-0.35, 0.3):
        p.drawEllipse(QPointF(dx * r, -3), r * 0.2, r * 0.13)
    # Ohren, flach angelegt
    for ox, w in ((0.25, 30), (0.62, 55)):
        p.save()
        p.translate(ox * r, cy - r * 0.86)
        p.rotate(w)
        ohr = QPainterPath()
        ohr.moveTo(-6, 2)
        ohr.lineTo(0, -12)
        ohr.lineTo(6, 2)
        ohr.closeSubpath()
        p.setBrush(dunkel)
        p.drawPath(ohr)
        p.restore()
    # Schnauze und riesige Augen
    p.setBrush(bauch)
    p.drawEllipse(QPointF(r * 0.55, cy + r * 0.25), r * 0.32, r * 0.22)
    for ax in (0.2, 0.58):
        p.setBrush(WEISS)
        kreis(p, ax * r, cy - r * 0.18, r * 0.2)
        p.setBrush(QColor('#2B2B2B'))
        kreis(p, ax * r + 1, cy - r * 0.17, r * 0.07 + 0.6 * math.sin(t * 9) ** 2)
        p.setBrush(WEISS)
        kreis(p, ax * r - 0.5, cy - r * 0.22, r * 0.035)
    p.setBrush(QColor('#E87A8A'))
    kreis(p, r * 0.72, cy + r * 0.14, r * 0.06)
    p.setPen(stift(QColor(60, 40, 30), 1.0))
    p.setBrush(KEIN_PINSEL)
    for k in (-1, 1):
        p.drawLine(QPointF(r * 0.8, cy + r * 0.25), QPointF(r * 1.25, cy + r * (0.2 + 0.1 * k)))
    p.setPen(KEIN_STIFT)


def zeichne_anschriebe(p, anschriebe, clip=None):
    """Kreideschrift wie in TafelSzene.zeichne_tafel (Objekte mit text, x, y, hoehe, striche,
    anteil, deck, durch, dreh); clip: Pfad, außerhalb dessen nichts erscheint."""
    from .labor import anschrieb_breite, zeichne_striche
    p.save()
    if clip is not None:
        p.setClipPath(clip, Qt.ClipOperation.IntersectClip)
    for a in anschriebe:
        if a.deck <= 0 or a.anteil <= 0:
            continue
        p.save()
        breite = anschrieb_breite(a.text, a.hoehe)
        if a.dreh:
            mx, my = a.x + breite / 2, a.y + a.hoehe / 2
            p.translate(mx, my)
            p.rotate(a.dreh)
            p.translate(-mx, -my)
        farbe = QColor(KREIDE)
        farbe.setAlphaF(farbe.alphaF() * a.deck)
        zeichne_striche(p, a.striche, a.anteil, farbe, getattr(a, 'dicke', 2.2 * a.hoehe / 22))
        if a.durch > 0:
            p.setPen(stift(farbe, 2.4))
            y = a.y + a.hoehe * 0.55
            p.drawLine(QPointF(a.x - 3, y + 3), QPointF(a.x - 3 + (breite + 6) * a.durch, y - 3))
            p.setPen(KEIN_STIFT)
        p.restore()
    p.restore()


class KatzeKugel:
    """Katze, die sich vor Schreck zur Fellkugel aufplustert: d.kugel 0..1 überblendet von der
    normalen Katze (Katze aus figuren.py, mit d.buckel) zur runden Kugel; hüpft beim Gehen."""
    KASTEN = QRectF(-82, -126, 172, 132)
    KOPF = (40, -120)

    @staticmethod
    def zeichne(p, d):
        from .figuren import KATER, Katze
        kugel = getattr(d, 'kugel', 0.0)
        if kugel < 1:
            p.save()
            if kugel > 0:
                p.setOpacity(1 - kugel)
            Katze.zeichne(p, d)
            p.restore()
        if kugel > 0:
            hell, dunkel, bauch = getattr(d, 'fell', KATER)
            hopp = abs(math.sin(d.phase * 1.6)) * 14 if getattr(d, 'phase', 0) else 0.0
            p.save()
            p.setOpacity(min(1.0, kugel * 1.5))
            p.translate(0, -hopp)
            zeichne_fellkugel(p, 26 + 18 * kugel, d.t, hell, dunkel, bauch)
            p.restore()


class WeihnachtsmannOhneSack:
    """Der Weihnachtsmann aus figuren.py, aber immer ohne Sack (für Schritte, die eigene Posen setzen)."""
    KASTEN = QRectF(-110, -262, 200, 268)
    KOPF = (6, -262)

    @staticmethod
    def zeichne(p, d):
        from dataclasses import replace
        from .figur import zeichne_weihnachtsmann
        zeichne_weihnachtsmann(p, replace(d.pose, sack=False))
