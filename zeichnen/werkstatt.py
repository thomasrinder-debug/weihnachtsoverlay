"""Wichtelwerkstatt: Fließband, Kiste, Blechmaus, Holzeisenbahn, Hammer, Säge, Sägebock,
Papierrolle, Rohrpost, Schraubstock und Spielzeugwanne. Alle Maße in Einheiten, Blick nach rechts."""
import math

from PyQt6.QtCore import QPointF, QRectF
from PyQt6.QtGui import QColor, QPainterPath

from .grundlagen import (GOLD, GOLD_HELL, GRUEN_DUNKEL, KEIN_PINSEL, KEIN_STIFT, ROT, ROT_DUNKEL, ROT_HELL,
                         SCHWARZ, WEISS, flausch, kreis, linear, radial, stift)
from .figuren import WICHTEL_GRUEN

HOLZ = QColor('#C98F55')
HOLZ_HELL = QColor('#E3B47E')
HOLZ_DUNKEL = QColor('#7C4F27')
METALL = QColor('#A7AFBA')
METALL_HELL = QColor('#E4E9EF')
METALL_DUNKEL = QColor('#4F5763')
GUMMI = QColor('#33363C')
BLAU = QColor('#2F6FC0')
PAKET_FARBEN = (QColor('#D3172E'), QColor('#2F6FC0'), QColor('#22834C'), QColor('#E3A928'), QColor('#9A4FC0'))


def maserung(p, rechteck, n=3, dunkel=HOLZ_DUNKEL):
    """Feine Holzmaserung als leicht gewellte Linien."""
    x, y, b, h = rechteck.x(), rechteck.y(), rechteck.width(), rechteck.height()
    c = QColor(dunkel)
    c.setAlpha(80)
    p.setPen(stift(c, 1.1))
    p.setBrush(KEIN_PINSEL)
    for k in range(n):
        yy = y + h * (k + 0.6) / (n + 0.2)
        pfad = QPainterPath()
        pfad.moveTo(x + 3, yy)
        pfad.cubicTo(x + b * 0.3, yy - 2, x + b * 0.6, yy + 2.5, x + b - 3, yy - 0.5)
        p.drawPath(pfad)
    p.setPen(KEIN_STIFT)


def holzbalken(p, rechteck, hell=HOLZ_HELL, dunkel=HOLZ_DUNKEL, rund=2.5):
    p.setBrush(linear(0, rechteck.top(), 0, rechteck.bottom(), hell, dunkel))
    p.drawRoundedRect(rechteck, rund, rund)
    maserung(p, rechteck, max(1, int(rechteck.height() // 7)), dunkel)


# ---------------------------------------------------------------- Fließband

def zeichne_foerderband(p, laenge, lauf, rueckeln=0.0):
    """Fließband vom Ursprung (linkes Ende, Boden) nach rechts, Lauffläche bei y=-40.
    lauf: wie weit das Band gelaufen ist (Einheiten), bewegt Rillen und Rollen."""
    p.setBrush(QColor(0, 0, 0, 45))
    p.drawEllipse(QRectF(-6, -4, laenge + 12, 8))
    for x in (18, laenge - 18):
        p.setBrush(linear(x - 5, 0, x + 5, 0, METALL, METALL_DUNKEL))
        p.drawRect(QRectF(x - 4, -32, 8, 32))
        p.setBrush(METALL_DUNKEL)
        p.drawRoundedRect(QRectF(x - 9, -4, 18, 4), 2, 2)
    p.setBrush(linear(0, -34, 0, -22, METALL, METALL_DUNKEL))
    p.drawRect(QRectF(10, -34, laenge - 20, 10))
    # Band mit Rillen
    p.setBrush(GUMMI)
    p.drawRoundedRect(QRectF(-2, -46 + rueckeln, laenge + 4, 16), 8, 8)
    p.save()
    p.setClipRect(QRectF(4, -46 + rueckeln, laenge - 8, 6))
    p.setBrush(QColor('#555A62'))
    versatz = lauf % 16
    x = -16 + versatz
    while x < laenge:
        p.drawRect(QRectF(x, -46 + rueckeln, 6, 6))
        x += 16
    p.restore()
    for x in (6, laenge - 6):
        p.setBrush(radial(x - 2, -40 + rueckeln, 8, METALL_HELL, METALL_DUNKEL))
        kreis(p, x, -38 + rueckeln, 6.5)
        p.save()
        p.translate(x, -38 + rueckeln)
        p.rotate(lauf / 6.5 * 180 / math.pi)
        p.setBrush(METALL_DUNKEL)
        p.drawRect(QRectF(-5, -0.8, 10, 1.6))
        p.restore()
    # Schaltkasten mit Lämpchen
    p.setBrush(linear(0, -30, 0, -8, QColor('#E6C33A'), QColor('#A88412')))
    p.drawRoundedRect(QRectF(laenge * 0.45 - 12, -30, 24, 22), 3, 3)
    p.setBrush(SCHWARZ)
    for k in range(4):
        p.drawRect(QRectF(laenge * 0.45 - 12 + k * 7, -9, 4, 1.6))


def zeichne_kiste(p, b, h, deckel=0.0, raeder=False, drall=0.0):
    """Holzkiste, Boden mittig im Ursprung. deckel: Öffnungswinkel des Deckels (Grad,
    Scharnier links oben). raeder: Spielzeugwanne auf Rädern, drall dreht die Räder."""
    p.setBrush(QColor(0, 0, 0, 50))
    p.drawEllipse(QRectF(-b * 0.55, -3, b * 1.1, 6))
    unten = -12 if raeder else 0
    p.setBrush(HOLZ_DUNKEL.darker(130))
    p.drawRect(QRectF(-b / 2 + 4, -h + unten, b - 8, 6))
    n = 3
    for k in range(n):
        y0 = -h + unten + k * h / n
        holzbalken(p, QRectF(-b / 2, y0 + 1, b, h / n - 2), rund=2)
    for x in (-b / 2 + 2, b / 2 - 10):
        p.setBrush(linear(x, 0, x + 8, 0, HOLZ, HOLZ_DUNKEL))
        p.drawRect(QRectF(x, -h + unten, 8, h))
    p.setBrush(METALL_DUNKEL)
    for x in (-b / 2 + 6, b / 2 - 6):
        for y in (-h + unten + 6, unten - 6):
            kreis(p, x, y, 1.6)
    if raeder:
        for x in (-b / 2 + 14, b / 2 - 14):
            p.setBrush(radial(x - 2, -10, 10, QColor('#6A6F78'), GUMMI))
            kreis(p, x, -9, 9)
            p.setBrush(ROT)
            kreis(p, x, -9, 4)
            p.setBrush(WEISS)
            kreis(p, x + 3 * math.cos(drall), -9 + 3 * math.sin(drall), 1.3)
    if deckel is not None:
        p.save()
        p.translate(-b / 2, -h + unten)
        p.rotate(-deckel)
        holzbalken(p, QRectF(-2, -8, b + 4, 8), HOLZ_HELL, HOLZ)
        p.restore()


def kistenrand(b, h, raeder=False):
    """Oberkante der Kiste über dem Boden."""
    return h + (12 if raeder else 0)


# ---------------------------------------------------------------- Blechmaus

def zeichne_aufziehmaus(p, schluessel=0.0, tippeln=0.0, zittern=0.0):
    """Blechmaus zum Aufziehen, Boden mittig im Ursprung, Nase rechts. schluessel: Drehwinkel
    des Schlüssels (Bogenmaß), tippeln: Phase der Rädchen, zittern: 0..1 vibriert vor Spannung."""
    p.save()
    if zittern:
        p.translate(math.sin(tippeln * 40) * 1.2 * zittern, -abs(math.sin(tippeln * 53)) * 1.5 * zittern)
    p.setBrush(QColor(0, 0, 0, 50))
    p.drawEllipse(QRectF(-28, -3, 58, 6))
    # Schwanz aus Draht
    schwanz = QPainterPath()
    schwanz.moveTo(-24, -12)
    schwanz.cubicTo(-40, -6, -46, -26, -36, -30)
    schwanz.cubicTo(-28, -33, -30, -22, -38, -20)
    p.setPen(stift(METALL_DUNKEL, 2.2))
    p.setBrush(KEIN_PINSEL)
    p.drawPath(schwanz)
    p.setPen(KEIN_STIFT)
    for x in (-12, 14):
        p.setBrush(GUMMI)
        kreis(p, x, -4, 4.5)
        p.setBrush(METALL)
        kreis(p, x + 1.8 * math.cos(tippeln * 3), -4 + 1.8 * math.sin(tippeln * 3), 1.2)
    koerper = QPainterPath()
    koerper.moveTo(-26, -6)
    koerper.cubicTo(-28, -30, -4, -38, 12, -30)
    koerper.cubicTo(24, -24, 34, -14, 38, -8)
    koerper.quadTo(38, -5, 34, -5)
    koerper.lineTo(-24, -5)
    koerper.closeSubpath()
    p.setBrush(linear(-10, -36, 4, -4, QColor('#C7CDD6'), QColor('#6C7480')))
    p.drawPath(koerper)
    p.setBrush(QColor(255, 255, 255, 120))
    p.drawEllipse(QRectF(-14, -32, 20, 6))
    p.setPen(stift(METALL_DUNKEL, 1.2))
    p.setBrush(KEIN_PINSEL)
    p.drawLine(QPointF(-25, -9), QPointF(34, -9))
    p.setPen(KEIN_STIFT)
    p.setBrush(METALL_DUNKEL)
    for x in (-18, -6, 6, 18):
        kreis(p, x, -11.5, 1.1)
    # Ohr, Auge, Nase, Schnurrhaare
    p.setBrush(radial(10, -34, 9, QColor('#F2B8C0'), QColor('#8E939C')))
    p.drawEllipse(QPointF(10, -34), 7, 8)
    p.setBrush(SCHWARZ)
    kreis(p, 24, -20, 2.4)
    p.setBrush(WEISS)
    kreis(p, 24.8, -20.8, 0.8)
    p.setBrush(QColor('#E86A7E'))
    kreis(p, 38, -7.5, 2.6)
    p.setPen(stift(QColor(40, 40, 40, 150), 0.8))
    for dy in (-3, 0, 3):
        p.drawLine(QPointF(36, -8), QPointF(46, -8 + dy * 1.4))
    p.setPen(KEIN_STIFT)
    # Schlüssel: Schaft und Griff, der sich dreht
    p.setBrush(linear(-4, 0, 4, 0, GOLD_HELL, GOLD.darker(120)))
    p.drawRect(QRectF(-8, -44, 4, 12))
    breite = abs(math.cos(schluessel))
    for seite in (-1, 1):
        p.drawEllipse(QPointF(-6 + seite * 8 * breite, -50), 1.5 + 6 * breite, 7)
    p.setBrush(GOLD.darker(130))
    kreis(p, -6, -50, 2.2)
    p.restore()


# ---------------------------------------------------------------- Holzeisenbahn

def zeichne_gleis(p, x0, x1):
    """Holzschiene zwischen x0 und x1 (Einheiten) auf dem Boden."""
    p.setBrush(linear(0, -7, 0, 0, HOLZ_HELL, HOLZ_DUNKEL))
    p.drawRoundedRect(QRectF(x0, -7, x1 - x0, 7), 2, 2)
    p.setBrush(QColor(0, 0, 0, 55))
    p.drawRect(QRectF(x0, -5, x1 - x0, 1.6))
    x = x0 + 40
    p.setBrush(HOLZ_DUNKEL)
    while x < x1:
        kreis(p, x, -2, 1.5)
        x += 60


def _raeder(p, xs, drall, r=7):
    for x in xs:
        p.setBrush(radial(x - 2, -r - 2, r + 2, QColor('#FFD861'), QColor('#B57E14')))
        kreis(p, x, -r - 1, r)
        p.setBrush(HOLZ_DUNKEL)
        kreis(p, x, -r - 1, 2)
        p.setPen(stift(HOLZ_DUNKEL, 1.4))
        p.drawLine(QPointF(x, -r - 1), QPointF(x + (r - 2) * math.cos(drall), -r - 1 + (r - 2) * math.sin(drall)))
        p.setPen(KEIN_STIFT)


def zeichne_lok(p, drall=0.0):
    """Holzlok, Boden mittig, fährt nach rechts. Höhe etwa 30."""
    p.setBrush(linear(0, -18, 0, -6, ROT_HELL, ROT_DUNKEL))
    p.drawRoundedRect(QRectF(-24, -18, 40, 11), 3, 3)
    p.setBrush(linear(0, -32, 0, -16, BLAU.lighter(130), BLAU.darker(130)))
    p.drawRoundedRect(QRectF(-24, -32, 16, 16), 2, 2)
    p.setBrush(QColor('#BFE3FF'))
    p.drawRect(QRectF(-20, -29, 8, 6))
    p.setBrush(linear(0, -28, 0, -14, QColor('#3A9A5A'), GRUEN_DUNKEL))
    p.drawRoundedRect(QRectF(-8, -26, 24, 10), 5, 5)
    p.setBrush(SCHWARZ)
    p.drawRect(QRectF(6, -34, 6, 9))
    p.drawRect(QRectF(4.5, -36, 9, 3))
    p.setBrush(GOLD)
    kreis(p, 16, -21, 2.5)
    p.setBrush(SCHWARZ)
    p.drawRect(QRectF(16, -9, 6, 3))
    _raeder(p, (-15, 0, 10), drall, 6)


def zeichne_wagen(p, drall=0.0, hoch=False, farbe=None):
    """Holzwagen, Boden mittig. hoch: hoher Güterwagen mit Dach (Höhe 62), sonst flacher Wagen."""
    farbe = farbe or (QColor('#E3A928') if hoch else QColor('#22834C'))
    p.setBrush(SCHWARZ)
    p.drawRect(QRectF(-30, -9, 4, 3))
    if hoch:
        p.setBrush(linear(-24, 0, 24, 0, farbe.lighter(120), farbe.darker(130)))
        p.drawRoundedRect(QRectF(-26, -58, 52, 49), 3, 3)
        maserung(p, QRectF(-24, -56, 48, 45), 5, farbe.darker(200))
        p.setBrush(farbe.darker(150))
        p.drawRect(QRectF(-8, -50, 16, 34))
        p.setBrush(linear(0, -64, 0, -56, ROT_HELL, ROT_DUNKEL))
        p.drawRoundedRect(QRectF(-30, -64, 60, 8), 4, 4)
        _raeder(p, (-16, 16), drall, 7)
    else:
        p.setBrush(linear(0, -22, 0, -9, farbe.lighter(130), farbe.darker(130)))
        p.drawRoundedRect(QRectF(-24, -20, 48, 11), 2, 2)
        p.setBrush(HOLZ)
        for k in range(3):
            kreis(p, -12 + k * 12, -24, 5)
        _raeder(p, (-13, 13), drall, 6)


# ---------------------------------------------------------------- Werkzeug

def zeichne_hammer(p, stiel=34, kopf=1.0):
    """Hammer in der Hand: Griff im Ursprung, Stiel entlang +y, Kopf quer am Ende.
    kopf: Größe des Kopfes (Riesenhammer > 1)."""
    p.setBrush(linear(-3, 0, 3, 0, HOLZ_HELL, HOLZ_DUNKEL))
    b = 2.5 + 1.5 * kopf
    p.drawRoundedRect(QRectF(-b, -6, 2 * b, stiel + 8), b, b)
    p.setBrush(QColor('#8E2B2B'))
    p.drawRoundedRect(QRectF(-b - 0.6, -7, 2 * b + 1.2, 10), 2, 2)
    kb, kh = 12 * kopf, 7 * kopf
    p.setBrush(linear(0, stiel - kh, 0, stiel + kh, METALL_HELL, METALL_DUNKEL))
    p.drawRoundedRect(QRectF(-kb, stiel - kh, 2 * kb, 2 * kh), 2 * kopf, 2 * kopf)
    p.setBrush(METALL_DUNKEL)
    p.drawRect(QRectF(kb - 2.5 * kopf, stiel - kh, 2.5 * kopf, 2 * kh))
    p.setBrush(QColor(255, 255, 255, 110))
    p.drawRect(QRectF(-kb + 2 * kopf, stiel - kh + 1.5 * kopf, 2 * kb - 6 * kopf, 1.5 * kopf))


def zeichne_nagel(p, laenge=26, knick=0.0):
    """Nagel mit Spitze im Ursprung, Kopf oben. knick: 0..1 seitlich verbogen."""
    pfad = QPainterPath()
    pfad.moveTo(0, 0)
    if knick:
        pfad.quadTo(0, -laenge * 0.5, laenge * 0.45 * knick, -laenge * (1 - 0.35 * knick))
    else:
        pfad.lineTo(0, -laenge)
    p.setBrush(KEIN_PINSEL)
    p.setPen(stift(METALL_DUNKEL, 3))
    p.drawPath(pfad)
    p.setPen(stift(METALL_HELL, 1.1))
    p.drawPath(pfad)
    p.setPen(KEIN_STIFT)
    kx = laenge * 0.45 * knick if knick else 0
    ky = -laenge * (1 - 0.35 * knick) if knick else -laenge
    p.setBrush(linear(0, ky - 2, 0, ky + 2, METALL_HELL, METALL_DUNKEL))
    p.drawRoundedRect(QRectF(kx - 5, ky - 2.5, 10, 3), 1.2, 1.2)


def zeichne_werkblock(p, b, h):
    """Holzklotz, Boden mittig im Ursprung."""
    p.setBrush(QColor(0, 0, 0, 50))
    p.drawEllipse(QRectF(-b * 0.55, -3, b * 1.1, 6))
    holzbalken(p, QRectF(-b / 2, -h, b, h))
    p.setBrush(QColor(255, 255, 255, 60))
    p.drawRect(QRectF(-b / 2 + 2, -h + 1, b - 4, 2))
    # Jahresringe an der Stirnseite
    p.setPen(stift(QColor(124, 79, 39, 110), 1))
    p.setBrush(KEIN_PINSEL)
    for r in (4, 8, 12):
        p.drawEllipse(QPointF(-b / 2 + 14, -h / 2), r * 0.7, min(r, h / 2 - 2))
    p.setPen(KEIN_STIFT)


def zeichne_saege(p):
    """Fuchsschwanz: Griff im Ursprung, Blatt nach +x."""
    blatt = QPainterPath()
    blatt.moveTo(6, -8)
    blatt.lineTo(70, -3)
    blatt.lineTo(70, 4)
    blatt.lineTo(6, 8)
    blatt.closeSubpath()
    p.setBrush(linear(0, -8, 0, 8, METALL_HELL, METALL))
    p.drawPath(blatt)
    p.setBrush(METALL_DUNKEL)
    zahn = QPainterPath()
    x = 8
    zahn.moveTo(x, 8)
    while x < 68:
        zahn.lineTo(x + 2, 10.5 - (x - 8) * 0.035)
        zahn.lineTo(x + 4, 8 - (x - 8) * 0.065)
        x += 4
    zahn.lineTo(70, 4)
    zahn.lineTo(6, 8)
    p.drawPath(zahn)
    griff = QPainterPath()
    griff.addRoundedRect(QRectF(-10, -10, 18, 20), 6, 6)
    loch = QPainterPath()
    loch.addRoundedRect(QRectF(-5, -5, 8, 10), 3, 3)
    p.setBrush(linear(-10, 0, 8, 0, QColor('#C0392B'), QColor('#7D1F16')))
    p.drawPath(griff.subtracted(loch))
    p.setBrush(GOLD)
    kreis(p, 5, -6, 1.4)
    kreis(p, 5, 6, 1.4)


def zeichne_saegebock(p, kipp=(0.0, 0.0), schnitt=0.0, hoehe=62, breite=112):
    """Sägebock von der Seite, Boden mittig im Ursprung, Balken oben bei y=-hoehe.
    Jede Hälfte hat ein schräges Bein; kipp = (links, rechts) dreht die Hälften in Grad
    um ihre Füße nach außen, sobald der Balken in der Mitte durchgesägt ist.
    schnitt: 0..1 wie tief die Säge schon im Balken steckt."""
    p.setBrush(QColor(0, 0, 0, 45))
    p.drawEllipse(QRectF(-breite * 0.5, -3, breite, 6))
    for seite, winkel in ((-1, kipp[0]), (1, kipp[1])):
        fx = seite * breite * 0.4
        p.save()
        p.translate(fx, 0)
        p.rotate(seite * winkel)
        bein = QPainterPath()
        bein.moveTo(-4.5, 0)
        bein.lineTo(4.5, 0)
        bein.lineTo(-seite * 12 + 4, -hoehe + 6)
        bein.lineTo(-seite * 12 - 4, -hoehe + 6)
        bein.closeSubpath()
        p.setBrush(linear(-6, 0, 6, 0, HOLZ, HOLZ_DUNKEL))
        p.drawPath(bein)
        p.setBrush(HOLZ_DUNKEL)
        p.drawRoundedRect(QRectF(-6, -2, 12, 3), 1.5, 1.5)
        # halber Balken bis zur Mitte
        x0 = -fx if seite > 0 else -fx - breite / 2
        holzbalken(p, QRectF(x0 + (1 if seite > 0 else 0), -hoehe, breite / 2 - 1, 11))
        p.setBrush(HOLZ_DUNKEL)
        p.drawRect(QRectF(-fx + (0 if seite > 0 else -26), -hoehe * 0.45, 26, 4))
        p.restore()
    if 0 < schnitt < 1:
        p.setBrush(QColor('#3B2412'))
        p.drawRect(QRectF(-1, -hoehe, 2, 11 * schnitt))


def zeichne_brett(p, laenge, dicke=9):
    """Brett, linke obere Ecke im Ursprung."""
    holzbalken(p, QRectF(0, 0, laenge, dicke), QColor('#EDC58F'), HOLZ, rund=1.5)
    p.setBrush(QColor(124, 79, 39, 120))
    p.drawEllipse(QRectF(laenge * 0.62, 2.5, 6, 3.5))


# ---------------------------------------------------------------- Geschenkpapier

def papiermuster_pinsel(p, x0, y0, x1, y1):
    return linear(x0, y0, x1, y1, ROT_HELL, ROT_DUNKEL)


def zeichne_papierstaender(p, r, feder=0.0):
    """Ständer mit federnder Geschenkpapierrolle, Boden mittig. Rollenmitte bei (0, -70).
    r: Halbmesser der Rolle, feder: Drehung der sichtbaren Spiralfeder (Bogenmaß)."""
    p.setBrush(QColor(0, 0, 0, 50))
    p.drawEllipse(QRectF(-30, -3, 60, 6))
    p.setBrush(linear(-4, 0, 4, 0, METALL, METALL_DUNKEL))
    p.drawRect(QRectF(-3, -70, 6, 70))
    p.drawRoundedRect(QRectF(-26, -6, 52, 6), 3, 3)
    zeichne_papierrolle(p, 0, -70, r, feder)
    p.setBrush(GOLD.darker(120))
    kreis(p, 0, -70, 3)


def zeichne_papierrolle(p, x, y, r, dreh=0.0):
    """Rolle Geschenkpapier von der Seite, mit Sternchen und Spiralfeder in der Mitte."""
    p.setBrush(radial(x - r * 0.3, y - r * 0.3, r * 1.3, ROT_HELL, ROT_DUNKEL))
    kreis(p, x, y, r)
    p.setBrush(GOLD_HELL)
    for k in range(5):
        w = dreh + k * 2 * math.pi / 5
        rr = r * (0.55 + 0.3 * (k % 2))
        kreis(p, x + rr * math.cos(w), y + rr * math.sin(w), max(1.2, r * 0.07))
    # Spiralfeder
    pfad = QPainterPath()
    n = 26
    for i in range(n + 1):
        w = dreh * 2 + i * 0.55
        rr = 2 + (r * 0.42) * i / n
        pt = QPointF(x + rr * math.cos(w), y + rr * math.sin(w))
        if i == 0:
            pfad.moveTo(pt)
        else:
            pfad.lineTo(pt)
    p.setBrush(KEIN_PINSEL)
    p.setPen(stift(METALL_HELL, 1.4))
    p.drawPath(pfad)
    p.setPen(KEIN_STIFT)


def zeichne_papierbahn(p, x0, y0, x1, y1, breite=7, wellen=0.0, t=0.0):
    """Papierbahn als Band von (x0, y0) nach (x1, y1) mit Sternchen."""
    dx, dy = x1 - x0, y1 - y0
    lg = math.hypot(dx, dy) or 1.0
    nx, ny = -dy / lg, dx / lg
    oben, unten = QPainterPath(), []
    n = max(2, int(lg / 8))
    punkte = []
    for i in range(n + 1):
        f = i / n
        w = math.sin(f * math.pi) * wellen * math.sin(t * 20 + f * 9)
        punkte.append((x0 + dx * f + nx * w, y0 + dy * f + ny * w))
    oben.moveTo(punkte[0][0] + nx * breite / 2, punkte[0][1] + ny * breite / 2)
    for x, y in punkte[1:]:
        oben.lineTo(x + nx * breite / 2, y + ny * breite / 2)
    for x, y in reversed(punkte):
        oben.lineTo(x - nx * breite / 2, y - ny * breite / 2)
    oben.closeSubpath()
    p.setBrush(linear(x0 + nx * breite, y0 + ny * breite, x0 - nx * breite, y0 - ny * breite,
                      ROT_HELL, ROT_DUNKEL))
    p.drawPath(oben)
    p.setBrush(GOLD_HELL)
    for i in range(1, n, 2):
        x, y = punkte[i]
        kreis(p, x, y, 1.3)


def zeichne_walze(p, x, y, r, dreh, strampeln):
    """Dicke Papierwalze mit eingerolltem Wichtel: zwei Schnabelschuhe ragen heraus,
    oben die steife Mützenspitze, abgeknickt."""
    for seite, phase in ((-1, 0.0), (1, 1.7)):
        w = dreh + (math.pi * 0.62 if seite < 0 else math.pi * 0.42)
        bx, by = x + r * math.cos(w), y + r * math.sin(w)
        p.save()
        p.translate(bx, by)
        p.rotate(math.degrees(w) - 90 + 18 * math.sin(strampeln * 14 + phase))
        p.setBrush(WEISS)
        p.drawRoundedRect(QRectF(-4.5, -2, 9, 12), 4, 4)
        p.setBrush(ROT)
        p.drawRect(QRectF(-4.5, 3, 9, 3))
        schuh = QPainterPath()
        schuh.moveTo(-6, 10)
        schuh.cubicTo(-6, 18, 4, 20, 12, 18)
        schuh.cubicTo(18, 17, 20, 11, 17, 9)
        schuh.cubicTo(15, 8, 13, 10, 14, 12)
        schuh.cubicTo(10, 13, 5, 12, 4, 9)
        schuh.closeSubpath()
        p.setBrush(linear(0, 9, 0, 19, WICHTEL_GRUEN.lighter(120), GRUEN_DUNKEL))
        p.drawPath(schuh)
        p.setBrush(GOLD)
        kreis(p, 17, 8.5, 2)
        p.restore()
    zeichne_papierrolle(p, x, y, r, dreh)
    w = dreh - math.pi / 2
    mx, my = x + r * math.cos(w), y + r * math.sin(w)
    p.save()
    p.translate(mx, my)
    p.rotate(math.degrees(w) + 90)
    spitze = QPainterPath()
    spitze.moveTo(-8, 2)
    spitze.lineTo(8, 2)
    spitze.lineTo(5, -14)
    spitze.lineTo(-5, -14)
    spitze.closeSubpath()
    p.setBrush(linear(-8, -14, 8, 2, ROT_HELL, ROT_DUNKEL))
    p.drawPath(spitze)
    p.translate(0, -13)
    p.rotate(-90)
    oben = QPainterPath()
    oben.moveTo(-5, 1)
    oben.lineTo(5, 1)
    oben.lineTo(1, -20)
    oben.lineTo(-1, -20)
    oben.closeSubpath()
    p.drawPath(oben)
    p.setBrush(radial(0, -22, 5, GOLD_HELL, GOLD.darker(115)))
    kreis(p, 0, -22, 3.5)
    p.restore()


# ---------------------------------------------------------------- Rohrpost

def zeichne_rohrpost(p, oben, mund, beule=0.0, beule_y=0.0, wackeln=0.0):
    """Senkrechtes Rohr von y=oben (negativ, Bildoberkante) bis zum Krümmer, der nach rechts
    in einen Trichter bei (46, -mund) mündet. Ursprung: Rohrmitte auf Bodenhöhe.
    beule: 0..1 Ausbeulung bei y=beule_y."""
    d = 15
    p.save()
    p.translate(math.sin(wackeln * 47) * 1.5 * (wackeln > 0), 0)
    # Halterungen an der Wand
    rohr = QPainterPath()
    rohr.addRect(QRectF(-d, oben, 2 * d, -mund - oben - d))
    if beule:
        rohr.addEllipse(QPointF(0, beule_y), d + 12 * beule, 30 + 10 * beule)
    bogen = QPainterPath()
    bogen.moveTo(-d, -mund - d - 1)
    bogen.quadTo(-d, -mund + d, d, -mund + d)
    bogen.lineTo(32, -mund + d)
    bogen.lineTo(32, -mund - d)
    bogen.lineTo(d, -mund - d)
    bogen.lineTo(d, -mund - d - 1)
    bogen.closeSubpath()
    rohr = rohr.united(bogen)
    p.setBrush(linear(-d - 12, 0, d + 12, 0, QColor('#E8C58A'), QColor('#8A5A1E')))
    p.drawPath(rohr)
    p.setBrush(QColor(255, 255, 255, 90))
    p.drawRect(QRectF(-d + 4, oben, 4, -mund - oben - d))
    # Ringe
    p.setBrush(linear(-d - 3, 0, d + 3, 0, QColor('#C9A066'), QColor('#6E4514')))
    y = -mund - d - 40
    while y > oben:
        p.drawRoundedRect(QRectF(-d - 3, y, 2 * d + 6, 6), 2, 2)
        y -= 90
    # Trichter
    trichter = QPainterPath()
    trichter.moveTo(30, -mund - d)
    trichter.lineTo(48, -mund - d - 9)
    trichter.lineTo(48, -mund + d + 9)
    trichter.lineTo(30, -mund + d)
    trichter.closeSubpath()
    p.setBrush(linear(30, -mund - 20, 30, -mund + 20, QColor('#F2D49C'), QColor('#8A5A1E')))
    p.drawPath(trichter)
    p.setBrush(QColor('#3A2410'))
    p.drawEllipse(QRectF(44, -mund - d - 8, 7, 2 * d + 16))
    # Druckanzeige
    p.setBrush(METALL_HELL)
    kreis(p, -d - 2, -mund - 70, 9)
    p.setPen(stift(ROT_DUNKEL, 1.6))
    w = -2.4 + min(1.0, wackeln) * 2.0 + math.sin(wackeln * 30) * 0.2 * (wackeln > 0)
    p.drawLine(QPointF(-d - 2, -mund - 70), QPointF(-d - 2 + 7 * math.cos(w), -mund - 70 + 7 * math.sin(w)))
    p.setPen(KEIN_STIFT)
    p.restore()


def zeichne_kapsel(p, laenge=34, farbe=None, dreh=0.0):
    """Rohrpostkapsel, Mitte im Ursprung, liegt waagerecht."""
    farbe = farbe or QColor('#2F6FC0')
    p.save()
    p.rotate(dreh)
    r = laenge * 0.24
    p.setBrush(linear(0, -r, 0, r, farbe.lighter(150), farbe.darker(140)))
    p.drawRoundedRect(QRectF(-laenge / 2, -r, laenge, 2 * r), r, r)
    p.setBrush(linear(0, -r, 0, r, GOLD_HELL, GOLD.darker(130)))
    for x in (-laenge / 2, laenge / 2 - laenge * 0.18):
        p.drawRoundedRect(QRectF(x, -r - 1, laenge * 0.18, 2 * r + 2), 2, 2)
    p.setBrush(QColor(255, 255, 255, 110))
    p.drawRect(QRectF(-laenge * 0.3, -r * 0.6, laenge * 0.6, r * 0.3))
    p.restore()


def zeichne_korb(p, b, h, vorn=True):
    """Drahtkorb, Boden mittig. vorn=False zeichnet nur die Rückwand."""
    c = QColor('#6E747E')
    if not vorn:
        p.setBrush(QColor(60, 64, 72, 120))
        p.drawRect(QRectF(-b / 2 + 4, -h, b - 8, h))
        return
    p.setBrush(KEIN_PINSEL)
    p.setPen(stift(c, 2.2))
    p.drawLine(QPointF(-b / 2, -h), QPointF(-b / 2 + 6, 0))
    p.drawLine(QPointF(b / 2, -h), QPointF(b / 2 - 6, 0))
    p.drawLine(QPointF(-b / 2 + 6, 0), QPointF(b / 2 - 6, 0))
    for k in range(1, 6):
        x = -b / 2 + b * k / 6
        p.drawLine(QPointF(x, -h), QPointF(x * 0.88, 0))
    for k in range(1, 3):
        y = -h * k / 3
        f = 1 - (h + y) / h * 0.12
        p.drawLine(QPointF(-b / 2 * f, y), QPointF(b / 2 * f, y))
    p.setPen(stift(METALL_HELL, 3.5))
    p.drawLine(QPointF(-b / 2 - 2, -h), QPointF(b / 2 + 2, -h))
    p.setPen(KEIN_STIFT)


# ---------------------------------------------------------------- Werkbank und Schraubstock

def zeichne_werkbank(p, b, h):
    """Werkbank, Boden mittig, Platte bei y=-h."""
    p.setBrush(QColor(0, 0, 0, 50))
    p.drawEllipse(QRectF(-b * 0.55, -3, b * 1.1, 6))
    for x in (-b / 2 + 6, b / 2 - 16):
        p.setBrush(linear(x, 0, x + 10, 0, HOLZ, HOLZ_DUNKEL))
        p.drawRect(QRectF(x, -h + 6, 10, h - 6))
    holzbalken(p, QRectF(-b / 2 + 8, -h * 0.35, b - 16, 7), HOLZ, HOLZ_DUNKEL)
    holzbalken(p, QRectF(-b / 2, -h - 4, b, 12))
    # Werkzeug auf dem Unterboden
    p.setBrush(linear(0, -h * 0.35 - 10, 0, -h * 0.35, QColor('#3A7BD5'), QColor('#1D4E8F')))
    p.drawRoundedRect(QRectF(-b * 0.3, -h * 0.35 - 10, 26, 10), 2, 2)


def zeichne_schraubstock(p, spalt, kurbel=0.0, wackeln=0.0):
    """Schraubstock auf der Werkbank: feste Backe links im Ursprung (Grundplatte), die bewegliche
    Backe steht spalt Einheiten rechts davon. Backenmitte bei y=-26. kurbel dreht den Knebel."""
    p.save()
    p.translate(math.sin(wackeln * 50) * wackeln * 1.5, 0)
    p.setBrush(linear(0, -6, 0, 0, METALL, METALL_DUNKEL))
    p.drawRoundedRect(QRectF(-24, -6, 40 + spalt, 6), 2, 2)
    p.setBrush(linear(0, -14, 0, -6, QColor('#3E7EC9'), QColor('#1E4C85')))
    p.drawRect(QRectF(-18, -14, 34 + spalt, 8))
    # Spindel
    p.setBrush(linear(0, -24, 0, -18, METALL_HELL, METALL_DUNKEL))
    p.drawRect(QRectF(0, -24, spalt + 34, 6))
    for k in range(int((spalt + 34) // 4)):
        p.setBrush(QColor(0, 0, 0, 50))
        p.drawRect(QRectF(k * 4 + 1, -24, 1.2, 6))
    for x0, b in ((-20, 20), (spalt, 20)):
        p.setBrush(linear(x0, 0, x0 + b, 0, QColor('#4D8FDB'), QColor('#1E4C85')))
        p.drawRoundedRect(QRectF(x0, -42, b, 30), 3, 3)
        p.setBrush(linear(0, -44, 0, -36, METALL_HELL, METALL_DUNKEL))
        p.drawRect(QRectF(x0 + (b - 6 if x0 < 0 else 0), -44, 6, 12))
    # Knebel am Spindelende
    kx = spalt + 34
    p.setBrush(METALL_DUNKEL)
    kreis(p, kx, -21, 4)
    p.save()
    p.translate(kx, -21)
    lg = 22 * math.cos(kurbel)
    p.setBrush(linear(0, -2, 0, 2, METALL_HELL, METALL_DUNKEL))
    p.drawRoundedRect(QRectF(-2, -abs(lg), 4, 2 * abs(lg)), 2, 2)
    for y in (-abs(lg), abs(lg)):
        kreis(p, 0, y, 3.5)
    p.restore()
    p.restore()


def zeichne_spielzeugpferd(p):
    """Kleines Holzpferd (Kopf und Hals) zum Einspannen, Fuß im Ursprung."""
    pfad = QPainterPath()
    pfad.moveTo(-5, 0)
    pfad.lineTo(-6, -22)
    pfad.cubicTo(-8, -32, 0, -38, 10, -34)
    pfad.lineTo(18, -26)
    pfad.quadTo(20, -21, 15, -21)
    pfad.lineTo(6, -24)
    pfad.lineTo(5, 0)
    pfad.closeSubpath()
    p.setBrush(linear(-6, -36, 16, 0, HOLZ_HELL, HOLZ_DUNKEL))
    p.drawPath(pfad)
    p.setBrush(ROT)
    for k in range(4):
        p.drawEllipse(QPointF(-7 - k * 0.3, -30 + k * 5), 3.2, 2.6)
    p.setBrush(SCHWARZ)
    kreis(p, 8, -30, 1.5)


def zeichne_bartstrang(p, ax, ay, bx, by, dicke):
    """Lang gezogener Bart zwischen Kinn (a) und Schraubstock (b), Weltkoordinaten."""
    lg = math.hypot(bx - ax, by - ay)
    n = max(3, int(lg / (dicke * 0.7)))
    pts = []
    for i in range(n + 1):
        f = i / n
        r = dicke * (1.0 - 0.45 * f)
        pts.append((ax + (bx - ax) * f, ay + (by - ay) * f + math.sin(f * math.pi) * dicke * 0.4, r))
    p.setPen(KEIN_STIFT)
    from .grundlagen import FELL_SCHATTEN
    p.setBrush(FELL_SCHATTEN)
    for x, y, r in pts:
        kreis(p, x + 0.6, y + 1.2, r)
    p.setBrush(WEISS)
    for x, y, r in pts:
        kreis(p, x, y, r)


def zeichne_paeckchen(p, b, h, farbe, band=GOLD):
    """Kleines Päckchen mit Kreuzband und kleiner Schleife, Boden mittig im Ursprung."""
    p.setBrush(QColor(0, 0, 0, 45))
    p.drawEllipse(QRectF(-b * 0.55, -2.5, b * 1.1, 5))
    p.setBrush(linear(-b / 2, -h, b / 2, 0, farbe.lighter(130), farbe.darker(140)))
    p.drawRoundedRect(QRectF(-b / 2, -h, b, h), 2, 2)
    p.setBrush(QColor(0, 0, 0, 40))
    p.drawRect(QRectF(-b / 2, -h, b, 3))
    p.setBrush(linear(0, -h, 0, 0, band.lighter(130), band.darker(110)))
    p.drawRect(QRectF(-b * 0.07, -h, b * 0.14, h))
    p.drawRect(QRectF(-b / 2, -h * 0.55, b, h * 0.14))
    for seite in (-1, 1):
        schl = QPainterPath()
        schl.moveTo(0, -h)
        schl.cubicTo(seite * 4, -h - 10, seite * 12, -h - 9, seite * 9, -h - 3)
        schl.cubicTo(seite * 7, -h, seite * 3, -h, 0, -h)
        p.setBrush(linear(0, -h - 10, 0, -h, band.lighter(140), band.darker(115)))
        p.drawPath(schl)
    p.setBrush(band.lighter(120))
    kreis(p, 0, -h - 1, 2.4)
