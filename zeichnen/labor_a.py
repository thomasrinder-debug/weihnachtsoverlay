"""Requisiten für die Professor-Szenen der Gruppe Labor A: Schaumberg, Seifenblase,
Explosion, Leuchtbommel, Mini-Rakete mit Fallschirm, Schneemaschine, Schneehülle,
lose Brille und Zauberstab. Alle in Zeichen-Einheiten, Fuß/Boden im Ursprung."""
import math

from PyQt6.QtCore import QPointF, QRectF
from PyQt6.QtGui import QColor, QPainterPath, QTransform

from .grundlagen import (GOLD, GOLD_HELL, KEIN_PINSEL, KEIN_STIFT, ROT, ROT_DUNKEL, ROT_HELL, WEISS, kreis,
                         linear, radial, stern, stift)
from .labor import METALL, METALL_DUNKEL
from .professor import BRILLE, KOPF_Y

SCHAUM_HELL = QColor('#FBF1FF')
SCHAUM = QColor('#E6CBF5')
SCHAUM_DUNKEL = QColor('#B892D6')
SCHNEE = QColor('#FBFDFF')
SCHNEE_SCHATTEN = QColor('#C4D8EE')


# ---------------------------------------------------------------- Mütze und Bommel am Kopf

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


def bommel_lokal(pose, haare=0.0):
    """Lage der Mützenbommel in Figur-Einheiten."""
    q = muetze_trafo(pose, haare).map(QPointF(-28 + pose.wipp, -24))
    return q.x(), q.y()


def zeichne_leuchtbommel(p, x, y, staerke, t=0.0):
    """Glühende Bommel mit Lichthof; staerke 0..1."""
    if staerke <= 0:
        return
    puls = 1 + 0.08 * math.sin(t * 9)
    p.setPen(KEIN_STIFT)
    p.setBrush(radial(x, y, 62 * puls, QColor(255, 236, 150, int(min(255, 175 * staerke))), QColor(255, 220, 120, 0)))
    kreis(p, x, y, 62 * puls)
    p.setBrush(radial(x, y, 22, QColor(255, 250, 220, int(min(255, 240 * staerke))), QColor(255, 225, 120, 0)))
    kreis(p, x, y, 18)
    staerke = min(1.0, staerke)
    innen = QColor(255, 255, 240, int(255 * staerke))
    aussen = QColor(255, 214, 90, int(255 * staerke))
    p.setBrush(radial(x - 2, y - 2, 9, innen, aussen))
    for dx, dy in ((0, 0), (-3, -3), (3, -3), (-3, 3), (3, 3)):
        kreis(p, x + dx, y + dy, 5.4)
    p.setBrush(QColor(255, 255, 255, int(230 * staerke)))
    kreis(p, x - 2.5, y - 3, 2.2)
    p.setPen(stift(QColor(255, 240, 170, int(200 * staerke)), 1.6))
    for k in range(8):
        w = k * math.pi / 4 + t * 0.8
        r0, r1 = 13, 19 + 3 * math.sin(t * 7 + k)
        p.drawLine(QPointF(x + math.cos(w) * r0, y + math.sin(w) * r0),
                   QPointF(x + math.cos(w) * r1, y + math.sin(w) * r1))
    p.setPen(KEIN_STIFT)


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


# ---------------------------------------------------------------- Schneemaschine

def zeichne_schneemaschine(p, kurbel=0.0, laeuft=0.0, t=0.0, rueck=False):
    """Schneekanone auf Rädern, Boden mittig im Ursprung. Kurbel an einem Ausleger links
    (KURBEL_ACHSE), die Düse biegt sich nach links oben (DUESE)."""
    p.setPen(KEIN_STIFT)
    p.setBrush(QColor(0, 0, 0, 40))
    p.drawEllipse(QRectF(-40, -3, 80, 6))
    for rx in (-20, 20):
        p.setBrush(radial(rx - 2, -11, 12, QColor('#5A5F6A'), QColor('#22252B')))
        kreis(p, rx, -10, 10)
        p.setBrush(METALL)
        kreis(p, rx, -10, 3)
    # Ausleger für die Kurbel
    ax, ay = KURBEL_ACHSE
    p.setPen(stift(METALL_DUNKEL, 5))
    p.drawLine(QPointF(-26, -60), QPointF(ax, ay + 4))
    p.setPen(stift(METALL, 2))
    p.drawLine(QPointF(-26, -61), QPointF(ax, ay + 3))
    p.setPen(KEIN_STIFT)
    # Gehäuse
    p.setBrush(linear(-32, -100, 32, -16, QColor('#8BCDF0'), QColor('#2E77A8')))
    p.drawRoundedRect(QRectF(-30, -100, 60, 84), 8, 8)
    p.setBrush(QColor(255, 255, 255, 90))
    p.drawRoundedRect(QRectF(-26, -96, 9, 74), 4, 4)
    p.setPen(stift(WEISS, 2.2))
    for k in range(3):
        w = math.radians(k * 60 + t * 90 * laeuft * (-1 if rueck else 1))
        p.drawLine(QPointF(6 - math.cos(w) * 12, -56 - math.sin(w) * 12),
                   QPointF(6 + math.cos(w) * 12, -56 + math.sin(w) * 12))
    p.setPen(KEIN_STIFT)
    an = QColor('#FF5A4A') if rueck else QColor('#7CFF8A')
    p.setBrush(an if laeuft > 0 and (t * 4) % 1 < 0.6 else QColor('#3E5560'))
    kreis(p, 20, -88, 3.5)
    p.setBrush(QColor(255, 255, 255, 230))
    for k in range(3):
        kreis(p, -12 + k * 10, -100 + abs(k - 1) * 1.5, 5)
    # Düse nach links oben
    wackel = math.sin(t * 30) * 1.2 * laeuft
    duese = QPainterPath()
    duese.moveTo(-16, -98)
    duese.cubicTo(-16, -128, -22, -146, -38, -158 + wackel)
    duese.lineTo(-44, -146 + wackel)
    duese.cubicTo(-30, -138, 2, -126, 6, -98)
    duese.closeSubpath()
    p.setBrush(linear(-44, -150, 6, -100, QColor('#E9EEF3'), METALL_DUNKEL))
    p.drawPath(duese)
    p.save()
    p.translate(DUESE[0], DUESE[1] + wackel)
    p.rotate(-30)
    p.setBrush(METALL_DUNKEL)
    p.drawEllipse(QPointF(0, 0), 5, 9)
    p.setBrush(QColor('#2C3138'))
    p.drawEllipse(QPointF(-1, 0), 3, 6.5)
    p.restore()
    # Kurbel
    p.setBrush(METALL_DUNKEL)
    kreis(p, ax, ay, 6)
    w = math.radians(kurbel)
    kx, ky = ax + math.cos(w) * KURBEL_R, ay + math.sin(w) * KURBEL_R
    p.setPen(stift(METALL_DUNKEL, 4))
    p.drawLine(QPointF(ax, ay), QPointF(kx, ky))
    p.setPen(KEIN_STIFT)
    p.setBrush(linear(kx - 4, ky, kx + 4, ky, ROT_HELL, ROT_DUNKEL))
    p.drawRoundedRect(QRectF(kx - 3.5, ky - 7, 7, 14), 3, 3)
    p.setBrush(METALL)
    kreis(p, ax, ay, 2.5)


KURBEL_ACHSE = (-44, -98)
KURBEL_R = 14
DUESE = (-41, -152)


def kurbel_griff(kurbel):
    w = math.radians(kurbel)
    return KURBEL_ACHSE[0] + math.cos(w) * KURBEL_R, KURBEL_ACHSE[1] + math.sin(w) * KURBEL_R


def _schnee_kugel(p, x, y, r):
    p.setBrush(radial(x - r * 0.35, y - r * 0.4, r * 1.35, SCHNEE, SCHNEE_SCHATTEN))
    kreis(p, x, y, r)


KUGELN = ((2, -46, 58), (0, -124, 48), (2, -192, 44), (-26, -200, 32), (-14, -226, 28))


def schneehuelle_pfad(arm=True):
    """Schneemann um den Professor in Figur-Einheiten (Blick nach rechts)."""
    pfad = QPainterPath()
    for x, y, r in KUGELN:
        pfad.addEllipse(QPointF(x, y), r, r)
    if arm:
        pfad.addEllipse(QPointF(34, -118), 26, 22)
    return pfad.simplified()


def zeichne_schneehuelle(p, hoehe, oben_ab=0.0, arm=True, gesicht=0.0, t=0.0):
    """Schnee wächst vom Boden bis 'hoehe' (Einheiten über dem Fuß); oben_ab schmilzt von oben bis zu dieser
    Höhe zurück (0: nichts). gesicht 0..1: Brille und Nase auf der Schneekugel."""
    if hoehe <= 0:
        return
    pfad = schneehuelle_pfad(arm)
    p.save()
    p.setPen(KEIN_STIFT)
    oben = -hoehe
    if oben_ab:
        oben = max(oben, -oben_ab)
    p.setClipRect(QRectF(-120, oben, 240, -oben + 4))
    p.setBrush(linear(0, -230, 0, 0, SCHNEE, SCHNEE_SCHATTEN))
    p.drawPath(pfad)
    for x, y, r in KUGELN:
        p.setBrush(radial(x - r * 0.4, y - r * 0.45, r * 0.9, QColor(255, 255, 255, 200), QColor(255, 255, 255, 0)))
        kreis(p, x - r * 0.3, y - r * 0.35, r * 0.7)
    # Schneerand oben: Klumpen
    if oben > -232:
        for k in range(7):
            kx = -50 + k * 16 + math.sin(k * 2.1) * 4
            if pfad.contains(QPointF(kx, oben + 3)):
                _schnee_kugel(p, kx, oben + 2, 9)
    p.setBrush(QColor(255, 255, 255, 230))
    for k in range(6):
        stern(p, -30 + k * 13, -30 - ((k * 37) % 180), 2.2 + math.sin(t * 6 + k))
    if gesicht > 0 and oben < -200:
        p.setPen(stift(QColor(BRILLE.red(), BRILLE.green(), BRILLE.blue(), int(255 * gesicht)), 2.4))
        p.setBrush(QColor(200, 230, 255, int(60 * gesicht)))
        kreis(p, 22, -194, 10)
        p.drawLine(QPointF(12, -195), QPointF(-8, -192))
        p.setPen(KEIN_STIFT)
        p.setBrush(QColor(242, 164, 143, int(255 * gesicht)))
        p.drawEllipse(QPointF(34, -186), 7, 6)
        p.setBrush(QColor(40, 36, 34, int(255 * gesicht)))
        for k in range(4):
            kreis(p, 12 + k * 6, -168 + abs(k - 1.5) * 1.5, 1.8)
    p.restore()


def zeichne_schneeball_po(p, groesse=1.0, t=0.0, dreh=0.0):
    """Schneekugel um den Hintern (Figur-Einheiten)."""
    r = 36 * groesse
    x, y = -30, -72
    p.setPen(KEIN_STIFT)
    _schnee_kugel(p, x, y, r)
    p.save()
    p.translate(x, y)
    p.rotate(dreh)
    p.setBrush(QColor(255, 255, 255, 200))
    for k in range(5):
        w = k * 1.25
        stern(p, math.cos(w) * r * 0.55, math.sin(w) * r * 0.55, 2.2 + math.sin(t * 6 + k))
    p.setBrush(QColor(170, 195, 225, 110))
    for k in range(4):
        w = k * 1.6 + 0.4
        kreis(p, math.cos(w) * r * 0.7, math.sin(w) * r * 0.7, 3)
    p.restore()


# ---------------------------------------------------------------- Brille und Zauberstab

def zeichne_brille(p, x, y, winkel=0.0, r=9.5):
    """Runde Brille des Professors allein, Steg bei (x, y)."""
    p.save()
    p.translate(x, y)
    p.rotate(winkel)
    p.setPen(KEIN_STIFT)
    for seite in (-1, 1):
        p.setBrush(QColor(200, 230, 255, 70))
        kreis(p, seite * (r + 1), 0, r)
    p.setPen(stift(BRILLE, 2.2))
    p.setBrush(KEIN_PINSEL)
    for seite in (-1, 1):
        kreis(p, seite * (r + 1), 0, r)
    p.drawLine(QPointF(-1.5, -1), QPointF(1.5, -1))
    p.drawLine(QPointF(-2 * r - 1, -1), QPointF(-2 * r - 6, -4))
    p.drawLine(QPointF(2 * r + 1, -1), QPointF(2 * r + 6, -4))
    p.setPen(stift(QColor(255, 255, 255, 190), 1.4))
    for seite in (-1, 1):
        cx = seite * (r + 1)
        p.drawArc(QRectF(cx - r * 0.7, -r * 0.7, r * 1.4, r * 1.4), 100 * 16, 60 * 16)
    p.setPen(KEIN_STIFT)
    p.restore()


def zeichne_zauberstab(p, x, y, winkel=0.0, funkeln=0.0, t=0.0):
    """Elektrode mit Messingkugel, Griff bei (x, y), zeigt bei winkel 0 nach oben."""
    p.save()
    p.translate(x, y)
    p.rotate(winkel)
    p.setPen(KEIN_STIFT)
    p.setBrush(linear(-3, 0, 3, 0, QColor('#3B3B44'), QColor('#15151A')))
    p.drawRoundedRect(QRectF(-3, -8, 6, 16), 2, 2)
    p.setBrush(linear(-2, 0, 2, 0, METALL, METALL_DUNKEL))
    p.drawRect(QRectF(-1.6, -30, 3.2, 23))
    p.setBrush(radial(-1.5, -34, 6, GOLD_HELL, GOLD))
    kreis(p, 0, -33, 4.5)
    if funkeln > 0:
        p.setBrush(radial(0, -33, 16, QColor(190, 230, 255, int(200 * funkeln)), QColor(190, 230, 255, 0)))
        kreis(p, 0, -33, 16)
        p.setBrush(QColor(255, 255, 255, int(230 * funkeln)))
        stern(p, 0, -33, 6 + 2 * math.sin(t * 30))
    p.restore()


def zeichne_sternchen_kreis(p, x, y, r, t):
    """Kreisende Sternchen über einem benommenen Kopf."""
    p.setPen(KEIN_STIFT)
    for k in range(4):
        w = t * 5 + k * math.pi / 2
        p.setBrush(GOLD_HELL if k % 2 else WEISS)
        stern(p, x + math.cos(w) * r, y + math.sin(w) * r * 0.35, 4.5)


def zeichne_kippschalter(p, x, y, an):
    """Kleiner Schaltkasten mit Hebel, Fuß mittig bei (x, y)."""
    p.setPen(KEIN_STIFT)
    p.setBrush(linear(x - 9, 0, x + 9, 0, QColor('#3E434C'), QColor('#1E2126')))
    p.drawRoundedRect(QRectF(x - 9, y - 14, 18, 14), 2, 2)
    p.setBrush(QColor('#7CFF8A') if an else QColor('#5A2A2A'))
    kreis(p, x + 5, y - 10, 2)
    w = math.radians(-30 if an else 30)
    p.setPen(stift(METALL, 2.4))
    p.drawLine(QPointF(x - 2, y - 7), QPointF(x - 2 + math.sin(w) * 10, y - 7 - math.cos(w) * 10))
    p.setPen(KEIN_STIFT)
    p.setBrush(ROT)
    kreis(p, x - 2 + math.sin(w) * 10, y - 7 - math.cos(w) * 10, 2.6)


def zeichne_kabel_bogen(p, x0, y0, x1, y1, durch=12):
    p.setPen(stift(QColor('#2E2E2E'), 2.2))
    p.setBrush(KEIN_PINSEL)
    k = QPainterPath()
    k.moveTo(x0, y0)
    k.quadTo((x0 + x1) / 2, max(y0, y1) + durch, x1, y1)
    p.drawPath(k)
    p.setPen(KEIN_STIFT)

