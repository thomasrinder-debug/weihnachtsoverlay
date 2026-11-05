"""Weitere Figuren: Lebkuchenmann, Schneemann, Wichtel, Pinguin, Nussknacker,
Tannenbaum, Eisbär und Rentier.

Jede Figur ist eine Klasse mit KASTEN (Umriss in Einheiten, Fuß im Ursprung,
Blick nach rechts), KOPF (Punkt über dem Kopf für die Schreckstriche) und
zeichne(p, d). d ist der Darsteller aus szenen/basis.py: d.pose (wie beim
Weihnachtsmann), d.t und eigene Merkmale wie d.nase oder d.biss.
"""
import math

from PyQt6.QtCore import QPointF, QRectF
from PyQt6.QtGui import QColor, QPainterPath, QTransform

from .grundlagen import *  # noqa: F401,F403  Farben und Hilfen
from .requisiten import zeichne_rentier

KEKS = QColor('#C98A4B')
KEKS_DUNKEL = QColor('#8A4F22')
SCHNEE = QColor('#FFFFFF')
SCHNEE_SCHATTEN = QColor('#BCD0E8')
KOHLE = QColor('#2B2B30')
KAROTTE = QColor('#F08A24')
WICHTEL_GRUEN = QColor('#2E9A52')
EISBAER = QColor('#F7F4EC')
EISBAER_SCHATTEN = QColor('#CFC6B4')
HOLZ_HAUT = QColor('#F6D7B5')
BLAU = QColor('#2B4C9B')


# ---------------------------------------------------------------- Gesichter

def augen(p, xs, y, rx, ry, pose, blick=(0.0, 0.0), pupille=0.6):
    """Augen mit Glanzpunkt: zu beim Blinzeln, groß beim Schreck."""
    g = 1 + 0.4 * pose.schreck
    for x in xs:
        if pose.auge_zu:
            lid = QPainterPath()
            lid.moveTo(x - rx, y)
            lid.quadTo(x, y + ry * 0.7, x + rx, y)
            p.setPen(stift(SCHWARZ, max(1.2, rx * 0.45)))
            p.setBrush(KEIN_PINSEL)
            p.drawPath(lid)
            p.setPen(KEIN_STIFT)
            continue
        p.setBrush(WEISS)
        p.drawEllipse(QPointF(x, y), rx * g, ry * g)
        px, py = x + blick[0] * rx * 0.45 * g, y + blick[1] * ry * 0.4 * g
        p.setBrush(SCHWARZ)
        p.drawEllipse(QPointF(px, py), rx * pupille * (1 - 0.3 * pose.schreck),
                      ry * pupille * (1 - 0.3 * pose.schreck))
        p.setBrush(WEISS)
        kreis(p, px + rx * 0.22, py - ry * 0.25, max(0.6, rx * 0.22))


def brauen(p, xs, y, breite, pose, farbe):
    """Brauen, die sich vor Sorge schräg stellen und beim Schreck hochgehen."""
    p.setPen(stift(farbe, breite * 0.35))
    mitte = sum(xs) / len(xs)
    hoch = y - breite * 0.6 * pose.schreck
    w, sorge = breite * 0.5, pose.sorge * breite * 0.4
    for x in xs:
        zur_mitte = 1 if x < mitte else -1
        p.drawLine(QPointF(x - zur_mitte * w, hoch), QPointF(x + zur_mitte * w, hoch - sorge))
    p.setPen(KEIN_STIFT)


def mund(p, x, y, b, pose, farbe=QColor('#7A1F1F')):
    """Lächeln, offen beim Rufen, rundes O beim Schreck."""
    if pose.schreck > 0.2:
        p.setBrush(farbe)
        p.drawEllipse(QPointF(x, y + b * 0.2), b * 0.38, b * (0.25 + 0.35 * pose.schreck))
    elif pose.mund_offen:
        p.setBrush(farbe)
        p.drawChord(QRectF(x - b * 0.5, y - b * 0.35, b, b * 0.8), 180 * 16, 180 * 16)
    else:
        p.setPen(stift(farbe, max(1.0, b * 0.14)))
        p.setBrush(KEIN_PINSEL)
        p.drawArc(QRectF(x - b * 0.5, y - b * 0.45, b, b * 0.6), 200 * 16, 140 * 16)
        p.setPen(KEIN_STIFT)


def wangen(p, xs, y, r):
    for x in xs:
        p.setBrush(radial(x, y, r, QColor(240, 110, 110, 160), QColor(240, 110, 110, 0)))
        kreis(p, x, y, r)


def blick_x(pose):
    return 0.0 if pose.kopf_vorn else 1.0


def huepfer(pose):
    """Wie hoch eine beinlose Figur gerade hüpft (0..1), aus dem Beinschwung der Gangart."""
    return min(1.0, abs(pose.bein_v) / 30)


# ---------------------------------------------------------------- Lebkuchenmann

def _glied(laenge, breite, x, y, winkel):
    pfad = QPainterPath()
    pfad.addRoundedRect(QRectF(-breite / 2, -breite / 2, breite, laenge + breite / 2), breite / 2, breite / 2)
    tr = QTransform()
    tr.translate(x, y)
    tr.rotate(winkel)
    return tr.map(pfad), tr


class Lebkuchenmann:
    """Flacher Keks mit Zuckerguss und Gummibonbon-Knöpfen. d.biss: ein Stück vom Kopf fehlt."""
    KASTEN = QRectF(-80, -160, 160, 166)
    KOPF = (0, -156)

    @staticmethod
    def zeichne(p, d):
        pose, h = d.pose, d.pose.hub
        glieder = [
            _glied(40, 21, 22, -88 + h, -30 + 0.9 * pose.arm_v),
            _glied(40, 21, -22, -88 + h, 30 - 0.9 * pose.arm_h),
            _glied(44, 23, 12, -48 + h, -6 + pose.bein_v),
            _glied(44, 23, -12, -48 + h, 6 + pose.bein_h),
        ]
        umriss = QPainterPath()
        umriss.addRoundedRect(QRectF(-27, -104 + h, 54, 64), 24, 24)
        umriss.addEllipse(QPointF(0, -124 + h), 28, 27)
        for pfad, _ in glieder:
            umriss = umriss.united(pfad)
        if getattr(d, 'biss', False):
            for bx, by, r in ((20, -146, 11), (27, -134, 9), (12, -152, 9)):
                loch = QPainterPath()
                loch.addEllipse(QPointF(bx, by + h), r, r)
                umriss = umriss.subtracted(loch)
        p.setPen(stift(KEKS_DUNKEL, 3))
        p.setBrush(radial(-10, -110 + h, 110, KEKS.lighter(115), KEKS.darker(118)))
        p.drawPath(umriss)
        p.setPen(KEIN_STIFT)
        # Zuckerguss-Wellen an Händen und Füßen
        p.setPen(stift(WEISS, 2.6))
        p.setBrush(KEIN_PINSEL)
        for i, (_, tr) in enumerate(glieder):
            yy = 30 if i < 2 else 34
            welle = QPainterPath()
            welle.moveTo(-8, yy)
            for k in range(4):
                welle.quadTo(-6 + k * 4, yy + (3 if k % 2 else -3), -4 + k * 4, yy)
            p.drawPath(tr.map(welle))
        p.setPen(KEIN_STIFT)
        for i, (farbe, yy) in enumerate(((ROT, -84), (GRUEN, -64))):
            p.setBrush(radial(-2, yy - 3 + h, 8, farbe.lighter(150), farbe))
            p.drawEllipse(QPointF(0, yy + h), 6, 5.5)
            p.setBrush(QColor(255, 255, 255, 170))
            kreis(p, -2, yy - 2 + h, 1.4)
        bx = 3 * blick_x(pose)
        wangen(p, (-15 + bx, 15 + bx), -116 + h, 7)
        augen(p, (-9 + bx, 9 + bx), -128 + h, 4.2, 5, pose, (blick_x(pose), 0), 0.7)
        if pose.schreck > 0.2 or pose.mund_offen:
            mund(p, bx, -112 + h, 14, pose, QColor('#5A2A10'))
        else:
            p.setPen(stift(WEISS, 2.4))
            p.setBrush(KEIN_PINSEL)
            p.drawArc(QRectF(-9 + bx, -121 + h, 18, 12), 200 * 16, 140 * 16)
            p.setPen(KEIN_STIFT)
        if pose.sorge or pose.schreck:
            brauen(p, (-9 + bx, 9 + bx), -138 + h, 7, pose, WEISS)


# ---------------------------------------------------------------- Schneemann

def zeichne_karotte(p, x, y, winkel, laenge=26):
    """Möhrennase, Wurzel in (x, y), Spitze in Richtung winkel (Grad, 0 = nach rechts)."""
    p.save()
    p.translate(x, y)
    p.rotate(winkel)
    nase = QPainterPath()
    nase.moveTo(-2, -5.5)
    nase.quadTo(laenge * 0.6, -3, laenge, 0)
    nase.quadTo(laenge * 0.6, 3, -2, 5.5)
    nase.closeSubpath()
    p.setBrush(linear(0, -5, 0, 5, KAROTTE.lighter(125), KAROTTE.darker(125)))
    p.drawPath(nase)
    p.setPen(stift(QColor(160, 70, 10, 150), 1.1))
    for k in (0.3, 0.5, 0.7):
        p.drawLine(QPointF(laenge * k, -3.6 * (1 - k)), QPointF(laenge * k, -1.2 * (1 - k) + 0.4))
    p.setPen(KEIN_STIFT)
    p.restore()


def zeichne_schneekugel(p, x, y, r):
    p.setBrush(radial(x - r * 0.35, y - r * 0.4, r * 1.5, SCHNEE, SCHNEE_SCHATTEN))
    kreis(p, x, y, r)
    p.setBrush(QColor(255, 255, 255, 200))
    for dx, dy, rr in ((-0.45, -0.5, 0.07), (-0.2, -0.65, 0.05), (0.3, -0.55, 0.04)):
        kreis(p, x + dx * r, y + dy * r, rr * r)


def zeichne_zweig(p, x, y, winkel, laenge=48, winken=0.0):
    p.save()
    p.translate(x, y)
    p.rotate(winkel)
    braun = QColor('#6B4423')
    p.setPen(stift(braun, 4))
    p.drawLine(QPointF(0, 0), QPointF(0, laenge))
    p.setPen(stift(braun, 2.6))
    p.drawLine(QPointF(0, laenge * 0.45), QPointF(-9, laenge * 0.62))
    for w in (-28 + winken, 0 + winken, 28 + winken):
        r = math.radians(w)
        p.drawLine(QPointF(0, laenge), QPointF(math.sin(r) * 11, laenge + math.cos(r) * 11))
    p.setPen(KEIN_STIFT)
    p.restore()


class Schneemann:
    """Drei Kugeln, Kohleaugen, Pudelmütze, Schal und Zweigarme.
    d.nase: Möhre im Gesicht, d.nase_dreh: wie herum sie steckt.
    d.teile: Versatz (dx, dy, drehung) für untere, mittlere und Kopfkugel."""
    KASTEN = QRectF(-85, -262, 170, 268)
    KOPF = (6, -258)
    KEINE_TEILE = ((0, 0, 0), (0, 0, 0), (0, 0, 0))

    @staticmethod
    def zeichne(p, d):
        pose, t = d.pose, d.t
        hupf = huepfer(pose)
        teile = getattr(d, 'teile', Schneemann.KEINE_TEILE)
        p.setBrush(QColor(90, 130, 190, 60))
        p.drawEllipse(QPointF(teile[0][0], 0), 48 * (1 - 0.3 * hupf), 6)
        p.save()
        p.translate(0, -16 * hupf)
        # untere Kugel
        dx, dy, dreh = teile[0]
        p.save()
        p.translate(dx, -50 + dy)
        p.rotate(dreh)
        zeichne_schneekugel(p, 0, 0, 50)
        p.restore()
        # Mitte mit Armen und Knöpfen
        dx, dy, dreh = teile[1]
        p.save()
        p.translate(dx, -128 + dy)
        p.rotate(dreh)
        zeichne_zweig(p, -22, -12, 105 - 0.6 * pose.arm_h)
        zeichne_schneekugel(p, 0, 0, 36)
        for bx, by in ((10, -18), (13, 0), (10, 18)):
            p.setBrush(radial(bx - 1, by - 1, 5, QColor('#55555C'), KOHLE))
            kreis(p, bx, by, 4)
        arm_hoch = pose.arm_v < -60
        arm = (20, -12, -105 + 0.32 * pose.arm_v, math.sin(t * 9) * 12 * arm_hoch)
        if not arm_hoch:
            zeichne_zweig(p, *arm[:3], winken=arm[3])
        mitte = p.transform()
        p.restore()
        # Kopf mit Schal und Mütze
        dx, dy, dreh = teile[2]
        p.save()
        p.translate(dx + 4, -188 + dy)
        p.rotate(dreh)
        flatter = math.sin(t * 7) * 4
        schal_ende = QPainterPath()
        schal_ende.moveTo(-14, 26)
        schal_ende.cubicTo(-26, 40, -24 + flatter, 54, -32 + flatter, 64)
        schal_ende.lineTo(-20 + flatter, 66)
        schal_ende.cubicTo(-14, 52, -4, 40, -2, 28)
        schal_ende.closeSubpath()
        p.setBrush(linear(-30, 30, 0, 60, ROT_HELL, ROT_DUNKEL))
        p.drawPath(schal_ende)
        zeichne_schneekugel(p, 0, 0, 28)
        bx = 7 * blick_x(pose)
        augen(p, (-7 + bx, 7 + bx), -6, 3.4, 3.8, pose, (blick_x(pose), 0), 0.75)
        if pose.sorge or pose.schreck:
            brauen(p, (-7 + bx, 7 + bx), -14, 7, pose, KOHLE)
        if pose.schreck > 0.2 or pose.mund_offen:
            mund(p, bx, 11, 12, pose, KOHLE)
        else:
            p.setBrush(KOHLE)
            for k in range(5):
                w = math.radians(200 + k * 35)
                kreis(p, bx + math.cos(w) * 10, 9 - math.sin(w) * 5, 1.9)
        if getattr(d, 'nase', True):
            dreh = getattr(d, 'nase_dreh', 0)
            winkel = dreh + (25 if pose.kopf_vorn else -8)
            zeichne_karotte(p, bx + 1, 2, winkel, 16 if pose.kopf_vorn and not dreh else 24)
        p.setBrush(linear(-30, 22, 30, 32, ROT_HELL, ROT_DUNKEL))
        p.drawRoundedRect(QRectF(-26, 20, 52, 13), 6, 6)
        p.setBrush(WEISS)
        for sx in (-14, 0, 14):
            p.drawRect(QRectF(sx - 2, 21, 4, 11))
        # Pudelmütze, schief
        if getattr(d, 'muetze', True):
            p.save()
            p.translate(-2, -18)
            p.rotate(-12 + math.sin(t * 2.5) * 2)
            haube = QPainterPath()
            haube.moveTo(-24, 4)
            haube.cubicTo(-24, -30, 22, -30, 22, 4)
            haube.closeSubpath()
            p.setBrush(linear(-20, -24, 20, 4, GRUEN.lighter(125), GRUEN_DUNKEL))
            p.drawPath(haube)
            p.setPen(stift(QColor(255, 255, 255, 120), 1.6))
            for sx in (-12, -4, 4, 12):
                p.drawLine(QPointF(sx, 0), QPointF(sx * 0.8, -16))
            p.setPen(KEIN_STIFT)
            p.setBrush(linear(0, 0, 0, 10, ROT_HELL, ROT_DUNKEL))
            p.drawRoundedRect(QRectF(-27, -1, 52, 10), 5, 5)
            flausch(p, [(-1 + dx2, -26 + dy2) for dx2, dy2 in ((0, 0), (-4, -3), (4, -3), (-3, 4), (4, 3))],
                    5.5, False)
            p.restore()
        p.restore()
        if arm_hoch:
            p.save()
            p.setTransform(mitte)
            zeichne_zweig(p, *arm[:3], winken=arm[3])
            p.restore()
        p.restore()


# ---------------------------------------------------------------- Wichtel

def _wichtelbein(p, y, winkel, hinten):
    d = 125 if hinten else 100
    p.save()
    p.translate(0, y)
    p.rotate(winkel)
    p.setBrush(WEISS.darker(d))
    p.drawRoundedRect(QRectF(-6, -2, 12, 42), 6, 6)
    p.setBrush(ROT.darker(d))
    for k in range(4):
        p.drawRect(QRectF(-6, 4 + k * 9, 12, 4.5))
    schuh = QPainterPath()
    schuh.moveTo(-8, 36)
    schuh.cubicTo(-8, 46, 4, 48, 14, 46)
    schuh.cubicTo(22, 45, 26, 38, 22, 34)
    schuh.cubicTo(20, 32, 17, 35, 19, 37)
    schuh.cubicTo(14, 40, 8, 38, 6, 34)
    schuh.closeSubpath()
    p.setBrush(linear(0, 34, 0, 48, WICHTEL_GRUEN.lighter(120).darker(d), GRUEN_DUNKEL.darker(d)))
    p.drawPath(schuh)
    p.setBrush(GOLD.darker(d))
    kreis(p, 22, 33, 2.6)
    p.restore()


def _wichtelarm(p, x, y, winkel, hinten):
    d = 125 if hinten else 100
    p.save()
    p.translate(x, y)
    p.rotate(winkel)
    p.setBrush(linear(-7, 0, 7, 0, WICHTEL_GRUEN.lighter(120).darker(d), GRUEN_DUNKEL.darker(d)))
    p.drawRoundedRect(QRectF(-7, -5, 14, 34), 7, 7)
    p.setBrush(ROT.darker(d))
    p.drawRoundedRect(QRectF(-7.5, 24, 15, 6), 3, 3)
    p.setBrush(radial(-2, 34, 9, HAUT.darker(d), HAUT_DUNKEL.darker(d)))
    kreis(p, 0, 35, 6.5)
    p.restore()


class Wichtel:
    """Kleiner Helfer mit Zipfelmütze und Glöckchen, Ringelstrümpfen und Schnabelschuhen."""
    KASTEN = QRectF(-75, -190, 150, 196)
    KOPF = (2, -184)

    @staticmethod
    def zeichne(p, d):
        pose, t, h = d.pose, d.t, d.pose.hub
        _wichtelarm(p, -8, -96 + h, pose.arm_h, True)
        _wichtelbein(p, -50 + h, pose.bein_h, True)
        _wichtelbein(p, -50 + h, pose.bein_v, False)
        # Kittel mit Zackensaum
        kittel = QPainterPath()
        kittel.moveTo(-18, -102 + h)
        kittel.lineTo(18, -102 + h)
        kittel.lineTo(27, -50 + h)
        for k in range(6):
            kittel.lineTo(27 - (k + 0.5) * 9, -42 + h)
            kittel.lineTo(27 - (k + 1) * 9, -50 + h)
        kittel.closeSubpath()
        p.setBrush(radial(-4, -86 + h, 60, WICHTEL_GRUEN.lighter(125), GRUEN_DUNKEL))
        p.drawPath(kittel)
        p.setBrush(QColor('#5A3A1E'))
        p.drawRect(QRectF(-23, -68 + h, 46, 7))
        p.setBrush(linear(0, -70 + h, 0, -58 + h, GOLD_HELL, GOLD))
        p.drawRoundedRect(QRectF(8, -70 + h, 11, 11), 2, 2)
        p.setBrush(QColor('#5A3A1E'))
        p.drawRect(QRectF(11, -67 + h, 5, 5))
        kragen = QPainterPath()
        kragen.moveTo(-18, -104 + h)
        for k in range(5):
            kragen.lineTo(-18 + (k + 0.5) * 7.6, -92 + h)
            kragen.lineTo(-18 + (k + 1) * 7.6, -104 + h)
        kragen.closeSubpath()
        p.setBrush(ROT)
        p.drawPath(kragen)
        Wichtel.kopf(p, pose, t, 4, -124 + h)
        _wichtelarm(p, 8, -96 + h, pose.arm_v, False)

    @staticmethod
    def kopf(p, pose, t, x, y):
        vorn = pose.kopf_vorn
        bx = 0 if vorn else 6
        # Haare und Ohren
        p.setBrush(QColor('#C2662D'))
        p.drawEllipse(QPointF(x - (0 if vorn else 8), y - 6), 22, 16)
        for seite in ((-1, 1) if vorn else (-1,)):
            ohr = QPainterPath()
            ox = x + seite * (20 if vorn else 12)
            ohr.moveTo(ox, y - 6)
            ohr.quadTo(ox + seite * 16, y - 18, ox + seite * 22, y - 26 + math.sin(t * 4) * 1.5)
            ohr.quadTo(ox + seite * 12, y + 2, ox, y + 6)
            ohr.closeSubpath()
            p.setBrush(linear(ox, y, ox + seite * 20, y - 20, HAUT, HAUT_DUNKEL))
            p.drawPath(ohr)
        p.setBrush(radial(x + bx - 4, y - 6, 30, HAUT, HAUT_DUNKEL))
        kreis(p, x, y, 21)
        wangen(p, (x + bx - 9, x + bx + 9) if vorn else (x + bx + 10,), y + 6, 6)
        p.setBrush(QColor(160, 80, 40, 120))
        for sx, sy in ((-11, 3), (-8, 6), (8, 5), (11, 2)):
            if vorn or sx > 0:
                kreis(p, x + bx + sx, y + sy, 0.9)
        augen(p, (x + bx - 6, x + bx + 6), y - 3, 3.2, 4, pose, (blick_x(pose), 0))
        brauen(p, (x + bx - 6, x + bx + 6), y - 11, 6, pose, QColor('#8A4520'))
        p.setBrush(radial(x + bx + (0 if vorn else 6), y + 2, 6, QColor('#F7A88C'), QColor('#D9735A')))
        kreis(p, x + bx + (0 if vorn else 6), y + 3, 3.6)
        mund(p, x + bx + (0 if vorn else 3), y + 12, 9, pose)
        # Zipfelmütze mit Glöckchen
        wipp = pose.wipp
        muetze = QPainterPath()
        muetze.moveTo(x - 23, y - 12)
        muetze.lineTo(x + 23, y - 12)
        muetze.cubicTo(x + 20, y - 44, x - 6, y - 52, x - 34 + wipp, y - 40)
        muetze.cubicTo(x - 46 + wipp, y - 34, x - 40 + wipp, y - 24, x - 50 + wipp, y - 18)
        muetze.cubicTo(x - 34, y - 24, x - 24, y - 26, x - 23, y - 12)
        p.setBrush(linear(x - 30, y - 50, x + 20, y - 12, ROT_HELL, ROT_DUNKEL))
        p.drawPath(muetze)
        p.setBrush(linear(0, y - 18, 0, y - 6, WICHTEL_GRUEN.lighter(130), GRUEN_DUNKEL))
        p.drawRoundedRect(QRectF(x - 25, y - 19, 50, 9), 4.5, 4.5)
        p.setBrush(radial(x - 51 + wipp, y - 18, 6, GOLD_HELL, GOLD.darker(115)))
        kreis(p, x - 51 + wipp, y - 16, 5)
        p.setBrush(QColor('#6B4A10'))
        kreis(p, x - 51 + wipp, y - 13, 1.3)


# ---------------------------------------------------------------- Pinguin

class Pinguin:
    """Rundlicher Pinguin mit Pudelmütze und Schal."""
    KASTEN = QRectF(-70, -150, 140, 156)
    KOPF = (2, -146)

    @staticmethod
    def zeichne(p, d):
        pose, t, h = d.pose, d.t, d.pose.hub
        dunkel = QColor('#24283A')

        def fuss(x, winkel, hinten):
            p.save()
            p.translate(x, -8 + h)
            p.rotate(winkel * 0.5)
            p.setBrush(KAROTTE.darker(130 if hinten else 105))
            p.drawEllipse(QRectF(-6, 2, 24, 9))
            p.restore()

        def fluegel(x, winkel, hinten):
            p.save()
            p.translate(x, -84 + h)
            p.rotate(winkel)
            p.setBrush(linear(-8, 0, 8, 0, QColor('#3A4060').darker(125 if hinten else 100), dunkel))
            p.drawEllipse(QRectF(-8, -4, 16, 46))
            p.restore()

        p.rotate(pose.bein_v * 0.3)      # watscheln
        fluegel(-14, pose.arm_h + 12, True)
        fuss(-10, pose.bein_h, True)
        fuss(6, pose.bein_v, False)
        p.setBrush(radial(-10, -90 + h, 90, QColor('#4A5275'), dunkel))
        p.drawEllipse(QRectF(-34, -124 + h, 68, 120))
        p.setBrush(radial(4, -60 + h, 50, WEISS, QColor('#D8DDE8')))
        p.drawEllipse(QRectF(-14, -92 + h, 44, 84))
        bx = 0 if pose.kopf_vorn else 8
        p.setBrush(radial(bx, -96 + h, 20, WEISS, QColor('#DDE2EC')))
        p.drawEllipse(QPointF(bx + 2, -98 + h), 19, 15)
        wangen(p, (bx - 10, bx + 14), -90 + h, 5)
        augen(p, (bx - 6, bx + 9), -100 + h, 4, 4.8, pose, (blick_x(pose), 0))
        if pose.sorge or pose.schreck:
            brauen(p, (bx - 6, bx + 9), -108 + h, 6, pose, dunkel)
        schnabel = QPainterPath()
        sx = bx + (2 if pose.kopf_vorn else 14)
        auf = 4 if (pose.mund_offen or pose.schreck > 0.2) else 0
        schnabel.moveTo(sx - 6, -94 + h)
        schnabel.quadTo(sx + 6, -96 + h, sx + 12, -91 + h - auf)
        schnabel.quadTo(sx + 4, -88 + h, sx - 6, -88 + h)
        schnabel.closeSubpath()
        p.setBrush(linear(0, -96 + h, 0, -88 + h, KAROTTE.lighter(130), KAROTTE.darker(120)))
        p.drawPath(schnabel)
        if auf:
            unten = QPainterPath()
            unten.moveTo(sx - 5, -88 + h)
            unten.quadTo(sx + 4, -86 + h, sx + 10, -84 + h)
            unten.quadTo(sx + 2, -82 + h, sx - 5, -86 + h)
            p.drawPath(unten)
        # Schal
        p.setBrush(linear(-30, -78, 30, -70, ROT_HELL, ROT_DUNKEL))
        p.drawRoundedRect(QRectF(-31, -80 + h, 62, 11), 5, 5)
        flatter = math.sin(t * 8) * 3
        ende = QPainterPath()
        ende.moveTo(-22, -74 + h)
        ende.quadTo(-34, -60 + h, -40 + flatter, -50 + h)
        ende.lineTo(-30 + flatter, -48 + h)
        ende.quadTo(-24, -60 + h, -14, -72 + h)
        ende.closeSubpath()
        p.drawPath(ende)
        p.setBrush(WEISS)
        for k in (-16, 0, 16):
            p.drawRect(QRectF(k - 1.5, -79 + h, 3, 9))
        # Pudelmütze
        p.save()
        p.translate(-2, -116 + h)
        p.rotate(-8 + pose.wipp)
        haube = QPainterPath()
        haube.moveTo(-24, 6)
        haube.cubicTo(-22, -26, 22, -26, 24, 6)
        haube.closeSubpath()
        p.setBrush(linear(-20, -20, 20, 6, ROT_HELL, ROT_DUNKEL))
        p.drawPath(haube)
        p.setBrush(WEISS)
        p.drawRoundedRect(QRectF(-26, 1, 52, 9), 4.5, 4.5)
        flausch(p, [(0 + a, -20 + b) for a, b in ((0, 0), (-4, -3), (4, -3), (-3, 4), (4, 3))], 5.5, False)
        p.restore()
        fluegel(0, pose.arm_v + 20, False)


# ---------------------------------------------------------------- Nussknacker

class Nussknacker:
    """Hölzerner Soldat mit hohem Tschako, Schnauzbart und Klappkiefer (d.kiefer 0..1)."""
    KASTEN = QRectF(-70, -322, 140, 328)
    KOPF = (2, -318)

    @staticmethod
    def zeichne(p, d):
        pose, t, h = d.pose, d.t, d.pose.hub

        def bein(winkel, hinten):
            k = 125 if hinten else 100
            p.save()
            p.translate(0, -84 + h)
            p.rotate(winkel * 1.2)
            p.setBrush(linear(-11, 0, 11, 0, BLAU.lighter(130).darker(k), BLAU.darker(140 + k - 100)))
            p.drawRect(QRectF(-11, 0, 22, 56))
            p.setBrush(linear(0, 54, 0, 84, QColor('#3A3A3A').darker(k), SCHWARZ.darker(k)))
            p.drawRoundedRect(QRectF(-12, 52, 24, 30), 3, 3)
            p.drawRoundedRect(QRectF(-12, 74, 32, 10), 4, 4)
            p.setBrush(QColor(255, 255, 255, 60))
            p.drawRect(QRectF(-8, 56, 3, 20))
            p.restore()

        def arm(x, winkel, hinten):
            k = 125 if hinten else 100
            p.save()
            p.translate(x, -160 + h)
            p.rotate(winkel)
            p.setBrush(linear(-10, 0, 10, 0, ROT_HELL.darker(k), ROT_DUNKEL.darker(k)))
            p.drawRoundedRect(QRectF(-10, -6, 20, 56), 6, 6)
            p.setBrush(GOLD.darker(k))
            p.drawRect(QRectF(-10, 40, 20, 5))
            p.setBrush(radial(-2, 54, 12, WEISS.darker(k), FELL_SCHATTEN.darker(k)))
            p.drawEllipse(QPointF(0, 56), 9, 10)
            p.restore()

        arm(-8, pose.arm_h * 1.1, True)
        bein(pose.bein_h, True)
        bein(pose.bein_v, False)
        p.setBrush(radial(-6, -140 + h, 70, ROT_HELL, ROT_DUNKEL))
        p.drawRoundedRect(QRectF(-26, -172 + h, 52, 92), 8, 8)
        p.setPen(stift(WEISS, 6))
        p.drawLine(QPointF(-20, -166 + h), QPointF(20, -96 + h))
        p.setPen(KEIN_STIFT)
        p.setBrush(SCHWARZ)
        p.drawRect(QRectF(-27, -100 + h, 54, 10))
        p.setBrush(GOLD)
        p.drawRoundedRect(QRectF(10, -102 + h, 12, 14), 2, 2)
        for k in range(4):
            p.setBrush(radial(20, -160 + k * 16 + h, 4, GOLD_HELL, GOLD))
            kreis(p, 21, -160 + k * 16 + h, 3)
        flausch(p, [(-14, -174 + h), (-20, -168 + h), (-24, -160 + h)], 6, False)
        # Kopf
        hy = -206 + h
        kiefer = max(getattr(d, 'kiefer', 0.0), pose.schreck, 0.5 if pose.mund_offen else 0.0)
        flausch(p, [(-24, hy - 14), (-28, hy), (-26, hy + 14), (-22, hy + 26)], 9)
        p.setBrush(radial(0, hy - 10, 50, HOLZ_HAUT, HAUT_DUNKEL))
        p.drawRoundedRect(QRectF(-24, hy - 30, 50, 46), 14, 14)
        p.setBrush(radial(14, hy + 2, 9, QColor(230, 70, 70, 220), QColor(230, 70, 70, 0)))
        kreis(p, 14, hy + 2, 9)
        bx = 0 if pose.kopf_vorn else 6
        augen(p, (bx + 2, bx + 16), hy - 12, 5, 6, pose, (blick_x(pose), 0))
        brauen(p, (bx + 2, bx + 16), hy - 22, 9, pose, SCHWARZ)
        # Klappkiefer, im Gelenk hinten drehbar
        p.save()
        p.translate(-16, hy + 8)
        p.rotate(kiefer * 40)
        p.setBrush(QColor('#5A1414'))
        p.drawRect(QRectF(4, -6, 34, 10))
        p.setBrush(radial(18, 6, 30, HOLZ_HAUT, HAUT_DUNKEL))
        p.drawRoundedRect(QRectF(0, 0, 42, 22), 8, 8)
        p.setBrush(WEISS)
        for k in range(5):
            p.drawRect(QRectF(16 + k * 5, -2, 4, 5))
        flausch(p, [(6 + k * 7, 22 + (k % 2) * 3) for k in range(6)], 6)
        p.restore()
        p.setBrush(WEISS)
        for k in range(5):
            p.drawRect(QRectF(bx + 2 + k * 5, hy + 8, 4, 5))
        flausch(p, [(bx + 4, hy + 6), (bx + 12, hy + 3), (bx + 20, hy + 3), (bx + 27, hy + 7)], 6.5)
        p.setBrush(radial(bx + 20, hy - 2, 7, HOLZ_HAUT, HAUT_DUNKEL.darker(110)))
        p.drawEllipse(QPointF(bx + 22, hy - 2), 6, 7)
        # Tschako
        p.setBrush(linear(-26, 0, 26, 0, QColor('#3A3A44'), SCHWARZ))
        p.drawRect(QRectF(-24, hy - 82, 50, 54))
        p.setBrush(linear(0, hy - 36, 0, hy - 26, GOLD_HELL, GOLD))
        p.drawRect(QRectF(-25, hy - 36, 52, 9))
        p.drawRect(QRectF(-25, hy - 82, 52, 6))
        p.setBrush(radial(10, hy - 58, 10, GOLD_HELL, GOLD))
        stern(p, 12, hy - 56, 10)
        p.setBrush(SCHWARZ)
        p.drawRoundedRect(QRectF(-4, hy - 30, 36, 6), 3, 3)
        feder = QPainterPath()
        feder.moveTo(-14, hy - 82)
        feder.cubicTo(-22, hy - 100, -10 + pose.wipp, hy - 110, -2 + pose.wipp, hy - 96)
        feder.cubicTo(-6, hy - 92, -8, hy - 86, -6, hy - 82)
        p.setBrush(linear(0, hy - 106, 0, hy - 82, ROT_HELL, ROT_DUNKEL))
        p.drawPath(feder)
        arm(10, pose.arm_v * 1.1, False)


# ---------------------------------------------------------------- Tannenbaum

class Tannenbaum:
    """Geschmückter Baum auf kleinen Stiefeln, Augen zwischen den Zweigen.
    d.kugeln: Liste [x, y, farbe] der Christbaumkugeln (in Einheiten)."""
    KASTEN = QRectF(-95, -262, 190, 268)
    KOPF = (0, -258)
    KUGELN = [[-40, -60, ROT], [32, -70, GOLD], [-8, -88, QColor('#2A6FD6')], [28, -142, ROT],
              [-26, -128, QColor('#B04AC8')], [6, -160, GOLD], [-14, -182, ROT]]

    @staticmethod
    def zeichne(p, d):
        pose, t, h = d.pose, d.t, d.pose.hub
        for winkel, hinten in ((pose.bein_h, True), (pose.bein_v, False)):
            k = 125 if hinten else 100
            p.save()
            p.translate(0 if hinten else 6, -28 + h)
            p.rotate(winkel)
            p.setBrush(QColor('#6B4423').darker(k))
            p.drawRoundedRect(QRectF(-5, 0, 10, 18), 4, 4)
            p.setBrush(SCHWARZ.lighter(140).darker(k))
            p.drawRoundedRect(QRectF(-7, 14, 22, 12), 5, 5)
            p.restore()
        p.setBrush(linear(-10, 0, 10, 0, QColor('#8A5A30'), QColor('#5A3A1E')))
        p.drawRect(QRectF(-10, -44 + h, 22, 20))
        stufen = ((-38, 150, 70), (-90, 118, 62), (-138, 84, 58), (-178, 50, 52))
        wackel = math.sin(t * 3) * 1.5
        for i, (unten, breite, hoehe) in enumerate(stufen):
            spitze_y = unten - hoehe - 20
            pfad = QPainterPath()
            x0 = -breite / 2
            pfad.moveTo(wackel * (i + 1) * 0.6, spitze_y + h)
            pfad.lineTo(x0, unten + h)
            n = 6
            for k in range(n):
                xa = x0 + breite * (k + 0.5) / n
                xb = x0 + breite * (k + 1) / n
                pfad.quadTo(xa, unten + 10 + h, xb, unten + h)
            pfad.closeSubpath()
            p.setBrush(linear(-breite / 2, spitze_y + h, breite / 2, unten + h,
                              GRUEN.lighter(135), GRUEN_DUNKEL.darker(110)))
            p.drawPath(pfad)
            p.setPen(stift(QColor(10, 60, 30, 120), 1.4))
            for k in range(3):
                xx = (k - 1) * breite * 0.25
                p.drawLine(QPointF(xx * 0.4, unten - hoehe * 0.6 + h), QPointF(xx, unten + 2 + h))
            p.setPen(KEIN_STIFT)
        # Girlande
        p.setPen(stift(GOLD_HELL, 2.4))
        p.setBrush(KEIN_PINSEL)
        for y0, b in ((-56, 120), (-104, 90), (-150, 62)):
            g = QPainterPath()
            g.moveTo(-b / 2, y0 - 10 + h)
            g.quadTo(0, y0 + 14 + h, b / 2, y0 - 16 + h)
            p.drawPath(g)
        p.setPen(KEIN_STIFT)
        for k in range(12):
            an = math.sin(t * 4 + k * 1.7) > 0
            lx = math.sin(k * 2.4) * (12 + k * 4)
            ly = -200 + k * 13
            c = QColor('#FFE680') if an else QColor('#A08A40')
            if an:
                p.setBrush(radial(lx, ly + h, 6, QColor(255, 240, 150, 160), QColor(255, 240, 150, 0)))
                kreis(p, lx, ly + h, 6)
            p.setBrush(c)
            kreis(p, lx, ly + h, 2)
        for x, y, farbe in getattr(d, 'kugeln', Tannenbaum.KUGELN):
            p.setPen(stift(GOLD.darker(130), 1))
            p.drawLine(QPointF(x, y - 9 + h), QPointF(x, y - 6 + h))
            p.setPen(KEIN_STIFT)
            p.setBrush(radial(x - 2.5, y - 3 + h, 9, farbe.lighter(160), farbe.darker(130)))
            kreis(p, x, y + h, 6.5)
            p.setBrush(QColor(255, 255, 255, 180))
            kreis(p, x - 2, y - 2.5 + h, 1.6)
        # Augen im Geäst
        bx = 0 if pose.kopf_vorn else 10
        p.setBrush(QColor(8, 50, 25, 200))
        p.drawEllipse(QPointF(bx, -110 + h), 22, 11)
        augen(p, (bx - 8, bx + 8), -110 + h, 5, 6, pose, (blick_x(pose), 0))
        brauen(p, (bx - 8, bx + 8), -121 + h, 7, pose, GRUEN_DUNKEL.darker(150))
        if pose.schreck > 0.2 or pose.mund_offen:
            mund(p, bx, -94 + h, 10, pose, QColor('#0C2A14'))
        # Spitze
        spitze = QPainterPath()
        spitze.moveTo(0, -260 + h)
        spitze.cubicTo(5, -246 + h, 5, -236 + h, 6, -224 + h)
        spitze.lineTo(-6, -224 + h)
        spitze.cubicTo(-5, -236 + h, -5, -246 + h, 0, -260 + h)
        p.setBrush(linear(-6, 0, 6, 0, GOLD_HELL, GOLD.darker(120)))
        p.drawPath(spitze)
        p.setBrush(radial(-2, -226 + h, 8, GOLD_HELL, GOLD))
        kreis(p, 0, -222 + h, 6)


# ---------------------------------------------------------------- Eisbär

class Eisbaer:
    """Eisbär auf allen vieren. d.liegt (0..1): eingerollt schlafend, d.blase: Größe der Schlafblase."""
    KASTEN = QRectF(-100, -138, 230, 144)
    KOPF = (70, -132)

    @staticmethod
    def zeichne(p, d):
        pose, t = d.pose, d.t
        liegt = getattr(d, 'liegt', 0.0)
        tief = 30 * liegt
        atmen = math.sin(t * 2.2) * 2 * liegt

        def bein(x, winkel, hinten):
            k = 118 if hinten else 100
            p.save()
            p.translate(x, -50 + tief)
            p.rotate(winkel * (1 - liegt) - 70 * liegt)
            p.setBrush(linear(-12, 0, 12, 0, EISBAER.darker(k), EISBAER_SCHATTEN.darker(k)))
            p.drawRoundedRect(QRectF(-12, -6, 24, 54 - 18 * liegt), 11, 11)
            p.setBrush(QColor('#3A3A3A').darker(k))
            for kk in (-6, 0, 6):
                kreis(p, kk + 3, 46 - 18 * liegt, 2)
            p.restore()

        bein(-44, pose.bein_h, True)
        bein(40, pose.bein_v, True)
        p.setBrush(radial(-10, -80 + tief, 110, EISBAER, EISBAER_SCHATTEN))
        p.drawEllipse(QRectF(-72, -102 + tief - atmen, 142, 72 + atmen))
        p.setBrush(EISBAER_SCHATTEN)
        kreis(p, -72, -78 + tief, 8)
        p.setPen(stift(EISBAER_SCHATTEN.darker(108), 1.6))
        for k in range(5):
            x = -50 + k * 20
            p.drawLine(QPointF(x, -98 + tief), QPointF(x + 3, -92 + tief))
        p.setPen(KEIN_STIFT)
        bein(-30, pose.bein_v, False)
        bein(52, pose.bein_h, False)
        # Kopf
        hx, hy = 72 + 6 * liegt, -86 + tief + 20 * liegt
        p.setBrush(radial(hx - 4, hy - 8, 34, EISBAER, EISBAER_SCHATTEN))
        kreis(p, hx, hy, 26)
        p.setBrush(EISBAER_SCHATTEN)
        kreis(p, hx - 10, hy - 22, 8)
        p.setBrush(QColor('#C8A6A0'))
        kreis(p, hx - 10, hy - 22, 4)
        p.setBrush(radial(hx + 20, hy + 2, 18, EISBAER, EISBAER_SCHATTEN))
        p.drawEllipse(QPointF(hx + 20, hy + 6), 16, 12)
        p.setBrush(radial(hx + 33, hy - 1, 6, QColor('#555555'), SCHWARZ))
        p.drawEllipse(QPointF(hx + 33, hy + 1), 6, 4.5)
        p.setBrush(QColor(255, 255, 255, 140))
        kreis(p, hx + 31, hy - 1, 1.3)
        wangen(p, (hx + 6,), hy + 6, 6)
        schlaeft = getattr(d, 'schlaeft', False)
        if schlaeft:
            p.setPen(stift(SCHWARZ, 1.8))
            p.setBrush(KEIN_PINSEL)
            p.drawArc(QRectF(hx + 4, hy - 12, 10, 7), 200 * 16, 140 * 16)
            p.setPen(KEIN_STIFT)
        else:
            augen(p, (hx + 9,), hy - 8, 4, 4.6, pose, (1, 0))
            brauen(p, (hx + 9,), hy - 16, 6, pose, EISBAER_SCHATTEN.darker(140))
        if pose.schreck > 0.2 or pose.mund_offen:
            mund(p, hx + 22, hy + 13, 10, pose, QColor('#5A1A1A'))
        blase = getattr(d, 'blase', 0.0)
        if blase > 0:
            bx, by = hx + 38 + blase * 0.7, hy + 2
            p.setBrush(radial(bx - blase * 0.3, by - blase * 0.3, blase * 1.2,
                              QColor(220, 240, 255, 60), QColor(160, 200, 240, 130)))
            p.setPen(stift(QColor(180, 215, 245, 200), 1.2))
            kreis(p, bx, by, blase)
            p.setPen(KEIN_STIFT)
            p.setBrush(QColor(255, 255, 255, 200))
            kreis(p, bx - blase * 0.35, by - blase * 0.4, blase * 0.18)


def zeichne_baerenkopf_vorn(p, x, y, pose, t):
    """Eisbärkopf von vorn, Mitte in (x, y)."""
    for seite in (-1, 1):
        p.setBrush(EISBAER_SCHATTEN)
        kreis(p, x + seite * 24, y - 24, 10)
        p.setBrush(QColor('#C8A6A0'))
        kreis(p, x + seite * 24, y - 24, 5)
    p.setBrush(radial(x - 8, y - 10, 46, EISBAER, EISBAER_SCHATTEN))
    p.drawEllipse(QPointF(x, y), 32, 29)
    wangen(p, (x - 18, x + 18), y + 8, 7)
    augen(p, (x - 11, x + 11), y - 6, 4.2, 5, pose, (pose.blick_x, pose.blick_y))
    brauen(p, (x - 11, x + 11), y - 15, 7, pose, EISBAER_SCHATTEN.darker(140))
    p.setBrush(radial(x, y + 10, 16, EISBAER, EISBAER_SCHATTEN.darker(105)))
    p.drawEllipse(QPointF(x, y + 12), 15, 11)
    p.setBrush(radial(x - 1, y + 5, 7, QColor('#555555'), SCHWARZ))
    p.drawEllipse(QPointF(x, y + 6), 6.5, 4.5)
    p.setBrush(QColor(255, 255, 255, 150))
    kreis(p, x - 2, y + 4.5, 1.4)
    if pose.schreck > 0.2 or pose.mund_offen:
        mund(p, x, y + 15, 10, pose, QColor('#5A1A1A'))
    else:
        p.setPen(stift(SCHWARZ, 1.4))
        p.setBrush(KEIN_PINSEL)
        p.drawArc(QRectF(x - 6, y + 10, 6, 6), 200 * 16, 140 * 16)
        p.drawArc(QRectF(x, y + 10, 6, 6), 200 * 16, 140 * 16)
        p.setPen(KEIN_STIFT)


# ---------------------------------------------------------------- Rentier

class Rentier:
    """Das Rentier aus requisiten.py im Galopp, Hufe im Ursprung."""
    KASTEN = QRectF(-66, -176, 180, 182)
    KOPF = (66, -168)

    @staticmethod
    def zeichne(p, d):
        p.translate(0, -60)
        zeichne_rentier(p, d.phase, d.t, False)
