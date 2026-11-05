"""Requisiten für die Computer-Szenen des Professors (er haut seinen Rechner kaputt):
Rollwagen, Röhrenmonitor in Einzelteilen (Fuß, Gehäuse, Schirm), Trümmer mit
einfacher Physik (Tasten, Turmteile, Schrauben), Ladekringel als Rad, Kabelknäuel,
Wicklungen um die Figur und eine Kabelschleife.

Einheiten wie in labor.py, Boden mittig im Ursprung.
"""
import math
import random

from PyQt6.QtCore import QPointF, QRectF
from PyQt6.QtGui import QColor, QPainterPath

from .grundlagen import *  # noqa: F401,F403  Farben und Hilfen
from .labor import BEIGE, BEIGE_DUNKEL, METALL, METALL_DUNKEL, zeichne_hammer, zeichne_taste, zeichne_tastatur

MON = 1.5            # Röhrenmonitor auf dem Wagen, vergrößert
WAGEN_B, WAGEN_H = 104, 66
WAGEN_OBEN = WAGEN_H + 6   # Oberkante der Platte
TURM = 1.8           # Rechnerturm, vergrößert
SCHIRM = QRectF(-27, -72, 54, 44)


# ---------------------------------------------------------------- Rollwagen

def zeichne_rollwagen(p, x, y, roll=0.0, b=WAGEN_B, h=WAGEN_H):
    """Metallwagen mit zwei Böden und Rollen; roll dreht die Rollen (Bogenmaß)."""
    p.setPen(KEIN_STIFT)
    p.setBrush(QColor(0, 0, 0, 45))
    p.drawEllipse(QRectF(x - b * 0.55, y - 3, b * 1.1, 6))
    for sx in (-1, 1):
        xx = x + sx * (b / 2 - 7)
        p.setBrush(linear(xx - 2.5, 0, xx + 2.5, 0, METALL.lighter(110), METALL_DUNKEL))
        p.drawRect(QRectF(xx - 2.5, y - h, 5, h - 9))
    p.setBrush(linear(0, y - 30, 0, y - 24, METALL.lighter(110), METALL_DUNKEL))
    p.drawRoundedRect(QRectF(x - b / 2 + 3, y - 30, b - 6, 5), 2, 2)
    p.setBrush(linear(0, y - h - 6, 0, y - h + 2, METALL.lighter(125), METALL_DUNKEL))
    p.drawRoundedRect(QRectF(x - b / 2, y - h - 6, b, 8), 2.5, 2.5)
    p.setBrush(QColor(255, 255, 255, 90))
    p.drawRect(QRectF(x - b / 2 + 4, y - h - 5, b - 8, 1.5))
    for sx in (-1, 1):
        rx = x + sx * (b / 2 - 7)
        p.setBrush(radial(rx - 1.5, y - 7.5, 7, QColor('#5A5A5A'), QColor('#1E1E1E')))
        kreis(p, rx, y - 6, 6)
        p.setBrush(METALL)
        kreis(p, rx, y - 6, 2)
        p.setPen(stift(QColor(170, 170, 170, 170), 1.2))
        for k in range(2):
            w = roll + k * math.pi
            p.drawLine(QPointF(rx + math.cos(w) * 2.5, y - 6 + math.sin(w) * 2.5),
                       QPointF(rx + math.cos(w) * 5, y - 6 + math.sin(w) * 5))
        p.setPen(KEIN_STIFT)


# ---------------------------------------------------------------- Röhrenmonitor in Teilen

def _rahmen_pfad():
    aussen = QPainterPath()
    aussen.addRoundedRect(QRectF(-34, -78, 68, 62), 6, 6)
    loch = QPainterPath()
    loch.addRoundedRect(SCHIRM, 8, 8)
    return aussen.subtracted(loch)


def zeichne_monitor_fuss(p):
    p.setPen(KEIN_STIFT)
    p.setBrush(QColor('#2B2B2B'))
    p.drawRect(QRectF(-3, -30, 6, 17))
    p.setBrush(linear(-16, 0, 16, 0, BEIGE, BEIGE_DUNKEL))
    p.drawRoundedRect(QRectF(-18, -8, 36, 8), 3, 3)
    p.drawRect(QRectF(-8, -14, 16, 7))


def zeichne_gehaeuse(p, an=True, leer=False):
    """Beiger Rahmen des Monitors; leer: ohne Schirm, man sieht ins dunkle Innere."""
    p.setPen(KEIN_STIFT)
    if leer:
        p.setBrush(QColor('#3A352C'))
        p.drawRoundedRect(SCHIRM, 8, 8)
        p.setBrush(QColor(255, 255, 255, 18))
        p.drawRoundedRect(SCHIRM.adjusted(6, 6, -20, -20), 5, 5)
    p.setBrush(linear(-34, -76, 34, -14, BEIGE.lighter(105), BEIGE_DUNKEL))
    p.drawPath(_rahmen_pfad())
    p.setBrush(QColor(255, 255, 255, 70))
    p.drawRoundedRect(QRectF(-31, -76, 50, 2.5), 1, 1)
    p.setBrush(BEIGE_DUNKEL)
    for k in range(4):
        p.drawRect(QRectF(-27 + k * 4, -23, 2, 4.5))
    p.setBrush(BEIGE_DUNKEL.darker(110))
    kreis(p, 19, -21, 2.2)
    p.setBrush(QColor('#4DCB6A') if an else QColor('#5A5A50'))
    kreis(p, 26, -21, 1.8)


def zeichne_schirm(p, bild=1.0, t=0.0, flackern=0.0, stoerung=0.0, kringel=None, farbe='gruen', gesicht=0.0,
                   allein=False, sprung=0.0):
    """Bildröhre. flackern/stoerung 0..1, kringel: Winkel des Ladekringels (None: keiner),
    gesicht > 0 lächelt, < 0 ist traurig, allein: ohne Gehäuse (dünner Rand), sprung 0..1: Glas gesprungen."""
    p.setPen(KEIN_STIFT)
    if allein:
        p.setBrush(linear(0, SCHIRM.top(), 0, SCHIRM.bottom(), QColor('#4A443A'), QColor('#1E1B17')))
        p.drawRoundedRect(SCHIRM.adjusted(-3, -3, 3, 3), 10, 10)
    p.setBrush(QColor('#1E2A26'))
    p.drawRoundedRect(SCHIRM, 8, 8)
    an = bild
    if flackern and ((t * 13) % 1 < 0.35 or (t * 5.3) % 1 < 0.18):
        an *= 1 - 0.7 * flackern
    if an > 0:
        p.save()
        pf = QPainterPath()
        pf.addRoundedRect(SCHIRM.adjusted(1.5, 1.5, -1.5, -1.5), 7, 7)
        p.setClipPath(pf)
        dx = stoerung * 5 * math.sin(t * 41)
        if farbe == 'blau':
            innen, aussen = QColor(120, 170, 255), QColor(20, 50, 170)
        else:
            innen, aussen = QColor(120, 255, 170), QColor(30, 90, 70)
        innen.setAlpha(int(225 * an))
        aussen.setAlpha(int(210 * an))
        p.setBrush(radial(-6 + dx, -56, 44, innen, aussen))
        p.drawRect(SCHIRM)
        p.setBrush(QColor(255, 255, 255, int(28 * an)))
        for k in range(8):
            p.drawRect(QRectF(SCHIRM.left() + 2 + dx, SCHIRM.top() + 3 + k * 5.2, SCHIRM.width() - 4, 1.4))
        if stoerung:
            for k in range(2):
                band = SCHIRM.top() + ((t * (0.9 + 0.6 * k) + 0.4 * k) % 1) * SCHIRM.height()
                p.setBrush(QColor(255, 255, 255, int(110 * stoerung * an)))
                p.drawRect(QRectF(SCHIRM.left(), band - 2.5, SCHIRM.width(), 5))
        weiss = QColor(240, 255, 245, int(240 * an))
        if kringel is not None:
            for k in range(8):
                w = kringel + k * math.pi / 4
                c = QColor(230, 255, 240, int(255 * an * (0.2 + 0.8 * k / 7)))
                p.setBrush(c)
                kreis(p, math.cos(w) * 10, -50 + math.sin(w) * 10, 1.6 + 1.2 * k / 7)
        if gesicht:
            p.setBrush(weiss)
            for sx in (-1, 1):
                p.drawEllipse(QPointF(sx * 8 + dx, -56), 2.6, 3.4)
            p.setPen(stift(weiss, 2.4))
            p.setBrush(KEIN_PINSEL)
            if gesicht > 0:
                p.drawArc(QRectF(-10 + dx, -56, 20, 12), 200 * 16, 140 * 16)
            else:
                p.drawArc(QRectF(-9 + dx, -44, 18, 10), 30 * 16, 120 * 16)
            p.setPen(KEIN_STIFT)
        elif kringel is None and farbe != 'blau' and (t * 2) % 1 < 0.6:
            p.setBrush(weiss)
            p.drawRect(QRectF(-20, -46, 5, 6))
        p.restore()
    p.setBrush(QColor(255, 255, 255, 50))
    p.drawEllipse(QRectF(-22, -70, 18, 8))
    if sprung:
        p.setPen(stift(QColor(240, 250, 255, 230), 1.4))
        z = random.Random(11)
        for _ in range(int(3 + 5 * sprung)):
            q = QPointF(4, -54)
            for _ in range(3):
                n = q + QPointF(z.uniform(-13, 13), z.uniform(-10, 10))
                p.drawLine(q, n)
                q = n
        p.setPen(KEIN_STIFT)


def zeichne_roehre(p, x, y, s, dreh=0.0, gehaeuse=True, **schirm):
    """Ganzer Monitor (Fuß bei x, y, Maßstab s); schirm: Werte für zeichne_schirm."""
    p.save()
    p.translate(x, y)
    p.rotate(dreh)
    p.scale(s, s)
    zeichne_monitor_fuss(p)
    zeichne_schirm(p, allein=not gehaeuse, **schirm)
    if gehaeuse:
        zeichne_gehaeuse(p, an=schirm.get('bild', 1.0) > 0)
    p.restore()


def zeichne_tastatur_gross(p, x, y, fehlt=0, g=1.8):
    p.save()
    p.translate(x, y)
    p.scale(g, g)
    zeichne_tastatur(p, 0, 0, fehlt)
    p.restore()


def zeichne_hammer_gross(p, x, y, winkel, g=1.6):
    p.save()
    p.translate(x, y)
    p.scale(g, g)
    zeichne_hammer(p, 0, -6, winkel)
    p.restore()


# ---------------------------------------------------------------- Teile, die herumfliegen

def _teil_front(p, farbe):
    p.setBrush(linear(-14, 0, 14, 0, BEIGE, BEIGE_DUNKEL))
    p.drawRoundedRect(QRectF(-14, -31, 28, 62), 3, 3)
    p.setBrush(QColor('#3A372E'))
    p.drawRect(QRectF(-10, -25, 20, 5))
    p.drawRect(QRectF(-10, -17, 20, 5))
    p.setBrush(QColor('#C9BFA4'))
    kreis(p, 0, 9, 3.5)
    p.setBrush(QColor('#5A5A50'))
    kreis(p, 7, 19, 1.8)


def _teil_wand(p, farbe):
    p.setBrush(linear(-13, 0, 13, 0, BEIGE.darker(104), BEIGE_DUNKEL.darker(110)))
    p.drawRoundedRect(QRectF(-13, -29, 26, 58), 2, 2)
    p.setBrush(BEIGE_DUNKEL.darker(120))
    for k in range(5):
        p.drawRoundedRect(QRectF(-8, -22 + k * 4, 16, 1.6), 0.8, 0.8)


def _teil_platine(p, farbe):
    p.setBrush(linear(-11, -8, 11, 8, QColor('#3FA65A'), QColor('#1D6B34')))
    p.drawRoundedRect(QRectF(-11, -8, 22, 16), 1.5, 1.5)
    p.setPen(stift(QColor('#E3C04F'), 0.7))
    for k in range(4):
        p.drawLine(QPointF(-9, -5 + k * 3.5), QPointF(9, -5 + k * 3.5))
    p.setPen(KEIN_STIFT)
    p.setBrush(QColor('#1E1E1E'))
    p.drawRect(QRectF(-7, -5, 7, 6))
    p.drawRect(QRectF(3, -6, 5, 3))
    p.setBrush(QColor('#D3172E'))
    p.drawRoundedRect(QRectF(3, 1, 3, 5), 1.2, 1.2)
    p.setBrush(QColor('#4FB4FF'))
    p.drawRoundedRect(QRectF(-9, 3, 3, 3.5), 1, 1)


def _teil_luefter(p, farbe):
    p.setBrush(QColor('#2C2C30'))
    p.drawRoundedRect(QRectF(-8, -8, 16, 16), 2, 2)
    p.setBrush(QColor('#55555C'))
    for k in range(4):
        p.save()
        p.rotate(k * 90 + 20)
        p.drawEllipse(QRectF(-2, -7, 4.5, 6.5))
        p.restore()
    p.setBrush(METALL)
    kreis(p, 0, 0, 2)


def _teil_laufwerk(p, farbe):
    p.setBrush(linear(0, -3, 0, 3, QColor('#5C5A55'), QColor('#2E2C29')))
    p.drawRect(QRectF(-11, -3, 22, 6))
    p.setBrush(QColor('#121212'))
    p.drawRect(QRectF(-7, -1, 14, 1.2))


def _teil_netzteil(p, farbe):
    p.setBrush(linear(-9, -6, 9, 6, METALL.lighter(110), METALL_DUNKEL))
    p.drawRoundedRect(QRectF(-9, -6, 18, 12), 1.5, 1.5)
    p.setPen(stift(METALL_DUNKEL.darker(130), 0.8))
    p.setBrush(KEIN_PINSEL)
    kreis(p, -2, 0, 4)
    p.drawLine(QPointF(-6, 0), QPointF(2, 0))
    p.drawLine(QPointF(-2, -4), QPointF(-2, 4))
    p.setPen(KEIN_STIFT)
    p.setBrush(QColor('#D9A43C'))
    p.drawRect(QRectF(5, -2, 2.5, 4))


def _teil_feder(p, farbe):
    p.setPen(stift(METALL.lighter(110), 1.4))
    p.setBrush(KEIN_PINSEL)
    pfad = QPainterPath()
    pfad.moveTo(-3, -8)
    for k in range(8):
        pfad.lineTo(3 if k % 2 == 0 else -3, -6 + k * 2)
    p.drawPath(pfad)
    p.setPen(KEIN_STIFT)


def zeichne_schraube(p, x=0.0, y=0.0, dreh=0.0, g=1.0):
    """Dicke Cartoon-Schraube, Mitte bei (x, y)."""
    p.save()
    p.translate(x, y)
    p.rotate(dreh)
    p.scale(g, g)
    p.setPen(KEIN_STIFT)
    p.setBrush(linear(-3, 0, 3, 0, METALL.lighter(125), METALL_DUNKEL))
    p.drawRect(QRectF(-2.6, -4, 5.2, 11))
    pfad = QPainterPath()
    pfad.moveTo(-2.6, 7)
    pfad.lineTo(0, 10)
    pfad.lineTo(2.6, 7)
    p.drawPath(pfad)
    p.setPen(stift(METALL_DUNKEL.darker(120), 0.8))
    for k in range(4):
        p.drawLine(QPointF(-2.8, -2 + k * 2.4), QPointF(2.8, -0.8 + k * 2.4))
    p.setPen(KEIN_STIFT)
    p.setBrush(radial(-1.5, -7, 6, METALL.lighter(135), METALL_DUNKEL))
    p.drawRoundedRect(QRectF(-5.5, -7.5, 11, 4), 1.8, 1.8)
    p.setBrush(METALL_DUNKEL.darker(140))
    p.drawRect(QRectF(-0.6, -7.5, 1.2, 2.4))
    p.restore()


def _teil_schraube(p, farbe):
    zeichne_schraube(p)


def _teil_taste(p, farbe):
    zeichne_taste(p, 0, 0, 0, farbe or QColor('#F6F1E2'))


# art: (Zeichnung, Breite, Höhe) in Teil-Einheiten
TEILE = {
    'front': (_teil_front, 28, 62), 'wand': (_teil_wand, 26, 58), 'platine': (_teil_platine, 22, 16),
    'luefter': (_teil_luefter, 16, 16), 'laufwerk': (_teil_laufwerk, 22, 6), 'netzteil': (_teil_netzteil, 18, 12),
    'feder': (_teil_feder, 6, 16), 'schraube': (_teil_schraube, 11, 17), 'taste': (_teil_taste, 6, 5),
}


class Truemmer:
    """Ein herumfliegendes Teil mit Schwerkraft. Weltkoordinaten in Pixeln, groesse in Einheiten je Teil-Einheit.
    durch=True: fällt durch die Unterkante aus dem Bild; flattern: Höchsttempo beim Fallen (Konfetti)."""

    def __init__(self, art, x, y, vx=0.0, vy=0.0, dreh=0.0, vdreh=0.0, groesse=1.0, farbe=None, durch=False,
                 flattern=0.0):
        self.art, self.x, self.y, self.vx, self.vy = art, x, y, vx, vy
        self.dreh, self.vdreh, self.groesse, self.farbe = dreh, vdreh, groesse, farbe
        self.durch, self.flattern = durch, flattern
        self.ruht = False
        self.alter = 0.0
        self.phase = random.uniform(0, 6.3)

    def halb(self, s):
        _, b, h = TEILE[self.art]
        quer = round(self.dreh / 90) % 2
        return (b if quer else h) / 2 * self.groesse * s

    def schritt(self, dt, boden, s, schwere=900):
        if self.ruht:
            return
        self.alter += dt
        self.vy += schwere * s * dt
        if self.flattern and self.vy > self.flattern * s:
            self.vy = self.flattern * s
            self.vx *= 1 - 2.0 * dt
            self.x += math.sin(self.alter * 6 + self.phase) * 50 * s * dt
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.dreh += self.vdreh * dt
        if self.durch:
            return
        unten = boden - self.halb(s)
        if self.y >= unten and self.vy > 0:
            self.y = unten
            if self.vy > 160 * s:
                self.vy *= -0.3
                self.vx *= 0.55
                self.vdreh *= 0.4
            else:
                self.ruht = True
                self.vy = self.vx = 0.0
                _, b, h = TEILE[self.art]
                if h > b * 1.5:
                    self.dreh = round((self.dreh - 90) / 180) * 180 + 90    # lange Teile legen sich hin
                else:
                    self.dreh = round(self.dreh / 90) * 90
                self.y = boden - self.halb(s)

    def kasten(self, s):
        _, b, h = TEILE[self.art]
        r = max(b, h) / 2 * self.groesse * s
        return QRectF(self.x - r, self.y - r, 2 * r, 2 * r)

    def zeichne(self, p, s):
        fn = TEILE[self.art][0]
        p.save()
        p.translate(self.x, self.y)
        p.rotate(self.dreh)
        p.scale(s * self.groesse, s * self.groesse)
        p.setPen(KEIN_STIFT)
        fn(p, self.farbe)
        p.restore()


# ---------------------------------------------------------------- Ladekringel als Rad

def zeichne_kringel(p, x, y, r, dreh, an=1.0):
    """Ladekringel aus Punkten um (x, y) mit Radius r; dreh in Bogenmaß."""
    p.setPen(stift(QColor(150, 255, 195, int(55 * an)), max(1.0, r * 0.26)))
    p.setBrush(KEIN_PINSEL)
    kreis(p, x, y, r)
    p.setPen(KEIN_STIFT)
    n = 10
    for k in range(n):
        w = dreh + k * 2 * math.pi / n
        a = 0.22 + 0.78 * k / (n - 1)
        rr = r * (0.1 + 0.05 * k / (n - 1))
        px, py = x + math.cos(w) * r, y + math.sin(w) * r
        hell = QColor(240, 255, 245, int(255 * a * an))
        dunkel = QColor(90, 210, 140, int(255 * a * an))
        p.setBrush(radial(px - rr * 0.3, py - rr * 0.3, rr * 1.2, hell, dunkel))
        kreis(p, px, py, rr)


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


def zeichne_knaeuel(p, x, y, menge=1.0, t=0.0, saat=4):
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
        kabel_strich(p, pfad, 3.0)
        p.restore()


WICKLUNG = ((-30, 19), (-52, 32), (-74, 44), (-94, 46), (-114, 46), (-133, 43), (-151, 38))


def wicklung_punkt(anteil):
    """Wo das Kabel gerade auf der Figur ankommt (Figur-Einheiten)."""
    i = min(len(WICKLUNG) - 1, int(anteil * len(WICKLUNG)))
    y, rx = WICKLUNG[i]
    return rx, y


def zeichne_wicklung(p, anteil, eng=0.0, vorn=True):
    """Kabelwindungen um die Figur (in Figur-Einheiten): vorn die untere, hinten die obere Bogenhälfte."""
    voll = anteil * len(WICKLUNG)
    for i, (y, rx) in enumerate(WICKLUNG):
        f = min(1.0, voll - i)
        if f <= 0 or (not vorn and f < 1):
            break
        rx = rx * (1 - 0.14 * eng)
        ry = 6.5 - 2.5 * eng
        p.save()
        p.translate(0, y)
        p.rotate((-1) ** i * 7)
        r = QRectF(-rx, -ry, 2 * rx, 2 * ry)
        pfad = QPainterPath()
        if vorn:
            pfad.arcMoveTo(r, 180)
            pfad.arcTo(r, 180, 180 * f)
        else:
            pfad.arcMoveTo(r, 0)
            pfad.arcTo(r, 0, 180)
        kabel_strich(p, pfad, 3.6)
        p.restore()


def zeichne_kabelschleife(p, x, y, g=1.0):
    """Paketschleife aus Kabel mit baumelndem Stecker, Knoten bei (x, y)."""
    if g <= 0:
        return
    p.save()
    p.translate(x, y)
    p.scale(g, g)
    for sx in (-1, 1):
        pfad = QPainterPath()
        pfad.moveTo(0, 0)
        pfad.cubicTo(sx * 10, -16, sx * 24, -12, sx * 18, -2)
        pfad.cubicTo(sx * 14, 4, sx * 6, 2, 0, 0)
        kabel_strich(p, pfad, 3.6)
    kabel_linie(p, [(0, 0), (-4, 10), (-2, 18)], 3.4)
    kabel_linie(p, [(0, 0), (5, 8), (9, 14)], 3.4)
    p.setBrush(KABEL)
    kreis(p, 0, 0, 3.4)
    zeichne_stecker(p, 9, 14, 70)
    p.restore()
