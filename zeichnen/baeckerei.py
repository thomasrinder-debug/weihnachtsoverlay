"""Requisiten der Weihnachtsbäckerei: Teig, Nudelholz, Ausstechform, Spritzbeutel, Mehlsack,
Ofen, Lebkuchenhaus, Bratapfel, Keksdose. Alle Maße in Zeichen-Einheiten, Ursprung unten in
der Mitte, wenn nicht anders gesagt."""
import math

from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import QColor, QImage, QPainter, QPainterPath, QTransform

from .figuren import KEKS, KEKS_DUNKEL, augen
from .grundlagen import (GOLD, GOLD_HELL, GRUEN, KEIN_PINSEL, KEIN_STIFT, ROT, ROT_DUNKEL, SCHWARZ, WEISS, kreis,
                         linear, radial, stift)
from .requisiten import zeichne_keks

TEIG = QColor('#F4DFB4')
TEIG_DUNKEL = QColor('#D2AC6E')
HOLZ = QColor('#D29A5C')
HOLZ_DUNKEL = QColor('#8A5A2B')
SILBER = QColor('#E6EBF1')
SILBER_DUNKEL = QColor('#7F8A98')
GUSS = QColor('#FFFDF5')
GUSS_SCHATTEN = QColor('#E4DED0')
MEHL = QColor('#FBF8F0')
SACK = QColor('#E9DDC4')
SACK_DUNKEL = QColor('#B5A07A')
EMAILLE = QColor('#F0E7D3')
EMAILLE_DUNKEL = QColor('#BFAF90')
GLUT = QColor('#FF9A2E')
APFEL = QColor('#D3312F')
APFEL_DUNKEL = QColor('#86161A')
DOSE = QColor('#2F62B3')
DOSE_DUNKEL = QColor('#173670')
KRUEMEL = [QColor('#E9BE72'), QColor('#C98A4B'), QColor('#F2D49A')]


# ---------------------------------------------------------------- Teig und Nudelholz

def zeichne_teig(p, b, h, pose=None, boese=0.0, grinsen=False):
    """Teigklumpen der Breite b und Höhe h. Mit pose bekommt er Augen, boese 0..1 zieht die Brauen
    zusammen, grinsen zeigt ein schadenfrohes Grinsen."""
    pfad = QPainterPath()
    pfad.moveTo(-b / 2, 0)
    pfad.cubicTo(-b / 2, -h * 0.75, -b * 0.3, -h, 0, -h)
    pfad.cubicTo(b * 0.3, -h, b / 2, -h * 0.75, b / 2, 0)
    pfad.closeSubpath()
    p.setPen(KEIN_STIFT)
    p.setBrush(QColor(0, 0, 0, 40))
    p.drawEllipse(QRectF(-b / 2 - 3, -3, b + 6, 6))
    p.setBrush(radial(-b * 0.15, -h * 0.7, max(b, h) * 0.9, TEIG.lighter(108), TEIG_DUNKEL))
    p.drawPath(pfad)
    p.setBrush(QColor(255, 255, 255, 90))
    p.drawEllipse(QRectF(-b * 0.25, -h * 0.85, b * 0.22, h * 0.18))
    p.setBrush(QColor(170, 120, 60, 70))
    for dx, dy in ((0.2, 0.45), (-0.25, 0.3), (0.05, 0.2)):
        kreis(p, dx * b, -dy * h, max(0.8, min(b, h) * 0.04))
    if pose is None or h < 14:
        return
    zeichne_teiggesicht(p, -h * 0.6, pose, boese, grinsen)


def zeichne_teiggesicht(p, ay, pose, boese=0.0, grinsen=False):
    """Augen (Höhe ay), Brauen und Grinsen des lebendigen Teigs."""
    augen(p, (-7, 7), ay, 3.6, 4.4, pose, (pose.blick_x, pose.blick_y), 0.62)
    if boese:
        p.setPen(stift(HOLZ_DUNKEL, 2.2))
        for x, z in ((-7, 1), (7, -1)):
            p.drawLine(QPointF(x - 5 * z, ay - 8 - 3 * boese), QPointF(x + 4 * z, ay - 6 + 2 * boese))
        p.setPen(KEIN_STIFT)
    if grinsen:
        p.setBrush(QColor('#6A3A14'))
        p.drawChord(QRectF(-9, ay + 2, 18, 11), 180 * 16, 180 * 16)
        p.setBrush(WEISS)
        p.drawRect(QRectF(-6, ay + 7.5, 12, 2))


def zeichne_nudelholz(p, laenge=86):
    """Nudelholz waagerecht, Mitte im Ursprung."""
    w = laenge * 0.62
    p.setPen(KEIN_STIFT)
    p.setBrush(linear(0, -7, 0, 7, HOLZ.darker(110), HOLZ_DUNKEL))
    griff = (laenge - w) / 2
    p.drawRoundedRect(QRectF(-laenge / 2, -3.5, griff + 2, 7), 3, 3)
    p.drawRoundedRect(QRectF(w / 2 - 2, -3.5, griff + 2, 7), 3, 3)
    p.setBrush(linear(0, -9, 0, 9, HOLZ.lighter(125), HOLZ_DUNKEL))
    p.drawRoundedRect(QRectF(-w / 2, -9, w, 18), 6, 6)
    p.setBrush(QColor(255, 255, 255, 70))
    p.drawRoundedRect(QRectF(-w / 2 + 4, -6, w - 8, 3.5), 2, 2)
    p.setBrush(HOLZ_DUNKEL)
    for z in (-1, 1):
        kreis(p, z * laenge / 2, 0, 4.2)


# ---------------------------------------------------------------- Ausstechform

def stern_pfad(r, zacken=5, innen=0.48, flach=1.0, dreh=-90):
    pfad = QPainterPath()
    for i in range(zacken * 2):
        w = math.radians(dreh + i * 180 / zacken)
        rr = r if i % 2 == 0 else r * innen
        pt = QPointF(math.cos(w) * rr, math.sin(w) * rr * flach)
        pfad.moveTo(pt) if i == 0 else pfad.lineTo(pt)
    pfad.closeSubpath()
    return pfad


def zeichne_ausstecher(p, r, flach=1.0, rand=9):
    """Sternförmige Ausstechform, Mitte im Ursprung. flach < 1: liegt auf dem Boden (Aufsicht
    schräg von vorn), dann ragt der Blechrand rand Einheiten nach oben."""
    pfad = stern_pfad(r, flach=flach)
    p.setBrush(KEIN_PINSEL)
    if flach < 1:
        p.setPen(stift(SILBER_DUNKEL, 4.5))
        p.drawPath(pfad)
        for i in range(10):
            w = math.radians(-90 + i * 36)
            rr = r if i % 2 == 0 else r * 0.48
            x, y = math.cos(w) * rr, math.sin(w) * rr * flach
            if y > -r * flach * 0.3:
                p.drawLine(QPointF(x, y), QPointF(x, y - rand))
        p.translate(0, -rand)
    p.setPen(stift(SILBER_DUNKEL, 5.5))
    p.drawPath(pfad)
    p.setPen(stift(SILBER, 3))
    p.drawPath(pfad)
    p.setPen(stift(QColor(255, 255, 255, 220), 1.2))
    p.drawPath(stern_pfad(r * 0.97, flach=flach))
    p.setPen(KEIN_STIFT)
    if flach < 1:
        p.translate(0, rand)


def zeichne_teigplatte(p, b, dicke=7, loch=None, delle=0.0):
    """Ausgerollter Teig, Mitte oben im Ursprung, liegt nach unten. loch: (x, r) Sternloch.
    delle: Einsinken in der Mitte (Trampolin), Einheiten."""
    pfad = QPainterPath()
    pfad.moveTo(-b / 2, 0)
    pfad.cubicTo(-b / 6, delle, b / 6, delle, b / 2, 0)
    pfad.lineTo(b / 2, dicke)
    pfad.cubicTo(b / 6, dicke + delle, -b / 6, dicke + delle, -b / 2, dicke)
    pfad.closeSubpath()
    p.setPen(KEIN_STIFT)
    p.setBrush(linear(0, 0, 0, dicke + delle, TEIG.lighter(105), TEIG_DUNKEL))
    p.drawPath(pfad)
    p.setBrush(QColor(255, 255, 255, 60))
    p.drawRect(QRectF(-b / 2 + 4, 0.6, b - 8, 1.6))
    if loch:
        x, r = loch
        p.save()
        p.translate(x, 2)
        p.setBrush(QColor(90, 60, 30, 150))
        p.drawPath(stern_pfad(r * 0.95, flach=0.22))
        p.restore()


def zeichne_teigstern(p, r, flach=1.0):
    p.setPen(stift(TEIG_DUNKEL, 2))
    p.setBrush(radial(-r * 0.3, -r * 0.3 * flach, r * 1.4, TEIG.lighter(108), TEIG_DUNKEL))
    p.drawPath(stern_pfad(r * 0.93, flach=flach))
    p.setPen(KEIN_STIFT)


# ---------------------------------------------------------------- Spritzbeutel und Guss

def zeichne_spritzbeutel(p, druck=0.0, leer=0.0, drall=0.0):
    """Spritzbeutel, Tülle zeigt nach +y, Spitze im Ursprung. druck 0..1 bläht den Beutel,
    leer 0..1 lässt ihn schlaff werden, drall 0..1 verdreht das Ende."""
    b = 22 * (1 + 0.25 * druck) * (1 - 0.55 * leer)
    pfad = QPainterPath()
    pfad.moveTo(-4, -8)
    pfad.cubicTo(-b * 0.9, -26, -b, -48, -b * 0.7, -62)
    pfad.lineTo(b * 0.7, -62)
    pfad.cubicTo(b, -48, b * 0.9, -26, 4, -8)
    pfad.closeSubpath()
    p.setPen(stift(QColor(150, 170, 190, 200), 1.5))
    p.setBrush(QColor(235, 244, 252, 190))
    p.drawPath(pfad)
    p.setPen(KEIN_STIFT)
    if leer < 0.95:
        guss = QPainterPath()
        f = 1 - leer
        guss.moveTo(-3, -10)
        guss.cubicTo(-b * 0.75, -24, -b * 0.82 * f, -44 * f - 4, 0, -46 * f - 6)
        guss.cubicTo(b * 0.82 * f, -44 * f - 4, b * 0.75, -24, 3, -10)
        guss.closeSubpath()
        p.setBrush(linear(-b, 0, b, 0, GUSS, GUSS_SCHATTEN))
        p.drawPath(guss)
    # gedrehtes Ende
    p.setBrush(QColor(210, 225, 240, 220))
    p.save()
    p.translate(0, -66)
    p.rotate(math.sin(drall * 30) * 25 * drall)
    p.drawRoundedRect(QRectF(-b * 0.55, -4, b * 1.1, 6), 3, 3)
    p.drawRoundedRect(QRectF(-3.5, -16, 7, 13), 3, 3)
    p.restore()
    p.setPen(stift(QColor(255, 255, 255, 200), 1.5))
    p.drawLine(QPointF(-b * 0.55, -52), QPointF(-b * 0.4, -24))
    p.setPen(KEIN_STIFT)
    # Tülle
    tuelle = QPainterPath()
    tuelle.moveTo(-6, -12)
    tuelle.lineTo(6, -12)
    tuelle.lineTo(2, 0)
    tuelle.lineTo(-2, 0)
    tuelle.closeSubpath()
    p.setBrush(linear(-6, 0, 6, 0, SILBER, SILBER_DUNKEL))
    p.drawPath(tuelle)
    p.setPen(stift(SILBER_DUNKEL, 1))
    for x in (-3, 0, 3):
        p.drawLine(QPointF(x * 1.3, -11), QPointF(x * 0.5, -1))
    p.setPen(KEIN_STIFT)


def zeichne_sahnehaube(p, g=1.0, kirsche=True):
    """Gussberg wie eine Torte: drei Wülste übereinander, Mitte unten im Ursprung."""
    p.setPen(KEIN_STIFT)
    for i, (b, h, y) in enumerate(((70, 30, 0), (54, 26, -22), (36, 22, -40))):
        b, h, y = b * g, h * g, y * g
        p.setBrush(radial(-b * 0.2, y - h * 0.8, b * 0.7, GUSS, GUSS_SCHATTEN))
        p.drawEllipse(QRectF(-b / 2, y - h, b, h))
        p.setPen(stift(GUSS_SCHATTEN, 1.6 * g))
        p.drawArc(QRectF(-b / 2 + 4 * g, y - h * 0.8, b - 8 * g, h * 0.7), 200 * 16, 140 * 16)
        p.setPen(KEIN_STIFT)
    spitze = QPainterPath()
    spitze.moveTo(-12 * g, -56 * g)
    spitze.quadTo(0, -74 * g, 4 * g, -84 * g)
    spitze.quadTo(6 * g, -70 * g, 13 * g, -57 * g)
    spitze.closeSubpath()
    p.setBrush(linear(-12 * g, 0, 12 * g, 0, GUSS, GUSS_SCHATTEN))
    p.drawPath(spitze)
    if kirsche:
        p.setBrush(radial(1 * g, -91 * g, 9 * g, ROT.lighter(150), ROT_DUNKEL))
        kreis(p, 3 * g, -88 * g, 7 * g)
        p.setBrush(QColor(255, 255, 255, 200))
        kreis(p, 1 * g, -91 * g, 2 * g)


def zeichne_gussklecks(p, r):
    p.setPen(KEIN_STIFT)
    p.setBrush(radial(-r * 0.3, -r * 0.3, r * 1.3, GUSS, GUSS_SCHATTEN))
    pfad = QPainterPath()
    for i in range(12):
        w = i * math.pi / 6
        rr = r * (1.0 if i % 2 else 0.78)
        pt = QPointF(math.cos(w) * rr, math.sin(w) * rr)
        pfad.moveTo(pt) if i == 0 else pfad.lineTo(pt)
    pfad.closeSubpath()
    p.drawPath(pfad)


def zeichne_riesenkeks(p, r, kringel=0.0):
    """Großer runder Keks, auf der Kante stehend, Mitte unten im Ursprung. kringel 0..1: Guss-Spirale."""
    p.save()
    p.translate(0, -r)
    p.setPen(stift(KEKS_DUNKEL, 2.5))
    p.setBrush(radial(-r * 0.3, -r * 0.3, r * 1.4, KEKS.lighter(130), KEKS.darker(110)))
    kreis(p, 0, 0, r)
    p.setPen(stift(QColor(255, 255, 255, 60), 2))
    p.drawArc(QRectF(-r * 0.8, -r * 0.8, r * 1.6, r * 1.6), 100 * 16, 80 * 16)
    if kringel > 0:
        pfad = QPainterPath()
        n = int(60 * kringel)
        for i in range(n + 1):
            w = i * 0.32
            rr = r * 0.72 * (1 - i / 64)
            pt = QPointF(math.cos(w) * rr, math.sin(w) * rr)
            pfad.moveTo(pt) if i == 0 else pfad.lineTo(pt)
        p.setPen(stift(GUSS, 3.4))
        p.drawPath(pfad)
    p.setPen(KEIN_STIFT)
    p.restore()


# ---------------------------------------------------------------- Mehlsack

def zeichne_mehlsack(p, offen=False, platt=0.0, zug=0.0):
    """Mehlsack, Ursprung unten Mitte. zug: Einheiten, um die die Kordel nach -x gezogen wird.
    platt 0..1: leer und zusammengesunken."""
    h = 92 * (1 - 0.7 * platt)
    b = 66 * (1 + 0.25 * platt)
    pfad = QPainterPath()
    pfad.moveTo(-b / 2, 0)
    pfad.cubicTo(-b * 0.62, -h * 0.5, -b * 0.5, -h * 0.85, -b * 0.18, -h)
    pfad.lineTo(b * 0.18, -h)
    pfad.cubicTo(b * 0.5, -h * 0.85, b * 0.62, -h * 0.5, b / 2, 0)
    pfad.closeSubpath()
    p.setPen(KEIN_STIFT)
    p.setBrush(QColor(0, 0, 0, 40))
    p.drawEllipse(QRectF(-b / 2 - 4, -4, b + 8, 8))
    p.setBrush(radial(-b * 0.2, -h * 0.6, b, SACK.lighter(108), SACK_DUNKEL))
    p.drawPath(pfad)
    p.setPen(stift(SACK_DUNKEL, 1.2, Qt.PenStyle.DashLine))
    p.drawLine(QPointF(-b * 0.44, -h * 0.2), QPointF(b * 0.44, -h * 0.2))
    p.setPen(KEIN_STIFT)
    if platt < 0.5:
        # Ähre als Aufdruck
        p.setPen(stift(QColor('#B88A3A'), 2))
        p.drawLine(QPointF(0, -h * 0.3), QPointF(0, -h * 0.68))
        p.setPen(KEIN_STIFT)
        p.setBrush(QColor('#D9A845'))
        for k in range(4):
            y = -h * 0.42 - k * 7
            for z in (-1, 1):
                p.drawEllipse(QPointF(z * 4, y), 3.2, 5)
        kreis(p, 0, -h * 0.42 - 31, 3)
    if offen:
        p.setBrush(MEHL)
        p.drawEllipse(QRectF(-b * 0.3, -h - 5, b * 0.6, 10))
        return
    # Hals und Knoten mit Kordel
    p.setBrush(SACK_DUNKEL)
    hals = QPainterPath()
    hals.moveTo(-b * 0.18, -h)
    hals.lineTo(-b * 0.3, -h - 14)
    hals.lineTo(b * 0.3, -h - 14)
    hals.lineTo(b * 0.18, -h)
    hals.closeSubpath()
    p.drawPath(hals)
    p.setBrush(QColor('#C2412F'))
    p.drawRoundedRect(QRectF(-b * 0.2, -h - 4, b * 0.4, 5), 2, 2)
    kreis(p, -b * 0.2, -h - 1.5, 4)
    p.setPen(stift(QColor('#C2412F'), 2.4))
    p.setBrush(KEIN_PINSEL)
    kordel = QPainterPath()
    kordel.moveTo(-b * 0.2, -h - 1.5)
    kordel.quadTo(-b * 0.2 - zug * 0.4, -h + 12 - zug * 0.1, -b * 0.2 - 8 - zug, -h + 4)
    p.drawPath(kordel)
    p.setPen(KEIN_STIFT)


# ---------------------------------------------------------------- Ofen

def zeichne_ofen(p, tuer=0.0, wackel=0.0, t=0.0):
    """Kleiner Backofen von vorn auf Füßchen, Ursprung unten Mitte. tuer 0..1 klappt die Tür
    nach unten auf, wackel 0..1 lässt ihn zittern."""
    p.save()
    p.translate(math.sin(t * 60) * 2 * wackel, -abs(math.sin(t * 47)) * 3 * wackel)
    p.setPen(KEIN_STIFT)
    p.setBrush(QColor('#4A4A4A'))
    for x in (-34, 28):
        p.drawRoundedRect(QRectF(x, -8, 6, 8), 2, 2)
    p.setBrush(linear(-46, 0, 46, 0, EMAILLE.lighter(104), EMAILLE_DUNKEL))
    p.drawRoundedRect(QRectF(-46, -104, 92, 98), 10, 10)
    # Bedienleiste mit Knöpfen
    p.setBrush(QColor('#C8312C'))
    p.drawRoundedRect(QRectF(-40, -98, 80, 16), 5, 5)
    for x in (-24, 0, 24):
        p.setBrush(radial(x - 1, -92, 6, SILBER, SILBER_DUNKEL))
        kreis(p, x, -90, 4.5)
    # Innenraum
    p.setBrush(radial(0, -40, 46, GLUT.lighter(130), QColor('#7A2E0A')))
    p.drawRoundedRect(QRectF(-34, -74, 68, 56), 6, 6)
    p.setBrush(QColor(60, 30, 10, 150))
    p.drawRect(QRectF(-30, -40, 60, 3))
    if tuer < 0.98:
        h = 56 * math.cos(tuer * math.pi / 2)
        p.setBrush(linear(0, -74, 0, -18, EMAILLE, EMAILLE_DUNKEL))
        p.drawRoundedRect(QRectF(-38, -18 - h, 76, h + 2), 6, 6)
        if h > 14:
            p.setBrush(radial(0, -18 - h / 2, 40, QColor(255, 160, 60, 230), QColor(90, 30, 10, 240)))
            p.drawRoundedRect(QRectF(-26, -18 - h + 9, 52, h - 18), 5, 5)
            p.setBrush(QColor(255, 255, 255, 70))
            p.drawRect(QRectF(-22, -18 - h + 12, 16, 3))
        p.setBrush(linear(0, 0, 0, 4, SILBER, SILBER_DUNKEL))
        p.drawRoundedRect(QRectF(-24, -18 - h - 2, 48, 5), 2.5, 2.5)
    if tuer > 0.02:
        tief = 22 * math.sin(tuer * math.pi / 2)
        klappe = QPainterPath()
        klappe.moveTo(-38, -18)
        klappe.lineTo(38, -18)
        klappe.lineTo(44, -18 + tief)
        klappe.lineTo(-44, -18 + tief)
        klappe.closeSubpath()
        p.setBrush(linear(0, -18, 0, -18 + tief, EMAILLE_DUNKEL, EMAILLE))
        p.drawPath(klappe)
    p.restore()


# ---------------------------------------------------------------- Lebkuchenhaus

def zeichne_lebkuchenplatte(p, b, h, fenster=0, tuer=False):
    """Lebkuchenplatte mit Zuckergussrand, Ursprung unten Mitte, steht aufrecht."""
    p.setPen(stift(KEKS_DUNKEL, 2))
    p.setBrush(linear(-b / 2, -h, b / 2, 0, KEKS.lighter(115), KEKS.darker(112)))
    p.drawRoundedRect(QRectF(-b / 2, -h, b, h), 3, 3)
    p.setPen(stift(GUSS, 2))
    p.setBrush(KEIN_PINSEL)
    welle = QPainterPath()
    n = max(2, int(b / 7))
    welle.moveTo(-b / 2 + 2, -h + 4)
    for k in range(n):
        x0 = -b / 2 + 2 + (b - 4) * k / n
        welle.quadTo(x0 + (b - 4) / n / 2, -h + 8, x0 + (b - 4) / n, -h + 4)
    p.drawPath(welle)
    if fenster:
        for i in range(fenster):
            x = -b / 2 + b * (i + 0.5) / fenster - 6
            p.setPen(stift(GUSS, 1.8))
            p.setBrush(QColor('#F6C344'))
            p.drawRoundedRect(QRectF(x, -h * 0.68, 12, 12), 2, 2)
            p.drawLine(QPointF(x + 6, -h * 0.68), QPointF(x + 6, -h * 0.68 + 12))
            p.drawLine(QPointF(x, -h * 0.68 + 6), QPointF(x + 12, -h * 0.68 + 6))
    if tuer:
        p.setPen(stift(GUSS, 1.8))
        p.setBrush(KEKS.darker(140))
        p.drawRoundedRect(QRectF(-7, -20, 14, 20), 6, 6)
    p.setPen(KEIN_STIFT)
    p.setBrush(ROT)
    for x in (-b * 0.3, 0, b * 0.3):
        kreis(p, x, -5, 2.4)


def zeichne_dachplatte(p, laenge, dicke=9):
    """Dachplatte mit Schneeguss und Bonbons, liegt von (0, 0) nach (laenge, 0)."""
    p.setPen(stift(KEKS_DUNKEL, 2))
    p.setBrush(linear(0, -dicke, 0, 0, KEKS.lighter(110), KEKS.darker(115)))
    p.drawRoundedRect(QRectF(0, -dicke, laenge, dicke), 3, 3)
    p.setPen(KEIN_STIFT)
    p.setBrush(GUSS)
    p.drawRoundedRect(QRectF(-2, -dicke - 4, laenge + 4, 6), 3, 3)
    for k in range(int(laenge / 10)):
        p.drawEllipse(QRectF(2 + k * 10, -dicke, 5, 6 + (k % 3) * 2))
    for k, farbe in enumerate((ROT, GRUEN, GOLD)):
        p.setBrush(radial(laenge * (0.25 + 0.25 * k) - 1, -dicke - 6, 4, farbe.lighter(150), farbe))
        kreis(p, laenge * (0.25 + 0.25 * k), -dicke - 5, 3.2)


# ---------------------------------------------------------------- Bratapfel

def zeichne_teller(p, r=30):
    p.setPen(KEIN_STIFT)
    p.setBrush(linear(0, -5, 0, 4, WEISS, QColor('#C9D2DE')))
    p.drawEllipse(QRectF(-r, -5, 2 * r, 9))
    p.setBrush(QColor('#E8EDF4'))
    p.drawEllipse(QRectF(-r * 0.7, -4, r * 1.4, 5))


def zeichne_bratapfel(p, r=17, deckel=0.0):
    """Bratapfel mit Deckelchen und Stiel, Ursprung unten Mitte. deckel: Einheiten, die das
    Deckelchen abhebt."""
    p.setPen(KEIN_STIFT)
    p.setBrush(radial(-r * 0.35, -r * 1.2, r * 1.5, APFEL.lighter(140), APFEL_DUNKEL))
    p.drawEllipse(QRectF(-r, -r * 1.85, 2 * r, r * 1.85))
    p.setBrush(QColor(255, 255, 255, 110))
    p.drawEllipse(QRectF(-r * 0.6, -r * 1.55, r * 0.35, r * 0.5))
    # Füllung
    p.setBrush(QColor('#E8B95A'))
    p.drawEllipse(QRectF(-r * 0.5, -r * 1.92, r, r * 0.3))
    p.save()
    p.translate(0, -r * 1.8 - deckel)
    p.setBrush(radial(-2, -4, r * 0.7, APFEL.lighter(130), APFEL_DUNKEL))
    p.drawChord(QRectF(-r * 0.55, -r * 0.45, r * 1.1, r * 0.8), 0, 180 * 16)
    p.setPen(stift(HOLZ_DUNKEL, 2.2))
    p.drawLine(QPointF(0, -r * 0.4), QPointF(2, -r * 0.75))
    p.setPen(KEIN_STIFT)
    p.setBrush(GRUEN)
    p.drawEllipse(QRectF(2, -r * 0.85, 8, 4))
    p.restore()


# ---------------------------------------------------------------- Keksdose

def zeichne_keksdose(p, offen=False):
    """Runde blaue Blechdose, Ursprung unten Mitte."""
    p.setPen(KEIN_STIFT)
    p.setBrush(linear(-40, 0, 40, 0, DOSE.lighter(130), DOSE_DUNKEL))
    p.drawRect(QRectF(-40, -40, 80, 34))
    p.drawEllipse(QRectF(-40, -12, 80, 12))
    p.setBrush(GOLD)
    p.drawRect(QRectF(-40, -34, 80, 3))
    p.drawRect(QRectF(-40, -16, 80, 3))
    for k in range(5):
        x = -28 + k * 14
        p.setBrush(GOLD_HELL if k % 2 else GOLD)
        p.drawPath(stern_pfad(4.5).translated(x, -23))
    if offen:
        p.setBrush(QColor('#14284F'))
        p.drawEllipse(QRectF(-40, -46, 80, 12))
        p.setBrush(radial(0, -42, 30, QColor('#F2C878'), QColor('#B97E32')))
        p.drawEllipse(QRectF(-34, -45, 68, 8))
    else:
        p.save()
        p.translate(0, -40)
        zeichne_dosendeckel(p)
        p.restore()


def zeichne_dosendeckel(p):
    """Deckel, Ursprung Mitte unten."""
    p.setPen(KEIN_STIFT)
    p.setBrush(linear(-42, 0, 42, 0, DOSE.lighter(145), DOSE_DUNKEL))
    p.drawRect(QRectF(-42, -9, 84, 9))
    p.drawEllipse(QRectF(-42, -15, 84, 12))
    p.setBrush(GOLD)
    p.drawRect(QRectF(-42, -3, 84, 2.5))
    p.setBrush(radial(0, -10, 22, GOLD_HELL, GOLD))
    p.drawEllipse(QRectF(-16, -13, 32, 7))


def zeichne_keksberg(p, b, h, t=0.0):
    """Haufen aus Keksen, Ursprung unten Mitte."""
    if h < 2:
        return
    p.setPen(KEIN_STIFT)
    pfad = QPainterPath()
    pfad.moveTo(-b / 2, 0)
    pfad.cubicTo(-b * 0.4, -h * 0.9, -b * 0.15, -h, 0, -h)
    pfad.cubicTo(b * 0.15, -h, b * 0.4, -h * 0.9, b / 2, 0)
    pfad.closeSubpath()
    p.setBrush(linear(0, -h, 0, 0, QColor('#E2AE62'), QColor('#9A6428')))
    p.drawPath(pfad)
    p.save()
    p.setClipPath(pfad.translated(0, -8).united(pfad))
    r = 11
    reihe = 0
    y = -6.0
    while y > -h - r:
        breite = b * (1 - ((-y) / (h + r)) ** 2) * 0.55
        x = -breite + (reihe % 2) * r
        while x <= breite:
            p.save()
            p.translate(x, y)
            p.rotate((x * 7 + y * 13) % 40 - 20)
            p.scale(1, 0.8)
            zeichne_keks(p, r)
            p.restore()
            x += 2 * r - 2
        y -= r * 1.3
        reihe += 1
    p.restore()


# ---------------------------------------------------------------- Mehl auf einer Figur

class Bestaeubt:
    """Hülle um eine Figurenart: zeichnet sie mit Mehl überstäubt (d.mehl 0..1), etwa
    self.dazu('w', Bestaeubt(Wichtel), groesse=0.6). Die Augen bleiben dunkel sichtbar,
    wenn die Figur Punkte für sie angibt (augen=[(x, y), ...] in Figuren-Einheiten)."""

    def __init__(self, art, augen=()):
        self.art, self.augen = art, list(augen)
        self.KASTEN, self.KOPF = art.KASTEN, art.KOPF

    def zeichne(self, p, d):
        m = getattr(d, 'mehl', 0.0)
        if m <= 0.01:
            self.art.zeichne(p, d)
            return
        tr = p.transform()
        rahmen = tr.mapRect(self.KASTEN.adjusted(-20, -30, 20, 10)).toAlignedRect()
        if rahmen.width() < 2 or rahmen.height() < 2:
            return
        dpr = max(1.0, p.device().devicePixelRatioF())
        bild = QImage(int(rahmen.width() * dpr), int(rahmen.height() * dpr),
                      QImage.Format.Format_ARGB32_Premultiplied)
        bild.setDevicePixelRatio(dpr)
        bild.fill(Qt.GlobalColor.transparent)
        q = QPainter(bild)
        q.setRenderHint(QPainter.RenderHint.Antialiasing)
        q.setTransform(tr * QTransform.fromTranslate(-rahmen.x(), -rahmen.y()))
        q.setPen(KEIN_STIFT)
        self.art.zeichne(q, d)
        q.resetTransform()
        q.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceAtop)
        c = QColor(MEHL)
        c.setAlphaF(0.9 * m)
        q.fillRect(QRectF(0, 0, rahmen.width(), rahmen.height()), c)
        q.end()
        p.save()
        p.resetTransform()
        p.drawImage(QPointF(rahmen.x(), rahmen.y()), bild)
        p.restore()
        if m > 0.5 and not d.pose.auge_zu:
            p.setBrush(SCHWARZ)
            for x, y in self.augen:
                p.drawEllipse(QPointF(x, y + d.pose.hub), 2.6, 3.4)
