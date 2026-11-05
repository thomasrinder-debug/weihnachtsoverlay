"""Rentier, Schlitten, Fahrrad, Schornstein, Seil, Geschenke, Lichterkette und anderer Kleinkram."""
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


def zeichne_geschenk(p, b, h, farbe, band=GOLD, deckel=(0.0, 0.0, 0.0), muster=True):
    """Geschenk mit Schleife, Boden mittig im Ursprung. deckel = (dx, dy, drehung)."""
    p.setBrush(QColor(0, 0, 0, 45))
    p.drawEllipse(QRectF(-b * 0.55, -3, b * 1.1, 6))
    p.setBrush(linear(-b / 2, 0, b / 2, 0, farbe.lighter(125), farbe.darker(135)))
    p.drawRect(QRectF(-b / 2, -h, b, h))
    if muster:
        p.setBrush(QColor(255, 255, 255, 70))
        for i in range(int(b // 14)):
            for k in range(int(h // 14)):
                if (i + k) % 2 == 0:
                    kreis(p, -b / 2 + 7 + i * 14, -h + 10 + k * 14, 2.2)
    p.setBrush(QColor(0, 0, 0, 50))
    p.drawRect(QRectF(-b / 2, -h, b, 5))
    p.setBrush(linear(0, -h, 0, 0, band.lighter(120), band.darker(110)))
    p.drawRect(QRectF(-b * 0.08, -h, b * 0.16, h))
    dx, dy, dreh = deckel
    p.save()
    p.translate(dx, -h + dy)
    p.rotate(dreh)
    p.setBrush(linear(0, -14, 0, 0, farbe.lighter(140), farbe.darker(110)))
    p.drawRoundedRect(QRectF(-b / 2 - 5, -14, b + 10, 15), 3, 3)
    p.setBrush(linear(0, -14, 0, 0, band.lighter(130), band))
    p.drawRect(QRectF(-b * 0.08, -14, b * 0.16, 15))
    for seite in (-1, 1):
        schlaufe = QPainterPath()
        schlaufe.moveTo(0, -14)
        schlaufe.cubicTo(seite * 10, -40, seite * 30, -36, seite * 24, -22)
        schlaufe.cubicTo(seite * 20, -14, seite * 8, -14, 0, -14)
        p.setBrush(linear(0, -40, 0, -14, band.lighter(140), band.darker(115)))
        p.drawPath(schlaufe)
        ende = QPainterPath()
        ende.moveTo(0, -14)
        ende.quadTo(seite * 12, -8, seite * 16, 2)
        ende.lineTo(seite * 10, 0)
        ende.quadTo(seite * 6, -8, 0, -14)
        p.drawPath(ende)
    p.setBrush(radial(-1, -17, 6, band.lighter(150), band))
    kreis(p, 0, -15, 5)
    p.restore()


def zeichne_feder(p, x, unten, oben, breite=16, windungen=6):
    """Spiralfeder von unten nach oben."""
    pfad = QPainterPath()
    pfad.moveTo(x, unten)
    n = windungen * 2
    for i in range(1, n + 1):
        y = unten + (oben - unten) * i / n
        pfad.lineTo(x + (breite / 2 if i % 2 else -breite / 2), y)
    pfad.lineTo(x, oben)
    p.setBrush(KEIN_PINSEL)
    p.setPen(stift(QColor('#6C7280'), 3.4))
    p.drawPath(pfad)
    p.setPen(stift(QColor('#D5DAE2'), 1.4))
    p.drawPath(pfad)
    p.setPen(KEIN_STIFT)


LICHTER = (QColor('#FF4D4D'), QColor('#FFD23F'), QColor('#3FA7FF'), QColor('#5BE06A'), QColor('#FF7AE0'))


def zeichne_lichterkette(p, pfad, s, an, t, abstand=34, groesse=1.0):
    """Kabel entlang pfad (QPainterPath in Pixeln) mit Birnchen alle 'abstand' Einheiten.
    an: 0..1 Helligkeit, die Birnchen blinken versetzt."""
    k = s * groesse
    p.setBrush(KEIN_PINSEL)
    p.setPen(stift(QColor('#1E4A2A'), 2.6 * k))
    p.drawPath(pfad)
    p.setPen(KEIN_STIFT)
    laenge = pfad.length()
    n = int(laenge / (abstand * k))
    for i in range(1, n + 1):
        anteil = pfad.percentAtLength(i * abstand * k - abstand * k * 0.5)
        pt = pfad.pointAtPercent(anteil)
        w = -pfad.angleAtPercent(anteil)
        farbe = LICHTER[i % len(LICHTER)]
        hell = an * (0.65 + 0.35 * math.sin(t * 5 + i * 2.1))
        if hell > 0.05:
            schein = QColor(farbe)
            schein.setAlpha(int(150 * hell))
            aus = QColor(farbe)
            aus.setAlpha(0)
            p.setBrush(radial(pt.x(), pt.y(), 13 * k, schein, aus))
            kreis(p, pt.x(), pt.y(), 13 * k)
        p.save()
        p.translate(pt)
        p.rotate(w)
        p.setBrush(QColor('#2E6B3A'))
        p.drawRect(QRectF(-2.6 * k, 0, 5.2 * k, 4 * k))
        innen = farbe.lighter(100 + int(70 * hell)) if hell > 0.05 else farbe.darker(170)
        p.setBrush(radial(-1 * k, 7 * k, 6 * k, innen, farbe.darker(120 if hell > 0.05 else 220)))
        p.drawEllipse(QRectF(-4 * k, 3 * k, 8 * k, 11 * k))
        p.restore()


def zeichne_steckdose(p, x, y, s, stecker=False):
    """Bodensteckdose, Unterkante bei y."""
    p.save()
    p.translate(x, y)
    p.scale(s, s)
    p.setBrush(linear(0, -26, 0, 0, QColor('#F4F4F2'), QColor('#BFC3C9')))
    p.drawRoundedRect(QRectF(-18, -26, 36, 26), 5, 5)
    p.setBrush(QColor('#D9DCE0'))
    kreis(p, 0, -13, 9)
    p.setBrush(QColor('#555A62'))
    kreis(p, -3.5, -13, 1.7)
    kreis(p, 3.5, -13, 1.7)
    if stecker:
        p.setBrush(linear(-8, 0, 8, 0, QColor('#3E8E52'), QColor('#1E4A2A')))
        p.drawRoundedRect(QRectF(-7, -30, 14, 18), 4, 4)
    p.restore()


def zeichne_stecker(p, x, y, winkel, s):
    p.save()
    p.translate(x, y)
    p.rotate(winkel)
    p.scale(s, s)
    p.setBrush(linear(-7, 0, 7, 0, QColor('#3E8E52'), QColor('#1E4A2A')))
    p.drawRoundedRect(QRectF(-7, -9, 14, 18), 4, 4)
    p.setBrush(QColor('#C9CDD4'))
    p.drawRect(QRectF(-4.5, 9, 2, 6))
    p.drawRect(QRectF(2.5, 9, 2, 6))
    p.restore()


def zeichne_eisflaeche(p, x0, x1, y, s):
    """Spiegelglatte Eisfläche am Boden von x0 bis x1."""
    b = x1 - x0
    p.setBrush(linear(x0, y - 10 * s, x0, y, QColor(225, 245, 255, 230), QColor(150, 205, 240, 230)))
    p.drawRoundedRect(QRectF(x0, y - 9 * s, b, 12 * s), 6 * s, 6 * s)
    p.setPen(stift(QColor(255, 255, 255, 210), 1.6 * s))
    for k in (0.15, 0.45, 0.7):
        p.drawLine(QPointF(x0 + b * k, y - 6 * s), QPointF(x0 + b * k + 18 * s, y - 6 * s))
    p.setPen(KEIN_STIFT)
    p.setBrush(QColor(255, 255, 255, 230))
    stern(p, x0 + b * 0.3, y - 7 * s, 5 * s)
    stern(p, x0 + b * 0.8, y - 5 * s, 3.5 * s)


def zeichne_muetze_lose(p):
    """Die Mütze des Weihnachtsmanns ohne Kopf, Krempe mittig im Ursprung."""
    muetze = QPainterPath()
    muetze.moveTo(-30, 0)
    muetze.cubicTo(-28, -42, 22, -56, 44, -26)
    muetze.cubicTo(34, -30, 28, -20, 30, 0)
    muetze.closeSubpath()
    p.setBrush(linear(-30, -50, 30, 0, ROT_HELL, ROT_DUNKEL))
    p.drawPath(muetze)
    flausch(p, [(x, 0) for x in range(-30, 31, 6)], 7.5)
    flausch(p, [(46 + dx, -24 + dy) for dx, dy in ((0, 0), (-4, -3), (4, -3), (-3, 4), (4, 3))], 6)


def zeichne_schneeball(p, x, y, r):
    p.setBrush(radial(x - r * 0.35, y - r * 0.4, r * 1.6, WEISS, QColor('#B8CBE2')))
    kreis(p, x, y, r)
    p.setBrush(QColor(255, 255, 255, 220))
    kreis(p, x - r * 0.35, y - r * 0.35, r * 0.25)


def zeichne_walnuss(p, x, y, r):
    p.setBrush(radial(x - r * 0.3, y - r * 0.3, r * 1.5, QColor('#C9965A'), QColor('#7A5228')))
    p.drawEllipse(QPointF(x, y), r, r * 0.9)
    p.setPen(stift(QColor('#6A4420'), r * 0.12))
    p.setBrush(KEIN_PINSEL)
    p.drawLine(QPointF(x, y - r * 0.9), QPointF(x, y + r * 0.9))
    p.drawArc(QRectF(x - r * 0.7, y - r * 0.5, r * 0.6, r), 60 * 16, 240 * 16)
    p.drawArc(QRectF(x + r * 0.1, y - r * 0.5, r * 0.6, r), -120 * 16, 240 * 16)
    p.setPen(KEIN_STIFT)


def zeichne_strumpf(p, voll=0.0):
    """Weihnachtsstrumpf an seiner Schlaufe im Ursprung, hängt nach unten, Spitze nach rechts.
    voll (0..1) beult ihn aus."""
    p.setPen(stift(QColor('#7A5428'), 2.4))
    p.setBrush(KEIN_PINSEL)
    p.drawEllipse(QRectF(-5, -2, 10, 12))
    p.setPen(KEIN_STIFT)
    b = 6 * voll
    bein = QPainterPath()
    bein.moveTo(-24 - b, 22)
    bein.lineTo(24 + b, 22)
    bein.cubicTo(26 + b, 70, 24 + b, 92, 34, 108)
    bein.cubicTo(44, 118, 70, 116, 76, 128)
    bein.cubicTo(82, 142, 66, 156, 40, 152)
    bein.cubicTo(8, 150, -14, 140, -22, 118)
    bein.cubicTo(-28 - b, 96, -26 - b, 60, -24 - b, 22)
    p.setBrush(radial(-6, 60, 110, ROT_HELL, ROT_DUNKEL))
    p.drawPath(bein)
    p.save()
    p.setClipPath(bein)
    p.setBrush(GRUEN)
    p.drawEllipse(QPointF(70, 140), 24, 22)
    p.drawEllipse(QPointF(-18, 132), 18, 22)
    p.setBrush(QColor(255, 255, 255, 200))
    for k in range(5):
        stern(p, -10 + k * 9, 58 + (k % 2) * 16, 4)
    p.restore()
    flausch(p, [(x, 22 + (5 if (x // 8) % 2 else 0)) for x in range(-24, 27, 8)], 8)
    flausch(p, [(x, 30) for x in range(-24, 27, 8)], 8)


EIS = QColor(205, 235, 255, 235)
EIS_DUNKEL = QColor(120, 180, 225, 235)


def zeichne_eiszapfen(p, laenge, breite=18, ab=0.0):
    """Eiszapfen, Wurzel im Ursprung, hängt nach unten. ab: so viel (0..1) ist unten abgebrochen."""
    bis = laenge * (1 - ab)
    pfad = QPainterPath()
    pfad.moveTo(-breite / 2, 0)
    pfad.lineTo(breite / 2, 0)
    if ab > 0:
        rest = breite / 2 * (1 - bis / laenge)
        pfad.lineTo(rest, bis - 3)
        pfad.lineTo(rest * 0.2, bis + 2)
        pfad.lineTo(-rest, bis - 1)
    else:
        pfad.quadTo(breite * 0.25, laenge * 0.6, 0, laenge)
        pfad.quadTo(-breite * 0.3, laenge * 0.6, -breite / 2, 0)
    pfad.closeSubpath()
    p.setBrush(linear(-breite / 2, 0, breite / 2, 0, EIS, EIS_DUNKEL))
    p.drawPath(pfad)
    p.setPen(stift(QColor(255, 255, 255, 220), 1.6))
    p.drawLine(QPointF(-breite * 0.22, 4), QPointF(-breite * 0.08, bis * 0.7))
    p.setPen(KEIN_STIFT)


def zeichne_eisstueck(p, laenge, breite=12):
    """Abgebrochene Zapfenspitze, Mitte im Ursprung, Spitze nach unten."""
    pfad = QPainterPath()
    pfad.moveTo(-breite / 2, -laenge / 2)
    pfad.lineTo(breite * 0.1, -laenge / 2 - 3)
    pfad.lineTo(breite / 2, -laenge / 2 + 1)
    pfad.quadTo(breite * 0.2, laenge * 0.2, 0, laenge / 2)
    pfad.quadTo(-breite * 0.3, laenge * 0.1, -breite / 2, -laenge / 2)
    p.setBrush(linear(-breite / 2, 0, breite / 2, 0, EIS, EIS_DUNKEL))
    p.drawPath(pfad)
    p.setBrush(QColor(255, 255, 255, 230))
    stern(p, -breite * 0.15, -laenge * 0.15, 3.5)


def zeichne_rodel(p):
    """Holzrodel, Kufen im Ursprung auf dem Boden, Spitze nach rechts."""
    holz, dunkel = QColor('#C98A4B'), QColor('#7A4A22')
    p.setBrush(KEIN_PINSEL)
    p.setPen(stift(dunkel, 4.5))
    for dy in (0,):
        kufe = QPainterPath()
        kufe.moveTo(-52, -3 + dy)
        kufe.lineTo(40, -3 + dy)
        kufe.cubicTo(58, -3, 62, -22, 50, -28)
        p.drawPath(kufe)
    p.setPen(stift(dunkel, 3.5))
    for x in (-38, -6, 26):
        p.drawLine(QPointF(x, -4), QPointF(x, -20))
    p.setPen(KEIN_STIFT)
    for i, x in enumerate(range(-50, 40, 15)):
        p.setBrush(linear(0, -26, 0, -18, holz.lighter(115 + 4 * (i % 2)), holz.darker(110)))
        p.drawRoundedRect(QRectF(x, -27, 13, 8), 2, 2)
    p.setPen(stift(QColor('#B8322A'), 2))
    zug = QPainterPath()
    zug.moveTo(48, -26)
    zug.cubicTo(62, -30, 64, -10, 56, -4)
    p.drawPath(zug)
    p.setPen(KEIN_STIFT)


def zeichne_ski(p, x, y, winkel, laenge=120):
    """Ein Ski, Bindung in (x, y), Spitze nach rechts."""
    p.save()
    p.translate(x, y)
    p.rotate(winkel)
    ski = QPainterPath()
    ski.moveTo(-laenge * 0.4, 0)
    ski.lineTo(laenge * 0.5, 0)
    ski.quadTo(laenge * 0.62, -1, laenge * 0.6, -10)
    ski.lineTo(laenge * 0.55, -4)
    ski.lineTo(-laenge * 0.4, -4)
    ski.closeSubpath()
    p.setBrush(linear(0, -4, 0, 0, QColor('#2A6FD6').lighter(130), QColor('#1C4A99')))
    p.drawPath(ski)
    p.setBrush(QColor(255, 255, 255, 200))
    p.drawRect(QRectF(-laenge * 0.3, -3.2, laenge * 0.7, 1.2))
    p.setBrush(QColor('#333333'))
    p.drawRoundedRect(QRectF(-8, -7, 16, 4), 1.5, 1.5)
    p.restore()


def zeichne_schneehaufen(p, x, y, b, h):
    """Weicher Schneehaufen am Boden, Mitte unten in (x, y), Breite b, Höhe h (Pixel)."""
    if h <= 0.5:
        return
    pfad = QPainterPath()
    pfad.moveTo(x - b / 2, y + 2)
    pfad.cubicTo(x - b * 0.35, y - h * 0.9, x - b * 0.15, y - h * 1.05, x, y - h)
    pfad.cubicTo(x + b * 0.18, y - h * 1.02, x + b * 0.38, y - h * 0.8, x + b / 2, y + 2)
    pfad.closeSubpath()
    p.setBrush(linear(x, y - h, x, y, WEISS, QColor('#C7D8EC')))
    p.drawPath(pfad)
    p.setBrush(QColor(255, 255, 255, 200))
    for dx, dy, r in ((-0.2, 0.75, 0.05), (0.1, 0.85, 0.035), (0.25, 0.5, 0.03)):
        kreis(p, x + dx * b, y - dy * h, max(1.0, r * b))


def zeichne_topf(p):
    """Alter Kochtopf als Hut, Rand mittig im Ursprung (Öffnung nach unten)."""
    p.setBrush(linear(-26, 0, 26, 0, QColor('#C9CDD4'), QColor('#6C727C')))
    p.drawRoundedRect(QRectF(-24, -34, 48, 34), 4, 4)
    p.setBrush(linear(-29, 0, 29, 0, QColor('#DDE1E6'), QColor('#7A808A')))
    p.drawRoundedRect(QRectF(-29, -5, 58, 7), 3, 3)
    p.setBrush(QColor('#4A4F57'))
    p.drawRoundedRect(QRectF(-36, -26, 9, 5), 2, 2)
    p.drawRoundedRect(QRectF(27, -26, 9, 5), 2, 2)
    p.setBrush(QColor(255, 255, 255, 120))
    p.drawRect(QRectF(-16, -31, 5, 24))
    p.setBrush(QColor(120, 70, 40, 90))
    kreis(p, 10, -14, 3)


def zeichne_zimtstern(p, r, fehlt=-1):
    """Zimtstern mit Eiweißglasur, Mitte im Ursprung. fehlt: Index der abgebissenen Zacke."""
    def stern_pfad(ra, ri):
        pfad = QPainterPath()
        for i in range(10):
            w = math.radians(-90 + i * 36)
            rr = ra if i % 2 == 0 else ri
            if i % 2 == 0 and i // 2 == fehlt:
                rr = ri * 1.05
            pt = QPointF(math.cos(w) * rr, math.sin(w) * rr)
            pfad.moveTo(pt) if i == 0 else pfad.lineTo(pt)
        pfad.closeSubpath()
        return pfad
    p.setPen(stift(QColor('#6B3E1E'), r * 0.08))
    p.setBrush(radial(-r * 0.2, -r * 0.2, r * 1.3, QColor('#B9773E'), QColor('#7A4520')))
    p.drawPath(stern_pfad(r, r * 0.48))
    p.setPen(KEIN_STIFT)
    p.setBrush(linear(0, -r, 0, r, QColor('#FFFFFF'), QColor('#E9E2D6')))
    p.drawPath(stern_pfad(r * 0.82, r * 0.38))
    if fehlt >= 0:
        w = math.radians(-90 + fehlt * 72)
        p.setBrush(QColor('#A8692F'))
        for k in (-0.12, 0.0, 0.12):
            kreis(p, math.cos(w + k) * r * 0.52, math.sin(w + k) * r * 0.52, r * 0.07)


def zeichne_besen(p, winkel=0.0):
    """Reisigbesen, Borstenende im Ursprung, Stiel nach oben."""
    p.save()
    p.rotate(winkel)
    p.setBrush(linear(-3, 0, 3, 0, QColor('#B07A42'), QColor('#6B4423')))
    p.drawRoundedRect(QRectF(-3, -150, 6, 120), 3, 3)
    p.setPen(stift(QColor('#8A6A2A'), 1.6))
    for i in range(9):
        dx = -16 + i * 4
        p.drawLine(QPointF(dx * 0.4, -36), QPointF(dx, 0))
    p.setPen(KEIN_STIFT)
    p.setBrush(QColor('#B23A2A'))
    p.drawRoundedRect(QRectF(-8, -40, 16, 7), 2, 2)
    p.restore()


def zeichne_kehrblech(p):
    """Kleines Kehrblech, Kante vorn im Ursprung am Boden, Griff nach hinten (links)."""
    p.setBrush(linear(0, -14, 0, 0, QColor('#E04A3A'), QColor('#8A1E14')))
    blech = QPainterPath()
    blech.moveTo(10, 0)
    blech.lineTo(-48, 0)
    blech.lineTo(-48, -16)
    blech.quadTo(-20, -8, 10, 0)
    p.drawPath(blech)
    p.drawRoundedRect(QRectF(-72, -14, 26, 6), 3, 3)


def zeichne_keks(p, r):
    """Runder Butterkeks mit Zackenrand, Mitte im Ursprung."""
    pfad = QPainterPath()
    n = 18
    for i in range(n * 2):
        w = i * math.pi / n
        rr = r if i % 2 == 0 else r * 0.9
        pt = QPointF(math.cos(w) * rr, math.sin(w) * rr)
        pfad.moveTo(pt) if i == 0 else pfad.lineTo(pt)
    pfad.closeSubpath()
    p.setBrush(radial(-r * 0.3, -r * 0.3, r * 1.4, QColor('#F2C878'), QColor('#B97E32')))
    p.drawPath(pfad)
    p.setBrush(QColor(120, 70, 20, 150))
    for dx, dy in ((-0.35, -0.3), (0.3, -0.25), (0.0, 0.1), (-0.3, 0.35), (0.35, 0.3)):
        kreis(p, dx * r, dy * r, r * 0.07)


def zeichne_taennchen(p, abgesaegt=False, nur_spitze=False):
    """Kleine Tanne, Stamm im Ursprung am Boden. abgesaegt: nur der Stumpf bleibt.
    nur_spitze: nur der Baum ohne Stamm, Schnittkante im Ursprung (als Mütze)."""
    if not nur_spitze:
        p.setBrush(linear(-4, 0, 4, 0, QColor('#8A5A30'), QColor('#5A3A1E')))
        p.drawRect(QRectF(-4, -12 if abgesaegt else -16, 8, 12 if abgesaegt else 16))
        if abgesaegt:
            p.setBrush(QColor('#E8C890'))
            p.drawEllipse(QRectF(-4, -14, 8, 4))
            return
        p.translate(0, -16)
    for i, (unten, b) in enumerate(((0, 46), (-16, 36), (-30, 24))):
        pfad = QPainterPath()
        pfad.moveTo(0, unten - 24)
        pfad.lineTo(b / 2, unten)
        pfad.lineTo(-b / 2, unten)
        pfad.closeSubpath()
        p.setBrush(linear(-b / 2, unten - 24, b / 2, unten, GRUEN.lighter(130), GRUEN_DUNKEL))
        p.drawPath(pfad)
    p.setBrush(QColor(255, 255, 255, 210))
    for dx, dy in ((-8, -6), (6, -20), (-4, -36)):
        p.drawEllipse(QPointF(dx, dy), 4, 2)


def zeichne_schaufel(p, winkel=0.0, last=False):
    """Schneeschaufel, Griff im Ursprung, Blatt am Stielende in Richtung winkel (0 = nach rechts)."""
    p.save()
    p.rotate(winkel)
    p.setBrush(linear(0, -3, 0, 3, QColor('#B07A42'), QColor('#6B4423')))
    p.drawRoundedRect(QRectF(-6, -3, 96, 6), 3, 3)
    p.setBrush(QColor('#333333'))
    p.drawRoundedRect(QRectF(-12, -7, 10, 14), 4, 4)
    blatt = QPainterPath()
    blatt.moveTo(88, -16)
    blatt.lineTo(122, -18)
    blatt.lineTo(124, 18)
    blatt.lineTo(88, 16)
    blatt.closeSubpath()
    p.setBrush(linear(88, -18, 124, 18, QColor('#3FA0D8'), QColor('#1E5F8F')))
    p.drawPath(blatt)
    if last:
        zeichne_schneewuerfel(p, 106, 0, 26, 0)
    p.restore()


def zeichne_schneewuerfel(p, x, y, a, dreh=0.0):
    """Sauber geschippter Schneewürfel mit Kantenlänge a, Mitte in (x, y)."""
    p.save()
    p.translate(x, y)
    p.rotate(dreh)
    h = a / 2
    t = a * 0.28
    oben = QPainterPath()
    oben.moveTo(-h, -h)
    oben.lineTo(-h + t, -h - t)
    oben.lineTo(h + t, -h - t)
    oben.lineTo(h, -h)
    oben.closeSubpath()
    seite = QPainterPath()
    seite.moveTo(h, -h)
    seite.lineTo(h + t, -h - t)
    seite.lineTo(h + t, h - t)
    seite.lineTo(h, h)
    seite.closeSubpath()
    p.setBrush(WEISS)
    p.drawPath(oben)
    p.setBrush(QColor('#B9CCE4'))
    p.drawPath(seite)
    p.setBrush(linear(0, -h, 0, h, QColor('#F2F7FF'), QColor('#D2E0F0')))
    p.drawRect(QRectF(-h, -h, a, a))
    p.setBrush(QColor(255, 255, 255, 230))
    stern(p, -h * 0.4, -h * 0.4, a * 0.08)
    p.restore()
