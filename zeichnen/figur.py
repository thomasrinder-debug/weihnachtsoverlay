"""Der Weihnachtsmann: Posen, Kopf seitlich und von vorn, Arme, Beine, Sack."""

import math
from dataclasses import dataclass

from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import QColor, QPainterPath, QPen

from .grundlagen import *  # noqa: F401,F403  Farben und Hilfen


@dataclass
class Pose:
    bein_v: float = 0.0       # Winkel vorderes Bein (negativ = nach vorn)
    bein_h: float = 0.0
    arm_v: float = 0.0        # Winkel vorderer Arm (-90 = waagerecht nach vorn, -180 = nach oben)
    arm_h: float = 0.0
    arm_v_x: float = 10.0     # Schulterposition vorderer Arm
    hub: float = 0.0          # Auf und Ab beim Gehen
    wipp: float = 0.0         # Mützenspitze
    sack: bool = True
    sitzt: bool = False
    auge_zu: bool = False
    mund_offen: bool = False
    kopf_vorn: bool = False   # schaut das Publikum an
    blick_x: float = 0.0
    blick_y: float = 0.0
    schreck: float = 0.0      # 0..1: große Augen, offener Mund
    sorge: float = 0.0        # 0..1: ängstlich hochgezogene Brauen


def geh_pose(phase, t):
    sw = math.sin(phase)
    return Pose(bein_v=-22 * sw, bein_h=22 * sw, arm_v=25 * sw, arm_h=-25 * sw,
                hub=-abs(math.cos(phase)) * 4, wipp=math.sin(phase * 2) * 3, auge_zu=blinzeln(t))


def renn_pose(phase):
    sw = math.sin(phase)
    return Pose(bein_v=-38 * sw, bein_h=38 * sw, arm_v=55 * sw, arm_h=-55 * sw,
                hub=-abs(math.cos(phase)) * 6, wipp=math.sin(phase * 2) * 7, mund_offen=True)


def winke_pose(wt, t):
    return Pose(arm_v=-125 + 20 * math.sin(wt * 9), arm_v_x=26, wipp=math.sin(wt * 6) * 3,
                auge_zu=blinzeln(t), mund_offen=wt < 1.6 and (wt * 5) % 2 < 1)


def zeichne_bein(p, y, winkel, hinten):
    d = 128 if hinten else 100
    p.save()
    p.translate(0, y)
    p.rotate(winkel)
    p.setPen(KEIN_STIFT)
    p.setBrush(linear(-12, 0, 12, 0, ROT_HELL.darker(d), ROT_DUNKEL.darker(d)))
    p.drawRoundedRect(QRectF(-12, -4, 24, 50), 9, 9)
    stiefel = QPainterPath()
    stiefel.addRoundedRect(QRectF(-13, 44, 22, 20), 6, 6)
    stiefel.addRoundedRect(QRectF(-13, 52, 34, 13), 6.5, 6.5)
    p.setBrush(linear(0, 44, 0, 66, QColor('#444444').darker(d), SCHWARZ.darker(d)))
    p.drawPath(stiefel.simplified())
    p.setBrush(QColor('#4A3426').darker(d))
    p.drawRoundedRect(QRectF(-14, 62, 36, 4.5), 2, 2)
    p.setBrush(QColor(255, 255, 255, 55))
    p.drawEllipse(QRectF(7, 54, 10, 4))
    flausch(p, [(x, 43) for x in (-10, -4, 2, 8)], 5, not hinten)
    p.restore()


def zeichne_arm(p, x, y, winkel, hinten):
    d = 128 if hinten else 100
    p.save()
    p.translate(x, y)
    p.rotate(winkel)
    p.setPen(KEIN_STIFT)
    p.setBrush(linear(-10, 0, 10, 0, ROT_HELL.darker(d), ROT_DUNKEL.darker(d)))
    p.drawRoundedRect(QRectF(-10, -6, 20, 50), 9, 9)
    p.setBrush(radial(-3, 53, 14, GRUEN.lighter(135).darker(d), GRUEN_DUNKEL.darker(d)))
    p.drawEllipse(QPointF(0, 56), 10, 11)
    p.drawEllipse(QPointF(8, 50), 4, 6.5)
    flausch(p, [(-8, 44), (-3, 45), (3, 45), (8, 44)], 4.5)
    p.restore()


def zeichne_sack(p, x, y, winkel, groesse=1.0):
    p.save()
    p.translate(x, y)
    p.rotate(winkel)
    p.scale(groesse, groesse)
    # Zuckerstange
    stange = QPainterPath()
    stange.moveTo(10, -28)
    stange.lineTo(10, -58)
    stange.cubicTo(10, -72, 26, -72, 26, -60)
    p.setBrush(KEIN_PINSEL)
    p.setPen(QPen(WEISS, 7, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
    p.drawPath(stange)
    streifen = QPen(ROT, 7, Qt.PenStyle.CustomDashLine, Qt.PenCapStyle.FlatCap)
    streifen.setDashPattern([0.8, 0.8])
    p.setPen(streifen)
    p.drawPath(stange)
    p.setPen(KEIN_STIFT)
    # Geschenk
    p.save()
    p.translate(-12, -40)
    p.rotate(-14)
    p.setBrush(linear(-12, 0, 12, 0, GRUEN.lighter(120), GRUEN_DUNKEL))
    p.drawRect(QRectF(-12, -12, 24, 22))
    p.setBrush(GOLD)
    p.drawRect(QRectF(-3, -12, 6, 22))
    p.drawRect(QRectF(-12, -4, 24, 5))
    p.drawEllipse(QPointF(-5, -15), 5, 3.5)
    p.drawEllipse(QPointF(5, -15), 5, 3.5)
    p.restore()
    # Sack
    p.setBrush(radial(-10, -6, 62, SACK_HELL, SACK_DUNKEL))
    p.drawEllipse(QRectF(-38, -34, 76, 84))
    hals = QPainterPath()
    hals.moveTo(-15, -28)
    hals.lineTo(15, -28)
    hals.lineTo(9, -40)
    hals.lineTo(-9, -40)
    hals.closeSubpath()
    p.setBrush(SACK_DUNKEL)
    p.drawPath(hals)
    p.setBrush(QColor('#D9B272'))
    p.drawRoundedRect(QRectF(-13, -34, 26, 6), 3, 3)
    # Flicken mit Naht
    p.save()
    p.translate(-14, 16)
    p.rotate(8)
    p.setBrush(QColor('#C4955E'))
    p.drawRect(QRectF(-9, -8, 18, 16))
    p.setPen(QPen(QColor('#5A3818'), 1.4, Qt.PenStyle.DashLine))
    p.setBrush(KEIN_PINSEL)
    p.drawRect(QRectF(-7, -6, 14, 12))
    p.restore()
    # Falten
    falten = QPainterPath()
    falten.moveTo(-6, -26)
    falten.quadTo(-14, 0, -8, 30)
    falten.moveTo(8, -26)
    falten.quadTo(16, 4, 14, 24)
    p.setPen(stift(QColor(60, 35, 15, 90), 2))
    p.setBrush(KEIN_PINSEL)
    p.drawPath(falten)
    p.setPen(KEIN_STIFT)
    p.restore()


def zeichne_rumpf(p, h):
    pfad = QPainterPath()
    pfad.addEllipse(QRectF(-48, -162 + h, 96, 108))
    p.setBrush(radial(-8, -132 + h, 88, ROT_HELL, ROT_DUNKEL))
    p.drawPath(pfad)
    p.save()
    p.setClipPath(pfad)
    p.setBrush(SCHWARZ)
    p.drawRect(QRectF(-60, -113 + h, 120, 14))
    p.setBrush(QColor(255, 255, 255, 45))
    p.drawRect(QRectF(-60, -112 + h, 120, 3))
    p.setBrush(WEISS)
    p.drawRect(QRectF(-60, -70 + h, 120, 30))
    p.restore()
    flausch(p, [(-32 + 6.4 * i, -70 + h) for i in range(11)], 4.5)
    flausch(p, [(x, -108 + h + 54 * math.sqrt(max(0.0, 1 - (x / 48) ** 2)) - 3) for x in range(-42, 43, 6)], 5.5)
    p.setBrush(linear(0, -116 + h, 0, -96 + h, GOLD_HELL, GOLD))
    p.drawRoundedRect(QRectF(29, -116 + h, 17, 18), 3, 3)
    p.setBrush(SCHWARZ)
    p.drawRect(QRectF(33.5, -111.5 + h, 8, 9))


def zeichne_kopf(p, pose, hy):
    flausch(p, [(-14, hy - 8), (-18, hy + 2), (-16, hy + 12), (-10, hy + 18)], 8)
    p.setBrush(HAUT_DUNKEL)
    p.drawEllipse(QPointF(-6, hy - 1), 6, 8)
    p.setBrush(radial(16, hy - 8, 36, HAUT, HAUT_DUNKEL))
    kreis(p, 8, hy, 28)
    p.setBrush(radial(20, hy + 6, 10, QColor(240, 110, 110, 170), QColor(240, 110, 110, 0)))
    kreis(p, 20, hy + 6, 10)
    if pose.auge_zu:
        lid = QPainterPath()
        lid.moveTo(20, hy - 6)
        lid.quadTo(24, hy - 3, 28, hy - 6)
        p.setPen(stift(SCHWARZ, 2.2))
        p.setBrush(KEIN_PINSEL)
        p.drawPath(lid)
        p.setPen(KEIN_STIFT)
    else:
        p.setBrush(SCHWARZ)
        p.drawEllipse(QPointF(24, hy - 6), 3.6, 4.6)
        p.setBrush(WEISS)
        kreis(p, 25.3, hy - 7.8, 1.3)
    flausch(p, [(20, hy - 14), (25, hy - 15), (30, hy - 13)], 3.2, False)
    # Bart mit lockigem Rand
    bart = QPainterPath()
    bart.moveTo(-8, hy + 2)
    bart.cubicTo(-14, hy + 40, 2, hy + 62, 22, hy + 58)
    bart.cubicTo(42, hy + 52, 46, hy + 28, 38, hy + 10)
    bart.quadTo(14, hy + 24, -8, hy + 2)
    p.setBrush(WEISS)
    p.drawPath(bart)
    flausch(p, [(-6, hy + 18), (-3, hy + 32), (4, hy + 44), (14, hy + 52), (25, hy + 54),
                (34, hy + 47), (40, hy + 36), (42, hy + 23)], 8)
    if pose.mund_offen:
        p.setBrush(QColor('#7A1F1F'))
        p.drawEllipse(QPointF(31, hy + 19), 4.5, 5.5)
    flausch(p, [(20, hy + 11), (27, hy + 13), (34, hy + 12), (40, hy + 9)], 6)
    p.setBrush(radial(34, hy + 1, 8, QColor('#F59185'), QColor('#C94A3E')))
    p.drawEllipse(QPointF(36, hy + 3), 6.5, 6)
    p.setBrush(QColor(255, 255, 255, 150))
    kreis(p, 34, hy + 0.5, 1.6)
    # Mütze
    w = pose.wipp
    muetze = QPainterPath()
    muetze.moveTo(-22, hy - 16)
    muetze.lineTo(36, hy - 16)
    muetze.cubicTo(32, hy - 56, -6, hy - 70, -40 + w, hy - 40)
    muetze.cubicTo(-30, hy - 46, -22, hy - 32, -22, hy - 16)
    p.setBrush(linear(-30, hy - 60, 30, hy - 16, ROT_HELL, ROT_DUNKEL))
    p.drawPath(muetze)
    flausch(p, [(x, hy - 17) for x in range(-24, 41, 7)], 7.5)
    tx, ty = -42 + w, hy - 38
    flausch(p, [(tx + dx, ty + dy) for dx, dy in ((0, 0), (-4, -3), (4, -3), (-3, 4), (4, 3))], 6)


def zeichne_weihnachtsmann(p, pose, zwischen=None):
    """Fußpunkt im Ursprung, Blick nach rechts. zwischen(p) wird vor dem
    vorderen Arm aufgerufen, etwa für ein Seil, das er umklammert."""
    h = pose.hub
    p.setPen(KEIN_STIFT)
    if pose.sack:
        zeichne_sack(p, -56, -134 + h, -12)
    zeichne_arm(p, -10, -140 + h, pose.arm_h, True)
    if not pose.sitzt:
        zeichne_bein(p, -68 + h, pose.bein_h, True)
        zeichne_bein(p, -68 + h, pose.bein_v, False)
    zeichne_rumpf(p, h)
    # Ein hochgereckter Arm liegt hinter dem Kopf, sonst verdeckt er das Gesicht.
    arm_hinter_kopf = pose.arm_v < -150
    if arm_hinter_kopf:
        zeichne_arm(p, pose.arm_v_x, -140 + h, pose.arm_v, False)
    if pose.kopf_vorn:
        zeichne_kopf_vorn(p, 6, -188 + h, (pose.blick_x, pose.blick_y), pose.schreck, pose.sorge,
                          pose.auge_zu, pose.wipp)
    else:
        zeichne_kopf(p, pose, -186 + h)
    if zwischen:
        zwischen(p)
    if not arm_hinter_kopf:
        zeichne_arm(p, pose.arm_v_x, -140 + h, pose.arm_v, False)


def figur(p, x, y, s, richtung, pose, zwischen=None, stauchen=1.0, neigung=0.0):
    p.save()
    p.translate(x, y)
    p.rotate(neigung * richtung)
    p.scale(s * richtung * (2 - stauchen), s * stauchen)
    zeichne_weihnachtsmann(p, pose, zwischen)
    p.restore()


def figur_kasten(x, y, s):
    return QRectF(x - 120 * s, y - 280 * s, 240 * s, 288 * s)


def zeichne_kopf_vorn(p, x, y, blick=(0.0, 0.0), schreck=0.0, sorge=0.0, zu=False, wipp=0.0):
    """Kopf von vorn, Mitte im Punkt (x, y), schaut die Zuschauer an."""
    p.save()
    p.translate(x, y)
    p.setPen(KEIN_STIFT)
    flausch(p, [(-27, 2), (-29, 12), (-25, 22), (27, 2), (29, 12), (25, 22)], 8)
    p.setBrush(HAUT_DUNKEL)
    p.drawEllipse(QPointF(-28, 0), 5.5, 8)
    p.drawEllipse(QPointF(28, 0), 5.5, 8)
    p.setBrush(radial(-6, -8, 40, HAUT, HAUT_DUNKEL))
    kreis(p, 0, 0, 28)
    for cx in (-17, 17):
        p.setBrush(radial(cx, 7, 9, QColor(240, 110, 110, 170), QColor(240, 110, 110, 0)))
        kreis(p, cx, 7, 9)
    g = 1 + 0.35 * schreck
    for ax in (-10, 10):
        if zu:
            lid = QPainterPath()
            lid.moveTo(ax - 5, -6)
            lid.quadTo(ax, -3, ax + 5, -6)
            p.setPen(stift(SCHWARZ, 2.2))
            p.setBrush(KEIN_PINSEL)
            p.drawPath(lid)
            p.setPen(KEIN_STIFT)
        else:
            p.setBrush(WEISS)
            p.drawEllipse(QPointF(ax, -6), 6 * g, 7.5 * g)
            px, py = ax + blick[0] * 2.6 * g, -6 + blick[1] * 3 * g
            p.setBrush(SCHWARZ)
            kreis(p, px, py, 3.6 * (1 - 0.3 * schreck))
            p.setBrush(WEISS)
            kreis(p, px + 1.2, py - 1.4, 1.2)
    for seite in (-1, 1):
        p.save()
        p.translate(seite * 10, -17 - 5 * schreck)
        p.rotate(seite * 18 * sorge)
        flausch(p, [(-4.5, 0), (0, -1), (4.5, 0)], 3.2, False)
        p.restore()
    bart = QPainterPath()
    bart.moveTo(-27, 4)
    bart.cubicTo(-32, 40, -12, 56, 0, 56)
    bart.cubicTo(12, 56, 32, 40, 27, 4)
    bart.quadTo(0, 24, -27, 4)
    p.setBrush(WEISS)
    p.drawPath(bart)
    flausch(p, [(-26, 14), (-25, 28), (-18, 40), (-9, 48), (0, 51), (9, 48), (18, 40), (25, 28), (26, 14)], 8)
    if schreck > 0.2:
        p.setBrush(QColor('#6E1A1A'))
        p.drawEllipse(QPointF(0, 22), 4.5, 3 + 4 * schreck)
    flausch(p, [(-16, 12), (-9, 14), (-3, 13), (3, 13), (9, 14), (16, 12)], 5.5)
    p.setBrush(radial(-2, 2, 9, QColor('#F59185'), QColor('#C94A3E')))
    kreis(p, 0, 4, 6.5)
    p.setBrush(QColor(255, 255, 255, 150))
    kreis(p, -2, 1.5, 1.6)
    muetze = QPainterPath()
    muetze.moveTo(-30, -20)
    muetze.cubicTo(-28, -62, 22, -76, 44 + wipp, -46)
    muetze.cubicTo(34, -50, 28, -40, 30, -20)
    muetze.closeSubpath()
    p.setBrush(linear(-30, -70, 30, -20, ROT_HELL, ROT_DUNKEL))
    p.drawPath(muetze)
    flausch(p, [(x, -21) for x in range(-30, 31, 6)], 7.5)
    tx, ty = 46 + wipp, -44
    flausch(p, [(tx + dx, ty + dy) for dx, dy in ((0, 0), (-4, -3), (4, -3), (-3, 4), (4, 3))], 6)
    p.restore()


def zeichne_schreckstriche(p, x, y, s):
    """Drei kleine Striche über dem Kopf: Huch!"""
    p.setPen(stift(ROT_DUNKEL, 3 * s))
    for w in (-55, -90, -125):
        r = math.radians(w)
        p.drawLine(QPointF(x + math.cos(r) * 10 * s, y + math.sin(r) * 10 * s),
                   QPointF(x + math.cos(r) * 24 * s, y + math.sin(r) * 24 * s))
    p.setPen(KEIN_STIFT)


def zeichne_tropfen(p, x, y):
    tropfen = QPainterPath()
    tropfen.moveTo(x, y - 7)
    tropfen.cubicTo(x + 5, y - 1, x + 5, y + 5, x, y + 5)
    tropfen.cubicTo(x - 5, y + 5, x - 5, y - 1, x, y - 7)
    p.setBrush(radial(x - 1.5, y, 7, QColor(235, 248, 255, 240), QColor(120, 185, 235, 220)))
    p.drawPath(tropfen)


def zeichne_faeustling_vorn(p, x, y):
    """Fäustling von vorn, der sich an einer Kante festhält."""
    p.setBrush(radial(x - 3, y - 3, 14, GRUEN.lighter(135), GRUEN_DUNKEL))
    p.drawEllipse(QPointF(x, y), 12, 10)
    p.setBrush(GRUEN_DUNKEL)
    for dx in (-6, 0, 6):
        p.drawEllipse(QPointF(x + dx, y - 7), 3.6, 3.2)
    flausch(p, [(x - 9, y + 9), (x - 3, y + 10), (x + 3, y + 10), (x + 9, y + 9)], 4.5)


def segment(p, ax, ay, bx, by, breite, hell, dunkel):
    laenge = math.hypot(bx - ax, by - ay)
    p.save()
    p.translate(ax, ay)
    p.rotate(math.degrees(math.atan2(by - ay, bx - ax)))
    p.setBrush(linear(0, -breite / 2, 0, breite / 2, hell, dunkel))
    p.drawRoundedRect(QRectF(-breite / 2, -breite / 2, laenge + breite, breite), breite / 2, breite / 2)
    p.restore()


def zeichne_bein_ik(p, hx, hy, fx, fy, hinten):
    """Bein mit Knie zwischen Hüfte und Fuß, Knie zeigt nach vorn."""
    l1 = l2 = 38
    d = min(math.hypot(fx - hx, fy - hy), l1 + l2 - 0.5)
    basis = math.atan2(fy - hy, fx - hx)
    a = math.acos(max(-1.0, min(1.0, (l1 * l1 + d * d - l2 * l2) / (2 * l1 * d))))
    kx, ky = hx + l1 * math.cos(basis - a), hy + l1 * math.sin(basis - a)
    k = 128 if hinten else 100
    segment(p, hx, hy, kx, ky, 24, ROT_HELL.darker(k), ROT_DUNKEL.darker(k))
    segment(p, kx, ky, fx, fy - 6, 22, ROT_HELL.darker(k), ROT_DUNKEL.darker(k))
    p.setBrush(linear(0, fy - 10, 0, fy + 4, QColor('#444444').darker(k), SCHWARZ.darker(k)))
    p.drawRoundedRect(QRectF(fx - 11, fy - 10, 30, 14), 6, 6)
    p.setBrush(QColor('#4A3426').darker(k))
    p.drawRoundedRect(QRectF(fx - 12, fy + 2, 32, 4), 2, 2)
    flausch(p, [(fx - 9, fy - 12), (fx - 3, fy - 13), (fx + 3, fy - 13), (fx + 9, fy - 12)], 4.8, not hinten)
