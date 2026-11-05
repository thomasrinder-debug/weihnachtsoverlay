"""Tafel-Varianten und Kreide-Requisiten für die Tafel-Szenen des Professors
(Unzerbrechliche Kreide, Radikaler Schwamm).

Alle in Zeichen-Einheiten, Boden der Tafel mittig im Ursprung, wie in labor.py.
"""
import random

from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import QColor, QPainterPath

from .grundlagen import *  # noqa: F401,F403  Farben und Hilfen
from .labor import (HOLZ, HOLZ_DUNKEL, SCHIEFER, SCHIEFER_DUNKEL, TAFEL_B, TAFEL_H, TAFEL_UNTEN,
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
                    loecher=(), flaeche=True):
    """Tafel wie in labor.py, aber zerlegbar:
    loecher   weggewischte Stellen der Schieferfläche (Liste (x, y, r))
    flaeche   False: nur noch der leere Rahmen
    """
    p.setPen(KEIN_STIFT)
    f = tafel_flaeche(b, h, unten)
    if beine:
        tafel_beine(p, b, h, unten, kurz=not flaeche)
    p.setBrush(linear(0, f.top() - 6, 0, f.bottom() + 6, HOLZ.lighter(115), HOLZ_DUNKEL))
    pfad = QPainterPath()
    pfad.addRoundedRect(f.adjusted(-6, -6, 6, 6), 3, 3)
    p.drawPath(pfad.subtracted(schiefer_pfad(f)))
    p.setBrush(QColor(40, 25, 10, 90))
    p.drawPath(schiefer_pfad(f.adjusted(-1, -1, 1, 1)).subtracted(schiefer_pfad(f)))
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
        p.restore()
    # Ablage mit Kreide und Schwamm
    p.setBrush(linear(0, f.bottom() + 4, 0, f.bottom() + 11, HOLZ.lighter(120), HOLZ_DUNKEL))
    p.drawRoundedRect(QRectF(f.left() - 4, f.bottom() + 5, f.width() + 8, 6), 2, 2)
    if kreide:
        p.setBrush(KREIDE_HELL)
        p.drawRoundedRect(QRectF(f.left() + 14, f.bottom() + 1, 14, 4.5), 2, 2)
    if schwamm:
        zeichne_schwamm(p, f.right() - 26, f.bottom() + 5)


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
