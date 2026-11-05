"""Requisiten für die Computer-Szenen des Professors (Gruppe E): Drucker mit Papier,
wandelnde Schuhe, Mauszeiger, Eisblock.

Alle in Zeichen-Einheiten, Boden mittig im Ursprung, wie in labor.py.
"""
import math
import random

from PyQt6.QtCore import QPointF, QRectF
from PyQt6.QtGui import QColor, QPainterPath

from .grundlagen import *  # noqa: F401,F403  Farben und Hilfen
from .professor import HANDSCHUH, HANDSCHUH_DUNKEL, HOSE, KITTEL, KITTEL_SCHATTEN, SCHUH

PAPIER = QColor('#FBFBF7')
PAPIER_SCHATTEN = QColor('#D9DBE0')
EIS_HELL = QColor(225, 245, 255, 150)
EIS_DUNKEL = QColor(140, 200, 235, 170)


# ---------------------------------------------------------------- Drucker und Papier

def zeichne_drucker(p, x, y, t=0.0, laeuft=0.0, wut=0.0, kaputt=0.0, seite=1):
    """Bürodrucker, Boden mittig bei (x, y), Ausgabeschlitz zur Seite 'seite' (+1 rechts).
    laeuft 0..1: rattert, wut 0..1: tobt (Lämpchen rot), kaputt 0..1: Ruß."""
    p.setPen(KEIN_STIFT)
    p.save()
    p.translate(x, y)
    p.scale(seite, 1)
    p.setBrush(QColor(0, 0, 0, 45))
    p.drawEllipse(QRectF(-48, -3, 96, 6))
    zitter = (math.sin(t * 55) * 0.8 * laeuft + math.sin(t * 71) * 2.2 * wut)
    p.translate(zitter, -abs(math.sin(t * 38)) * 2.5 * wut)
    # Papiereinzug hinten oben
    p.save()
    p.translate(-26, -46)
    p.rotate(-22)
    p.setBrush(linear(0, -26, 0, 0, QColor('#8E939C'), QColor('#5F646D')))
    p.drawRoundedRect(QRectF(-14, -28, 30, 30), 2, 2)
    p.setBrush(PAPIER)
    for k in range(3):
        p.drawRect(QRectF(-11 + k, -34 + k * 1.2, 24, 30))
    p.restore()
    # Gehäuse
    p.setBrush(linear(-40, -48, 40, 0, QColor('#E8EAEE'), QColor('#9EA3AC')))
    p.drawRoundedRect(QRectF(-42, -50, 84, 50), 6, 6)
    p.setBrush(QColor('#5F646D'))
    p.drawRoundedRect(QRectF(-42, -10, 84, 10), 4, 4)
    p.setBrush(QColor(255, 255, 255, 90))
    p.drawRoundedRect(QRectF(-38, -48, 60, 4), 2, 2)
    # Schlitz und Ablage zur Seite
    p.setBrush(QColor('#24272D'))
    p.drawRoundedRect(QRectF(26, -30, 17, 5), 2, 2)
    p.setBrush(linear(40, -26, 62, -18, QColor('#B4B9C2'), QColor('#7A808A')))
    ab = QPainterPath()
    ab.moveTo(40, -26)
    ab.lineTo(64, -20)
    ab.lineTo(64, -17)
    ab.lineTo(40, -22)
    ab.closeSubpath()
    p.drawPath(ab)
    # Bedienfeld: Anzeige, Lämpchen, großer Knopf
    p.setBrush(QColor('#2A2F38'))
    p.drawRoundedRect(QRectF(-30, -40, 26, 12), 2, 2)
    if laeuft or wut:
        p.setBrush(QColor(110, 230, 160, 200) if wut < 0.5 else QColor(255, 90, 80, 220))
        breite = 22 * ((t * 1.5) % 1)
        p.drawRect(QRectF(-28, -36, breite, 4))
    blink = (t * 4) % 1 < 0.5
    if wut > 0.3:
        p.setBrush(QColor('#FF4A3C') if blink else QColor('#7A2018'))
    else:
        p.setBrush(QColor('#4DCB6A') if (laeuft and blink) or not laeuft else QColor('#2A5A34'))
    kreis(p, 4, -34, 2.4)
    p.setBrush(radial(15, -36, 6, QColor('#7FE08F'), QColor('#2E8A44')))
    kreis(p, 15, -34, 4.5)
    p.setBrush(QColor(255, 255, 255, 120))
    kreis(p, 13.5, -35.5, 1.4)
    if kaputt > 0:
        p.setBrush(QColor(40, 34, 30, int(160 * kaputt)))
        p.drawEllipse(QPointF(0, -50), 22 * kaputt, 7 * kaputt)
        p.drawEllipse(QPointF(30, -28), 10 * kaputt, 6 * kaputt)
    p.restore()


def drucker_schlitz(x, y, s, seite=1):
    """Weltpunkt des Ausgabeschlitzes für zeichne_drucker bei (x, y) in Weltkoordinaten."""
    return x + seite * 44 * s, y - 27 * s


def zeichne_blatt(p, x, y, winkel=0.0, flattern=1.0, bild=True):
    """Ein Blatt Papier, Mitte bei (x, y); flattern: Breite durch Drehung (1 flach, 0 hochkant).
    Statt Schrift ein kleines Balkendiagramm."""
    p.setPen(KEIN_STIFT)
    p.save()
    p.translate(x, y)
    p.rotate(winkel)
    p.scale(max(0.08, flattern), 1)
    p.setBrush(QColor(0, 0, 0, 30))
    p.drawRect(QRectF(-11, -14, 24, 30))
    p.setBrush(linear(-12, -15, 12, 15, PAPIER, PAPIER_SCHATTEN))
    p.drawRect(QRectF(-12, -15, 24, 30))
    if bild:
        for k, h in enumerate((8, 13, 6, 16)):
            p.setBrush(QColor(('#4FB4FF', '#FF4F6A', '#5BE36B', '#FFB43C')[k]))
            p.drawRect(QRectF(-8 + k * 4.5, 9 - h, 3, h))
        p.setBrush(QColor('#9AA0AA'))
        p.drawRect(QRectF(-9, 9.5, 18, 0.8))
    p.restore()


def zeichne_papierberg(p, x, y, hoehe, breite=150, saat=4):
    """Haufen aus wild durcheinanderliegenden Blättern, Boden mittig bei (x, y)."""
    if hoehe <= 1:
        return
    p.setPen(KEIN_STIFT)
    z = random.Random(saat)
    halb = breite / 2 * min(1.0, 0.45 + hoehe / 140)

    def profil(u):           # u in -1..1
        return hoehe * (1 - u * u) ** 0.7

    berg = QPainterPath()
    berg.moveTo(x - halb, y)
    for k in range(21):
        u = -1 + k / 10
        berg.lineTo(x + u * halb, y - profil(u) - 3 * math.sin(k * 2.3))
    berg.lineTo(x + halb, y)
    berg.closeSubpath()
    p.setBrush(QColor(0, 0, 0, 40))
    p.drawEllipse(QRectF(x - halb * 1.1, y - 4, halb * 2.2, 8))
    p.setBrush(linear(x, y - hoehe, x, y, PAPIER, QColor('#C9CCD3')))
    p.drawPath(berg)
    n = int(14 + hoehe * 0.5)
    for i in range(n):
        u = z.uniform(-0.95, 0.95)
        oben = profil(u)
        v = z.random() ** 0.6
        bx = x + u * halb
        by = y - oben * v
        w = z.uniform(-60, 60)
        p.save()
        p.translate(bx, by)
        p.rotate(w)
        p.setBrush(QColor(0, 0, 0, 22))
        p.drawRect(QRectF(-10, -6, 22, 14))
        p.setBrush(PAPIER if i % 3 else QColor('#F1F2EC'))
        p.drawRect(QRectF(-11, -7, 22, 14))
        if i % 4 == 0:
            p.setBrush(QColor(('#4FB4FF', '#FF4F6A', '#5BE36B')[i % 3]))
            p.drawRect(QRectF(-6, -1, 2.5, 5))
            p.drawRect(QRectF(-2, -3, 2.5, 7))
        p.restore()


def zeichne_winkehand(p, x, y, winkel, laenge=30):
    """Ärmel mit gelbem Gummihandschuh, ragt bei (x, y) nach oben; winkel 0 = senkrecht."""
    p.setPen(KEIN_STIFT)
    p.save()
    p.translate(x, y)
    p.rotate(winkel)
    p.setBrush(linear(-8, 0, 8, 0, KITTEL, KITTEL_SCHATTEN))
    p.drawRoundedRect(QRectF(-8, -laenge, 16, laenge + 10), 7, 7)
    p.setBrush(KITTEL_SCHATTEN)
    p.drawRoundedRect(QRectF(-8.5, -laenge - 2, 17, 6), 3, 3)
    p.setBrush(radial(-2, -laenge - 12, 12, HANDSCHUH.lighter(125), HANDSCHUH_DUNKEL))
    p.drawRoundedRect(QRectF(-6.5, -laenge - 8, 13, 7), 3, 3)
    kreis(p, 0, -laenge - 13, 7.5)
    for k, (dx, dy) in enumerate(((-6, -20), (-2, -23), (2.5, -23), (6.5, -20))):
        p.drawRoundedRect(QRectF(dx - 2, -laenge + dy - 3, 4, 9), 2, 2)
    p.drawEllipse(QPointF(-8, -laenge - 10), 4.5, 3)
    p.setBrush(QColor(255, 255, 255, 80))
    kreis(p, -3, -laenge - 16, 2)
    p.restore()


def zeichne_schuhe(p, x, y, hoehe, phase=0.0, richtung=1):
    """Zwei Hosenbeine mit Schuhen, die unter einem Haufen hervorschauen und schlurfen.
    Boden mittig bei (x, y), Beine hoehe Einheiten sichtbar, Spitzen zur Seite richtung."""
    if hoehe <= 0:
        return
    p.setPen(KEIN_STIFT)
    p.save()
    p.translate(x, y)
    p.scale(richtung, 1)
    for k, versatz in enumerate((-15, 13)):
        sw = math.sin(phase + k * math.pi)
        fx = versatz + 9 * sw
        fy = -5 * max(0.0, sw)
        d = 125 if k == 0 else 100
        p.setBrush(linear(fx - 7, 0, fx + 7, 0, HOSE.lighter(130).darker(d), HOSE.darker(140).darker(d)))
        p.drawRoundedRect(QRectF(fx - 7, -hoehe - 8, 14, hoehe + 2 + fy), 5, 5)
        schuh = QPainterPath()
        schuh.moveTo(fx - 9, fy - 10)
        schuh.cubicTo(fx - 10, fy, fx - 4, fy, fx + 6, fy)
        schuh.cubicTo(fx + 18, fy, fx + 24, fy - 2, fx + 24, fy - 6)
        schuh.cubicTo(fx + 24, fy - 11, fx + 14, fy - 13, fx + 8, fy - 13)
        schuh.lineTo(fx - 7, fy - 13)
        schuh.closeSubpath()
        p.setBrush(linear(0, fy - 13, 0, fy, SCHUH.lighter(130).darker(d), SCHUH.darker(150).darker(d)))
        p.drawPath(schuh)
        p.setBrush(QColor('#2A1A10').darker(d))
        p.drawRoundedRect(QRectF(fx - 10, fy - 2.5, 35, 3), 1.5, 1.5)
    p.restore()


# ---------------------------------------------------------------- Mauszeiger

def zeichne_mauszeiger(p, x, y, groesse=1.0, winkel=0.0, beine=0.0, phase=0.0):
    """Schlichter weißer Pfeil mit dunklem Rand, Spitze bei (x, y);
    beine 0..1: kleine Strichbeinchen zum Weglaufen."""
    p.save()
    p.translate(x, y)
    p.rotate(winkel)
    p.scale(groesse, groesse)
    pfeil = QPainterPath()
    for i, (a, b) in enumerate(((0, 0), (0, 18), (4.2, 14), (7.5, 21), (10.2, 19.8), (7, 13), (12.5, 12.6))):
        pfeil.moveTo(a, b) if i == 0 else pfeil.lineTo(a, b)
    pfeil.closeSubpath()
    if beine > 0:
        p.setPen(stift(QColor('#1F1F1F'), 1.3))
        for k, (fx, fy) in enumerate(((3, 16), (8.5, 19.5))):
            w = math.sin(phase + k * math.pi) * 0.7
            p.drawLine(QPointF(fx, fy), QPointF(fx + math.sin(w) * 5 * beine, fy + math.cos(w) * 5 * beine))
    p.setPen(stift(QColor('#1F1F1F'), 1.4))
    p.setBrush(linear(0, 0, 10, 18, QColor('#FFFFFF'), QColor('#DCE3EA')))
    p.drawPath(pfeil)
    p.setPen(KEIN_STIFT)
    p.restore()


# ---------------------------------------------------------------- Eisblock

def zeichne_eisblock(p, x, y, b, h, anteil=1.0, rampe=1, t=0.0):
    """Eisblock um ein Gerät, Boden mittig bei (x, y), mit Eisrampe zur Seite 'rampe'.
    anteil 0..1: das Eis wächst von unten nach oben."""
    if anteil <= 0:
        return
    p.setPen(KEIN_STIFT)
    p.save()
    p.translate(x, y)
    p.scale(rampe, 1)
    hh = h * glatt(anteil)
    block = QPainterPath()
    block.moveTo(-b / 2, 0)
    block.lineTo(-b / 2, -hh + 6)
    block.quadTo(-b / 2, -hh, -b / 2 + 6, -hh)
    block.lineTo(b / 2 - 6, -hh)
    block.quadTo(b / 2, -hh, b / 2 + 2, -hh + 6)
    # Rampe: vom Blockrand weich zum Boden
    block.cubicTo(b / 2 + hh * 0.25, -hh * 0.55, b / 2 + hh * 0.55, -4, b / 2 + hh * 0.9, 0)
    block.closeSubpath()
    p.setBrush(linear(0, -hh, 0, 0, EIS_HELL, EIS_DUNKEL))
    p.drawPath(block)
    p.setPen(stift(QColor(245, 252, 255, 210), 1.6))
    p.setBrush(KEIN_PINSEL)
    p.drawPath(block)
    p.setPen(stift(QColor(255, 255, 255, 140), 2.2))
    p.drawLine(QPointF(-b / 2 + 8, -hh + 10), QPointF(-b / 2 + 8, -hh * 0.45))
    p.drawLine(QPointF(-b / 2 + 14, -hh + 10), QPointF(-b / 2 + 14, -hh + 22))
    p.setPen(KEIN_STIFT)
    p.setBrush(QColor(255, 255, 255, 90))
    p.drawRect(QRectF(-b / 2 + 4, -hh + 3, b * 0.5, 3))
    # Eiszapfen an der Oberkante
    if anteil > 0.8:
        p.setBrush(QColor(235, 250, 255, 200))
        for k, lang in enumerate((8, 5, 10, 6)):
            zx = -b / 2 + 10 + k * (b - 20) / 3
            z = QPainterPath()
            z.moveTo(zx - 3, -hh + 1)
            z.lineTo(zx + 3, -hh + 1)
            z.lineTo(zx, -hh + 1 + lang * (anteil - 0.8) * 5)
            z.closeSubpath()
            p.drawPath(z)
    p.setBrush(WEISS)
    for k in range(4):
        w = (t * 0.7 + k * 0.27) % 1
        if w < 0.3:
            stern(p, -b / 2 + 10 + (k * 37) % (b - 10), -hh * (0.2 + 0.2 * k), 3 * math.sin(w / 0.3 * math.pi))
    p.restore()
