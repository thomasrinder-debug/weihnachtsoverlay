"""Requisiten für Labor F: plattgedrücktes Gesicht und flache Handschuhe an der Glasglocke,
Riesenauge im Mikroskop-Okular.

Alle Funktionen zeichnen in Einheiten; der Aufrufer verschiebt und skaliert vorher.
"""
import math

from PyQt6.QtCore import QPointF, QRectF
from PyQt6.QtGui import QColor, QPainterPath

from .grundlagen import HAUT, HAUT_DUNKEL, KEIN_PINSEL, KEIN_STIFT, WEISS, flausch, kreis, linear, radial, stift
from .labor import METALL, METALL_DUNKEL
from .labor_b import zeichne_auge
from .professor import BRILLE, HANDSCHUH, HANDSCHUH_DUNKEL, NASE

GEDRUECKT = QColor(255, 236, 226)


def zeichne_plattgesicht(p, nebel=0.0, quetsch=1.0, auge_zu=False):
    """Gesicht von vorn, plattgedrückt an einer Glasscheibe. Mitte (0, 0) = Kopfmitte,
    etwa 1,3-mal so breit wie der normale Kopf. quetsch 0..1, nebel 0..1 Atemhauch."""
    q = quetsch
    p.setPen(KEIN_STIFT)
    # Gesicht, breit gequetscht
    p.setBrush(radial(-6, -8, 40, HAUT, HAUT_DUNKEL))
    p.drawEllipse(QPointF(0, 2), 26 + 6 * q, 26 - 2 * q)
    # Backen quellen seitlich heraus
    for sx in (-1, 1):
        p.setBrush(radial(sx * 22, 10, 12, QColor(245, 140, 130, 200), QColor(245, 140, 130, 0)))
        p.drawEllipse(QPointF(sx * (20 + 5 * q), 10), 11, 9)
    # blasse Druckfläche am Glas
    p.setBrush(radial(0, 2, 26 * q + 4, QColor(255, 244, 238, int(210 * q)), QColor(255, 244, 238, 0)))
    p.drawEllipse(QPointF(0, 2), 24 * q + 4, 20 * q + 4)
    # Brauen weit hochgeschoben
    for sx in (-1, 1):
        p.save()
        p.translate(sx * 13, -21 - 3 * q)
        p.rotate(-sx * 12)
        flausch(p, [(-5, 0.5), (0, -0.5), (5, 0.5)], 3.4, False)
        p.restore()
    # Augen: eines weit, eines zugekniffen
    p.setBrush(WEISS)
    p.drawEllipse(QPointF(-13, -7), 7.5, 6)
    p.setBrush(QColor('#3A2A20'))
    kreis(p, -12, -6.5, 3.6)
    p.setBrush(WEISS)
    kreis(p, -11, -8, 1.2)
    p.setPen(stift(QColor('#5A3A30'), 1.8))
    if auge_zu:
        p.drawLine(QPointF(-19, -7), QPointF(-7, -7))
    p.drawLine(QPointF(7, -6), QPointF(19, -8))
    p.drawLine(QPointF(8, -4), QPointF(18, -3))
    # Brille flach aufs Glas gepresst
    p.setPen(stift(BRILLE, 2.4))
    p.setBrush(QColor(200, 230, 255, 60))
    p.drawEllipse(QPointF(-13, -6), 11 + 2 * q, 8.5 - 2 * q)
    p.drawEllipse(QPointF(13, -6), 11 + 2 * q, 8.5 - 2 * q)
    p.drawLine(QPointF(-2, -7), QPointF(2, -7))
    p.setPen(KEIN_STIFT)
    # Nase als runde Scheibe, Mitte blass, Nasenlöcher sichtbar
    p.setBrush(radial(0, 6, 13, NASE.lighter(105), QColor('#D9735A')))
    p.drawEllipse(QPointF(0, 6), 10 + 3 * q, 8 + 2 * q)
    p.setBrush(QColor(255, 225, 215, int(220 * q)))
    p.drawEllipse(QPointF(0, 5), 6 + 2 * q, 4.5 + q)
    p.setBrush(QColor('#7A2A24'))
    for sx in (-1, 1):
        p.drawEllipse(QPointF(sx * 4, 9), 2.4, 1.8)
    # Mund breit gequetscht
    p.setBrush(QColor('#E07A70'))
    p.drawEllipse(QPointF(0, 19), 11 + 3 * q, 4.5)
    p.setBrush(QColor('#6E1A1A'))
    p.drawEllipse(QPointF(0, 19), 8 + 2 * q, 1.8)
    # Atemhauch auf der Scheibe
    if nebel > 0:
        p.setBrush(radial(0, 17, 22, QColor(240, 248, 255, int(190 * nebel)), QColor(240, 248, 255, 0)))
        p.drawEllipse(QPointF(0, 17), 22, 13)
    # Glanzstreifen der Scheibe davor
    p.setPen(stift(QColor(255, 255, 255, 150), 3))
    p.drawLine(QPointF(-24, 16), QPointF(-12, -22))
    p.setPen(stift(QColor(255, 255, 255, 90), 1.6))
    p.drawLine(QPointF(-17, 20), QPointF(-6, -12))
    p.setPen(KEIN_STIFT)


def zeichne_platthand(p, dreh=0.0):
    """Gummihandschuh flach an die Scheibe gedrückt, Finger gespreizt, Mitte (0, 0)."""
    p.save()
    p.rotate(dreh)
    p.setPen(KEIN_STIFT)
    p.setBrush(radial(0, 0, 14, HANDSCHUH.lighter(140), HANDSCHUH_DUNKEL))
    for k in range(4):
        w = math.radians(-60 + k * 30)
        p.save()
        p.rotate(math.degrees(w))
        p.drawRoundedRect(QRectF(-2.8, -20, 5.6, 14), 2.8, 2.8)
        p.restore()
    p.save()
    p.rotate(75)
    p.drawRoundedRect(QRectF(-2.8, -16, 5.6, 11), 2.8, 2.8)
    p.restore()
    p.drawEllipse(QPointF(0, 0), 10, 9)
    p.setBrush(QColor(255, 250, 220, 150))
    p.drawEllipse(QPointF(0, 0), 6, 5)
    p.restore()


def zeichne_riesenauge(p, r, offen=1.0, blick=(0.0, 0.0), dreh=0.0):
    """Riesiges Auge in einer Messing-Linsenfassung, Mitte (0, 0), Radius r."""
    p.setPen(KEIN_STIFT)
    p.setBrush(QColor(0, 0, 0, 50))
    kreis(p, 3, 4, r * 1.2)
    p.save()
    p.rotate(dreh)
    p.setBrush(linear(-r, -r, r, r, METALL, METALL_DUNKEL))
    kreis(p, 0, 0, r * 1.2)
    p.setBrush(linear(-r, -r, r, r, QColor('#E8C060'), QColor('#8A6420')))
    kreis(p, 0, 0, r * 1.12)
    p.setBrush(QColor('#1E2430'))
    kreis(p, 0, 0, r * 1.03)
    p.setBrush(QColor('#8A6420'))
    for k in range(8):
        a = math.radians(k * 45 + 22)
        kreis(p, math.cos(a) * r * 1.16, math.sin(a) * r * 1.16, r * 0.035)
    p.restore()
    zeichne_auge(p, 0, 0, r, offen, blick)
    # Wimpern
    if offen > 0.05:
        p.setPen(stift(QColor('#2A1A14'), max(1.2, r * 0.07)))
        for k in range(-3, 4):
            a = math.pi / 2 + k * 0.33
            ax, ay = -math.cos(a) * r * 0.95, -math.sin(a) * r * offen * 0.98
            p.drawLine(QPointF(ax, ay), QPointF(ax * 1.22, ay - r * 0.22))
        p.setPen(KEIN_STIFT)
    # Glanz auf der Linse
    p.setBrush(QColor(255, 255, 255, 90))
    p.drawEllipse(QPointF(-r * 0.45, -r * 0.5), r * 0.25, r * 0.14)


def zeichne_trichter(p, x0, y0, x1, y1, b0, b1):
    """Messingtrichter vom Okular (x0, y0, Breite b0) zur Fassung (x1, y1, Breite b1)."""
    dx, dy = x1 - x0, y1 - y0
    n = math.hypot(dx, dy) or 1.0
    nx, ny = -dy / n, dx / n
    pfad = QPainterPath()
    pfad.moveTo(x0 + nx * b0 / 2, y0 + ny * b0 / 2)
    pfad.lineTo(x1 + nx * b1 / 2, y1 + ny * b1 / 2)
    pfad.lineTo(x1 - nx * b1 / 2, y1 - ny * b1 / 2)
    pfad.lineTo(x0 - nx * b0 / 2, y0 - ny * b0 / 2)
    pfad.closeSubpath()
    p.setPen(KEIN_STIFT)
    p.setBrush(linear(x0 + nx * b1, y0 + ny * b1, x0 - nx * b1, y0 - ny * b1, QColor('#5A667C'), QColor('#20262F')))
    p.drawPath(pfad)
    p.setBrush(KEIN_PINSEL)
