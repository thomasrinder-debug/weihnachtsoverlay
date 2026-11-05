"""Requisiten für die Szenen kabel und ventilator: Kabelknäuel, dicke Kabelwindungen
um die Figur, Stecker, ein Standventilator und der zum Ballon aufgeblähte Kittel.

Einheiten wie in labor.py, Boden mittig im Ursprung.
"""
import math
import random

from PyQt6.QtCore import QPointF, QRectF
from PyQt6.QtGui import QColor, QPainterPath

from .grundlagen import *  # noqa: F401,F403  Farben und Hilfen
from .labor import METALL, METALL_DUNKEL
from .professor import KITTEL, KITTEL_SCHATTEN, KOPF_Y, PULLI, _arm, _bein, _kopf_seite, _kopf_vorn


# ---------------------------------------------------------------- Kabel

KABEL = QColor('#2F3136')
KABEL_HELL = QColor('#7A808A')


def kabel_strich(p, pfad, breite=3.4):
    p.setBrush(KEIN_PINSEL)
    p.setPen(stift(KABEL, breite))
    p.drawPath(pfad)
    p.setPen(stift(KABEL_HELL, breite * 0.3))
    p.drawPath(pfad.translated(-0.3, -breite * 0.25))
    p.setPen(KEIN_STIFT)


def kabel_linie(p, punkte, breite=3.4):
    """Weiches Kabel durch die Punkte (mit Glanz)."""
    if len(punkte) < 2:
        return
    pfad = QPainterPath()
    pfad.moveTo(*punkte[0])
    for a, b in zip(punkte, punkte[1:]):
        pfad.quadTo(a[0], a[1], (a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
    pfad.lineTo(*punkte[-1])
    kabel_strich(p, pfad, breite)


def zeichne_stecker(p, x, y, dreh=0.0):
    """Schukostecker-artiger Stecker, Kabelansatz bei (x, y), Stifte zeigen in Richtung dreh (0 = rechts)."""
    p.save()
    p.translate(x, y)
    p.rotate(dreh)
    p.setPen(KEIN_STIFT)
    p.setBrush(linear(0, -5, 0, 5, QColor('#4A4C52'), QColor('#1E1F22')))
    p.drawRoundedRect(QRectF(0, -5, 11, 10), 3, 3)
    p.setBrush(linear(0, -2, 0, 2, METALL.lighter(120), METALL_DUNKEL))
    p.drawRoundedRect(QRectF(10, -3.8, 6, 2.2), 1, 1)
    p.drawRoundedRect(QRectF(10, 1.6, 6, 2.2), 1, 1)
    p.restore()


def zeichne_knaeuel(p, x, y, menge=1.0, t=0.0, saat=4, breite=3.0):
    """Kabelsalat auf dem Boden (Unterkante mittig bei x, y); menge 0..1 schrumpft ihn."""
    if menge <= 0.02:
        return
    z = random.Random(saat)
    g = 0.35 + 0.65 * menge
    n = 13
    p.setBrush(QColor(0, 0, 0, 40))
    p.setPen(KEIN_STIFT)
    p.drawEllipse(QRectF(x - 34 * g, y - 3, 68 * g, 6))
    for k in range(n):
        if k > n * menge + 2:
            break
        rx = z.uniform(9, 19) * g
        ry = z.uniform(5, 11) * g
        cx = x + z.uniform(-20, 20) * g
        cy = y - ry - 2 - z.uniform(0, 16) * g
        w = z.uniform(-35, 35) + math.sin(t * 3 + k) * 2
        p.save()
        p.translate(cx, cy)
        p.rotate(w)
        pfad = QPainterPath()
        pfad.addEllipse(QRectF(-rx, -ry, 2 * rx, 2 * ry))
        kabel_strich(p, pfad, breite)
        p.restore()


# (Höhe, Halbbreite): erst die Beine, dann der Bauch, zuletzt die Arme
WICKLUNG = ((-10, 17), (-26, 17), (-42, 19), (-60, 43), (-80, 41), (-100, 38), (-120, 44), (-138, 41))


def wicklung_punkt(anteil):
    """Wo das Kabel gerade auf der Figur ankommt (Figur-Einheiten)."""
    i = max(0, min(len(WICKLUNG) - 1, math.ceil(anteil * len(WICKLUNG)) - 1))
    y, rx = WICKLUNG[i]
    return rx, y


def zeichne_wicklung(p, anteil, eng=0.0, vorn=True, breite=7.0):
    """Dicke Kabelwindungen um die Figur (in Figur-Einheiten): vorn die untere, hinten die obere Bogenhälfte."""
    voll = anteil * len(WICKLUNG)
    for i, (y, rx) in enumerate(WICKLUNG):
        f = min(1.0, voll - i)
        if f <= 0 or (not vorn and f < 1):
            break
        rx = rx * (1 - 0.1 * eng) + breite * 0.3
        ry = 8 - 3 * eng
        p.save()
        p.translate(0, y)
        p.rotate((-1) ** i * 8)
        r = QRectF(-rx, -ry, 2 * rx, 2 * ry)
        pfad = QPainterPath()
        if vorn:
            pfad.arcMoveTo(r, 180)
            pfad.arcTo(r, 180, 180 * f)
        else:
            pfad.arcMoveTo(r, 0)
            pfad.arcTo(r, 0, 180)
        kabel_strich(p, pfad, breite)
        p.restore()


# ---------------------------------------------------------------- Ventilator

VENT_MITTE = (4, -104)    # Mitte des Schutzkorbs
VENT_R = 40               # Radius des Korbs
VENT_KNOPF = (76, -6)     # Fußschalter auf dem Boden, mit Kabel am Sockel


def zeichne_ventilator(p, dreh=0.0, wirbel=0.0, stufe=0, druck=0.0):
    """Standventilator, bläst nach rechts (+x). Ursprung: Boden mittig unter dem Sockel.
    dreh: Flügelwinkel (Grad), wirbel 0..1 verwischt die Flügel, stufe 0..3 Lämpchen,
    druck 0..1 drückt den Fußschalter hinein."""
    cx, cy = VENT_MITTE
    r = VENT_R
    p.setPen(KEIN_STIFT)
    p.setBrush(QColor(0, 0, 0, 45))
    p.drawEllipse(QRectF(-46, -3, 92, 7))
    # Sockel
    p.setBrush(linear(0, -16, 0, 0, QColor('#5D86B5'), QColor('#2F4F78')))
    p.drawRoundedRect(QRectF(-40, -16, 80, 16), 7, 7)
    p.setBrush(QColor(255, 255, 255, 70))
    p.drawRoundedRect(QRectF(-34, -14, 60, 3), 1.5, 1.5)
    for k in range(3):
        an = k < stufe
        p.setBrush(QColor('#7CFF8A') if an else QColor('#24384F'))
        kreis(p, -24 + k * 9, -7, 2.6)
        if an:
            p.setBrush(QColor(124, 255, 138, 80))
            kreis(p, -24 + k * 9, -7, 5)
    kx, ky = VENT_KNOPF
    kabel_linie(p, [(36, -4), (50, 1), (kx - 12, -1)], 2.4)
    hoch = 7 * (1 - druck)
    p.setBrush(QColor(0, 0, 0, 45))
    p.drawEllipse(QRectF(kx - 15, -3, 30, 6))
    p.setBrush(linear(0, -6, 0, 0, QColor('#4A4C52'), QColor('#1E1F22')))
    p.drawRoundedRect(QRectF(kx - 13, -6, 26, 6), 2.5, 2.5)
    p.setBrush(radial(kx - 3, -6 - hoch, 12, ROT_HELL, ROT_DUNKEL))
    p.drawEllipse(QRectF(kx - 10, -9 - hoch, 20, 8 + hoch))
    p.setBrush(QColor(255, 255, 255, 110))
    p.drawEllipse(QRectF(kx - 6, -8 - hoch, 7, 3))
    # Stange und Motor
    p.setBrush(linear(-4, 0, 4, 0, METALL.lighter(115), METALL_DUNKEL))
    p.drawRect(QRectF(-4, cy, 8, -cy - 14))
    p.setBrush(linear(cx - 30, cy - 14, cx - 30, cy + 14, QColor('#6E97C6'), QColor('#2F4F78')))
    p.drawRoundedRect(QRectF(cx - 34, cy - 15, 30, 30), 11, 11)
    p.setBrush(QColor(255, 255, 255, 60))
    p.drawRoundedRect(QRectF(cx - 30, cy - 12, 20, 4), 2, 2)
    # Flügel, im Halbprofil (Scheibe gestaucht)
    p.save()
    p.translate(cx, cy)
    p.scale(0.5, 1)
    p.setBrush(QColor(110, 160, 220, int(30 + 150 * wirbel)))
    kreis(p, 0, 0, r - 3)
    a = int(235 * (1 - 0.8 * wirbel))
    for k in range(4):
        p.save()
        p.rotate(dreh + k * 90)
        fl = QPainterPath()
        fl.moveTo(0, 0)
        fl.cubicTo(r * 0.3, -r * 0.35, r * 0.95, -r * 0.3, r * 0.9, r * 0.05)
        fl.cubicTo(r * 0.75, r * 0.3, r * 0.3, r * 0.2, 0, 0)
        p.setBrush(QColor(60, 110, 185, a))
        p.drawPath(fl)
        p.restore()
    p.setBrush(radial(-2, -2, 8, METALL.lighter(130), METALL_DUNKEL))
    kreis(p, 0, 0, 7)
    p.setBrush(KEIN_PINSEL)
    p.setPen(stift(QColor('#D8DEE6'), 3.4))
    kreis(p, 0, 0, r)
    p.setPen(stift(QColor(216, 222, 230, 170), 1.6))
    kreis(p, 0, 0, r * 0.62)
    for k in range(8):
        w = math.radians(k * 22.5)
        p.drawLine(QPointF(math.cos(w) * r, math.sin(w) * r), QPointF(-math.cos(w) * r, -math.sin(w) * r))
    p.restore()
    p.setPen(KEIN_STIFT)


# ---------------------------------------------------------------- Kittel als Ballon

def ballon_mass(bal):
    """Mitte (y), Halbachsen und Beinansatz des aufgeblähten Kittels in Figur-Einheiten."""
    rx = 36 + 58 * bal
    ry = 56 + 36 * bal
    cy = -100 - 4 * bal
    bein = max(-62.0, cy + ry - 14)
    return cy, rx, ry, bein


def zeichne_ballonprof(p, d, bal):
    """Der Professor mit zum Ballon aufgeblähtem Kittel (bal 0..1), Figur-Einheiten wie Professor.zeichne:
    Beine baumeln darunter, oben schaut der Kopf heraus, die Arme stehen seitlich ab."""
    pose, t = d.pose, d.t
    h = pose.hub
    cy, rx, ry, bein = ballon_mass(bal)
    cy += h
    bein += h
    flatter = math.sin(t * 23) * 2 * bal
    _arm(p, -rx * 0.5, cy - ry * 0.45, pose.arm_h, True)
    _bein(p, bein, pose.bein_h, True)
    _bein(p, bein, pose.bein_v, False)
    p.save()
    p.translate(0, cy)
    p.scale(1 + 0.02 * flatter, 1 - 0.02 * flatter)
    p.setBrush(QColor('#3A3C48'))
    p.drawEllipse(QRectF(-rx * 0.35, ry - 14, rx * 0.7, 14))
    p.setBrush(radial(-rx * 0.3, -ry * 0.35, max(rx, ry) * 1.5, KITTEL, KITTEL_SCHATTEN.darker(110)))
    p.drawEllipse(QRectF(-rx, -ry, 2 * rx, 2 * ry))
    p.setBrush(QColor(255, 255, 255, 150))
    p.drawEllipse(QRectF(-rx * 0.55, -ry * 0.7, rx * 0.45, ry * 0.3))
    p.setBrush(KEIN_PINSEL)
    p.setPen(stift(KITTEL_SCHATTEN.darker(115), 1.6))
    for k in (-0.45, 0.25):
        naht = QPainterPath()
        naht.moveTo(rx * k, -ry * 0.95)
        naht.quadTo(rx * (k + 0.35), 0, rx * k, ry * 0.95)
        p.drawPath(naht)
    p.setPen(KEIN_STIFT)
    p.setBrush(QColor('#C7CED6'))
    for k in range(4):
        w = -0.8 + k * 0.5
        kreis(p, rx * 0.62 * math.cos(w * 0.6) + 2, ry * math.sin(w) * 0.85, 2.6 + bal)
    for k, farbe in enumerate((QColor('#D3172E'), QColor('#2B4C9B'), QColor('#22834C'))):
        p.setBrush(farbe)
        p.drawRoundedRect(QRectF(-rx * 0.2 + k * 4.5, -ry * 0.45 - k * 2, 3.2, 14), 1.5, 1.5)
    p.setBrush(KITTEL_SCHATTEN.lighter(108))
    p.drawRoundedRect(QRectF(-rx * 0.24, -ry * 0.35, 16 + 8 * bal, 13), 2, 2)
    p.setBrush(PULLI.darker(110))
    p.drawEllipse(QRectF(-12, -ry - 6, 30, 12))
    p.setBrush(ROT)
    fl = QPainterPath()
    for sx in (-1, 1):
        fl.moveTo(10, -ry)
        fl.lineTo(10 + sx * 8, -ry - 6)
        fl.lineTo(10 + sx * 8, -ry + 6)
        fl.closeSubpath()
    p.drawPath(fl)
    p.restore()
    p.save()
    p.translate(5, ballon_kopf_y(bal) + h)
    p.scale(1.12, 1.12)
    if pose.kopf_vorn:
        _kopf_vorn(p, d, 1, 0)
    else:
        _kopf_seite(p, d, -1, 0)
    p.restore()
    _arm(p, rx * 0.35, cy - ry * 0.35, pose.arm_v, False)


def ballon_kopf_y(bal):
    cy, rx, ry, _ = ballon_mass(bal)
    return min(KOPF_Y, cy - ry - 16)
