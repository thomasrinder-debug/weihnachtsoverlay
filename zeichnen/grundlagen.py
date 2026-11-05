"""Farben, Verläufe, Pelz, Sterne und Teilchen (Funken, Rauch, Ruß)."""
import math

from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import QBrush, QColor, QLinearGradient, QPainterPath, QPen, QRadialGradient

ROT = QColor('#D3172E')
ROT_HELL = QColor('#EC3A4F')
ROT_DUNKEL = QColor('#930B21')
WEISS = QColor('#FAFAFA')
FELL_SCHATTEN = QColor('#CDD2DC')
HAUT = QColor('#F8D6B8')
HAUT_DUNKEL = QColor('#E3A985')
SCHWARZ = QColor('#1F1F1F')
GOLD = QColor('#E3A928')
GOLD_HELL = QColor('#FFE38F')
GRUEN = QColor('#22834C')
GRUEN_DUNKEL = QColor('#11502C')
SACK_HELL = QColor('#B8834B')
SACK_DUNKEL = QColor('#6A421F')
FELL_R = QColor('#946139')
FELL_R_DUNKEL = QColor('#62401F')
BAUCH_R = QColor('#D6B48C')

FIGUR_HOEHE = 250      # Höhe des Weihnachtsmanns in Zeichen-Einheiten (Fuß bis Mützenspitze)
KEIN_STIFT = Qt.PenStyle.NoPen
KEIN_PINSEL = Qt.BrushStyle.NoBrush


# ---------------------------------------------------------------- Hilfen

def glatt(u):
    u = max(0.0, min(1.0, u))
    return u * u * (3 - 2 * u)


def kreis(p, x, y, r):
    p.drawEllipse(QPointF(x, y), r, r)


def linear(x1, y1, x2, y2, a, b):
    g = QLinearGradient(QPointF(x1, y1), QPointF(x2, y2))
    g.setColorAt(0, a)
    g.setColorAt(1, b)
    return QBrush(g)


def radial(x, y, r, innen, aussen):
    g = QRadialGradient(QPointF(x, y), r)
    g.setColorAt(0, innen)
    g.setColorAt(1, aussen)
    return QBrush(g)


def stift(farbe, breite, stil=Qt.PenStyle.SolidLine):
    pen = QPen(farbe, breite, stil, Qt.PenCapStyle.RoundCap)
    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    return pen


def flausch(p, punkte, r, schatten=True):
    """Pelz als Kette weicher Kreise, optional mit leichtem Schatten."""
    p.setPen(KEIN_STIFT)
    if schatten:
        p.setBrush(FELL_SCHATTEN)
        for x, y in punkte:
            kreis(p, x + 0.8, y + 1.5, r)
    p.setBrush(WEISS)
    for x, y in punkte:
        kreis(p, x, y, r)


def stern(p, x, y, r):
    pfad = QPainterPath()
    pfad.moveTo(x, y - r)
    pfad.quadTo(x, y, x + r, y)
    pfad.quadTo(x, y, x, y + r)
    pfad.quadTo(x, y, x - r, y)
    pfad.quadTo(x, y, x, y - r)
    p.drawPath(pfad)


def blinzeln(t, versatz=0.0):
    return (t + versatz) % 3.4 < 0.14


class Teilchen:
    __slots__ = ('x', 'y', 'vx', 'vy', 'alter', 'dauer', 'r0', 'r1', 'farbe', 'art')

    def __init__(self, x, y, vx, vy, dauer, r0, r1, farbe, art):
        self.x, self.y, self.vx, self.vy = x, y, vx, vy
        self.alter, self.dauer = 0.0, dauer
        self.r0, self.r1, self.farbe, self.art = r0, r1, farbe, art


def teilchen_schritt(liste, dt, schwere=0.0, bremse=0.0):
    for t in liste:
        t.alter += dt
        t.x += t.vx * dt
        t.y += t.vy * dt
        t.vy += schwere * dt
        t.vx *= 1 - bremse * dt
        t.vy *= 1 - bremse * dt
    liste[:] = [t for t in liste if t.alter < t.dauer]


def zeichne_teilchen(p, liste):
    p.setPen(KEIN_STIFT)
    for t in liste:
        u = t.alter / t.dauer
        r = t.r0 + (t.r1 - t.r0) * u
        c = QColor(t.farbe)
        c.setAlphaF(c.alphaF() * (1 - u))
        if t.art == 'stern':
            p.setBrush(c)
            stern(p, t.x, t.y, r * (0.7 + 0.3 * math.sin(t.alter * 22)))
        else:
            aussen = QColor(c)
            aussen.setAlpha(0)
            p.setBrush(radial(t.x, t.y, r, c, aussen))
            kreis(p, t.x, t.y, r)


def teilchen_kasten(liste):
    if not liste:
        return QRectF()
    r = max(max(t.r0, t.r1) for t in liste)
    x0 = min(t.x for t in liste) - r
    y0 = min(t.y for t in liste) - r
    x1 = max(t.x for t in liste) + r
    y1 = max(t.y for t in liste) + r
    return QRectF(x0, y0, x1 - x0, y1 - y0)


def bildstueck(p, bild, bildrechteck, stueck, mitte, winkel=0.0, groesse=1.0, deckkraft=1.0, unten=False):
    """Zeichnet den Teil 'stueck' (logisches Rechteck) eines Bildschirmausschnitts 'bild', der das
    logische Rechteck 'bildrechteck' bedeckt, mit seiner Mitte (unten=True: Unterkante) bei 'mitte',
    gedreht und vergrößert."""
    f = bild.width() / bildrechteck.width() if bildrechteck.width() else 1.0
    quelle = QRectF((stueck.x() - bildrechteck.x()) * f, (stueck.y() - bildrechteck.y()) * f,
                    stueck.width() * f, stueck.height() * f)
    w, h = stueck.width(), stueck.height()
    p.save()
    p.translate(mitte)
    p.rotate(winkel)
    p.scale(groesse, groesse)
    p.setOpacity(p.opacity() * deckkraft)
    p.drawImage(QRectF(-w / 2, -h if unten else -h / 2, w, h), bild, quelle)
    p.restore()
