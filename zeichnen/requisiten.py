"""Rentier, Schlitten, Fahrrad, Schornstein und Seil."""
import math

from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import QColor, QPainterPath, QPen

from .grundlagen import *  # noqa: F401,F403  Farben und Hilfen
from .figur import zeichne_bein_ik, zeichne_sack, zeichne_weihnachtsmann


def zeichne_geweih(p, x, y, farbe, v):
    g = QPainterPath()
    g.moveTo(x, y)
    g.quadTo(x - 4 + v, y - 18, x - 12 + v, y - 30)
    g.moveTo(x - 3 + v * 0.3, y - 14)
    g.lineTo(x + 6 + v, y - 24)
    g.moveTo(x - 8 + v * 0.7, y - 24)
    g.lineTo(x - 20 + v, y - 28)
    g.moveTo(x - 10 + v, y - 27)
    g.lineTo(x - 6 + v, y - 38)
    p.setPen(stift(farbe, 4))
    p.setBrush(KEIN_PINSEL)
    p.drawPath(g)
    p.setPen(KEIN_STIFT)


def zeichne_rentier(p, phase, t, leuchtnase):
    """Körpermitte im Ursprung, Blick nach rechts, im Galopp."""
    geweih = QColor('#EDDDB6')

    def bein(x, winkel, knie, hinten):
        p.save()
        p.translate(x, 8)
        p.rotate(winkel)
        p.setBrush(FELL_R_DUNKEL.darker(125) if hinten else FELL_R_DUNKEL)
        p.drawRoundedRect(QRectF(-5.5, -4, 11, 28), 5, 5)
        p.translate(0, 22)
        p.rotate(knie)
        p.drawRoundedRect(QRectF(-4, -2, 8, 24), 4, 4)
        p.setBrush(QColor('#33241A'))
        p.drawRoundedRect(QRectF(-5, 19, 10, 7), 2, 2)
        p.restore()

    p.setPen(KEIN_STIFT)
    zeichne_geweih(p, 54, -70, geweih.darker(125), -6)
    bein(30, -40 * math.sin(phase) - 5, 20 + 20 * math.sin(phase + 1.5), True)
    bein(-32, 40 * math.sin(phase + 0.9) + 5, -20 - 20 * math.sin(phase + 2.4), True)
    flausch(p, [(-46, -14), (-50, -18)], 6, False)
    p.setBrush(radial(0, -14, 56, FELL_R.lighter(118), FELL_R_DUNKEL))
    p.drawEllipse(QRectF(-48, -24, 96, 46))
    p.setBrush(BAUCH_R)
    p.drawEllipse(QRectF(-30, 2, 60, 16))
    hals = QPainterPath()
    hals.moveTo(24, -16)
    hals.cubicTo(38, -28, 44, -44, 50, -58)
    hals.lineTo(68, -52)
    hals.cubicTo(60, -36, 54, -12, 42, 6)
    hals.closeSubpath()
    p.setBrush(FELL_R)
    p.drawPath(hals)
    p.save()
    p.translate(46, -26)
    p.rotate(-28)
    p.setBrush(ROT)
    p.drawRoundedRect(QRectF(-14, -4, 28, 8), 4, 4)
    p.restore()
    for i, (bx, by) in enumerate(((42, -17), (52, -22))):
        schw = math.sin(t * 14 + i * 2) * 2
        p.setBrush(radial(bx - 1, by + 2, 6, GOLD_HELL, GOLD))
        kreis(p, bx + schw, by + 4, 4.2)
        p.setBrush(QColor('#6B4A10'))
        kreis(p, bx + schw, by + 6, 1.2)
    p.setBrush(radial(62, -66, 20, FELL_R.lighter(118), FELL_R_DUNKEL))
    p.drawEllipse(QPointF(64, -60), 16, 12)
    p.setBrush(BAUCH_R)
    p.drawEllipse(QPointF(80, -54), 12, 8)
    p.save()
    p.translate(54, -68)
    p.rotate(-30 + math.sin(t * 3) * 8)
    p.setBrush(FELL_R_DUNKEL)
    p.drawEllipse(QRectF(-12, -3.5, 12, 7))
    p.restore()
    zeichne_geweih(p, 60, -70, geweih, 0)
    if blinzeln(t, 1.3):
        p.setPen(stift(SCHWARZ, 1.6))
        p.drawLine(QPointF(68, -63), QPointF(72.5, -63))
        p.setPen(KEIN_STIFT)
    else:
        p.setBrush(SCHWARZ)
        kreis(p, 70, -63, 2.4)
        p.setBrush(WEISS)
        kreis(p, 70.8, -63.8, 0.8)
    if leuchtnase:
        puls = 0.75 + 0.25 * math.sin(t * 5)
        p.setBrush(radial(91, -55, 20, QColor(255, 60, 60, int(170 * puls)), QColor(255, 60, 60, 0)))
        kreis(p, 91, -55, 20)
        p.setBrush(radial(90, -57, 6, QColor('#FF8A80'), QColor('#D01818')))
        kreis(p, 91, -55, 5.5)
    else:
        p.setBrush(QColor('#2A1A12'))
        kreis(p, 91, -55, 4.5)
    bein(36, -40 * math.sin(phase + 0.35) - 5, 20 + 20 * math.sin(phase + 1.85), False)
    bein(-26, 40 * math.sin(phase + 1.25) + 5, -20 - 20 * math.sin(phase + 2.75), False)


def zeichne_schlitten(p):
    """Kufenunterkante im Ursprung, Spitze nach rechts."""
    kufe = QPainterPath()
    kufe.moveTo(-100, -4)
    kufe.lineTo(78, -4)
    kufe.cubicTo(100, -4, 110, -22, 98, -32)
    kufe.cubicTo(92, -37, 84, -32, 88, -26)
    p.setBrush(KEIN_PINSEL)
    p.setPen(stift(GOLD, 5))
    p.drawPath(kufe)
    p.setPen(stift(GOLD.darker(115), 4))
    p.drawLine(QPointF(-70, -4), QPointF(-66, -30))
    p.drawLine(QPointF(48, -4), QPointF(44, -30))
    kasten = QPainterPath()
    kasten.moveTo(-96, -28)
    kasten.lineTo(60, -28)
    kasten.cubicTo(92, -28, 104, -52, 96, -76)
    kasten.cubicTo(92, -86, 80, -84, 82, -74)
    kasten.cubicTo(84, -62, 70, -54, 50, -56)
    kasten.lineTo(-60, -56)
    kasten.cubicTo(-80, -56, -84, -80, -90, -100)
    kasten.cubicTo(-104, -104, -110, -90, -106, -70)
    kasten.cubicTo(-104, -50, -104, -34, -96, -28)
    p.setPen(KEIN_STIFT)
    p.setBrush(linear(0, -100, 0, -28, ROT_HELL, ROT_DUNKEL))
    p.drawPath(kasten)
    p.setPen(QPen(GOLD, 3))
    p.setBrush(KEIN_PINSEL)
    p.drawPath(kasten)
    ranke = QPainterPath()
    ranke.moveTo(-60, -42)
    ranke.cubicTo(-40, -52, -20, -32, 0, -42)
    ranke.cubicTo(20, -52, 40, -32, 56, -42)
    p.setPen(stift(GOLD_HELL, 2.2))
    p.drawPath(ranke)
    p.setPen(KEIN_STIFT)
    p.setBrush(GOLD_HELL)
    for x in (-60, 0, 56):
        stern(p, x, -42, 5)


def zeichne_rad(p, cx, cy, winkel):
    p.setBrush(KEIN_PINSEL)
    p.setPen(QPen(QColor('#C9CDD4'), 1.1))
    for i in range(12):
        w = winkel + i * math.pi / 6
        p.drawLine(QPointF(cx, cy), QPointF(cx + math.cos(w) * 28, cy + math.sin(w) * 28))
    p.setPen(QPen(QColor('#B8BCC4'), 2.2))
    kreis(p, cx, cy, 28)
    p.setPen(QPen(QColor('#2A2A2A'), 5.5))
    kreis(p, cx, cy, 31.5)
    p.setPen(KEIN_STIFT)
    p.setBrush(QColor('#8A8F98'))
    kreis(p, cx, cy, 3.5)


def zeichne_fahrrad(p, rad, kurbel, t, pose, klingel):
    """Fahrrad mit Weihnachtsmann; Boden im Ursprung, Fahrtrichtung rechts."""
    hinten, vorn, tretlager = (-60, -34), (62, -34), (0, -30)
    sattel, steuer_o, steuer_u, vorbau = (-16, -86), (42, -94), (46, -72), (40, -118)
    huefte = (-14, -92)
    P = QPointF
    p.setPen(KEIN_STIFT)
    zeichne_rad(p, *hinten, rad)
    zeichne_rad(p, *vorn, rad)

    def pedal(w):
        return tretlager[0] + 13 * math.cos(w), tretlager[1] + 13 * math.sin(w)

    nah, fern = pedal(kurbel), pedal(kurbel + math.pi)
    p.setPen(stift(QColor('#6C7078'), 3.5))
    p.drawLine(P(*tretlager), P(*fern))
    p.setPen(KEIN_STIFT)
    zeichne_bein_ik(p, *huefte, fern[0], fern[1] - 2, True)
    # Gepäckträger mit Sack
    p.setPen(stift(QColor('#8A8F98'), 2.5))
    p.drawLine(P(*hinten), P(-58, -74))
    p.drawLine(P(-84, -74), P(-34, -74))
    p.setPen(KEIN_STIFT)
    zeichne_sack(p, -62, -112, -6, 0.8)
    # Rahmen, Gabel, Lenker, Kette
    p.setPen(stift(GRUEN, 5))
    for a, b in ((hinten, tretlager), (hinten, sattel), (tretlager, sattel), (sattel, steuer_o), (tretlager, steuer_u)):
        p.drawLine(P(*a), P(*b))
    p.setPen(stift(GRUEN_DUNKEL, 7))
    p.drawLine(P(*steuer_o), P(*steuer_u))
    p.setPen(stift(QColor('#B8BCC4'), 4))
    p.drawLine(P(*steuer_u), P(*vorn))
    p.drawLine(P(*steuer_o), P(*vorbau))
    p.setPen(stift(QColor('#8A8F98'), 4))
    p.drawLine(P(*vorbau), P(30, -122))
    p.setPen(QPen(QColor('#555A62'), 1.5))
    p.drawLine(P(0, -40), P(-60, -37))
    p.drawLine(P(0, -20), P(-60, -31))
    p.setPen(stift(QColor('#9AA0A8'), 2.5))
    p.setBrush(KEIN_PINSEL)
    kreis(p, *tretlager, 10)
    p.setPen(KEIN_STIFT)
    p.setBrush(SCHWARZ)
    p.drawEllipse(P(-18, -88), 14, 4.5)
    # Korb mit Geschenk
    p.setBrush(linear(54, 0, 68, 0, ROT_HELL, ROT_DUNKEL))
    p.drawRect(QRectF(55, -124, 15, 13))
    p.setBrush(GOLD)
    p.drawRect(QRectF(61, -124, 3, 13))
    p.drawEllipse(P(60, -126), 3.5, 2.5)
    p.drawEllipse(P(65, -126), 3.5, 2.5)
    p.setBrush(QColor('#B98A4E'))
    p.drawRoundedRect(QRectF(50, -114, 28, 20), 3, 3)
    p.setPen(QPen(QColor('#8A6232'), 1.3))
    for y in (-108, -101):
        p.drawLine(P(50, y), P(78, y))
    for x in (56, 62, 68, 74):
        p.drawLine(P(x, -114), P(x, -94))
    p.setPen(KEIN_STIFT)
    p.save()
    p.translate(-14, -24)
    zeichne_weihnachtsmann(p, pose)
    p.restore()
    zeichne_bein_ik(p, *huefte, nah[0], nah[1] - 2, False)
    p.setPen(stift(QColor('#8A8F98'), 3.5))
    p.drawLine(P(*tretlager), P(*nah))
    p.setPen(KEIN_STIFT)
    p.setBrush(SCHWARZ)
    p.drawRect(QRectF(nah[0] - 6, nah[1] - 1.5, 12, 3))
    # Klingel
    wackel = math.sin(t * 60) * 1.5 if klingel else 0
    p.setBrush(radial(32 + wackel, -129, 6, GOLD_HELL, GOLD))
    kreis(p, 33 + wackel, -127, 4.5)
    if klingel:
        p.setPen(stift(GOLD, 1.8))
        p.setBrush(KEIN_PINSEL)
        for r in (9, 14):
            rahmen = QRectF(33 - r, -127 - r, 2 * r, 2 * r)
            p.drawArc(rahmen, 20 * 16, 50 * 16)
            p.drawArc(rahmen, 110 * 16, 50 * 16)
        p.setPen(KEIN_STIFT)


def zeichne_schornstein(p, xc, oben, boden, s):
    p.save()
    p.translate(xc, oben)
    p.scale(s, s)
    tief = (boden - oben) / s + 10
    p.setPen(KEIN_STIFT)
    p.setBrush(linear(-56, 0, 56, 0, QColor('#C9593D'), QColor('#87301E')))
    p.drawRect(QRectF(-56, 14, 112, tief))
    p.setPen(QPen(QColor(235, 215, 195, 140), 1.6))
    reihe, y = 0, 14.0
    while y < tief + 14:
        p.drawLine(QPointF(-56, y), QPointF(56, y))
        x = -56 + (14 if reihe % 2 else 0) + 28
        while x < 56:
            p.drawLine(QPointF(x, y), QPointF(x, y + 14))
            x += 28
        y += 14
        reihe += 1
    p.setPen(KEIN_STIFT)
    p.setBrush(QColor(0, 0, 0, 70))
    p.drawRect(QRectF(-56, 14, 112, 7))
    p.setBrush(linear(-68, 0, 68, 0, QColor('#B44C34'), QColor('#77291A')))
    p.drawRoundedRect(QRectF(-68, -4, 136, 20), 3, 3)
    schnee = QPainterPath()
    schnee.moveTo(-72, 4)
    schnee.cubicTo(-74, -12, -50, -16, -30, -12)
    schnee.cubicTo(-10, -20, 20, -18, 40, -12)
    schnee.cubicTo(60, -16, 76, -8, 72, 4)
    schnee.lineTo(64, 4)
    schnee.quadTo(60, 14, 56, 4)
    schnee.lineTo(20, 4)
    schnee.quadTo(14, 18, 8, 4)
    schnee.lineTo(-30, 4)
    schnee.quadTo(-36, 12, -42, 4)
    schnee.closeSubpath()
    p.setBrush(linear(0, -18, 0, 8, WEISS, QColor('#D8E3F0')))
    p.drawPath(schnee)
    p.setBrush(QColor(215, 236, 255, 220))
    for x, laenge in ((-50, 12), (-12, 9), (30, 14), (50, 8)):
        zapfen = QPainterPath()
        zapfen.moveTo(x - 3, 15)
        zapfen.lineTo(x + 3, 15)
        zapfen.lineTo(x, 15 + laenge)
        zapfen.closeSubpath()
        p.drawPath(zapfen)
    p.restore()


def zeichne_seil(p, seil_x, oben, ende, s):
    """Seil vom oberen Rand bis 'ende' mit Knoten und Fransen; seil_x(y) gibt die Lage beim Pendeln."""
    pfad = QPainterPath()
    n = 40
    for i in range(n + 1):
        yy = oben - 20 * s + (ende - oben + 20 * s) * i / n
        if i == 0:
            pfad.moveTo(seil_x(yy), yy)
        else:
            pfad.lineTo(seil_x(yy), yy)
    p.setBrush(KEIN_PINSEL)
    p.setPen(stift(QColor('#7A5428'), 7 * s))
    p.drawPath(pfad)
    drall = QPen(QColor('#C9A46A'), 7 * s, Qt.PenStyle.CustomDashLine, Qt.PenCapStyle.FlatCap)
    drall.setDashPattern([0.5, 0.9])
    p.setPen(drall)
    p.drawPath(pfad)
    p.setPen(KEIN_STIFT)
    ex = seil_x(ende)
    p.setBrush(radial(ex - 2 * s, ende - 2 * s, 9 * s, QColor('#C9A46A'), QColor('#7A5428')))
    kreis(p, ex, ende, 7.5 * s)
    p.setPen(stift(QColor('#9A7040'), 2.2 * s))
    for dx in (-4, -1.5, 1.5, 4):
        p.drawLine(QPointF(ex + dx * s, ende + 5 * s), QPointF(ex + dx * 1.6 * s, ende + 15 * s))
    p.setPen(KEIN_STIFT)
