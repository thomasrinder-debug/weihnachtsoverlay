"""Requisiten für Labor B: Magnet mit Galgen und Schaltkasten, Mikroskop mit Auge,
Balkenwaage mit Feder und Klotz, Ball und Kescher, Glasglocke und Schneeflöckchen.

Alle Funktionen zeichnen in Einheiten; der Aufrufer verschiebt und skaliert vorher.
"""
import math

from PyQt6.QtCore import QPointF, QRectF
from PyQt6.QtGui import QColor, QPainterPath

from .grundlagen import (GOLD, GOLD_HELL, KEIN_PINSEL, KEIN_STIFT, ROT, ROT_DUNKEL, ROT_HELL, SCHWARZ, WEISS, kreis,
                         linear, radial, stift)
from .labor import GLAS, GLAS_RAND, HOLZ, HOLZ_DUNKEL, METALL, METALL_DUNKEL

LACK = QColor('#E9EDF1')
BLAU_FELD = QColor(120, 200, 255)


# ---------------------------------------------------------------- Magnet

def zeichne_schwanenhals(p, hoehe, arm, rollen=True):
    """Magnetständer: Fuß mittig bei (0, 0), Säule mit geschwungenem Hals, der vorn bei
    (arm, -hoehe) im Gelenk für den Magneten endet."""
    p.setPen(KEIN_STIFT)
    p.setBrush(QColor(0, 0, 0, 45))
    p.drawEllipse(QRectF(-30, -3, 60, 6))
    p.setBrush(linear(0, -12, 0, 0, METALL, METALL_DUNKEL))
    p.drawRoundedRect(QRectF(-26, -12, 52, 9), 3, 3)
    if rollen:
        for x in (-18, 18):
            p.setBrush(radial(x - 1, -4, 6, QColor('#5A5F66'), QColor('#25282C')))
            kreis(p, x, -3, 4.5)
            p.setBrush(METALL)
            kreis(p, x, -3, 1.5)
    hals = QPainterPath()
    hals.moveTo(0, -10)
    hals.lineTo(0, -hoehe * 0.55)
    hals.cubicTo(0, -hoehe * 1.08, arm * 1.05, -hoehe * 1.12, arm, -hoehe + 4)
    p.setBrush(KEIN_PINSEL)
    p.setPen(stift(METALL_DUNKEL, 9))
    p.drawPath(hals)
    p.setPen(stift(METALL.lighter(115), 5))
    p.drawPath(hals)
    p.setPen(stift(QColor(255, 255, 255, 120), 1.6))
    p.drawPath(hals.translated(-1.5, -1))
    p.setPen(KEIN_STIFT)
    # Ringe am Hals und das Gelenk vorn
    for k in range(1, 6):
        q = hals.pointAtPercent(0.45 + k * 0.09)
        p.setBrush(METALL_DUNKEL)
        p.drawEllipse(q, 5.5, 5.5)
        p.setBrush(METALL)
        p.drawEllipse(q, 3.6, 3.6)
    p.setBrush(linear(arm - 3, 0, arm + 3, 0, METALL.lighter(110), METALL_DUNKEL))
    p.drawRect(QRectF(arm - 3, -hoehe + 3, 6, 14))
    p.setBrush(radial(arm - 1, -hoehe + 2, 7, METALL.lighter(120), METALL_DUNKEL))
    kreis(p, arm, -hoehe + 3, 6)


def zeichne_hufeisen(p, an=0.0, t=0.0, gross=1.0):
    """Hufeisenmagnet, Aufhängung bei (0, 0), Pole zeigen nach unten (Polenden bei y = 62)."""
    p.save()
    p.scale(gross, gross)
    p.setPen(KEIN_STIFT)
    if an > 0:
        p.setBrush(radial(0, 60, 46, QColor(150, 215, 255, int(110 * an)), QColor(150, 215, 255, 0)))
        kreis(p, 0, 60, 46)
    bogen = QPainterPath()
    bogen.moveTo(-30, 52)
    bogen.lineTo(-30, 30)
    bogen.cubicTo(-30, 4, 30, 4, 30, 30)
    bogen.lineTo(30, 52)
    bogen.lineTo(16, 52)
    bogen.lineTo(16, 30)
    bogen.cubicTo(16, 20, -16, 20, -16, 30)
    bogen.lineTo(-16, 52)
    bogen.closeSubpath()
    p.setBrush(linear(-30, 0, 30, 30, ROT_HELL, ROT_DUNKEL))
    p.drawPath(bogen)
    p.setBrush(QColor(255, 255, 255, 90))
    p.drawRoundedRect(QRectF(-27, 26, 3.5, 22), 1.5, 1.5)
    for x in (-30, 16):
        p.setBrush(linear(x, 0, x + 14, 0, LACK, METALL_DUNKEL))
        p.drawRect(QRectF(x, 50, 14, 12))
    # Spule mit Kupferdraht
    p.setBrush(linear(-10, 0, 10, 0, QColor('#E0904A'), QColor('#8A4A18')))
    p.drawRoundedRect(QRectF(-12, 7, 24, 12), 3, 3)
    p.setPen(stift(QColor('#6A3410'), 1.0))
    for k in range(5):
        p.drawLine(QPointF(-9 + k * 4.5, 8), QPointF(-9 + k * 4.5, 18))
    p.setPen(KEIN_STIFT)
    p.setBrush(METALL_DUNKEL)
    p.drawRect(QRectF(-2, -2, 4, 10))
    if an > 0:
        p.setPen(stift(QColor(170, 225, 255, int(200 * an)), 1.6))
        p.setBrush(KEIN_PINSEL)
        for k in range(3):
            u = (t * 1.6 + k / 3) % 1
            r = 6 + u * 28
            c = QColor(170, 225, 255, int(220 * an * (1 - u)))
            p.setPen(stift(c, 1.6))
            p.drawArc(QRectF(-r, 62 - r * 0.4, 2 * r, r * 1.2), 200 * 16, 140 * 16)
        p.setPen(KEIN_STIFT)
    p.restore()


def zeichne_schaltkasten(p, hebel=0.0, lampe=0.0, t=0.0):
    """Schaltpult auf einer Säule, Fuß mittig bei (0, 0); hebel 0 = aus (unten), 1 = an (oben)."""
    p.setPen(KEIN_STIFT)
    p.setBrush(QColor(0, 0, 0, 40))
    p.drawEllipse(QRectF(-20, -3, 40, 6))
    p.setBrush(linear(-14, 0, 14, 0, QColor('#6A7480'), QColor('#3A4048')))
    p.drawRoundedRect(QRectF(-16, -8, 32, 8), 2, 2)
    p.drawRect(QRectF(-4, -72, 8, 66))
    p.setBrush(linear(-20, -100, 20, -70, QColor('#F0C850'), QColor('#B08418')))
    p.drawRoundedRect(QRectF(-20, -100, 40, 30), 4, 4)
    p.setBrush(QColor('#2B2B2B'))
    for k in range(4):
        p.drawRect(QRectF(-16 + k * 4, -76, 2.5, 4))
    # Lampe
    farbe = QColor('#FF5040') if lampe > 0.5 else QColor('#802018')
    p.setBrush(radial(10, -86, 8, farbe.lighter(140), farbe))
    kreis(p, 11, -86, 4)
    if lampe > 0.5:
        p.setBrush(radial(11, -86, 14, QColor(255, 120, 90, 120), QColor(255, 120, 90, 0)))
        kreis(p, 11, -86, 14)
    # Hebel
    p.save()
    p.translate(-6, -96)
    p.rotate(-60 + 120 * hebel)
    p.setBrush(linear(-2, 0, 2, 0, METALL.lighter(120), METALL_DUNKEL))
    p.drawRect(QRectF(-2, -26, 4, 26))
    p.setBrush(radial(-2, -29, 7, QColor('#FF6060'), ROT_DUNKEL))
    kreis(p, 0, -28, 5.5)
    p.restore()
    p.setBrush(QColor('#3A3A3A'))
    kreis(p, -6, -96, 3.5)


def hebel_knauf(hebel):
    """Lage des Hebelknaufs in Einheiten (wie in zeichne_schaltkasten)."""
    w = math.radians(-60 + 120 * hebel)
    return -6 + math.sin(w) * 28, -96 - math.cos(w) * 28


# ---------------------------------------------------------------- Reagenzglas

def zeichne_reagenzglas(p, farbe, winkel=0.0, fuell=0.6, t=0.0):
    """Offenes Reagenzglas, Mitte bei (0, 0), Länge 36; winkel 0 = Öffnung oben."""
    p.save()
    p.rotate(winkel)
    p.setPen(KEIN_STIFT)
    pfad = QPainterPath()
    pfad.moveTo(-5, -18)
    pfad.lineTo(-5, 13)
    pfad.arcTo(QRectF(-5, 8, 10, 10), 180, 180)
    pfad.lineTo(5, -18)
    pfad.closeSubpath()
    p.setBrush(GLAS)
    p.drawPath(pfad)
    if fuell > 0:
        p.save()
        p.setClipPath(pfad)
        oben = 18 - 34 * fuell
        p.setBrush(linear(-5, 0, 5, 0, farbe.lighter(140), farbe.darker(130)))
        p.drawRect(QRectF(-6, oben + math.sin(t * 9) * 1.2, 12, 40))
        p.setBrush(QColor(255, 255, 255, 150))
        kreis(p, -1, 12, 1.2)
        kreis(p, 1.5, 6, 0.9)
        p.restore()
    p.setPen(stift(GLAS_RAND, 1.4))
    p.setBrush(KEIN_PINSEL)
    p.drawPath(pfad)
    p.drawLine(QPointF(-6.5, -18), QPointF(6.5, -18))
    p.setPen(stift(QColor(255, 255, 255, 200), 1.4))
    p.drawLine(QPointF(-2.5, -12), QPointF(-2.5, 8))
    p.setPen(KEIN_STIFT)
    p.restore()


def zeichne_klecks(p, farbe, laenge=1.0, t=0.0):
    """Herablaufende Flüssigkeit, Ausguss bei (0, 0), Tropfen bis laenge·30 nach unten."""
    p.setPen(KEIN_STIFT)
    for k, (dx, l) in enumerate(((-7, 1.0), (0, 0.6), (7, 0.85))):
        y1 = 30 * laenge * l
        p.setBrush(linear(0, 0, 0, y1, farbe.lighter(130), farbe))
        p.drawRoundedRect(QRectF(dx - 2.2, -2, 4.4, y1 + 2), 2.2, 2.2)
        kreis(p, dx, y1, 3.2)


# ---------------------------------------------------------------- Mikroskop

def zeichne_auge(p, x, y, r, offen=1.0, blick=(0.0, 0.0), ader=True):
    """Großes Auge, offen 0..1 (Lider), blick in -1..1."""
    if offen <= 0.02:
        p.setPen(stift(QColor('#5A3A30'), max(1.2, r * 0.12)))
        p.drawLine(QPointF(x - r, y), QPointF(x + r, y))
        p.setPen(KEIN_STIFT)
        return
    p.setPen(KEIN_STIFT)
    p.save()
    lid = QPainterPath()
    lid.addEllipse(QPointF(x, y), r, r * offen)
    p.setClipPath(lid)
    p.setBrush(radial(x - r * 0.3, y - r * 0.3, r * 1.4, WEISS, QColor('#E6D8D2')))
    kreis(p, x, y, r)
    if ader:
        p.setPen(stift(QColor(200, 60, 60, 120), max(0.6, r * 0.04)))
        for w in (10, 160, 200, 340):
            a = math.radians(w)
            p.drawLine(QPointF(x + math.cos(a) * r, y + math.sin(a) * r * 0.6),
                       QPointF(x + math.cos(a) * r * 0.6, y + math.sin(a) * r * 0.4))
        p.setPen(KEIN_STIFT)
    px, py = x + blick[0] * r * 0.4, y + blick[1] * r * 0.35
    p.setBrush(radial(px, py, r * 0.55, QColor('#7FC36A'), QColor('#2F6E3A')))
    kreis(p, px, py, r * 0.5)
    p.setBrush(SCHWARZ)
    kreis(p, px, py, r * 0.24)
    p.setBrush(WEISS)
    kreis(p, px + r * 0.16, py - r * 0.18, r * 0.11)
    p.restore()
    p.setPen(stift(QColor('#5A3A30'), max(1.2, r * 0.12)))
    p.setBrush(KEIN_PINSEL)
    p.drawArc(QRectF(x - r, y - r * offen, 2 * r, 2 * r * offen), 0, 180 * 16)
    p.setPen(stift(QColor('#5A3A30'), max(0.8, r * 0.06)))
    for k in (-0.5, 0, 0.5):
        a = math.pi / 2 + k * 0.9
        ax, ay = x - math.cos(a) * r * 0.9, y - math.sin(a) * r * offen * 0.95
        p.drawLine(QPointF(ax, ay), QPointF(ax - math.cos(a) * r * 0.25, ay - math.sin(a) * r * 0.25))
    p.setPen(KEIN_STIFT)


def mikroskop_okular(strecke=0.0, neig=0.0):
    """Lage der Okular-Öffnung in Einheiten (wie in zeichne_mikroskop)."""
    w = math.radians(neig)
    lx, ly = 0.0, -36 - 30 * strecke
    return 6 + lx * math.cos(w) - ly * math.sin(w), -58 + lx * math.sin(w) + ly * math.cos(w)


def zeichne_mikroskop(p, strecke=0.0, neig=0.0, auge=0.0, auge_oben=0.0, blick=(0, 0), knopf=0.0, oben_offen=1.0):
    """Mikroskop, Fuß mittig bei (0, 0), Blick nach rechts. strecke 0..1 reckt den Tubus,
    neig dreht ihn (Grad, positiv nach rechts), auge 0..1 Auge auf dem Objekttisch,
    auge_oben 0..1 Auge im Okular."""
    p.setPen(KEIN_STIFT)
    p.setBrush(QColor(0, 0, 0, 40))
    p.drawEllipse(QRectF(-24, -3, 48, 6))
    fuss = QPainterPath()
    fuss.moveTo(-22, 0)
    fuss.cubicTo(-24, -10, -10, -12, 0, -12)
    fuss.cubicTo(14, -12, 22, -8, 22, 0)
    fuss.closeSubpath()
    p.setBrush(linear(0, -12, 0, 0, QColor('#3E4A5C'), QColor('#1E2430')))
    p.drawPath(fuss)
    # Stativbogen
    arm = QPainterPath()
    arm.moveTo(-10, -10)
    arm.cubicTo(-22, -30, -20, -56, -2, -66)
    arm.lineTo(6, -58)
    arm.cubicTo(-8, -50, -8, -30, 0, -10)
    arm.closeSubpath()
    p.setBrush(linear(-20, 0, 6, 0, QColor('#56637A'), QColor('#2A3242')))
    p.drawPath(arm)
    # Objekttisch
    p.setBrush(linear(0, -34, 0, -28, QColor('#4A566A'), QColor('#222833')))
    p.drawRoundedRect(QRectF(-6, -34, 34, 6), 2, 2)
    p.setBrush(QColor(220, 240, 255, 150))
    p.drawRect(QRectF(4, -36, 20, 2.5))
    if auge > 0:
        zeichne_auge(p, 13, -44, 12, auge, blick)
    # Fokusknopf
    p.save()
    p.translate(-10, -30)
    p.rotate(knopf * 360)
    p.setBrush(radial(-1, -1, 6, QColor('#8C96A8'), QColor('#3A4250')))
    kreis(p, 0, 0, 5.5)
    p.setBrush(QColor('#2A3040'))
    p.drawRect(QRectF(-0.8, -5.5, 1.6, 4))
    p.restore()
    # Tubus (dreht um den Kopf des Stativs)
    p.save()
    p.translate(6, -58)
    p.rotate(neig)
    lang = 30 * strecke
    p.setBrush(linear(-6, 0, 6, 0, LACK, QColor('#8890A0')))
    p.drawRect(QRectF(-5, -30 - lang, 10, 24 + lang))
    p.setBrush(linear(-5, 0, 5, 0, QColor('#C8D0DC'), QColor('#6A7280')))
    for k in range(int(lang // 8)):
        p.drawRect(QRectF(-5.5, -12 - k * 8, 11, 2))
    p.setBrush(linear(-7, 0, 7, 0, QColor('#56637A'), QColor('#2A3242')))
    p.drawRoundedRect(QRectF(-7, -8, 14, 12), 3, 3)
    # Objektiv nach unten
    p.setBrush(linear(-3, 0, 3, 0, METALL, METALL_DUNKEL))
    p.drawRect(QRectF(2, 2, 6, 14))
    p.setBrush(QColor('#C8A040'))
    p.drawRect(QRectF(2, 12, 6, 2))
    # Okular
    p.setBrush(linear(-6, 0, 6, 0, QColor('#3A4252'), QColor('#161A22')))
    p.drawRoundedRect(QRectF(-6.5, -36 - lang, 13, 8), 2, 2)
    p.setBrush(QColor(120, 170, 220, 160))
    p.drawEllipse(QPointF(0, -36 - lang), 6, 2)
    if auge_oben > 0:
        p.save()
        p.translate(0, -44 - lang)
        p.setBrush(QColor('#2A3242'))
        p.drawEllipse(QPointF(0, 0), 14 * auge_oben, 13 * auge_oben)
        zeichne_auge(p, 0, 0, 12 * auge_oben, oben_offen * min(1.0, auge_oben * 1.4) if auge_oben > 0.3 else 0.02, blick)
        p.restore()
    p.restore()


# ---------------------------------------------------------------- Waage

def zeichne_waage(p, w, schale_l, schale_r, arm=58, hoehe=118):
    """Balkenwaage, Fuß mittig bei (0, 0); w in Grad (positiv: rechte Seite tiefer).
    schale_l/schale_r(p, x, y): zeichnen den Inhalt der Schale, Schalenmitte (x, y)."""
    p.setPen(KEIN_STIFT)
    p.setBrush(QColor(0, 0, 0, 45))
    p.drawEllipse(QRectF(-34, -3, 68, 6))
    p.setBrush(linear(0, -14, 0, 0, HOLZ.lighter(115), HOLZ_DUNKEL))
    p.drawRoundedRect(QRectF(-30, -12, 60, 11), 3, 3)
    for x in (-22, 22):
        p.setBrush(radial(x - 1, -3, 5, QColor('#5A5F66'), QColor('#25282C')))
        kreis(p, x, -2, 4)
    p.setBrush(linear(-4, 0, 4, 0, GOLD_HELL, GOLD.darker(130)))
    p.drawRect(QRectF(-3.5, -hoehe, 7, hoehe - 10))
    p.setBrush(GOLD)
    kreis(p, 0, -hoehe, 6)
    # Zeiger
    p.save()
    p.translate(0, -hoehe)
    p.rotate(w)
    p.setBrush(QColor('#7A4A10'))
    p.drawRect(QRectF(-1, 0, 2, 30))
    p.restore()
    a = math.radians(w)
    enden = []
    for seite in (-1, 1):
        ex = seite * arm * math.cos(a)
        ey = -hoehe + seite * arm * math.sin(a)
        enden.append((ex, ey))
    p.setPen(stift(GOLD.darker(115), 5))
    p.drawLine(QPointF(*enden[0]), QPointF(*enden[1]))
    p.setPen(stift(GOLD_HELL, 1.5))
    p.drawLine(QPointF(enden[0][0], enden[0][1] - 1.5), QPointF(enden[1][0], enden[1][1] - 1.5))
    p.setPen(KEIN_STIFT)
    p.setBrush(GOLD_HELL)
    kreis(p, 0, -hoehe, 3)
    for (ex, ey), inhalt in zip(enden, (schale_l, schale_r)):
        sy = ey + 52
        p.setPen(stift(QColor('#9A8A60'), 1.2))
        for dx in (-20, 0, 20):
            p.drawLine(QPointF(ex, ey), QPointF(ex + dx, sy))
        p.setPen(KEIN_STIFT)
        p.setBrush(GOLD.darker(115))
        kreis(p, ex, ey, 3)
        if inhalt:
            inhalt(p, ex, sy)
        zeichne_schale(p, ex, sy)
    return enden


def zeichne_schale(p, x, y):
    """Waagschale, Mitte des Rands bei (x, y)."""
    p.setPen(KEIN_STIFT)
    schale = QPainterPath()
    schale.moveTo(x - 24, y)
    schale.quadTo(x, y + 14, x + 24, y)
    schale.closeSubpath()
    p.setBrush(linear(x - 24, y, x + 24, y + 8, GOLD_HELL, GOLD.darker(130)))
    p.drawPath(schale)


def waage_schale(w, seite, arm=58, hoehe=118):
    """Mitte der Schale (seite -1 links, +1 rechts) in Einheiten."""
    a = math.radians(w)
    return seite * arm * math.cos(a), -hoehe + seite * arm * math.sin(a) + 52


def zeichne_klotz(p, x, y):
    """Schwerer Eisenklotz mit Griff, steht auf (x, y)."""
    p.setPen(KEIN_STIFT)
    k = QPainterPath()
    k.moveTo(x - 20, y)
    k.lineTo(x - 15, y - 30)
    k.lineTo(x + 15, y - 30)
    k.lineTo(x + 20, y)
    k.closeSubpath()
    p.setBrush(linear(x - 20, y - 30, x + 20, y, QColor('#6F7782'), QColor('#2C3038')))
    p.drawPath(k)
    p.setPen(stift(QColor('#3A3F48'), 4))
    p.setBrush(KEIN_PINSEL)
    p.drawArc(QRectF(x - 9, y - 40, 18, 18), 0, 180 * 16)
    p.setPen(stift(QColor(255, 255, 255, 70), 1.5))
    p.drawLine(QPointF(x - 13, y - 27), QPointF(x - 17, y - 4))
    p.setPen(KEIN_STIFT)
    p.setBrush(QColor(255, 255, 255, 40))
    p.drawRect(QRectF(x - 15, y - 30, 30, 3))


def zeichne_feder(p, x, y, winkel=0.0, laenge=34):
    """Weiße Feder, Kielende bei (x, y); winkel 0 = Spitze nach rechts."""
    p.save()
    p.translate(x, y)
    p.rotate(winkel)
    p.setPen(KEIN_STIFT)
    fahne = QPainterPath()
    fahne.moveTo(4, 0)
    fahne.cubicTo(10, -10, laenge * 0.7, -9, laenge, -1)
    fahne.cubicTo(laenge * 0.7, 6, 10, 7, 4, 0)
    p.setBrush(linear(0, -8, 0, 6, WEISS, QColor('#C8D2E0')))
    p.drawPath(fahne)
    p.setPen(stift(QColor('#B8C2D0'), 0.9))
    for k in range(5):
        u = 0.25 + k * 0.14
        p.drawLine(QPointF(laenge * u, -0.5), QPointF(laenge * u + 4, -6 + abs(k - 2)))
        p.drawLine(QPointF(laenge * u, 0.5), QPointF(laenge * u + 4, 5 - abs(k - 2)))
    p.setPen(stift(QColor('#9AA6B8'), 1.3))
    p.drawLine(QPointF(0, 0), QPointF(laenge - 2, -0.6))
    p.setPen(KEIN_STIFT)
    p.restore()


# ---------------------------------------------------------------- Ball und Kescher

def zeichne_ball(p, x, y, r, dreh=0.0, farbe=ROT, streifen=GOLD_HELL):
    """Bunter Ball mit Sternstreifen, damit man das Drehen sieht."""
    p.setPen(KEIN_STIFT)
    p.setBrush(radial(x - r * 0.35, y - r * 0.35, r * 1.5, farbe.lighter(150), farbe.darker(150)))
    kreis(p, x, y, r)
    p.save()
    clip = QPainterPath()
    clip.addEllipse(QPointF(x, y), r, r)
    p.setClipPath(clip)
    p.translate(x, y)
    p.rotate(dreh)
    p.setBrush(streifen)
    p.drawRect(QRectF(-r, -r * 0.22, 2 * r, r * 0.44))
    p.setBrush(WEISS)
    p.drawEllipse(QPointF(r * 0.45, -r * 0.55), r * 0.18, r * 0.18)
    p.restore()
    p.setBrush(QColor(255, 255, 255, 150))
    p.drawEllipse(QPointF(x - r * 0.4, y - r * 0.45), r * 0.25, r * 0.16)


def zeichne_kescher(p, x, y, winkel, stiel=46, netz=0.0):
    """Kescher in der Hand bei (x, y); winkel 0 = Stiel nach oben; netz 0..1 beult das Netz aus."""
    p.save()
    p.translate(x, y)
    p.rotate(winkel)
    p.setPen(stift(HOLZ_DUNKEL, 3))
    p.drawLine(QPointF(0, 4), QPointF(0, -stiel))
    p.setPen(stift(HOLZ, 1.2))
    p.drawLine(QPointF(-0.8, 2), QPointF(-0.8, -stiel + 2))
    # Netzbeutel hängt vom Reifen nach unten weg (in Figur-Richtung nach "oben" = -y)
    tief = 22 + 8 * netz
    beutel = QPainterPath()
    beutel.moveTo(-16, -stiel - 4)
    beutel.cubicTo(-16, -stiel - 4 - tief, 16, -stiel - 4 - tief, 16, -stiel - 4)
    p.setPen(KEIN_STIFT)
    p.setBrush(QColor(240, 240, 230, 70))
    p.drawPath(beutel)
    p.setPen(stift(QColor(240, 240, 230, 200), 0.9))
    p.setBrush(KEIN_PINSEL)
    for k in range(1, 5):
        u = k / 5
        p.drawLine(QPointF(-16 + 32 * u, -stiel - 4), QPointF(-6 + 12 * u, -stiel - 4 - tief * 0.75))
    for k in (0.35, 0.65):
        p.drawArc(QRectF(-16 * (1 - k * 0.5), -stiel - 4 - tief * k, 32 * (1 - k * 0.5), tief * k * 0.6),
                  0, -180 * 16)
    p.drawPath(beutel)
    p.setPen(stift(QColor('#C84030'), 2.4))
    p.drawEllipse(QRectF(-16, -stiel - 7, 32, 6))
    p.setPen(KEIN_STIFT)
    p.restore()


def kescher_mitte(x, y, winkel, stiel=46, netz=0.0):
    """Tiefster Punkt im Netzbeutel (wo ein gefangener Ball liegt), gleiche Lage wie zeichne_kescher."""
    w = math.radians(winkel)
    d = stiel + 4 + 12 + 4 * netz
    return x + math.sin(w) * d, y - math.cos(w) * d


# ---------------------------------------------------------------- Glasglocke und Flöckchen

def zeichne_glocke(p, b, h, glanz_t=0.0, platz=0.0):
    """Glasglocke, Rand mittig bei (0, 0), Breite b, Höhe h (ohne Knauf). platz 0..1: zerplatzt."""
    if platz >= 1:
        return
    p.setPen(KEIN_STIFT)
    a = 1 - platz
    pfad = QPainterPath()
    pfad.moveTo(-b / 2, 0)
    pfad.lineTo(-b / 2, -h * 0.55)
    pfad.cubicTo(-b / 2, -h * 1.02, b / 2, -h * 1.02, b / 2, -h * 0.55)
    pfad.lineTo(b / 2, 0)
    pfad.closeSubpath()
    g = QColor(215, 238, 255, int(55 * a))
    p.setBrush(linear(-b / 2, 0, b / 2, 0, QColor(235, 248, 255, int(80 * a)), g))
    p.drawPath(pfad)
    if platz > 0:
        # Schillern wie eine Seifenblase kurz vorm Platzen
        p.setBrush(linear(-b / 2, -h, b / 2, 0, QColor(255, 120, 200, int(70 * a)), QColor(120, 255, 200, int(70 * a))))
        p.drawPath(pfad)
    p.setPen(stift(QColor(240, 250, 255, int(210 * a)), max(1.2, b / 60)))
    p.setBrush(KEIN_PINSEL)
    p.drawPath(pfad)
    p.setPen(stift(QColor(255, 255, 255, int(200 * a)), max(1.5, b / 30)))
    p.drawLine(QPointF(-b * 0.36, -h * 0.15), QPointF(-b * 0.36, -h * 0.55))
    p.drawArc(QRectF(-b * 0.36, -h * 0.9, b * 0.5, h * 0.6), 105 * 16, 50 * 16)
    p.setPen(stift(QColor(255, 255, 255, int(120 * a)), max(1.0, b / 60)))
    p.drawLine(QPointF(b * 0.34, -h * 0.2), QPointF(b * 0.34, -h * 0.4))
    p.setPen(KEIN_STIFT)
    # Glanzpunkt wandert sacht
    gx = -b * 0.2 + math.sin(glanz_t * 1.3) * b * 0.05
    p.setBrush(radial(gx, -h * 0.7, b * 0.12, QColor(255, 255, 255, int(200 * a)), QColor(255, 255, 255, 0)))
    kreis(p, gx, -h * 0.7, b * 0.12)
    # Rand und Knauf
    p.setBrush(QColor(240, 250, 255, int(150 * a)))
    p.drawRoundedRect(QRectF(-b / 2 - 2, -3, b + 4, 4), 2, 2)
    p.setBrush(radial(-2, -h * 0.78 - 6, 8, QColor(255, 255, 255, int(230 * a)), QColor(180, 210, 230, int(200 * a))))
    kreis(p, 0, -h * 0.78 - 4, max(4.0, b / 14))


def zeichne_flocke(p, r=18, dreh=0.0, auge_zu=False, blick=(0.0, 0.0), froh=0.0, staunen=0.0, t=0.0):
    """Kleines lebendiges Schneeflöckchen, Mitte bei (0, 0), mit Äuglein und Mündchen."""
    p.setPen(KEIN_STIFT)
    p.setBrush(radial(0, 0, r * 1.6, QColor(200, 235, 255, 110), QColor(200, 235, 255, 0)))
    kreis(p, 0, 0, r * 1.6)
    p.save()
    p.rotate(dreh)
    p.setPen(stift(QColor('#EAF7FF'), r * 0.16))
    for k in range(6):
        a = math.radians(k * 60)
        ca, sa = math.cos(a), math.sin(a)
        p.drawLine(QPointF(0, 0), QPointF(ca * r, sa * r))
        for u, l in ((0.55, 0.3), (0.8, 0.2)):
            bx, by = ca * r * u, sa * r * u
            for z in (-1, 1):
                b = a + z * math.radians(45)
                p.drawLine(QPointF(bx, by), QPointF(bx + math.cos(b) * r * l, by + math.sin(b) * r * l))
    p.setPen(stift(QColor('#9FD6F5'), r * 0.06))
    for k in range(6):
        a = math.radians(k * 60)
        p.drawLine(QPointF(math.cos(a) * r * 0.2, math.sin(a) * r * 0.2), QPointF(math.cos(a) * r * 0.9,
                                                                                    math.sin(a) * r * 0.9))
    p.setPen(KEIN_STIFT)
    p.setBrush(WEISS)
    for k in range(6):
        a = math.radians(k * 60)
        kreis(p, math.cos(a) * r, math.sin(a) * r, r * 0.11)
    p.restore()
    # Gesicht
    p.setBrush(radial(-r * 0.15, -r * 0.15, r * 0.6, WEISS, QColor('#CFEFFF')))
    kreis(p, 0, 0, r * 0.46)
    g = 1 + 0.4 * staunen
    for sx in (-1, 1):
        ax, ay = sx * r * 0.17, -r * 0.06
        if auge_zu:
            p.setPen(stift(QColor('#24304A'), r * 0.06))
            p.drawLine(QPointF(ax - r * 0.07, ay), QPointF(ax + r * 0.07, ay))
            p.setPen(KEIN_STIFT)
            continue
        p.setBrush(QColor('#24304A'))
        p.drawEllipse(QPointF(ax + blick[0] * r * 0.05, ay + blick[1] * r * 0.05), r * 0.075 * g, r * 0.1 * g)
        p.setBrush(WEISS)
        kreis(p, ax + blick[0] * r * 0.05 + r * 0.03, ay + blick[1] * r * 0.05 - r * 0.04, r * 0.03)
    p.setBrush(QColor(255, 150, 170, 140))
    for sx in (-1, 1):
        kreis(p, sx * r * 0.3, r * 0.14, r * 0.07)
    if staunen > 0.3:
        p.setBrush(QColor('#24304A'))
        p.drawEllipse(QPointF(0, r * 0.2), r * 0.06, r * 0.08)
    else:
        p.setPen(stift(QColor('#24304A'), r * 0.05))
        p.setBrush(KEIN_PINSEL)
        tief = r * (0.08 + 0.1 * froh)
        p.drawArc(QRectF(-r * 0.12, r * 0.1 - tief / 2, r * 0.24, tief), 200 * 16, 140 * 16)
        p.setPen(KEIN_STIFT)


def glitzer(p, x, y, r, t):
    """Kleiner funkelnder Stern."""
    p.setPen(KEIN_STIFT)
    p.setBrush(QColor(255, 255, 255, int(160 + 90 * math.sin(t * 9))))
    pfad = QPainterPath()
    pfad.moveTo(x, y - r)
    pfad.quadTo(x, y, x + r, y)
    pfad.quadTo(x, y, x, y + r)
    pfad.quadTo(x, y, x - r, y)
    pfad.quadTo(x, y, x, y - r)
    p.drawPath(pfad)



# ---------------------------------------------------------------- Riesenklotz (Feder)

def zeichne_riesenklotz(p, x, y, b=64, h=56, dreh=0.0):
    """Riesiger Eisenklotz mit Bügelgriff und Nieten, steht mittig auf (x, y)."""
    p.save()
    p.translate(x, y)
    p.rotate(dreh)
    p.setPen(KEIN_STIFT)
    p.setPen(stift(QColor('#2A2E35'), 7))
    p.setBrush(KEIN_PINSEL)
    p.drawArc(QRectF(-b * 0.2, -h - b * 0.24, b * 0.4, b * 0.48), 0, 180 * 16)
    p.setPen(stift(QColor('#7A828E'), 2))
    p.drawArc(QRectF(-b * 0.2 + 1, -h - b * 0.24 + 1, b * 0.4 - 2, b * 0.48 - 2), 40 * 16, 100 * 16)
    p.setPen(KEIN_STIFT)
    k = QPainterPath()
    k.moveTo(-b / 2, 0)
    k.lineTo(-b * 0.38, -h)
    k.lineTo(b * 0.38, -h)
    k.lineTo(b / 2, 0)
    k.closeSubpath()
    p.setBrush(linear(-b / 2, -h, b / 2, 0, QColor('#7C8490'), QColor('#262A31')))
    p.drawPath(k)
    p.setBrush(QColor(255, 255, 255, 50))
    p.drawRect(QRectF(-b * 0.38, -h, b * 0.76, 4))
    p.setBrush(QColor(0, 0, 0, 60))
    p.drawRect(QRectF(-b / 2, -7, b, 7))
    # eingeprägter Ring statt Beschriftung
    p.setPen(stift(QColor(0, 0, 0, 70), 3))
    p.setBrush(KEIN_PINSEL)
    p.drawEllipse(QRectF(-b * 0.18, -h * 0.66, b * 0.36, h * 0.36))
    p.setPen(stift(QColor(255, 255, 255, 55), 1.5))
    p.drawArc(QRectF(-b * 0.18, -h * 0.66 + 1.5, b * 0.36, h * 0.36), 200 * 16, 140 * 16)
    p.setPen(stift(QColor(255, 255, 255, 80), 2))
    p.drawLine(QPointF(-b * 0.33, -h + 6), QPointF(-b * 0.44, -10))
    p.setPen(KEIN_STIFT)
    for nx, ny in ((-0.34, -0.82), (0.34, -0.82), (-0.42, -0.2), (0.42, -0.2)):
        p.setBrush(radial(nx * b - 1, ny * h - 1, 4, QColor('#9AA2AE'), QColor('#30343B')))
        kreis(p, nx * b, ny * h, 3)
    p.restore()
