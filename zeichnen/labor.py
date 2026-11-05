"""Requisiten des Professors: Tafel mit Kreideschrift, Labortisch, Kolben,
Bunsenbrenner, Röhrenmonitor, Tastatur, Rechnerturm, Blitze und mehr.

Alle in Zeichen-Einheiten, Boden mittig im Ursprung, wie in requisiten.py.
"""
import math
import random

from PyQt6.QtCore import QPointF, QRectF
from PyQt6.QtGui import QColor, QPainterPath

from .grundlagen import *  # noqa: F401,F403  Farben und Hilfen

HOLZ = QColor('#A8703C')
HOLZ_DUNKEL = QColor('#6A4220')
SCHIEFER = QColor('#2F4A3E')
SCHIEFER_DUNKEL = QColor('#1C2E26')
KREIDE = QColor(245, 245, 235, 235)
GLAS = QColor(215, 238, 255, 90)
GLAS_RAND = QColor(240, 250, 255, 200)
BEIGE = QColor('#E4DBC4')
BEIGE_DUNKEL = QColor('#A89C80')
METALL = QColor('#B8BEC6')
METALL_DUNKEL = QColor('#6C737C')

FLUESSIG = {
    'gruen': QColor('#5BE36B'), 'rot': QColor('#FF4F6A'), 'blau': QColor('#4FB4FF'),
    'lila': QColor('#B46BFF'), 'gelb': QColor('#FFD84F'), 'orange': QColor('#FF9A3C'),
}


# ---------------------------------------------------------------- Kreideschrift

def _kreis_punkte(cx, cy, rx, ry, n=12, a0=0.0, a1=2 * math.pi):
    return [(cx + rx * math.cos(a0 + (a1 - a0) * k / n), cy + ry * math.sin(a0 + (a1 - a0) * k / n))
            for k in range(n + 1)]


# Ziffern und Rechenzeichen als Striche in einem Kasten 0..0.6 × 0..1 (y nach unten)
ZEICHEN = {
    '0': [_kreis_punkte(0.3, 0.5, 0.26, 0.5, 14, -math.pi / 2, 1.5 * math.pi)],
    '1': [[(0.12, 0.25), (0.34, 0.0), (0.34, 1.0)]],
    '2': [[(0.05, 0.22), (0.18, 0.03), (0.42, 0.02), (0.55, 0.2), (0.48, 0.42), (0.05, 1.0), (0.6, 0.98)]],
    '3': [[(0.06, 0.12), (0.3, 0.0), (0.54, 0.14), (0.5, 0.38), (0.24, 0.48), (0.5, 0.56), (0.58, 0.8),
           (0.42, 0.98), (0.18, 1.0), (0.02, 0.86)]],
    '4': [[(0.46, 1.0), (0.44, 0.0), (0.02, 0.68), (0.6, 0.68)]],
    '5': [[(0.56, 0.0), (0.12, 0.02), (0.07, 0.44), (0.3, 0.38), (0.54, 0.52), (0.56, 0.82), (0.32, 1.0),
           (0.04, 0.9)]],
    '6': [[(0.5, 0.04), (0.26, 0.06), (0.06, 0.42), (0.05, 0.8), (0.26, 1.0), (0.5, 0.92), (0.56, 0.66),
           (0.32, 0.5), (0.07, 0.62)]],
    '7': [[(0.02, 0.02), (0.6, 0.0), (0.22, 1.0)]],
    '8': [[(0.3, 0.48), (0.07, 0.28), (0.3, 0.0), (0.53, 0.25), (0.3, 0.48), (0.03, 0.72), (0.3, 1.0),
           (0.57, 0.74), (0.3, 0.48)]],
    '9': [[(0.55, 0.32), (0.3, 0.5), (0.05, 0.3), (0.3, 0.0), (0.55, 0.2), (0.55, 0.62), (0.32, 1.0),
           (0.06, 0.92)]],
    '+': [[(0.05, 0.55), (0.55, 0.55)], [(0.3, 0.3), (0.3, 0.8)]],
    '-': [[(0.08, 0.55), (0.52, 0.55)]],
    '=': [[(0.05, 0.42), (0.55, 0.42)], [(0.05, 0.68), (0.55, 0.68)]],
    'x': [[(0.08, 0.35), (0.52, 1.0)], [(0.52, 0.35), (0.08, 1.0)]],
    'y': [[(0.08, 0.35), (0.3, 0.72)], [(0.52, 0.35), (0.12, 1.25)]],
    '/': [[(0.5, 0.0), (0.1, 1.0)]],
    '(': [[(0.42, -0.05), (0.2, 0.25), (0.16, 0.6), (0.22, 0.85), (0.42, 1.05)]],
    ')': [[(0.18, -0.05), (0.4, 0.25), (0.44, 0.6), (0.38, 0.85), (0.18, 1.05)]],
    '?': [[(0.08, 0.2), (0.28, 0.0), (0.52, 0.18), (0.48, 0.36), (0.3, 0.5), (0.3, 0.72)],
          [(0.3, 0.94), (0.32, 0.97)]],
    '!': [[(0.3, 0.0), (0.3, 0.72)], [(0.3, 0.94), (0.32, 0.97)]],
    '.': [[(0.25, 0.94), (0.27, 0.97)]],
    '²': [[(0.04, 0.1), (0.14, 0.0), (0.3, 0.02), (0.32, 0.14), (0.04, 0.4), (0.36, 0.4)]],
    'π': [[(0.0, 0.38), (0.6, 0.32)], [(0.18, 0.35), (0.14, 1.0)], [(0.42, 0.34), (0.46, 0.94), (0.58, 1.0)]],
    '√': [[(0.0, 0.62), (0.12, 0.56), (0.26, 1.0), (0.46, -0.02), (0.95, -0.02)]],
    '∞': [_kreis_punkte(0.2, 0.6, 0.18, 0.18, 8, 0, 2 * math.pi) + _kreis_punkte(0.56, 0.6, 0.18, 0.18, 8,
                                                                               math.pi, 3 * math.pi)],
    '≠': [[(0.05, 0.42), (0.55, 0.42)], [(0.05, 0.68), (0.55, 0.68)], [(0.45, 0.22), (0.15, 0.88)]],
    '∫': [[(0.5, 0.0), (0.36, -0.04), (0.3, 0.2), (0.3, 0.8), (0.24, 1.04), (0.1, 1.0)]],
    '~': [[(0.02, 0.6), (0.15, 0.48), (0.3, 0.6), (0.45, 0.72), (0.58, 0.6)]],
    '*': [[(0.3, 0.2), (0.3, 0.9)], [(0.0, 0.38), (0.6, 0.72)], [(0.0, 0.72), (0.6, 0.38)]],
    ' ': [],
}
BREITE = {'√': 1.0, '∞': 0.8, ' ': 0.45, '.': 0.4, '²': 0.4, '!': 0.45, '(': 0.5, ')': 0.5}


def _strichlaenge(punkte):
    return sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(punkte, punkte[1:])) or 0.02


def kreide_striche(text, x, y, hoehe, wackel=7):
    """Striche (Punktlisten in Einheiten) für einen Kreideanschrieb, links oben bei (x, y)."""
    zufall = random.Random(sum(ord(c) * (i + 1) for i, c in enumerate(text)) + wackel)
    striche = []
    for ch in text:
        hoch = ch == '²'
        h = hoehe * (0.55 if hoch else 1.0)
        dy = -hoehe * 0.15 if hoch else zufall.uniform(-0.05, 0.05) * hoehe
        for linie in ZEICHEN.get(ch, ZEICHEN['?']):
            striche.append([(x + (px + zufall.uniform(-0.025, 0.025)) * h,
                             y + dy + (py + zufall.uniform(-0.025, 0.025)) * h) for px, py in linie])
        x += BREITE.get(ch, 0.72) * hoehe
    return striche


def anschrieb_breite(text, hoehe):
    return sum(BREITE.get(ch, 0.72) for ch in text) * hoehe


def zeichne_striche(p, striche, anteil=1.0, farbe=KREIDE, breite=2.4):
    """Zeichnet die ersten anteil·100 % der Striche (zum Mitschreiben); gibt die Spitze zurück."""
    p.setPen(KEIN_STIFT)
    gesamt = sum(_strichlaenge(s) for s in striche) or 1
    rest = gesamt * max(0.0, min(1.0, anteil))
    p.setPen(stift(farbe, breite))
    p.setBrush(KEIN_PINSEL)
    spitze = None
    for s in striche:
        if rest <= 0:
            break
        pfad = QPainterPath()
        pfad.moveTo(*s[0])
        spitze = s[0]
        for a, b in zip(s, s[1:]):
            l = math.hypot(b[0] - a[0], b[1] - a[1])
            if l >= rest:
                f = rest / l if l else 1
                spitze = (a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f)
                pfad.lineTo(*spitze)
                rest = 0
                break
            pfad.lineTo(*b)
            spitze = b
            rest -= l
        p.drawPath(pfad)
    p.setPen(KEIN_STIFT)
    return spitze


def striche_spitze(striche, anteil):
    """Wo die Kreide gerade ist, ohne zu zeichnen."""
    gesamt = sum(_strichlaenge(s) for s in striche) or 1
    rest = gesamt * max(0.0, min(1.0, anteil))
    spitze = striche[0][0] if striche else (0, 0)
    for s in striche:
        for a, b in zip(s, s[1:]):
            l = math.hypot(b[0] - a[0], b[1] - a[1])
            if l >= rest:
                f = rest / l if l else 1
                return a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f
            rest -= l
            spitze = b
    return spitze


# ---------------------------------------------------------------- Tafel

TAFEL_B, TAFEL_H, TAFEL_UNTEN = 150, 96, -96


def tafel_flaeche(b=TAFEL_B, h=TAFEL_H, unten=TAFEL_UNTEN):
    """Schreibfläche der Tafel (in Einheiten, Boden mittig im Ursprung)."""
    return QRectF(-b / 2, unten - h, b, h)


def zeichne_tafel(p, b=TAFEL_B, h=TAFEL_H, unten=TAFEL_UNTEN, wisch=(), kreide=True, schwamm=True, beine=True):
    """Kleine Tafel auf einem Holzständer. wisch: Liste (x, y, r) verschmierter Stellen."""
    p.setPen(KEIN_STIFT)
    f = tafel_flaeche(b, h, unten)
    if beine:
        for x0, x1 in ((-b * 0.38, -b * 0.3), (b * 0.38, b * 0.3)):
            p.setBrush(linear(x0 - 4, 0, x0 + 4, 0, HOLZ, HOLZ_DUNKEL))
            pfad = QPainterPath()
            pfad.moveTo(x0 - 3.5, 0)
            pfad.lineTo(x1 - 3, f.top() - 10)
            pfad.lineTo(x1 + 3, f.top() - 10)
            pfad.lineTo(x0 + 3.5, 0)
            pfad.closeSubpath()
            p.drawPath(pfad)
        p.setBrush(HOLZ_DUNKEL)
        p.drawRect(QRectF(-b * 0.36, -24, b * 0.72, 4))
    p.setBrush(linear(0, f.top() - 6, 0, f.bottom() + 6, HOLZ.lighter(115), HOLZ_DUNKEL))
    p.drawRoundedRect(f.adjusted(-6, -6, 6, 6), 3, 3)
    p.setBrush(linear(f.left(), f.top(), f.right(), f.bottom(), SCHIEFER.lighter(115), SCHIEFER_DUNKEL))
    p.drawRect(f)
    p.setBrush(QColor(255, 255, 255, 14))
    for k in range(4):
        p.drawEllipse(QPointF(f.left() + (0.2 + 0.2 * k) * f.width(), f.top() + (0.3 + 0.13 * (k % 3)) * f.height()),
                      18, 7)
    for x, y, r in wisch:
        p.setBrush(radial(x, y, r, QColor(220, 230, 225, 70), QColor(220, 230, 225, 0)))
        p.drawEllipse(QPointF(x, y), r * 1.4, r)
    # Ablage mit Kreide und Schwamm
    p.setBrush(linear(0, f.bottom() + 4, 0, f.bottom() + 11, HOLZ.lighter(120), HOLZ_DUNKEL))
    p.drawRoundedRect(QRectF(f.left() - 4, f.bottom() + 5, f.width() + 8, 6), 2, 2)
    if kreide:
        p.setBrush(QColor('#F7F4EA'))
        p.drawRoundedRect(QRectF(f.left() + 14, f.bottom() + 1, 14, 4.5), 2, 2)
    if schwamm:
        zeichne_schwamm(p, f.right() - 26, f.bottom() + 5)


def zeichne_schwamm(p, x, y, nass=0.0):
    """Tafelschwamm, Unterkante mittig bei (x, y)."""
    p.setPen(KEIN_STIFT)
    p.setBrush(linear(0, y - 10, 0, y, QColor('#F4C430').darker(100 + int(30 * nass)), QColor('#C28E12')))
    p.drawRoundedRect(QRectF(x - 11, y - 10, 22, 10), 3, 3)
    p.setBrush(QColor('#2B6E4A'))
    p.drawRoundedRect(QRectF(x - 11, y - 3.5, 22, 3.5), 1.5, 1.5)
    p.setBrush(QColor(140, 90, 10, 120))
    for dx, dy in ((-6, -7), (-1, -5), (5, -7), (7, -4.5)):
        kreis(p, x + dx, y + dy, 1.1)


def zeichne_kreide(p, x, y, winkel=0.0, laenge=12):
    p.setPen(KEIN_STIFT)
    p.save()
    p.translate(x, y)
    p.rotate(winkel)
    p.setBrush(QColor('#F7F4EA'))
    p.drawRoundedRect(QRectF(-laenge / 2, -2.4, laenge, 4.8), 2, 2)
    p.setBrush(QColor(0, 0, 0, 30))
    p.drawRect(QRectF(-laenge / 2, 0.8, laenge, 1.6))
    p.restore()


# ---------------------------------------------------------------- Labor

def zeichne_labortisch(p, b=130, h=64):
    """Kleiner Holztisch, Platte bei y = -h."""
    p.setPen(KEIN_STIFT)
    p.setBrush(QColor(0, 0, 0, 40))
    p.drawEllipse(QRectF(-b * 0.55, -3, b * 1.1, 6))
    for x in (-b / 2 + 8, b / 2 - 8):
        p.setBrush(linear(x - 4, 0, x + 4, 0, HOLZ, HOLZ_DUNKEL))
        p.drawRect(QRectF(x - 4, -h, 8, h))
    p.setBrush(HOLZ_DUNKEL)
    p.drawRect(QRectF(-b / 2 + 8, -h * 0.35, b - 16, 4))
    p.setBrush(linear(0, -h - 8, 0, -h, HOLZ.lighter(125), HOLZ_DUNKEL))
    p.drawRoundedRect(QRectF(-b / 2, -h - 8, b, 9), 2, 2)


def zeichne_kolben(p, x, y, farbe, fuell=0.6, art='erlen', groesse=1.0, blasen=0.0, t=0.0, leer_hals=True):
    """Glaskolben mit Flüssigkeit, Boden mittig bei (x, y). art: erlen, rund, glas (Reagenzglas)."""
    p.setPen(KEIN_STIFT)
    p.save()
    p.translate(x, y)
    p.scale(groesse, groesse)
    pfad = QPainterPath()
    if art == 'erlen':
        pfad.moveTo(-15, 0)
        pfad.lineTo(15, 0)
        pfad.quadTo(18, 0, 16, -4)
        pfad.lineTo(4, -26)
        pfad.lineTo(4, -38)
        pfad.lineTo(-4, -38)
        pfad.lineTo(-4, -26)
        pfad.lineTo(-16, -4)
        pfad.quadTo(-18, 0, -15, 0)
        hoehe, boden = 26, 0
    elif art == 'rund':
        pfad.addEllipse(QPointF(0, -14), 14, 14)
        hals = QPainterPath()
        hals.addRect(QRectF(-4, -42, 8, 18))
        pfad = pfad.united(hals)
        hoehe, boden = 28, 0
    else:
        pfad.addRoundedRect(QRectF(-5, -34, 10, 34), 5, 5)
        hoehe, boden = 32, 0
    p.setBrush(GLAS)
    p.drawPath(pfad)
    if fuell > 0:
        p.save()
        p.setClipPath(pfad)
        oben = boden - hoehe * fuell
        welle = math.sin(t * 6) * 1.2
        f = QPainterPath()
        f.moveTo(-20, oben + welle)
        f.quadTo(0, oben - welle, 20, oben + welle)
        f.lineTo(20, 2)
        f.lineTo(-20, 2)
        f.closeSubpath()
        p.setBrush(linear(0, oben, 0, 0, farbe.lighter(130), farbe.darker(140)))
        p.drawPath(f)
        if blasen:
            p.setBrush(QColor(255, 255, 255, 170))
            for k in range(int(3 + 5 * blasen)):
                u = (t * (0.8 + 0.3 * k) + k * 0.37) % 1
                kreis(p, -9 + (k * 7) % 18, -2 - u * (boden - oben + 2), 1.0 + 0.8 * (k % 2))
        p.restore()
    p.setPen(stift(GLAS_RAND, 1.6))
    p.setBrush(KEIN_PINSEL)
    p.drawPath(pfad)
    p.drawLine(QPointF(-8, -8), QPointF(-11 if art == 'erlen' else -8, -18))
    p.setPen(KEIN_STIFT)
    p.restore()


def zeichne_brenner(p, x, y, flamme=0.0, t=0.0):
    """Bunsenbrenner, Fuß mittig bei (x, y); flamme 0..1 (über 1: Stichflamme)."""
    p.setPen(KEIN_STIFT)
    p.setBrush(linear(x - 12, 0, x + 12, 0, METALL, METALL_DUNKEL))
    p.drawRoundedRect(QRectF(x - 12, y - 5, 24, 5), 2, 2)
    p.drawRect(QRectF(x - 3.5, y - 34, 7, 30))
    p.setBrush(QColor('#C9A43C'))
    p.drawRect(QRectF(x - 4.5, y - 20, 9, 4))
    p.setBrush(QColor('#E36B2B'))
    p.drawRoundedRect(QRectF(x + 3, y - 10, 14, 3), 1.5, 1.5)
    if flamme > 0:
        h = 22 * flamme * (1 + 0.08 * math.sin(t * 30))
        for farbe, breite, hh in ((QColor(90, 150, 255, 150), 6.5, h), (QColor(180, 220, 255, 230), 3.2, h * 0.55)):
            fl = QPainterPath()
            fl.moveTo(x - breite, y - 34)
            fl.cubicTo(x - breite, y - 34 - hh * 0.5, x - 1, y - 34 - hh * 0.8, x + math.sin(t * 17), y - 34 - hh)
            fl.cubicTo(x + 1, y - 34 - hh * 0.8, x + breite, y - 34 - hh * 0.5, x + breite, y - 34)
            fl.closeSubpath()
            p.setBrush(farbe)
            p.drawPath(fl)


def zeichne_stativ(p, x, y, hoehe=70):
    """Stativ mit Ring, auf dem ein Kolben über dem Brenner steht. Ring bei y - hoehe."""
    p.setPen(KEIN_STIFT)
    p.setBrush(linear(x - 18, 0, x + 18, 0, METALL, METALL_DUNKEL))
    p.drawRoundedRect(QRectF(x - 30, y - 4, 32, 4), 2, 2)
    p.drawRect(QRectF(x - 26, y - hoehe - 20, 3, hoehe + 18))
    p.drawRect(QRectF(x - 25, y - hoehe - 2, 15, 3))
    p.setPen(stift(METALL_DUNKEL, 2))
    p.setBrush(KEIN_PINSEL)
    p.drawEllipse(QRectF(x - 12, y - hoehe - 3, 24, 5))
    p.setPen(KEIN_STIFT)


def zeichne_blitz(p, x0, y0, x1, y1, saat, breite=2.5, farbe=QColor(200, 235, 255)):
    """Zuckender Blitz zwischen zwei Punkten; saat ändert die Zacken."""
    zufall = random.Random(saat)
    n = 7
    punkte = [(x0, y0)]
    nx, ny = -(y1 - y0), x1 - x0
    l = math.hypot(nx, ny) or 1
    for k in range(1, n):
        f = k / n
        a = zufall.uniform(-0.12, 0.12) * l
        punkte.append((x0 + (x1 - x0) * f + nx / l * a, y0 + (y1 - y0) * f + ny / l * a))
    punkte.append((x1, y1))
    pfad = QPainterPath()
    pfad.moveTo(*punkte[0])
    for q in punkte[1:]:
        pfad.lineTo(*q)
    p.setBrush(KEIN_PINSEL)
    p.setPen(stift(QColor(farbe.red(), farbe.green(), farbe.blue(), 90), breite * 3.5))
    p.drawPath(pfad)
    p.setPen(stift(WEISS, breite))
    p.drawPath(pfad)
    p.setPen(KEIN_STIFT)


def zeichne_teslaspule(p, x, y, an=0.0, t=0.0):
    """Tesla-Spule mit Kugel oben (Kugelmitte bei y - 96)."""
    p.setPen(KEIN_STIFT)
    p.setBrush(linear(x - 22, 0, x + 22, 0, QColor('#5A5F6A'), QColor('#2C2F36')))
    p.drawRoundedRect(QRectF(x - 22, y - 14, 44, 14), 3, 3)
    p.setBrush(linear(x - 9, 0, x + 9, 0, QColor('#E9A15A'), QColor('#9C5A22')))
    p.drawRect(QRectF(x - 8, y - 80, 16, 66))
    p.setPen(stift(QColor('#7A3D12'), 1))
    for k in range(18):
        yy = y - 18 - k * 3.4
        p.drawLine(QPointF(x - 8, yy), QPointF(x + 8, yy - 1))
    p.setPen(KEIN_STIFT)
    p.setBrush(radial(x - 5, y - 101, 18, QColor('#F2F5F8'), METALL_DUNKEL))
    p.drawEllipse(QPointF(x, y - 96), 18, 12)
    if an > 0:
        p.setBrush(radial(x, y - 96, 40, QColor(170, 210, 255, int(120 * an)), QColor(170, 210, 255, 0)))
        kreis(p, x, y - 96, 40)
        saat = int(t * 14)
        for k in range(int(1 + 3 * an)):
            w = math.radians(-160 + ((saat * 37 + k * 71) % 140))
            zeichne_blitz(p, x, y - 96, x + math.cos(w) * 34, y - 96 + math.sin(w) * 34, saat * 7 + k, 1.4)


# ---------------------------------------------------------------- Computer

def zeichne_monitor(p, x, y, bild=1.0, t=0.0, kaputt=0.0, kringel=False, flackern=False, dreh=0.0):
    """Alter Röhrenmonitor, Fuß mittig bei (x, y). bild: Helligkeit des Schirms, kaputt 0..1: Sprünge, Ruß."""
    p.setPen(KEIN_STIFT)
    p.save()
    p.translate(x, y)
    p.rotate(dreh)
    p.setBrush(linear(-16, 0, 16, 0, BEIGE, BEIGE_DUNKEL))
    p.drawRoundedRect(QRectF(-18, -8, 36, 8), 3, 3)
    p.drawRect(QRectF(-8, -14, 16, 7))
    # Gehäuse mit Röhrenbuckel hinten
    p.setBrush(linear(-30, -70, 30, -14, BEIGE.darker(108), BEIGE_DUNKEL.darker(110)))
    p.drawRoundedRect(QRectF(-24, -66, 48, 48), 10, 10)
    p.setBrush(linear(-34, -76, 34, -14, BEIGE.lighter(105), BEIGE_DUNKEL))
    p.drawRoundedRect(QRectF(-34, -78, 68, 62), 6, 6)
    schirm = QRectF(-27, -72, 54, 44)
    an = bild * (0.4 if flackern and (t * 13) % 1 < 0.35 else 1.0)
    p.setBrush(QColor('#1E2A26'))
    p.drawRoundedRect(schirm, 8, 8)
    if an > 0:
        p.setBrush(radial(-6, -56, 44, QColor(120, 255, 170, int(210 * an)), QColor(30, 90, 70, int(200 * an))))
        p.drawRoundedRect(schirm.adjusted(1.5, 1.5, -1.5, -1.5), 7, 7)
        p.setBrush(QColor(255, 255, 255, int(28 * an)))
        for k in range(8):
            p.drawRect(QRectF(schirm.left() + 2, schirm.top() + 3 + k * 5.2, schirm.width() - 4, 1.4))
        if kringel:
            for k in range(8):
                w = t * 6 + k * math.pi / 4
                c = QColor(230, 255, 240, int(255 * an * (0.25 + 0.75 * k / 7)))
                p.setBrush(c)
                kreis(p, math.cos(w) * 9, -50 + math.sin(w) * 9, 2.4)
    p.setBrush(QColor(255, 255, 255, 50))
    p.drawEllipse(QRectF(-22, -70, 18, 8))
    p.setBrush(QColor('#4DCB6A') if bild > 0 else QColor('#5A5A50'))
    kreis(p, 26, -21, 1.8)
    if kaputt > 0:
        p.setPen(stift(QColor(240, 250, 255, 220), 1.3))
        p.setBrush(KEIN_PINSEL)
        z = random.Random(5)
        for _ in range(int(2 + 5 * kaputt)):
            q = QPointF(z.uniform(-8, 8), -50 + z.uniform(-6, 6))
            for _ in range(3):
                n = q + QPointF(z.uniform(-12, 12), z.uniform(-10, 10))
                p.drawLine(q, n)
                q = n
        p.setPen(KEIN_STIFT)
        p.setBrush(QColor(40, 34, 30, int(170 * kaputt)))
        p.drawEllipse(QPointF(10, -74), 16 * kaputt, 7 * kaputt)
    p.restore()


def zeichne_tastatur(p, x, y, fehlt=0, dreh=0.0, b=56):
    """Flache Tastatur, Unterkante mittig bei (x, y); fehlt: wie viele Tasten herausgeflogen sind."""
    p.setPen(KEIN_STIFT)
    p.save()
    p.translate(x, y)
    p.rotate(dreh)
    p.setBrush(linear(0, -9, 0, 0, BEIGE.lighter(108), BEIGE_DUNKEL))
    p.drawRoundedRect(QRectF(-b / 2, -9, b, 9), 2, 2)
    n = int(b // 6)
    for reihe in range(2):
        for k in range(n):
            nr = reihe * n + k
            if (nr * 7) % (2 * n) < fehlt:
                p.setBrush(QColor('#4A4436'))
                p.drawRect(QRectF(-b / 2 + 2 + k * 6, -8.5 + reihe * 4, 4.5, 3))
                continue
            p.setBrush(QColor('#F6F1E2') if (k + reihe) % 5 else QColor('#C9BFA4'))
            p.drawRoundedRect(QRectF(-b / 2 + 2 + k * 6, -10.5 + reihe * 4, 4.5, 3.4), 0.8, 0.8)
    p.restore()


def zeichne_taste(p, x, y, dreh, farbe=QColor('#F6F1E2')):
    p.setPen(KEIN_STIFT)
    p.save()
    p.translate(x, y)
    p.rotate(dreh)
    p.setBrush(farbe)
    p.drawRoundedRect(QRectF(-3, -2.5, 6, 5), 1, 1)
    p.setBrush(QColor(0, 0, 0, 40))
    p.drawRect(QRectF(-3, 1.5, 6, 1))
    p.restore()


def zeichne_turm(p, x, y, kaputt=0.0, dreh=0.0, t=0.0):
    """Rechnerturm, Boden mittig bei (x, y); kaputt: Seitenwand hängt, Lämpchen aus."""
    p.setPen(KEIN_STIFT)
    p.save()
    p.translate(x, y)
    p.rotate(dreh)
    p.setBrush(linear(-14, 0, 14, 0, BEIGE, BEIGE_DUNKEL))
    p.drawRoundedRect(QRectF(-14, -62, 28, 62), 3, 3)
    p.setBrush(QColor('#3A372E'))
    p.drawRect(QRectF(-10, -56, 20, 5))
    p.drawRect(QRectF(-10, -48, 20, 5))
    p.setBrush(QColor('#8D846C'))
    p.drawRect(QRectF(-6, -36, 12, 2))
    lampe = kaputt < 0.5 and (t * 3) % 1 < 0.7
    p.setBrush(QColor('#4DCB6A') if lampe else QColor('#5A5A50'))
    kreis(p, 7, -12, 1.8)
    p.setBrush(QColor('#C9BFA4'))
    kreis(p, 0, -22, 3.5)
    if kaputt > 0:
        p.save()
        p.translate(14, -2)
        p.rotate(-50 * kaputt)
        p.setBrush(linear(0, 0, 28, 0, BEIGE_DUNKEL, BEIGE.darker(115)))
        p.drawRect(QRectF(0, -60, 4, 60))
        p.restore()
    p.restore()


def zeichne_maus_geraet(p, x, y, dreh=0.0):
    p.setPen(KEIN_STIFT)
    p.save()
    p.translate(x, y)
    p.rotate(dreh)
    p.setBrush(linear(0, -7, 0, 0, BEIGE.lighter(110), BEIGE_DUNKEL))
    p.drawEllipse(QRectF(-6, -7, 12, 8))
    p.setPen(stift(BEIGE_DUNKEL.darker(130), 0.8))
    p.drawLine(QPointF(0, -7), QPointF(0, -3))
    p.setPen(KEIN_STIFT)
    p.restore()


def zeichne_kabel(p, punkte, farbe=QColor('#3A3A3A'), breite=2.5):
    """Weiches Kabel durch die Punkte."""
    if len(punkte) < 2:
        return
    pfad = QPainterPath()
    pfad.moveTo(*punkte[0])
    for a, b in zip(punkte, punkte[1:]):
        pfad.quadTo(a[0], a[1], (a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
    pfad.lineTo(*punkte[-1])
    p.setPen(stift(farbe, breite))
    p.setBrush(KEIN_PINSEL)
    p.drawPath(pfad)
    p.setPen(KEIN_STIFT)


def zeichne_hammer(p, x, y, winkel, laenge=40):
    """Hammer, Griffende bei (x, y), winkel wie ein Arm (0 = nach unten)."""
    p.setPen(KEIN_STIFT)
    p.save()
    p.translate(x, y)
    p.rotate(winkel)
    p.setBrush(linear(-2.5, 0, 2.5, 0, HOLZ.lighter(115), HOLZ_DUNKEL))
    p.drawRoundedRect(QRectF(-2.5, -4, 5, laenge), 2, 2)
    p.setBrush(linear(-10, laenge, 10, laenge, METALL, METALL_DUNKEL))
    p.drawRoundedRect(QRectF(-11, laenge - 4, 22, 9), 2, 2)
    p.restore()
