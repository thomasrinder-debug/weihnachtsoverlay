"""Requisiten für die Hörsaal-Szenen (szenen/hs_*.py): Laserpointer, Minibeamer mit
Schattenspiel, Folienwisch, Mikrofon, Klausurstempel, Glocken, Wanduhr, Klappsitz.
Alle Zeichnungen in Einheiten (Figur 250 hoch), Boden bzw. Aufhängung im Ursprung."""
import math

from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import QColor, QPainterPath, QTransform

from .figur import zeichne_bein, zeichne_sack
from .grundlagen import (GOLD, GOLD_HELL, KEIN_PINSEL, KEIN_STIFT, ROT, ROT_DUNKEL, SCHWARZ, WEISS, flausch, kreis,
                         linear, radial, stift)

P = QPointF
LASER = QColor('#FF2A2A')
HOLZ_HELL, HOLZ_DUNKEL = QColor('#C98B4E'), QColor('#7A4A22')
METALL_HELL, METALL_DUNKEL = QColor('#D9DDE3'), QColor('#6C7078')
STEMPEL_ROT = QColor(214, 24, 40, 235)


def figur_trafo(sz):
    """Dieselbe Abbildung wie figur(): Einheiten der Weihnachtsmann-Zeichnung -> Bildschirm."""
    tr = QTransform()
    tr.translate(sz.x, sz.y - sz.hopp)
    tr.rotate(sz.neigung * sz.richtung)
    tr.scale(sz.s * sz.richtung * (2 - sz.stauchen), sz.s * sz.stauchen)
    return tr


# ---------------------------------------------------------------- Laserpointer

def zeichne_laserpointer(p, an=True):
    """Stift von hinten (Ursprung) nach vorn (+x), 34 lang."""
    p.setPen(KEIN_STIFT)
    p.setBrush(linear(0, -4, 0, 4, QColor('#5C6170'), QColor('#1E2028')))
    p.drawRoundedRect(QRectF(-4, -4, 38, 8), 4, 4)
    p.setBrush(METALL_HELL)
    p.drawRect(QRectF(28, -4.2, 5, 8.4))
    p.setBrush(LASER if an else QColor('#7A2020'))
    kreis(p, 12, -4, 2.2)


def zeichne_laserpunkt(p, x, y, r, t):
    """Roter Punkt mit flirrendem Leuchten; r in Pixeln."""
    p.setPen(KEIN_STIFT)
    g = r * (2.6 + 0.4 * math.sin(t * 31))
    p.setBrush(radial(x, y, g, QColor(255, 60, 60, 150), QColor(255, 40, 40, 0)))
    kreis(p, x, y, g)
    p.setBrush(radial(x - r * 0.2, y - r * 0.2, r, QColor('#FFE0E0'), LASER))
    kreis(p, x, y, r)


def zeichne_laserstrahl(p, x0, y0, x1, y1, breite):
    p.setPen(stift(QColor(255, 50, 50, 70), breite * 2.5))
    p.drawLine(P(x0, y0), P(x1, y1))
    p.setPen(stift(QColor(255, 90, 90, 150), breite))
    p.drawLine(P(x0, y0), P(x1, y1))
    p.setPen(KEIN_STIFT)


# ---------------------------------------------------------------- Beamer und Schattenspiel

def zeichne_beamer(p, an):
    """Kleiner Projektor, Boden im Ursprung, Objektiv nach +x bei (30, -22)."""
    p.setPen(KEIN_STIFT)
    p.setBrush(QColor('#2A2C33'))
    for fx in (-26, 22):
        p.drawRoundedRect(QRectF(fx - 4, -6, 10, 6), 2, 2)
    p.setBrush(linear(0, -40, 0, -6, QColor('#F1F2F5'), QColor('#A7ABB4')))
    p.drawRoundedRect(QRectF(-34, -40, 64, 34), 8, 8)
    p.setBrush(QColor('#8F939C'))
    for k in range(4):
        p.drawRoundedRect(QRectF(-28 + k * 7, -34, 3.5, 20), 1.5, 1.5)
    p.setBrush(QColor('#3A3D46'))
    p.drawEllipse(P(30, -23), 9, 13)
    p.setBrush(radial(31, -24, 9, QColor('#FFF6C8') if an else QColor('#6A7488'), QColor('#2B3040')))
    p.drawEllipse(P(31, -23), 6.5, 10)
    p.setBrush(QColor(255, 255, 255, 170))
    kreis(p, 29, -27, 2)
    p.setBrush(QColor('#5BE06A') if an else QColor('#7A1F1F'))
    kreis(p, 0, -44, 2.6)


def zeichne_lichtkegel(p, quelle, oben, unten, staerke):
    """Lichtkegel vom Objektiv (Punkt) zu einer senkrechten Bildkante (oben, unten: Punkte)."""
    if staerke <= 0:
        return
    a = int(110 * staerke)
    pfad = QPainterPath()
    pfad.moveTo(quelle)
    pfad.lineTo(oben)
    pfad.lineTo(unten)
    pfad.closeSubpath()
    p.setPen(KEIN_STIFT)
    mitte = P((oben.x() + unten.x()) / 2, (oben.y() + unten.y()) / 2)
    p.setBrush(linear(quelle.x(), quelle.y(), mitte.x(), mitte.y(), QColor(255, 248, 210, a),
                      QColor(255, 248, 210, a // 3)))
    p.drawPath(pfad)


def zeichne_projektion(p, rechteck, staerke):
    """Helle Projektionsfläche am Rand."""
    if staerke <= 0:
        return
    p.setPen(KEIN_STIFT)
    c = rechteck.center()
    r = max(rechteck.width(), rechteck.height()) * 0.7
    p.setBrush(radial(c.x(), c.y(), r, QColor(255, 250, 225, int(200 * staerke)), QColor(255, 244, 200, int(90 * staerke))))
    p.drawRoundedRect(rechteck, 10, 10)


def zeichne_schatten(p, ohren=0.0, geweih=0.0, krallen=0.0, t=0.0):
    """Riesenschatten des Wichtels, Fuß im Ursprung, etwa 190 hoch (dann vergrößert)."""
    p.setPen(KEIN_STIFT)
    p.setBrush(QColor(28, 24, 48, 215))
    k = QPainterPath()
    # Körper, Kopf, Zipfelmütze
    k.addEllipse(QRectF(-26, -110, 52, 70))
    k.addRoundedRect(QRectF(-20, -50, 14, 50), 7, 7)
    k.addRoundedRect(QRectF(6, -50, 14, 50), 7, 7)
    k.addEllipse(QRectF(-24, -150, 48, 46))
    m = QPainterPath()
    m.moveTo(-22, -138)
    m.cubicTo(-14, -190, 26, -200, 38, -178)
    m.lineTo(18, -140)
    m.closeSubpath()
    k.addPath(m)
    # Arme: zwischen hängend und hoch über dem Kopf mit Krallen
    hoch = max(ohren, geweih, krallen)
    for seite in (-1, 1):
        w = math.radians(seite * (20 + 140 * hoch * (0.8 if krallen else 1.0)))
        sx, sy = seite * 22, -100
        ex, ey = sx + math.sin(w) * 60, sy + math.cos(w) * 60
        arm = QPainterPath()
        arm.moveTo(sx, sy)
        arm.lineTo(ex, ey)
        p.setPen(stift(QColor(28, 24, 48, 215), 14))
        p.drawPath(arm)
        p.setPen(KEIN_STIFT)
        if ohren > 0.05:
            for d in (-1, 1):
                k.addEllipse(QRectF(ex + d * 6 - 6, ey - 46 * ohren, 12, 46 * ohren))
        if geweih > 0.05:
            g = QPainterPath()
            g.moveTo(ex, ey)
            g.lineTo(ex + seite * 12 * geweih, ey - 50 * geweih)
            g.moveTo(ex + seite * 5 * geweih, ey - 22 * geweih)
            g.lineTo(ex + seite * 30 * geweih, ey - 34 * geweih)
            g.moveTo(ex + seite * 9 * geweih, ey - 38 * geweih)
            g.lineTo(ex - seite * 12 * geweih, ey - 60 * geweih)
            p.setPen(stift(QColor(28, 24, 48, 215), 7))
            p.setBrush(KEIN_PINSEL)
            p.drawPath(g)
            p.setPen(KEIN_STIFT)
        if krallen > 0.05:
            for f in range(4):
                fw = w + math.radians((f - 1.5) * 22)
                p.setPen(stift(QColor(28, 24, 48, 215), 5))
                p.drawLine(P(ex, ey), P(ex + math.sin(fw) * 26 * krallen, ey + math.cos(fw) * 26 * krallen - 6))
            p.setPen(KEIN_STIFT)
    p.setBrush(QColor(28, 24, 48, 215))
    k.setFillRule(Qt.FillRule.WindingFill)
    p.drawPath(k.simplified())
    if krallen > 0.05:
        # Augen und Zackenmaul leuchten aus dem Schatten
        p.setBrush(QColor(255, 250, 225, int(230 * krallen)))
        for ax in (-10, 10):
            e = QPainterPath()
            e.moveTo(ax - 7, -134)
            e.lineTo(ax + 7, -130 + (2 if ax < 0 else -2))
            e.lineTo(ax, -124)
            e.closeSubpath()
            p.drawPath(e)
        z = QPainterPath()
        z.moveTo(-14, -116)
        for i in range(7):
            z.lineTo(-14 + (i + 0.5) * 4, -108 + (4 if i % 2 else 0))
            z.lineTo(-14 + (i + 1) * 4, -116)
        z.lineTo(14, -112)
        z.lineTo(-14, -112)
        z.closeSubpath()
        p.drawPath(z)


def zeichne_sack_mit_beinen(p, strampeln, t, bauch=1.0):
    """Sack am Boden (Ursprung), aus dessen Öffnung zwei Stiefel strampeln."""
    for k, seite in enumerate((-1, 1)):
        p.save()
        p.translate(seite * 10, -96 * bauch)
        p.rotate(180 + seite * (12 + strampeln * 24 * math.sin(t * 19 + k * 2.1)))
        zeichne_bein(p, 0, 0, k == 0)
        p.restore()
    p.save()
    p.translate(0, -50 * bauch)
    p.scale(1.45 * bauch, 1.25 * bauch)
    p.translate(0, -0)
    zeichne_sack(p, 0, 0, math.sin(t * 13) * 6 * strampeln)
    p.restore()


# ---------------------------------------------------------------- Folienwisch

def zeichne_wisch(p, x, oben, unten, s, richtung, t):
    """Kante eines Folienübergangs: heller Balken mit Lichtschweif, bewegt sich nach richtung."""
    p.setPen(KEIN_STIFT)
    b = 26 * s
    schweif = 220 * s
    p.setBrush(linear(x, 0, x - richtung * schweif, 0, QColor(220, 240, 255, 150), QColor(220, 240, 255, 0)))
    p.drawRect(QRectF(min(x, x - richtung * schweif), oben, schweif, unten - oben))
    p.setBrush(linear(x - b, 0, x + b, 0, QColor(255, 255, 255, 0), QColor(255, 255, 255, 0)))
    g = linear(x - b, 0, x + b, 0, QColor(170, 215, 255, 0), QColor(170, 215, 255, 0))
    g.gradient().setColorAt(0.5, QColor(255, 255, 255, 245))
    p.setBrush(g)
    p.drawRect(QRectF(x - b, oben, 2 * b, unten - oben))
    p.setPen(stift(QColor(255, 255, 255, 170), 3 * s))
    for k in range(7):
        y = oben + (unten - oben) * ((k * 0.37 + t * 0.9) % 1.0)
        laenge = (60 + 50 * ((k * 0.61) % 1.0)) * s
        p.drawLine(P(x - richtung * 30 * s, y), P(x - richtung * (30 * s + laenge), y))
    p.setPen(KEIN_STIFT)
    p.setBrush(QColor(255, 255, 255, 230))
    for k in range(5):
        y = oben + (unten - oben) * ((k * 0.23 + t * 1.7) % 1.0)
        kreis(p, x + math.sin(t * 9 + k) * 10 * s, y, (3 + 2 * math.sin(t * 20 + k)) * s)


# ---------------------------------------------------------------- Mikrofon

def zeichne_mikrofon(p, hoehe=150, zittern=0.0):
    """Mikrofonständer, Fuß im Ursprung, Mikrofonkopf bei (18, -hoehe - 8), zeigt nach +x."""
    p.setPen(KEIN_STIFT)
    p.setBrush(linear(-30, -6, 30, 0, QColor('#4A4E58'), QColor('#1C1E24')))
    p.drawEllipse(QRectF(-30, -8, 60, 12))
    p.setBrush(linear(-3, 0, 3, 0, METALL_HELL, METALL_DUNKEL))
    p.drawRect(QRectF(-3, -hoehe * 0.55, 6, hoehe * 0.55))
    p.drawRect(QRectF(-2, -hoehe, 4, hoehe * 0.47))
    p.setBrush(QColor('#2A2C33'))
    p.drawRoundedRect(QRectF(-5, -hoehe * 0.56, 10, 6), 2, 2)
    p.save()
    p.translate(0, -hoehe)
    p.rotate(-28 + zittern)
    p.setBrush(QColor('#2A2C33'))
    p.drawRoundedRect(QRectF(-2, -3, 18, 6), 3, 3)
    p.setBrush(radial(20, -3, 12, QColor('#B9BDC6'), QColor('#4A4E58')))
    kreis(p, 22, 0, 9)
    p.setPen(stift(QColor(40, 40, 46, 140), 0.8))
    for d in (-5, 0, 5):
        p.drawLine(P(22 + d, -8), P(22 + d, 8))
        p.drawLine(P(14, d), P(30, d))
    p.restore()
    p.setPen(KEIN_STIFT)


def mikro_kopf(hoehe=150):
    w = math.radians(-28)
    return 22 * math.cos(w), -hoehe + 22 * math.sin(w)


def zeichne_schallringe(p, x, y, richtung, staerke, phase, s, offen=70):
    """Schallbögen nach richtung; staerke 0..1 bestimmt Reichweite und Zahl."""
    if staerke <= 0:
        return
    p.setBrush(KEIN_PINSEL)
    n = 2 + int(staerke * 4)
    weite = (40 + 260 * staerke) * s
    for k in range(n):
        f = (k / n + phase) % 1.0
        r = 10 * s + weite * f
        a = int(230 * (1 - f) * min(1.0, staerke * 2))
        p.setPen(stift(QColor(255, 255, 255, a), (2 + 5 * staerke) * s * (1 - 0.5 * f)))
        start = (0 if richtung > 0 else 180) - offen / 2
        p.drawArc(QRectF(x - r, y - r, 2 * r, 2 * r), int(-(start + offen) * 16) + 0, int(offen * 16))
    p.setPen(KEIN_STIFT)


def zeichne_kreischen(p, x, y, richtung, staerke, t, s):
    """Zackenlinie des Rückkopplungspfeifens."""
    if staerke <= 0:
        return
    for k, farbe in enumerate((QColor(255, 230, 90, 230), QColor(255, 120, 60, 200))):
        pfad = QPainterPath()
        pfad.moveTo(x, y)
        laenge = (80 + 200 * staerke) * s
        n = 9
        for i in range(1, n + 1):
            dx = richtung * laenge * i / n
            dy = (1 if (i + k) % 2 else -1) * (8 + 16 * staerke) * s * (0.6 + 0.4 * math.sin(t * 40 + i))
            pfad.lineTo(x + dx, y + dy - k * 14 * s * staerke)
        p.setPen(stift(farbe, (2.5 + 2 * staerke) * s))
        p.setBrush(KEIN_PINSEL)
        p.drawPath(pfad)
    p.setPen(KEIN_STIFT)


# ---------------------------------------------------------------- Klausur und Stempel

def zeichne_stempel(p, farbe_frisch=1.0):
    """Riesenstempel, Gummifläche unten im Ursprung (50 breit), Griff nach oben."""
    p.setPen(KEIN_STIFT)
    p.setBrush(QColor(170, 20, 30))
    p.drawRoundedRect(QRectF(-27, -8, 54, 8), 2, 2)
    p.setBrush(linear(-28, 0, 28, 0, HOLZ_HELL, HOLZ_DUNKEL))
    p.drawRoundedRect(QRectF(-30, -30, 60, 23), 4, 4)
    p.setBrush(QColor(255, 255, 255, 60))
    p.drawRect(QRectF(-28, -28, 56, 4))
    p.setBrush(linear(-7, 0, 7, 0, HOLZ_HELL.lighter(110), HOLZ_DUNKEL))
    p.drawRoundedRect(QRectF(-7, -66, 14, 40), 5, 5)
    p.setBrush(radial(-5, -76, 18, QColor('#E7B07A'), HOLZ_DUNKEL))
    p.drawEllipse(P(0, -74), 15, 12)


def zeichne_haken(p, x, y, g, farbe=STEMPEL_ROT, breite=None):
    """Stempelabdruck: Kreis mit Haken, g = Radius."""
    p.setBrush(KEIN_PINSEL)
    p.setPen(stift(farbe, breite or g * 0.16))
    kreis(p, x, y, g)
    h = QPainterPath()
    h.moveTo(x - g * 0.5, y)
    h.lineTo(x - g * 0.12, y + g * 0.42)
    h.lineTo(x + g * 0.55, y - g * 0.45)
    p.setPen(stift(farbe, (breite or g * 0.16) * 1.5))
    p.drawPath(h)
    p.setPen(KEIN_STIFT)


def zeichne_blatt(p, haken=False):
    """Klausurblatt (50 x 64) mit Zeilen ohne lesbaren Text, Mitte im Ursprung."""
    p.setPen(KEIN_STIFT)
    p.setBrush(QColor(0, 0, 0, 40))
    p.drawRect(QRectF(-23, -30, 50, 64))
    p.setBrush(QColor('#FBFBF6'))
    p.drawRect(QRectF(-25, -32, 50, 64))
    p.setPen(stift(QColor(70, 80, 110, 150), 2))
    for k in range(7):
        y = -22 + k * 7.5
        p.drawLine(P(-18, y), P(18 - (k * 13) % 17, y))
    p.setPen(KEIN_STIFT)
    if haken:
        zeichne_haken(p, 6, 6, 15)


# ---------------------------------------------------------------- Glocken

def zeichne_handglocke(p, schwung=0.0):
    """Handglocke, Griff im Ursprung, Glocke hängt nach unten; schwung in Grad."""
    p.save()
    p.rotate(schwung)
    p.setPen(KEIN_STIFT)
    p.setBrush(linear(-4, 0, 4, 0, HOLZ_HELL, HOLZ_DUNKEL))
    p.drawRoundedRect(QRectF(-4, -6, 8, 22), 4, 4)
    glocke = QPainterPath()
    glocke.moveTo(-6, 14)
    glocke.cubicTo(-14, 16, -12, 30, -20, 40)
    glocke.lineTo(20, 40)
    glocke.cubicTo(12, 30, 14, 16, 6, 14)
    glocke.closeSubpath()
    p.setBrush(linear(-20, 0, 20, 0, GOLD_HELL, GOLD.darker(130)))
    p.drawPath(glocke)
    p.setBrush(GOLD.darker(150))
    kreis(p, math.sin(math.radians(-schwung * 1.6)) * 10, 42, 4)
    p.restore()


def zeichne_riesenglocke(p, schwung=0.0, glanz=0.0):
    """Große Schulglocke am Bügel, Bügelspitze im Ursprung, etwa 110 hoch."""
    p.save()
    p.rotate(schwung)
    p.setPen(stift(METALL_DUNKEL, 6))
    p.setBrush(KEIN_PINSEL)
    p.drawArc(QRectF(-18, -8, 36, 30), 0, 180 * 16)
    p.setPen(KEIN_STIFT)
    glocke = QPainterPath()
    glocke.moveTo(-14, 8)
    glocke.cubicTo(-40, 10, -34, 62, -56, 96)
    glocke.lineTo(56, 96)
    glocke.cubicTo(34, 62, 40, 10, 14, 8)
    glocke.closeSubpath()
    p.setBrush(linear(-56, 0, 56, 0, GOLD_HELL, GOLD.darker(140)))
    p.drawPath(glocke)
    p.setBrush(GOLD.darker(115))
    p.drawRoundedRect(QRectF(-58, 90, 116, 10), 5, 5)
    p.setBrush(QColor(255, 255, 255, 90 + int(120 * glanz)))
    p.drawEllipse(QRectF(-30, 24, 10, 46))
    p.setBrush(GOLD.darker(160))
    kreis(p, math.sin(math.radians(-schwung * 1.4)) * 30, 104, 9)
    p.restore()


# ---------------------------------------------------------------- Wanduhr

def zeichne_wanduhr(p, r, minute, stunde, sekunde, zittern=0.0):
    """Runde Wanduhr, Mitte im Ursprung; Zeigerwinkel in Grad (0 = zwölf, im Uhrzeigersinn)."""
    p.save()
    p.rotate(zittern)
    p.setPen(KEIN_STIFT)
    p.setBrush(QColor(0, 0, 0, 50))
    kreis(p, 4, 5, r + 4)
    p.setBrush(linear(-r, -r, r, r, QColor('#E9C46A'), QColor('#8A5A1A')))
    kreis(p, 0, 0, r + 4)
    p.setBrush(radial(-r * 0.3, -r * 0.3, r * 1.3, QColor('#FFFFFA'), QColor('#E3E0D6')))
    kreis(p, 0, 0, r - 4)
    for k in range(12):
        w = math.radians(k * 30)
        lang = 10 if k % 3 == 0 else 5
        p.setPen(stift(SCHWARZ, 3.5 if k % 3 == 0 else 2))
        p.drawLine(P(math.sin(w) * (r - 8), -math.cos(w) * (r - 8)),
                   P(math.sin(w) * (r - 8 - lang), -math.cos(w) * (r - 8 - lang)))

    def zeiger(winkel, laenge, breite, farbe):
        p.save()
        p.rotate(winkel)
        p.setPen(KEIN_STIFT)
        p.setBrush(farbe)
        z = QPainterPath()
        z.moveTo(-breite / 2, 8)
        z.lineTo(-breite * 0.3, -laenge)
        z.lineTo(0, -laenge - breite)
        z.lineTo(breite * 0.3, -laenge)
        z.lineTo(breite / 2, 8)
        z.closeSubpath()
        p.drawPath(z)
        p.restore()

    zeiger(stunde, r * 0.48, 8, SCHWARZ)
    zeiger(minute, r * 0.74, 6, SCHWARZ)
    zeiger(sekunde, r * 0.8, 2, ROT)
    p.setPen(KEIN_STIFT)
    p.setBrush(ROT_DUNKEL)
    kreis(p, 0, 0, 4)
    p.setBrush(QColor(255, 255, 255, 60))
    p.drawEllipse(QRectF(-r * 0.6, -r * 0.75, r * 0.7, r * 0.35))
    p.restore()


def zeichne_bart_lang(p, laenge, wehen=0.0, t=0.0):
    """Verlängerung des Barts in Weihnachtsmann-Einheiten (Seitenansicht): fällt vom Kinn
    (etwa (16, -130)) wallend bis zum Boden und häuft sich davor. laenge 0..1."""
    if laenge <= 0:
        return
    unten = -130 + 128 * min(1.0, laenge / 0.6)
    haufen = max(0.0, (laenge - 0.6) / 0.4)

    def rand(y, seite):
        f = (y + 140) / 140
        mitte = 18 + wehen * f + 6 * math.sin(y * 0.05 + t * 2)
        return mitte + seite * (20 + 16 * f)

    pfad = QPainterPath()
    ys = list(range(-140, int(unten) + 1, 6)) + [unten]
    pfad.moveTo(rand(-140, -1), -140)
    for y in ys:
        pfad.lineTo(rand(y, -1), y)
    for y in reversed(ys):
        pfad.lineTo(rand(y, 1), y)
    pfad.closeSubpath()
    p.setPen(KEIN_STIFT)
    p.setBrush(linear(0, -140, 0, unten, WEISS, QColor('#E6E9F0')))
    p.drawPath(pfad)
    locken = [(rand(y, -1), y) for y in range(-132, int(unten), 11)]
    locken += [(rand(y, 1), y) for y in range(-128, int(unten), 11)]
    flausch(p, locken, 7.5)
    if haufen > 0:
        n = int(4 + 10 * haufen)
        flausch(p, [(rand(unten, -1) + k * (12 + 4 * haufen), -7 - 5 * abs(math.sin(k * 1.3))) for k in range(n)],
                8 + 5 * haufen)
    p.setPen(stift(QColor(200, 205, 218, 170), 1.6))
    p.setBrush(KEIN_PINSEL)
    for k, y in enumerate(range(-120, int(unten) - 8, 14)):
        x = rand(y, 0) + (k % 3 - 1) * 9
        p.drawArc(QRectF(x - 5, y - 4, 10, 9), 200 * 16, 200 * 16)
    p.setPen(KEIN_STIFT)


# ---------------------------------------------------------------- Klappsitz

def zeichne_klappsitz(p, klappe):
    """Hörsaal-Klappsitz, Boden im Ursprung, Sitzfläche zeigt nach +x.
    klappe: 0 = Sitz unten (waagerecht), 1 = hochgeklappt (senkrecht)."""
    p.setPen(KEIN_STIFT)
    # Seitenwange mit Fuß
    p.setBrush(linear(-40, 0, 20, 0, QColor('#5A5F6B'), QColor('#2E313A')))
    wange = QPainterPath()
    wange.moveTo(-34, 0)
    wange.lineTo(-30, -112)
    wange.lineTo(-14, -112)
    wange.lineTo(-10, -60)
    wange.lineTo(18, -60)
    wange.lineTo(22, 0)
    wange.closeSubpath()
    p.drawPath(wange)
    p.setBrush(QColor('#24262D'))
    p.drawRoundedRect(QRectF(-44, -6, 74, 8), 3, 3)
    # Rückenlehne
    p.save()
    p.translate(-26, -64)
    p.rotate(-8)
    p.setBrush(linear(-10, 0, 10, 0, HOLZ_HELL, HOLZ_DUNKEL))
    p.drawRoundedRect(QRectF(-12, -96, 18, 100), 8, 8)
    p.setBrush(linear(0, -90, 0, 0, QColor('#C23B3B'), QColor('#7A1F2A')))
    p.drawRoundedRect(QRectF(-6, -88, 12, 80), 5, 5)
    p.restore()
    # Sitzfläche am Gelenk (-12, -62)
    p.save()
    p.translate(-12, -62)
    p.rotate(-90 * klappe)
    p.setBrush(linear(0, -6, 0, 10, HOLZ_HELL, HOLZ_DUNKEL))
    p.drawRoundedRect(QRectF(-2, -4, 66, 12), 6, 6)
    p.setBrush(linear(0, -14, 0, -2, QColor('#D24A4A'), QColor('#8A2230')))
    p.drawRoundedRect(QRectF(2, -14, 60, 12), 6, 6)
    p.restore()
    p.setBrush(METALL_DUNKEL)
    kreis(p, -12, -62, 4.5)
    p.setBrush(METALL_HELL)
    kreis(p, -12, -62, 2)


def zeichne_staubwolke(p, x, y, r, a):
    p.setPen(KEIN_STIFT)
    for k in range(6):
        w = k * math.pi / 5
        p.setBrush(radial(x + math.cos(w) * r, y - abs(math.sin(w)) * r * 0.5, r * 0.6,
                          QColor(235, 230, 220, a), QColor(235, 230, 220, 0)))
        kreis(p, x + math.cos(w) * r, y - abs(math.sin(w)) * r * 0.5, r * 0.6)

