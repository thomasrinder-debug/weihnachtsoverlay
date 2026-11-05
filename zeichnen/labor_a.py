"""Requisiten für die Professor-Szenen der Gruppe Labor A: Schaumberg, Seifenblase,
Explosion, Rakete mit Fallschirm und Fernauslöser, Paddelarm. Alle in Zeichen-Einheiten, Fuß/Boden im Ursprung."""
import math

from PyQt6.QtCore import QPointF, QRectF
from PyQt6.QtGui import QColor, QPainterPath, QTransform

from .grundlagen import (KEIN_PINSEL, KEIN_STIFT, ROT_DUNKEL, ROT_HELL, kreis,
                         linear, radial, stern, stift)
from .labor import METALL, METALL_DUNKEL
from .professor import KOPF_Y, _arm

SCHAUM_HELL = QColor('#FBF1FF')
SCHAUM = QColor('#E6CBF5')
SCHAUM_DUNKEL = QColor('#B892D6')


# ---------------------------------------------------------------- Mütze am Kopf

def muetze_trafo(pose, haare=0.0, vorn=None):
    """Figur-Einheiten der Mütze, wie zeichne_muetze_prof(p, 0, 0) sie erwartet, wenn sie auf dem Kopf sitzt."""
    vorn = pose.kopf_vorn if vorn is None else vorn
    tr = QTransform()
    tr.translate(5, KOPF_Y + pose.hub)
    tr.scale(1.12, 1.12)
    if vorn:
        tr.translate(1, 0)
        tr.rotate(-8)
        tr.scale(-1, 1)
        tr.translate(0, -14 - 22 * haare)
    else:
        tr.translate(-3, -16 - 22 * haare)
    return tr


# ---------------------------------------------------------------- Schaum

def schaum_pfad(b, h, t=0.0):
    """Umriss eines Schaumbergs (Boden mittig im Ursprung)."""
    kuppel = QPainterPath()
    kuppel.moveTo(-b / 2, 0)
    kuppel.cubicTo(-b / 2, -h * 0.75, -b * 0.32, -h, 0, -h)
    kuppel.cubicTo(b * 0.32, -h, b / 2, -h * 0.75, b / 2, 0)
    kuppel.closeSubpath()
    pfad = QPainterPath(kuppel)
    rand = QPainterPath()
    rand.moveTo(-b / 2, 0)
    rand.cubicTo(-b / 2, -h * 0.75, -b * 0.32, -h, 0, -h)
    rand.cubicTo(b * 0.32, -h, b / 2, -h * 0.75, b / 2, 0)
    n = 11
    r0 = max(6.0, min(b, h) * 0.11)
    for k in range(1, n):
        q = rand.pointAtPercent(k / n)
        r = r0 * (0.8 + 0.35 * ((k * 7) % 3) / 2) * (1 + 0.06 * math.sin(t * 4 + k * 1.3))
        blase = QPainterPath()
        blase.addEllipse(QPointF(q.x(), min(q.y() + r * 0.35, -r * 0.6)), r, r)
        pfad = pfad.united(blase)
    return pfad


def zeichne_schaum(p, b, h, t=0.0):
    """Quellender Schaumberg, Boden mittig im Ursprung."""
    if h <= 2 or b <= 2:
        return
    pfad = schaum_pfad(b, h, t)
    p.setPen(KEIN_STIFT)
    p.setBrush(linear(0, -h * 1.05, 0, 0, SCHAUM_HELL, SCHAUM_DUNKEL))
    p.drawPath(pfad)
    p.save()
    p.setClipPath(pfad)
    # Lichtseite und kleine Bläschen
    p.setBrush(radial(-b * 0.18, -h * 0.82, b * 0.45, QColor(255, 255, 255, 150), QColor(255, 255, 255, 0)))
    kreis(p, -b * 0.18, -h * 0.82, b * 0.45)
    p.setPen(stift(QColor(255, 255, 255, 150), 1.1))
    p.setBrush(QColor(255, 255, 255, 40))
    for k in range(int(10 + b * h / 2500)):
        fx = (math.sin(k * 12.9898) * 43758.5453) % 1 - 0.5
        fy = (math.sin(k * 78.233 + 1.7) * 24634.6345) % 1
        r = 2.5 + (k % 4) * 1.4
        kreis(p, fx * b * 0.9, -fy * h * 0.95 + math.sin(t * 3 + k) * 1.5, r)
    p.setPen(KEIN_STIFT)
    p.setBrush(linear(0, -h * 0.3, 0, 0, QColor(150, 110, 190, 0), QColor(150, 110, 190, 70)))
    p.drawRect(QRectF(-b, -h * 0.3, 2 * b, h * 0.32))
    p.restore()
    p.setPen(stift(QColor(255, 255, 255, 200), 1.6))
    p.setBrush(KEIN_PINSEL)
    for k in range(4):
        q = QPointF(-b * 0.3 + k * b * 0.08, -h * 0.9 + abs(k - 1.5) * h * 0.04)
        p.drawArc(QRectF(q.x() - 6, q.y() - 4, 12, 8), 30 * 16, 120 * 16)
    p.setPen(KEIN_STIFT)


def zeichne_seifenblase(p, x, y, r, t=0.0):
    """Große schillernde Blase."""
    if r <= 0.5:
        return
    p.setPen(KEIN_STIFT)
    p.setBrush(radial(x, y, r, QColor(255, 255, 255, 10), QColor(220, 190, 255, 70)))
    kreis(p, x, y, r)
    for k, farbe in enumerate((QColor(255, 140, 210, 150), QColor(120, 220, 255, 150), QColor(255, 230, 120, 140))):
        p.setPen(stift(farbe, 1.6))
        a = (t * 90 + k * 120) % 360
        p.drawArc(QRectF(x - r, y - r, 2 * r, 2 * r), int(a * 16), 80 * 16)
    p.setPen(stift(QColor(255, 255, 255, 160), 1.2))
    p.setBrush(KEIN_PINSEL)
    kreis(p, x, y, r)
    p.setPen(stift(QColor(255, 255, 255, 230), 2.2))
    p.drawArc(QRectF(x - r * 0.7, y - r * 0.7, r * 1.4, r * 1.4), 105 * 16, 50 * 16)
    p.setPen(KEIN_STIFT)
    p.setBrush(QColor(255, 255, 255, 220))
    kreis(p, x - r * 0.42, y - r * 0.42, max(1.0, r * 0.09))


def zeichne_schaumflocke(p, x, y, r):
    p.setPen(KEIN_STIFT)
    p.setBrush(radial(x - r * 0.3, y - r * 0.3, r * 1.3, SCHAUM_HELL, SCHAUM))
    for dx, dy, f in ((0, 0, 1.0), (r * 0.7, r * 0.2, 0.7), (-r * 0.6, r * 0.3, 0.65)):
        kreis(p, x + dx, y + dy, r * f)


# ---------------------------------------------------------------- Explosion

def zeichne_explosion(p, x, y, u, groesse=60):
    """Grelle Explosion, u 0..1 (danach weg)."""
    if not 0 <= u < 1:
        return
    r = groesse * (0.4 + 0.9 * math.sqrt(u))
    a = 1 - u
    p.setPen(KEIN_STIFT)
    p.setBrush(radial(x, y, r * 1.6, QColor(255, 250, 220, int(200 * a)), QColor(255, 160, 60, 0)))
    kreis(p, x, y, r * 1.6)
    zacken = QPainterPath()
    n = 14
    for k in range(2 * n):
        w = k * math.pi / n
        rr = r * (1.0 if k % 2 == 0 else 0.55) * (1 + 0.15 * math.sin(k * 2.3))
        q = QPointF(x + math.cos(w) * rr, y + math.sin(w) * rr)
        zacken.moveTo(q) if k == 0 else zacken.lineTo(q)
    zacken.closeSubpath()
    p.setBrush(radial(x, y, r, QColor(255, 255, 230, int(255 * a)), QColor(255, 140, 40, int(230 * a))))
    p.drawPath(zacken)
    p.setBrush(QColor(255, 255, 255, int(255 * a)))
    kreis(p, x, y, r * 0.35)


# ---------------------------------------------------------------- Rakete

def zeichne_rakete(p, x, y, winkel=0.0, flamme=0.0, t=0.0, zuendschnur=1.0, funke=False):
    """Mini-Rakete, Heck mittig bei (x, y), winkel in Grad (0 = senkrecht)."""
    p.save()
    p.translate(x, y)
    p.rotate(winkel)
    p.setPen(KEIN_STIFT)
    if flamme > 0:
        h = 26 * flamme * (1 + 0.15 * math.sin(t * 40))
        for farbe, b, f in ((QColor(255, 150, 40, 200), 7, 1.0), (QColor(255, 240, 160, 240), 3.5, 0.6)):
            fl = QPainterPath()
            fl.moveTo(-b, -2)
            fl.cubicTo(-b, h * 0.4 * f, -1, h * 0.8 * f, 0, h * f)
            fl.cubicTo(1, h * 0.8 * f, b, h * 0.4 * f, b, -2)
            fl.closeSubpath()
            p.setBrush(farbe)
            p.drawPath(fl)
    if zuendschnur > 0 and flamme <= 0:
        p.setPen(stift(QColor('#4A3A2A'), 1.6))
        p.setBrush(KEIN_PINSEL)
        schnur = QPainterPath()
        schnur.moveTo(0, -1)
        schnur.quadTo(4, 6 * zuendschnur, 9 * zuendschnur, 6 * zuendschnur)
        p.drawPath(schnur)
        p.setPen(KEIN_STIFT)
        if funke:
            p.setBrush(QColor(255, 220, 120, 230))
            stern(p, 9 * zuendschnur, 6 * zuendschnur, 4 + 1.5 * math.sin(t * 40))
    # Flossen
    p.setBrush(linear(-14, 0, 14, 0, ROT_HELL, ROT_DUNKEL))
    for seite in (-1, 1):
        fl = QPainterPath()
        fl.moveTo(seite * 5, -16)
        fl.lineTo(seite * 13, -2)
        fl.lineTo(seite * 13, 2)
        fl.lineTo(seite * 5, -3)
        fl.closeSubpath()
        p.drawPath(fl)
    # Rumpf
    p.setBrush(linear(-6, 0, 6, 0, QColor('#FFFFFF'), QColor('#C8CDD6')))
    p.drawRoundedRect(QRectF(-6, -38, 12, 38), 3, 3)
    p.setBrush(linear(-6, 0, 6, 0, ROT_HELL, ROT_DUNKEL))
    p.drawRect(QRectF(-6, -24, 12, 5))
    p.drawRect(QRectF(-6, -14, 12, 3))
    nase = QPainterPath()
    nase.moveTo(-6, -37)
    nase.cubicTo(-6, -46, -2, -52, 0, -55)
    nase.cubicTo(2, -52, 6, -46, 6, -37)
    nase.closeSubpath()
    p.drawPath(nase)
    p.setBrush(radial(-1, -31, 4, QColor('#BFE8FF'), QColor('#3A78A8')))
    kreis(p, 0, -31, 3)
    p.setBrush(QColor(255, 255, 255, 140))
    p.drawRect(QRectF(-4, -36, 1.6, 30))
    p.setBrush(METALL_DUNKEL)
    p.drawRect(QRectF(-4, -1, 8, 3))
    p.restore()


def zeichne_startrampe(p, x, y):
    """Kleines Startgestell, Fuß mittig bei (x, y)."""
    p.setPen(KEIN_STIFT)
    p.setBrush(linear(x - 18, 0, x + 18, 0, METALL, METALL_DUNKEL))
    p.drawRoundedRect(QRectF(x - 18, y - 5, 36, 5), 2, 2)
    p.setPen(stift(METALL_DUNKEL, 2))
    p.drawLine(QPointF(x - 14, y - 4), QPointF(x - 9, y - 14))
    p.drawLine(QPointF(x + 14, y - 4), QPointF(x + 9, y - 14))
    p.setPen(KEIN_STIFT)
    p.setBrush(QColor('#E3A928'))
    p.drawRect(QRectF(x - 12, y - 6, 24, 2))


def zeichne_fallschirm(p, x, y, offen=1.0, t=0.0):
    """Mini-Fallschirm, die Leinen treffen sich bei (x, y)."""
    if offen <= 0:
        return
    b = 30 * (0.35 + 0.65 * offen)
    h = 38
    top = y - h
    kappe = QPainterPath()
    kappe.moveTo(x - b, top + 8)
    kappe.cubicTo(x - b, top - 14 * offen, x + b, top - 14 * offen, x + b, top + 8)
    for k in range(4, 0, -1):
        x0 = x - b + (k) * b / 2
        kappe.quadTo(x0 - b / 4, top + 3, x0 - b / 2, top + 8)
    kappe.closeSubpath()
    p.setPen(stift(QColor(90, 90, 90, 200), 0.9))
    for k in range(5):
        p.drawLine(QPointF(x - b + k * b / 2, top + 7), QPointF(x, y))
    p.setPen(KEIN_STIFT)
    p.setBrush(linear(x - b, top, x + b, top, QColor('#FFFFFF'), QColor('#D9DEE8')))
    p.drawPath(kappe)
    p.save()
    p.setClipPath(kappe)
    p.setBrush(linear(x - b, top, x + b, top, ROT_HELL, ROT_DUNKEL))
    for k in (-1, 1):
        p.drawRect(QRectF(x + k * b * 0.5 - b * 0.18, top - 20, b * 0.36, 40))
    p.restore()
    p.setPen(stift(QColor(255, 255, 255, 200), 1.4))
    p.setBrush(KEIN_PINSEL)
    p.drawArc(QRectF(x - b * 0.8, top - 6 * offen, b * 0.9, 14), 100 * 16, 60 * 16)
    p.setPen(KEIN_STIFT)


def zeichne_streichholz(p, x, y, winkel=0.0, brennt=True, t=0.0):
    p.save()
    p.translate(x, y)
    p.rotate(winkel)
    p.setPen(KEIN_STIFT)
    p.setBrush(QColor('#E8C88E'))
    p.drawRect(QRectF(-1.3, -16, 2.6, 16))
    p.setBrush(QColor('#B5302A'))
    p.drawEllipse(QPointF(0, -17), 2.4, 3)
    if brennt:
        h = 9 + math.sin(t * 25)
        p.setBrush(QColor(255, 170, 50, 210))
        p.drawEllipse(QRectF(-3.5, -18 - h, 7, h + 2))
        p.setBrush(QColor(255, 245, 190, 240))
        p.drawEllipse(QRectF(-1.6, -17 - h * 0.6, 3.2, h * 0.6 + 1))
    p.restore()


def zeichne_ausloeser(p, x, y, druck=0.0):
    """Fernauslöser mit dickem roten Knopf, Griff mittig bei (x, y); druck 0..1."""
    p.setPen(KEIN_STIFT)
    p.setBrush(linear(x - 13, 0, x + 13, 0, QColor('#6A7280'), QColor('#2E333C')))
    p.drawRoundedRect(QRectF(x - 13, y - 7, 26, 17), 3, 3)
    p.setBrush(QColor('#E3A928'))
    p.drawRect(QRectF(x - 13, y + 4, 26, 3))
    p.setBrush(METALL_DUNKEL)
    p.drawRect(QRectF(x - 7, y - 9, 14, 3))
    kh = 6 * (1 - 0.75 * druck)
    p.setBrush(radial(x - 2, y - 9 - kh, 9, ROT_HELL, ROT_DUNKEL))
    p.drawRect(QRectF(x - 6, y - 8 - kh, 12, kh))
    p.drawEllipse(QRectF(x - 6, y - 11 - kh, 12, 6))
    p.setBrush(QColor(255, 255, 255, 150))
    kreis(p, x - 2.5, y - 9 - kh, 1.6)


def zeichne_paddelarm(p, x, y, winkel):
    """Kittelärmel mit gelbem Handschuh, Schulter bei (x, y), winkel wie Pose.arm_v."""
    p.setPen(KEIN_STIFT)
    _arm(p, x, y, winkel, False)
