"""Der verrückte Professor: wirres weißes Haar, runde Brille, Laborkittel, gelbe
Gummihandschuhe, Fliege und eine etwas zu kleine Weihnachtsmütze.

Wie die Figuren in figuren.py: KASTEN, KOPF und zeichne(p, d). d braucht pose
und t; eigene Merkmale (alle freiwillig):
    haare      0..1  Haare stehen senkrecht (nach Explosion oder Stromschlag)
    haar_farbe QColor, sonst Weiß
    gluehen    0..1  Haare leuchten (Tesla-Spule)
    brille     0..1  Brille rutscht schief
    russ       0..1  rußiges Gesicht (bleibt, egal welche Pose)
    muetze     False: Mütze ist weg (fliegt gerade, hängt woanders)
    halt       Funktion halt(p, hx, hy): zeichnet, was er in der vorderen Hand hält
               (in Figur-Einheiten, vor dem Kittel, hinter dem Ärmel)
    halt_h     dasselbe für die hintere Hand
"""
import math

from PyQt6.QtCore import QPointF, QRectF
from PyQt6.QtGui import QColor, QPainterPath, QTransform

from .figur import zeichne_russ
from .grundlagen import *  # noqa: F401,F403  Farben und Hilfen

KITTEL = QColor('#F4F7FA')
KITTEL_SCHATTEN = QColor('#B9C6D3')
HOSE = QColor('#4B4A5C')
SCHUH = QColor('#6B3F22')
HANDSCHUH = QColor('#F2C230')
HANDSCHUH_DUNKEL = QColor('#C18A12')
PULLI = QColor('#2E7D4F')
HAAR = QColor('#F7F7F2')
HAAR_SCHATTEN = QColor('#C9CCD2')
BRILLE = QColor('#3B2E28')
NASE = QColor('#F2A48F')

SCHULTER_Y = -146
ARM_LAENGE = 52
KOPF_Y = -180


def _bein(p, y, winkel, hinten):
    d = 125 if hinten else 100
    p.save()
    p.translate(0, y)
    p.rotate(winkel)
    p.setBrush(linear(-7, 0, 7, 0, HOSE.lighter(130).darker(d), HOSE.darker(140).darker(d)))
    p.drawRoundedRect(QRectF(-7, -4, 14, 58), 6, 6)
    schuh = QPainterPath()
    schuh.moveTo(-9, 50)
    schuh.cubicTo(-10, 60, -4, 62, 6, 62)
    schuh.cubicTo(18, 62, 26, 60, 26, 56)
    schuh.cubicTo(26, 51, 16, 48, 8, 48)
    schuh.lineTo(-7, 48)
    schuh.closeSubpath()
    p.setBrush(linear(0, 48, 0, 62, SCHUH.lighter(130).darker(d), SCHUH.darker(150).darker(d)))
    p.drawPath(schuh)
    p.setBrush(QColor(255, 255, 255, 60))
    p.drawEllipse(QRectF(10, 51, 9, 3))
    p.setBrush(QColor('#2A1A10').darker(d))
    p.drawRoundedRect(QRectF(-10, 60, 37, 3.5), 1.5, 1.5)
    p.restore()


def _arm(p, x, y, winkel, hinten, halt=None):
    d = 125 if hinten else 100
    p.save()
    p.translate(x, y)
    p.rotate(winkel)
    p.setBrush(linear(-8, 0, 8, 0, KITTEL.darker(d), KITTEL_SCHATTEN.darker(d)))
    p.drawRoundedRect(QRectF(-8, -6, 16, 46), 7, 7)
    p.setBrush(KITTEL_SCHATTEN.darker(d))
    p.drawRoundedRect(QRectF(-8.5, 34, 17, 6), 3, 3)
    # Gummihandschuh mit Daumen
    p.setBrush(radial(-2, 48, 11, HANDSCHUH.lighter(125).darker(d), HANDSCHUH_DUNKEL.darker(d)))
    p.drawRoundedRect(QRectF(-6.5, 38, 13, 7), 3, 3)
    kreis(p, 0, ARM_LAENGE - 3, 7.5)
    p.drawEllipse(QPointF(6.5, ARM_LAENGE - 8), 3, 4.5)
    p.setBrush(QColor(255, 255, 255, 80))
    kreis(p, -3, ARM_LAENGE - 6, 2)
    p.restore()


def _hand(x, y, winkel):
    w = math.radians(winkel)
    return x - math.sin(w) * ARM_LAENGE, y + math.cos(w) * ARM_LAENGE


def hand_lokal(pose, vorn=True):
    """Lage der Hand in Figur-Einheiten (Fuß im Ursprung, Blick nach rechts)."""
    h = pose.hub
    if vorn:
        return _hand(pose.arm_v_x, SCHULTER_Y + h, pose.arm_v)
    return _hand(-6, SCHULTER_Y + h, pose.arm_h)


def _kittel(p, h, t):
    flatter = math.sin(t * 5) * 1.5
    kittel = QPainterPath()
    kittel.moveTo(-20, -154 + h)
    kittel.lineTo(18, -154 + h)
    kittel.cubicTo(30, -124 + h, 40, -84 + h, 38 + flatter, -46 + h)
    kittel.lineTo(4, -44 + h)
    kittel.lineTo(-2, -60 + h)
    kittel.lineTo(-8, -44 + h)
    kittel.lineTo(-40 - flatter, -48 + h)
    kittel.cubicTo(-38, -90 + h, -30, -126 + h, -20, -154 + h)
    p.setBrush(linear(-30, -150 + h, 30, -46 + h, KITTEL, KITTEL_SCHATTEN))
    p.drawPath(kittel)
    # Pullover und Fliege im Ausschnitt
    pulli = QPainterPath()
    pulli.moveTo(6, -154 + h)
    pulli.lineTo(20, -154 + h)
    pulli.cubicTo(22, -136 + h, 20, -120 + h, 16, -108 + h)
    pulli.closeSubpath()
    p.setBrush(linear(6, -154 + h, 20, -108 + h, PULLI.lighter(125), PULLI.darker(130)))
    p.drawPath(pulli)
    p.setBrush(QColor(255, 255, 255, 170))
    for k in range(3):
        stern(p, 15 - k * 1.5, -140 + h + k * 10, 2.2)
    p.setPen(stift(KITTEL_SCHATTEN.darker(115), 1.4))
    p.drawLine(QPointF(16, -108 + h), QPointF(24, -48 + h))
    p.drawLine(QPointF(-14, -86 + h), QPointF(-12, -50 + h))
    p.setPen(KEIN_STIFT)
    p.setBrush(QColor('#C7CED6'))
    for k in range(3):
        kreis(p, 19 + k * 1.6, -98 + h + k * 16, 2)
    # Brusttasche mit Stiften
    for k, farbe in enumerate((QColor('#D3172E'), QColor('#2B4C9B'), QColor('#22834C'))):
        p.setBrush(farbe)
        p.drawRoundedRect(QRectF(-6 + k * 4.5, -136 + h - k * 2, 3.2, 14), 1.5, 1.5)
    p.setBrush(KITTEL_SCHATTEN.lighter(108))
    p.drawRoundedRect(QRectF(-9, -126 + h, 16, 13), 2, 2)
    p.setBrush(QColor('#9AA8B6'))
    p.drawRect(QRectF(-9, -126 + h, 16, 2))
    # Fliege
    p.setBrush(ROT)
    fl = QPainterPath()
    fl.moveTo(14, -152 + h)
    fl.lineTo(6, -158 + h)
    fl.lineTo(6, -146 + h)
    fl.closeSubpath()
    fl.moveTo(14, -152 + h)
    fl.lineTo(22, -158 + h)
    fl.lineTo(22, -146 + h)
    fl.closeSubpath()
    p.drawPath(fl)
    p.setBrush(ROT_DUNKEL)
    kreis(p, 14, -152 + h, 2.6)


def _haarbuschel(p, x, y, laenge, winkel, breite, farbe, schatten):
    p.save()
    p.translate(x, y)
    p.rotate(winkel)
    buschel = QPainterPath()
    buschel.moveTo(-breite, 0)
    buschel.cubicTo(-breite, -laenge * 0.6, -breite * 0.3, -laenge * 0.8, 0, -laenge)
    buschel.cubicTo(breite * 0.3, -laenge * 0.8, breite, -laenge * 0.6, breite, 0)
    buschel.closeSubpath()
    p.setBrush(linear(0, 0, 0, -laenge, schatten, farbe))
    p.drawPath(buschel)
    p.restore()


def _haare(p, x, y, d, seiten):
    """Wirre Haarbüschel rund um den Kopf; seiten: Winkelbereich in Grad (0 = oben, im Uhrzeigersinn)."""
    hoch = getattr(d, 'haare', 0.0)
    farbe = getattr(d, 'haar_farbe', None) or HAAR
    gluehen = getattr(d, 'gluehen', 0.0)
    if gluehen:
        p.setBrush(radial(x, y - 10, 70, QColor(170, 220, 255, int(170 * gluehen)), QColor(170, 220, 255, 0)))
        kreis(p, x, y - 10, 70)
        farbe = QColor(farbe).lighter(100 + int(15 * gluehen))
    schatten = QColor(farbe).darker(125) if farbe != HAAR else HAAR_SCHATTEN
    t = d.t
    a0, a1 = seiten
    n = 9
    for k in range(n):
        a = a0 + (a1 - a0) * k / (n - 1)
        wackel = math.sin(t * 7 + k * 1.7) * 4
        laenge = (20 + 9 * ((k * 5) % 3)) * (1 + 0.9 * hoch)
        winkel = a * (1 - hoch) + (a * 0.25) * hoch + wackel
        r = math.radians(a)
        _haarbuschel(p, x + math.sin(r) * 18, y - math.cos(r) * 18, laenge, winkel, 8, farbe, schatten)


def zeichne_muetze_prof(p, x, y, wipp=0.0):
    """Die Mütze allein, Rand mittig bei (x, y), etwa wenn sie davonfliegt."""
    _muetze(p, x, y + 14, wipp, 0.0)


def _muetze(p, x, y, wipp, hoch):
    """Kleine Weihnachtsmütze, die auf den Haaren sitzt (bei hoch=1 obenauf)."""
    y -= 22 * hoch
    m = QPainterPath()
    m.moveTo(x - 20, y - 14)
    m.lineTo(x + 20, y - 14)
    m.cubicTo(x + 18, y - 44, x - 2, y - 54, x - 26 + wipp, y - 40)
    m.cubicTo(x - 20, y - 40, x - 18, y - 30, x - 20, y - 14)
    p.setBrush(linear(x - 24, y - 50, x + 20, y - 14, ROT_HELL, ROT_DUNKEL))
    p.drawPath(m)
    flausch(p, [(x + dx, y - 15) for dx in range(-20, 22, 6)], 6)
    tx, ty = x - 28 + wipp, y - 38
    flausch(p, [(tx + dx, ty + dy) for dx, dy in ((0, 0), (-3, -3), (3, -3), (-3, 3), (3, 3))], 5)


def _auge_hinter_glas(p, x, y, r, pose, blick):
    g = 1 + 0.35 * pose.schreck
    if pose.auge_zu:
        p.setPen(stift(SCHWARZ, 1.8))
        p.setBrush(KEIN_PINSEL)
        lid = QPainterPath()
        lid.moveTo(x - r * 0.6, y)
        lid.quadTo(x, y + r * 0.4, x + r * 0.6, y)
        p.drawPath(lid)
        p.setPen(KEIN_STIFT)
        return
    p.setBrush(WEISS)
    p.drawEllipse(QPointF(x, y), r * 0.62 * g, r * 0.7 * g)
    px, py = x + blick[0] * r * 0.25, y + blick[1] * r * 0.25
    p.setBrush(QColor('#2F5E8C'))
    kreis(p, px, py, r * 0.38 * (1 - 0.35 * pose.schreck))
    p.setBrush(SCHWARZ)
    kreis(p, px, py, r * 0.2 * (1 - 0.35 * pose.schreck))
    p.setBrush(WEISS)
    kreis(p, px + r * 0.12, py - r * 0.14, r * 0.1)


def _glas(p, x, y, r):
    p.setBrush(QColor(200, 230, 255, 55))
    kreis(p, x, y, r)
    p.setPen(stift(BRILLE, 2.2))
    p.setBrush(KEIN_PINSEL)
    kreis(p, x, y, r)
    p.setPen(stift(QColor(255, 255, 255, 170), 1.4))
    p.drawArc(QRectF(x - r * 0.7, y - r * 0.7, r * 1.4, r * 1.4), 100 * 16, 60 * 16)
    p.setPen(KEIN_STIFT)


def _kopf_seite(p, d, x, y):
    pose = d.pose
    _haare(p, x - 4, y - 2, d, (-150, 10))
    p.setBrush(radial(x + 6, y - 8, 32, HAUT, HAUT_DUNKEL))
    p.drawEllipse(QPointF(x, y), 22, 24)
    p.setBrush(HAUT_DUNKEL)
    p.drawEllipse(QPointF(x - 9, y + 2), 5, 7)
    p.setBrush(radial(x + 15, y + 8, 8, QColor(240, 110, 110, 150), QColor(240, 110, 110, 0)))
    kreis(p, x + 15, y + 8, 8)
    russ = max(pose.russ, getattr(d, 'russ', 0.0))
    if russ:
        zeichne_russ(p, x + 4, y, 23, russ)
    schief = getattr(d, 'brille', 0.0)
    gy = y - 4 + 5 * schief
    _auge_hinter_glas(p, x + 15, y - 4, 9, pose, (1.0 if not pose.kopf_vorn else 0, pose.blick_y))
    p.setPen(stift(BRILLE, 1.8))
    p.drawLine(QPointF(x + 7, gy - 1), QPointF(x - 8, y - 2))
    p.setPen(KEIN_STIFT)
    p.save()
    p.translate(x + 15, gy)
    p.rotate(14 * schief)
    _glas(p, 0, 0, 9)
    p.restore()
    # buschige Braue
    by = y - 16 - 6 * pose.schreck
    flausch(p, [(x + 10, by + 1.5 - 2 * pose.sorge), (x + 15, by), (x + 20, by + 0.5 + 2 * pose.sorge)], 3.4, False)
    # Knubbelnase
    p.setBrush(radial(x + 25, y + 2, 9, NASE.lighter(108), QColor('#D9735A')))
    p.drawEllipse(QPointF(x + 25, y + 4), 7, 6)
    p.setBrush(QColor(255, 255, 255, 140))
    kreis(p, x + 23, y + 1.5, 1.4)
    if pose.schreck > 0.2:
        p.setBrush(QColor('#6E1A1A'))
        p.drawEllipse(QPointF(x + 18, y + 15), 3.5, 2 + 3.5 * pose.schreck)
    elif pose.mund_offen:
        p.setBrush(QColor('#6E1A1A'))
        p.drawChord(QRectF(x + 12, y + 11, 11, 8), 180 * 16, 180 * 16)
    else:
        p.setPen(stift(QColor('#7A2A24'), 1.6))
        p.setBrush(KEIN_PINSEL)
        p.drawArc(QRectF(x + 11, y + 8, 11, 7), 200 * 16, 130 * 16)
        p.setPen(KEIN_STIFT)
    if pose.muetze and getattr(d, 'muetze', True):
        _muetze(p, x - 2, y - 2, pose.wipp, getattr(d, 'haare', 0.0))


def _kopf_vorn(p, d, x, y):
    pose = d.pose
    hoch = getattr(d, 'haare', 0.0)
    _haare(p, x, y, d, (-125, -55))
    _haare(p, x, y, d, (55, 125))
    if hoch:
        _haare(p, x, y, d, (-40, 40))
    p.setBrush(HAUT_DUNKEL)
    for seite in (-1, 1):
        p.drawEllipse(QPointF(x + seite * 22, y + 2), 5, 7)
    p.setBrush(radial(x - 6, y - 8, 34, HAUT, HAUT_DUNKEL))
    p.drawEllipse(QPointF(x, y), 22, 24)
    for seite in (-1, 1):
        p.setBrush(radial(x + seite * 13, y + 9, 7, QColor(240, 110, 110, 150), QColor(240, 110, 110, 0)))
        kreis(p, x + seite * 13, y + 9, 7)
    russ = max(pose.russ, getattr(d, 'russ', 0.0))
    if russ:
        zeichne_russ(p, x, y, 23, russ)
    schief = getattr(d, 'brille', 0.0)
    for seite in (-1, 1):
        _auge_hinter_glas(p, x + seite * 9, y - 4, 8.5, pose, (pose.blick_x, pose.blick_y))
    p.save()
    p.translate(x, y - 4)
    p.rotate(12 * schief)
    for seite in (-1, 1):
        _glas(p, seite * 9.5, 0, 8.5)
    p.setPen(stift(BRILLE, 1.8))
    p.drawLine(QPointF(-2, -1), QPointF(2, -1))
    p.setPen(KEIN_STIFT)
    p.restore()
    by = y - 16 - 6 * pose.schreck
    for seite in (-1, 1):
        p.save()
        p.translate(x + seite * 9, by)
        p.rotate(seite * 20 * pose.sorge)
        flausch(p, [(-4.5, 0.5), (0, -0.5), (4.5, 0.5)], 3.2, False)
        p.restore()
    p.setBrush(radial(x - 1, y + 2, 9, NASE.lighter(108), QColor('#D9735A')))
    p.drawEllipse(QPointF(x, y + 5), 6, 6.5)
    p.setBrush(QColor(255, 255, 255, 140))
    kreis(p, x - 2, y + 2, 1.4)
    if pose.schreck > 0.2:
        p.setBrush(QColor('#6E1A1A'))
        p.drawEllipse(QPointF(x, y + 16), 4, 2 + 4 * pose.schreck)
    elif pose.mund_offen:
        p.setBrush(QColor('#6E1A1A'))
        p.drawChord(QRectF(x - 6, y + 11, 12, 9), 180 * 16, 180 * 16)
    else:
        p.setPen(stift(QColor('#7A2A24'), 1.6))
        p.setBrush(KEIN_PINSEL)
        p.drawArc(QRectF(x - 7, y + 9, 14, 7), 200 * 16, 140 * 16)
        p.setPen(KEIN_STIFT)
    if pose.muetze and getattr(d, 'muetze', True):
        p.save()
        p.translate(x, y)
        p.rotate(-8)
        p.scale(-1, 1)
        _muetze(p, 0, 0, pose.wipp, hoch)
        p.restore()


class Professor:
    """Verrückter Professor im Laborkittel mit Weihnachtsmütze."""
    KASTEN = QRectF(-70, -262, 150, 268)
    KOPF = (4, -250)

    @staticmethod
    def zeichne(p, d):
        pose, t, h = d.pose, d.t, d.pose.hub
        halt, halt_h = getattr(d, 'halt', None), getattr(d, 'halt_h', None)
        _arm(p, -6, SCHULTER_Y + h, pose.arm_h, True)
        if halt_h:
            halt_h(p, *hand_lokal(pose, False))
        _bein(p, -62 + h, pose.bein_h, True)
        _bein(p, -62 + h, pose.bein_v, False)
        _kittel(p, h, t)
        hoch_arm = pose.arm_v < -150
        if hoch_arm:
            _arm(p, pose.arm_v_x, SCHULTER_Y + h, pose.arm_v, False)
        p.save()
        p.translate(5, KOPF_Y + h)
        p.scale(1.12, 1.12)
        if pose.kopf_vorn:
            _kopf_vorn(p, d, 1, 0)
        else:
            _kopf_seite(p, d, -1, 0)
        p.restore()
        if halt:
            halt(p, *hand_lokal(pose))
        if not hoch_arm:
            _arm(p, pose.arm_v_x, SCHULTER_Y + h, pose.arm_v, False)


def professor_trafo(x, y, s, richtung, stauchen=1.0, neigung=0.0):
    tr = QTransform()
    tr.translate(x, y)
    tr.rotate(neigung * richtung)
    tr.scale(s * richtung * (2 - stauchen), s * stauchen)
    return tr
