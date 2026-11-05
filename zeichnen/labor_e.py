"""Requisiten für die Computer-Szenen des Professors (Gruppe E): Laptop, Drucker mit
Papier, Mauszeiger, Eisblock, Schraubstock und der Monitor als Ziehharmonika.

Alle in Zeichen-Einheiten, Boden mittig im Ursprung, wie in labor.py.
"""
import math
import random

from PyQt6.QtCore import QPointF, QRectF
from PyQt6.QtGui import QColor, QPainterPath, QTransform

from .grundlagen import *  # noqa: F401,F403  Farben und Hilfen
from .labor import METALL, METALL_DUNKEL, zeichne_monitor
from .professor import HANDSCHUH, HANDSCHUH_DUNKEL, KITTEL, KITTEL_SCHATTEN

SILBER = QColor('#C9CED6')
SILBER_DUNKEL = QColor('#7D848F')
GRAU_DUNKEL = QColor('#3A3E46')
PAPIER = QColor('#FBFBF7')
PAPIER_SCHATTEN = QColor('#D9DBE0')
EIS_HELL = QColor(225, 245, 255, 150)
EIS_DUNKEL = QColor(140, 200, 235, 170)
SCHRAUB_BLAU = QColor('#3F6EA6')
SCHRAUB_BLAU_DUNKEL = QColor('#22446E')


# ---------------------------------------------------------------- Laptop

def _laptop_deckel_zu(p, f):
    """Rückseite des zugeklappten Deckels über der Tastatur (f: 0 hochkant .. 1 ganz zu)."""
    tief = -14 + 11 * f
    pfad = QPainterPath()
    pfad.moveTo(-33, -14)
    pfad.lineTo(33, -14)
    pfad.lineTo(33 + 5 * f, tief)
    pfad.lineTo(-33 - 5 * f, tief)
    pfad.closeSubpath()
    p.setBrush(linear(0, -14, 0, tief + 1, SILBER.lighter(110), SILBER_DUNKEL))
    p.drawPath(pfad)
    if f > 0.6:
        p.setBrush(QColor(255, 255, 255, 120))
        p.drawRect(QRectF(-30, -13.5, 26, 1.2))
        p.setBrush(QColor('#E3A928'))
        stern(p, 0, (tief - 14) / 2, 2.6)


def zeichne_laptop(p, x, y, deckel=1.0, bild=1.0, t=0.0, fehler=0.0, kaputt=0.0, nur_deckel=False):
    """Klapprechner von vorn, Unterkante mittig bei (x, y). deckel 1 = offen, 0 = zu;
    fehler 0..1: Schirm blinkt rot, kaputt 0..1: Sprünge und dunkler Schirm."""
    p.setPen(KEIN_STIFT)
    p.save()
    p.translate(x, y)
    if not nur_deckel:
        p.setBrush(QColor(0, 0, 0, 45))
        p.drawEllipse(QRectF(-42, -2, 84, 5))
        p.setBrush(linear(0, -4, 0, 0, SILBER_DUNKEL, GRAU_DUNKEL))
        p.drawRoundedRect(QRectF(-39, -5, 78, 5), 2, 2)
        oben = QPainterPath()
        oben.moveTo(-38, -4)
        oben.lineTo(38, -4)
        oben.lineTo(32, -14)
        oben.lineTo(-32, -14)
        oben.closeSubpath()
        p.setBrush(linear(0, -14, 0, -4, SILBER.darker(105), SILBER.lighter(112)))
        p.drawPath(oben)
        p.setBrush(QColor('#4A4E58'))
        for reihe in range(3):
            v = (reihe + 0.5) / 3.6
            yy = -13 + v * 7
            halb = 29 + 5 * v
            n = 11
            for k in range(n):
                xx = -halb + (k + 0.15) * 2 * halb / n
                p.drawRect(QRectF(xx, yy, 2 * halb / n * 0.7, 1.6))
        p.setBrush(SILBER.darker(118))
        p.drawRoundedRect(QRectF(-8, -6.8, 16, 2.4), 1, 1)
    if deckel > 0.15:
        f = (deckel - 0.15) / 0.85
        oben_y = -14 - 52 * f
        aussen = QRectF(-33, oben_y, 66, -14 - oben_y)
        p.setBrush(linear(-33, oben_y, 33, -14, QColor('#5A5F6A'), QColor('#2B2E35')))
        p.drawRoundedRect(aussen, 3, 3)
        if f > 0.25:
            schirm = aussen.adjusted(3.5, 3.5, -3.5, -4)
            an = bild * (1 - kaputt * 0.85)
            rot = fehler * (0.5 + 0.5 * math.sin(t * 14))
            p.setBrush(QColor('#14181E'))
            p.drawRect(schirm)
            if an > 0:
                innen = QColor(int(110 + 145 * rot), int(190 - 140 * rot), int(255 - 200 * rot), int(230 * an))
                aus = QColor(int(30 + 120 * rot), int(70 - 40 * rot), int(140 - 100 * rot), int(220 * an))
                p.setBrush(radial(schirm.center().x() - 8, schirm.top() + 10, 46, innen, aus))
                p.drawRect(schirm)
                if fehler > 0:
                    # großes Warndreieck ohne Text
                    m = schirm.center()
                    d = QPainterPath()
                    d.moveTo(m.x(), m.y() - 12)
                    d.lineTo(m.x() + 13, m.y() + 10)
                    d.lineTo(m.x() - 13, m.y() + 10)
                    d.closeSubpath()
                    p.setBrush(QColor(255, 230, 90, int(255 * an * (0.4 + 0.6 * rot))))
                    p.drawPath(d)
                    p.setBrush(QColor(60, 20, 10, int(255 * an)))
                    p.drawRoundedRect(QRectF(m.x() - 1.6, m.y() - 5, 3.2, 9), 1.2, 1.2)
                    kreis(p, m.x(), m.y() + 7, 1.7)
            p.setBrush(QColor(255, 255, 255, 40))
            gl = QPainterPath()
            gl.moveTo(schirm.left(), schirm.top())
            gl.lineTo(schirm.left() + schirm.width() * 0.45, schirm.top())
            gl.lineTo(schirm.left(), schirm.top() + schirm.height() * 0.7)
            gl.closeSubpath()
            p.drawPath(gl)
            if kaputt > 0:
                _spruenge(p, schirm.center().x(), schirm.center().y(), kaputt, 9)
        p.setBrush(QColor(255, 255, 255, 70))
        p.drawRect(QRectF(-31, oben_y + 1, 62, 1))
    else:
        _laptop_deckel_zu(p, (0.15 - deckel) / 0.15)
    p.restore()


def _spruenge(p, cx, cy, staerke, saat, weite=12):
    p.setPen(stift(QColor(240, 250, 255, 230), 1.1))
    p.setBrush(KEIN_PINSEL)
    z = random.Random(saat)
    for _ in range(int(3 + 5 * staerke)):
        q = QPointF(cx, cy)
        w = z.uniform(0, 2 * math.pi)
        for _ in range(3):
            w += z.uniform(-0.7, 0.7)
            n = q + QPointF(math.cos(w) * weite * 0.6, math.sin(w) * weite * 0.6)
            p.drawLine(q, n)
            q = n
    p.setPen(KEIN_STIFT)


def zeichne_laptop_klein(p, x, y, winkel=0.0, kappe=False):
    """Zugeklappter Laptop als flache Platte, etwa unter dem Arm; Mitte bei (x, y)."""
    p.setPen(KEIN_STIFT)
    p.save()
    p.translate(x, y)
    p.rotate(winkel)
    p.setBrush(linear(0, -5, 0, 5, SILBER.lighter(108), SILBER_DUNKEL))
    p.drawRoundedRect(QRectF(-30, -4, 60, 8), 2.5, 2.5)
    p.setBrush(GRAU_DUNKEL)
    p.drawRect(QRectF(-29, 0.5, 58, 1))
    p.setBrush(QColor('#E3A928'))
    stern(p, 8, -1.5, 2.4)
    if kappe:
        zeichne_kappe(p, (-22, -3), (2, -3), (-28, -26), 0.7)
    p.restore()


# ---------------------------------------------------------------- Mütze, frei gezogen

def zeichne_kappe(p, links, rechts, bommel, s=1.0, dick=1.0, teile='krb', zug=None):
    """Weihnachtsmütze als Gummizipfel: Rand von links nach rechts, Spitze mit Bommel
    beim Punkt bommel. Punkte in den aktuellen Koordinaten, s: Größe des Randes.
    teile: k = Körper, r = Rand, b = Bommel (für getrenntes Zeichnen vor und hinter der Figur);
    zug: Punkt, über den der Zipfel im Bogen läuft (etwa vor dem Gesicht vorbei)."""
    lx, ly = links
    rx, ry = rechts
    bx, by = bommel
    mx, my = (lx + rx) / 2, (ly + ry) / 2
    nx, ny = -(ry - ly), rx - lx          # zeigt vom Rand weg (zur Spitze hin, wenn Spitze "oben")
    nl = math.hypot(nx, ny) or 1.0
    if (bx - mx) * nx + (by - my) * ny < 0:
        nx, ny = -nx, -ny
    nx, ny = nx / nl, ny / nl
    hoch = 22 * s * dick
    pfad = QPainterPath()
    pfad.moveTo(lx, ly)
    pfad.lineTo(rx, ry)
    pfad.cubicTo(rx + nx * hoch, ry + ny * hoch, (rx + bx) / 2 + nx * hoch * 0.6, (ry + by) / 2 + ny * hoch * 0.6,
                 bx, by)
    pfad.cubicTo((lx + bx) / 2 + nx * hoch * 0.3, (ly + by) / 2 + ny * hoch * 0.3, lx + nx * hoch * 0.4,
                 ly + ny * hoch * 0.4, lx, ly)
    if zug is not None:
        zx, zy = zug
        ix, iy = zx + (mx - zx) * 0.3 + (bx - zx) * 0.12, zy + (my - zy) * 0.3 + (by - zy) * 0.12
        pfad = QPainterPath()
        pfad.moveTo(lx, ly)
        pfad.cubicTo(lx + (zx - lx) * 0.3, ly - 16 * s, zx, zy, bx, by)
        pfad.cubicTo(ix, iy, rx + (ix - rx) * 0.3, ry - 4 * s, rx, ry)
        pfad.closeSubpath()
    p.setPen(KEIN_STIFT)
    if 'k' in teile:
        p.setBrush(linear(bx, by, mx, my, ROT_HELL, ROT_DUNKEL))
        p.drawPath(pfad)
    if 'r' in teile:
        n = max(2, int(math.hypot(rx - lx, ry - ly) / (6 * s)))
        flausch(p, [(lx + (rx - lx) * k / n, ly + (ry - ly) * k / n) for k in range(n + 1)], 6 * s)
    if 'b' in teile:
        flausch(p, [(bx + dx * s, by + dy * s) for dx, dy in ((0, 0), (-3, -3), (3, -3), (-3, 3), (3, 3))], 5 * s)


# ---------------------------------------------------------------- Drucker und Papier

def zeichne_drucker(p, x, y, t=0.0, laeuft=0.0, wut=0.0, kaputt=0.0, seite=1):
    """Bürodrucker, Boden mittig bei (x, y), Ausgabeschlitz zur Seite 'seite' (+1 rechts).
    laeuft 0..1: rattert, wut 0..1: tobt (Lämpchen rot), kaputt 0..1: Ruß."""
    p.setPen(KEIN_STIFT)
    p.save()
    p.translate(x, y)
    p.scale(seite, 1)
    p.setBrush(QColor(0, 0, 0, 45))
    p.drawEllipse(QRectF(-48, -3, 96, 6))
    zitter = (math.sin(t * 55) * 0.8 * laeuft + math.sin(t * 71) * 2.2 * wut)
    p.translate(zitter, -abs(math.sin(t * 38)) * 2.5 * wut)
    # Papiereinzug hinten oben
    p.save()
    p.translate(-26, -46)
    p.rotate(-22)
    p.setBrush(linear(0, -26, 0, 0, QColor('#8E939C'), QColor('#5F646D')))
    p.drawRoundedRect(QRectF(-14, -28, 30, 30), 2, 2)
    p.setBrush(PAPIER)
    for k in range(3):
        p.drawRect(QRectF(-11 + k, -34 + k * 1.2, 24, 30))
    p.restore()
    # Gehäuse
    p.setBrush(linear(-40, -48, 40, 0, QColor('#E8EAEE'), QColor('#9EA3AC')))
    p.drawRoundedRect(QRectF(-42, -50, 84, 50), 6, 6)
    p.setBrush(QColor('#5F646D'))
    p.drawRoundedRect(QRectF(-42, -10, 84, 10), 4, 4)
    p.setBrush(QColor(255, 255, 255, 90))
    p.drawRoundedRect(QRectF(-38, -48, 60, 4), 2, 2)
    # Schlitz und Ablage zur Seite
    p.setBrush(QColor('#24272D'))
    p.drawRoundedRect(QRectF(26, -30, 17, 5), 2, 2)
    p.setBrush(linear(40, -26, 62, -18, QColor('#B4B9C2'), QColor('#7A808A')))
    ab = QPainterPath()
    ab.moveTo(40, -26)
    ab.lineTo(64, -20)
    ab.lineTo(64, -17)
    ab.lineTo(40, -22)
    ab.closeSubpath()
    p.drawPath(ab)
    # Bedienfeld: Anzeige, Lämpchen, großer Knopf
    p.setBrush(QColor('#2A2F38'))
    p.drawRoundedRect(QRectF(-30, -40, 26, 12), 2, 2)
    if laeuft or wut:
        p.setBrush(QColor(110, 230, 160, 200) if wut < 0.5 else QColor(255, 90, 80, 220))
        breite = 22 * ((t * 1.5) % 1)
        p.drawRect(QRectF(-28, -36, breite, 4))
    blink = (t * 4) % 1 < 0.5
    if wut > 0.3:
        p.setBrush(QColor('#FF4A3C') if blink else QColor('#7A2018'))
    else:
        p.setBrush(QColor('#4DCB6A') if (laeuft and blink) or not laeuft else QColor('#2A5A34'))
    kreis(p, 4, -34, 2.4)
    p.setBrush(radial(15, -36, 6, QColor('#7FE08F'), QColor('#2E8A44')))
    kreis(p, 15, -34, 4.5)
    p.setBrush(QColor(255, 255, 255, 120))
    kreis(p, 13.5, -35.5, 1.4)
    if kaputt > 0:
        p.setBrush(QColor(40, 34, 30, int(160 * kaputt)))
        p.drawEllipse(QPointF(0, -50), 22 * kaputt, 7 * kaputt)
        p.drawEllipse(QPointF(30, -28), 10 * kaputt, 6 * kaputt)
    p.restore()


def drucker_schlitz(x, y, s, seite=1):
    """Weltpunkt des Ausgabeschlitzes für zeichne_drucker bei (x, y) in Weltkoordinaten."""
    return x + seite * 44 * s, y - 27 * s


def zeichne_blatt(p, x, y, winkel=0.0, flattern=1.0, bild=True):
    """Ein Blatt Papier, Mitte bei (x, y); flattern: Breite durch Drehung (1 flach, 0 hochkant).
    Statt Schrift ein kleines Balkendiagramm."""
    p.setPen(KEIN_STIFT)
    p.save()
    p.translate(x, y)
    p.rotate(winkel)
    p.scale(max(0.08, flattern), 1)
    p.setBrush(QColor(0, 0, 0, 30))
    p.drawRect(QRectF(-11, -14, 24, 30))
    p.setBrush(linear(-12, -15, 12, 15, PAPIER, PAPIER_SCHATTEN))
    p.drawRect(QRectF(-12, -15, 24, 30))
    if bild:
        for k, h in enumerate((8, 13, 6, 16)):
            p.setBrush(QColor(('#4FB4FF', '#FF4F6A', '#5BE36B', '#FFB43C')[k]))
            p.drawRect(QRectF(-8 + k * 4.5, 9 - h, 3, h))
        p.setBrush(QColor('#9AA0AA'))
        p.drawRect(QRectF(-9, 9.5, 18, 0.8))
    p.restore()


def zeichne_papierberg(p, x, y, hoehe, breite=150, saat=4):
    """Haufen aus wild durcheinanderliegenden Blättern, Boden mittig bei (x, y)."""
    if hoehe <= 1:
        return
    p.setPen(KEIN_STIFT)
    z = random.Random(saat)
    halb = breite / 2 * min(1.0, 0.45 + hoehe / 140)

    def profil(u):           # u in -1..1
        return hoehe * (1 - u * u) ** 0.7

    berg = QPainterPath()
    berg.moveTo(x - halb, y)
    for k in range(21):
        u = -1 + k / 10
        berg.lineTo(x + u * halb, y - profil(u) - 3 * math.sin(k * 2.3))
    berg.lineTo(x + halb, y)
    berg.closeSubpath()
    p.setBrush(QColor(0, 0, 0, 40))
    p.drawEllipse(QRectF(x - halb * 1.1, y - 4, halb * 2.2, 8))
    p.setBrush(linear(x, y - hoehe, x, y, PAPIER, QColor('#C9CCD3')))
    p.drawPath(berg)
    n = int(14 + hoehe * 0.5)
    for i in range(n):
        u = z.uniform(-0.95, 0.95)
        oben = profil(u)
        v = z.random() ** 0.6
        bx = x + u * halb
        by = y - oben * v
        w = z.uniform(-60, 60)
        p.save()
        p.translate(bx, by)
        p.rotate(w)
        p.setBrush(QColor(0, 0, 0, 22))
        p.drawRect(QRectF(-10, -6, 22, 14))
        p.setBrush(PAPIER if i % 3 else QColor('#F1F2EC'))
        p.drawRect(QRectF(-11, -7, 22, 14))
        if i % 4 == 0:
            p.setBrush(QColor(('#4FB4FF', '#FF4F6A', '#5BE36B')[i % 3]))
            p.drawRect(QRectF(-6, -1, 2.5, 5))
            p.drawRect(QRectF(-2, -3, 2.5, 7))
        p.restore()


def zeichne_winkehand(p, x, y, winkel, laenge=30):
    """Ärmel mit gelbem Gummihandschuh, ragt bei (x, y) nach oben; winkel 0 = senkrecht."""
    p.setPen(KEIN_STIFT)
    p.save()
    p.translate(x, y)
    p.rotate(winkel)
    p.setBrush(linear(-8, 0, 8, 0, KITTEL, KITTEL_SCHATTEN))
    p.drawRoundedRect(QRectF(-8, -laenge, 16, laenge + 10), 7, 7)
    p.setBrush(KITTEL_SCHATTEN)
    p.drawRoundedRect(QRectF(-8.5, -laenge - 2, 17, 6), 3, 3)
    p.setBrush(radial(-2, -laenge - 12, 12, HANDSCHUH.lighter(125), HANDSCHUH_DUNKEL))
    p.drawRoundedRect(QRectF(-6.5, -laenge - 8, 13, 7), 3, 3)
    kreis(p, 0, -laenge - 13, 7.5)
    for k, (dx, dy) in enumerate(((-6, -20), (-2, -23), (2.5, -23), (6.5, -20))):
        p.drawRoundedRect(QRectF(dx - 2, -laenge + dy - 3, 4, 9), 2, 2)
    p.drawEllipse(QPointF(-8, -laenge - 10), 4.5, 3)
    p.setBrush(QColor(255, 255, 255, 80))
    kreis(p, -3, -laenge - 16, 2)
    p.restore()


# ---------------------------------------------------------------- Mauszeiger

def zeichne_mauszeiger(p, x, y, groesse=1.0, winkel=0.0, beine=0.0, phase=0.0):
    """Schlichter weißer Pfeil mit dunklem Rand, Spitze bei (x, y);
    beine 0..1: kleine Strichbeinchen zum Weglaufen."""
    p.save()
    p.translate(x, y)
    p.rotate(winkel)
    p.scale(groesse, groesse)
    pfeil = QPainterPath()
    for i, (a, b) in enumerate(((0, 0), (0, 18), (4.2, 14), (7.5, 21), (10.2, 19.8), (7, 13), (12.5, 12.6))):
        pfeil.moveTo(a, b) if i == 0 else pfeil.lineTo(a, b)
    pfeil.closeSubpath()
    if beine > 0:
        p.setPen(stift(QColor('#1F1F1F'), 1.3))
        for k, (fx, fy) in enumerate(((3, 16), (8.5, 19.5))):
            w = math.sin(phase + k * math.pi) * 0.7
            p.drawLine(QPointF(fx, fy), QPointF(fx + math.sin(w) * 5 * beine, fy + math.cos(w) * 5 * beine))
    p.setPen(stift(QColor('#1F1F1F'), 1.4))
    p.setBrush(linear(0, 0, 10, 18, QColor('#FFFFFF'), QColor('#DCE3EA')))
    p.drawPath(pfeil)
    p.setPen(KEIN_STIFT)
    p.restore()


# ---------------------------------------------------------------- Eisblock

def zeichne_eisblock(p, x, y, b, h, anteil=1.0, rampe=1, t=0.0):
    """Eisblock um ein Gerät, Boden mittig bei (x, y), mit Eisrampe zur Seite 'rampe'.
    anteil 0..1: das Eis wächst von unten nach oben."""
    if anteil <= 0:
        return
    p.setPen(KEIN_STIFT)
    p.save()
    p.translate(x, y)
    p.scale(rampe, 1)
    hh = h * glatt(anteil)
    block = QPainterPath()
    block.moveTo(-b / 2, 0)
    block.lineTo(-b / 2, -hh + 6)
    block.quadTo(-b / 2, -hh, -b / 2 + 6, -hh)
    block.lineTo(b / 2 - 6, -hh)
    block.quadTo(b / 2, -hh, b / 2 + 2, -hh + 6)
    # Rampe: vom Blockrand weich zum Boden
    block.cubicTo(b / 2 + hh * 0.25, -hh * 0.55, b / 2 + hh * 0.55, -4, b / 2 + hh * 0.9, 0)
    block.closeSubpath()
    p.setBrush(linear(0, -hh, 0, 0, EIS_HELL, EIS_DUNKEL))
    p.drawPath(block)
    p.setPen(stift(QColor(245, 252, 255, 210), 1.6))
    p.setBrush(KEIN_PINSEL)
    p.drawPath(block)
    p.setPen(stift(QColor(255, 255, 255, 140), 2.2))
    p.drawLine(QPointF(-b / 2 + 8, -hh + 10), QPointF(-b / 2 + 8, -hh * 0.45))
    p.drawLine(QPointF(-b / 2 + 14, -hh + 10), QPointF(-b / 2 + 14, -hh + 22))
    p.setPen(KEIN_STIFT)
    p.setBrush(QColor(255, 255, 255, 90))
    p.drawRect(QRectF(-b / 2 + 4, -hh + 3, b * 0.5, 3))
    # Eiszapfen an der Oberkante
    if anteil > 0.8:
        p.setBrush(QColor(235, 250, 255, 200))
        for k, lang in enumerate((8, 5, 10, 6)):
            zx = -b / 2 + 10 + k * (b - 20) / 3
            z = QPainterPath()
            z.moveTo(zx - 3, -hh + 1)
            z.lineTo(zx + 3, -hh + 1)
            z.lineTo(zx, -hh + 1 + lang * (anteil - 0.8) * 5)
            z.closeSubpath()
            p.drawPath(z)
    p.setBrush(WEISS)
    for k in range(4):
        w = (t * 0.7 + k * 0.27) % 1
        if w < 0.3:
            stern(p, -b / 2 + 10 + (k * 37) % (b - 10), -hh * (0.2 + 0.2 * k), 3 * math.sin(w / 0.3 * math.pi))
    p.restore()


def rampen_punkt(x, y, b, h, u, rampe=1):
    """Punkt auf der Rampe des Eisblocks (u 0 = oben am Blockrand, 1 = unten am Boden), in Einheiten
    relativ zu (x, y) wie zeichne_eisblock."""
    p0 = (b / 2 + 2, -h + 6)
    c1 = (b / 2 + h * 0.25, -h * 0.55)
    c2 = (b / 2 + h * 0.55, -4)
    p1 = (b / 2 + h * 0.9, 0)
    a = 1 - u
    px = a ** 3 * p0[0] + 3 * a * a * u * c1[0] + 3 * a * u * u * c2[0] + u ** 3 * p1[0]
    py = a ** 3 * p0[1] + 3 * a * a * u * c1[1] + 3 * a * u * u * c2[1] + u ** 3 * p1[1]
    return x + rampe * px, y + py


# ---------------------------------------------------------------- Schraubstock und Ziehharmonika

SCHRAUB_OBEN = -84       # Oberkante der Gleitbahn, auf der das Gerät steht


def zeichne_schraubstock(p, x, y, spalt, kurbel=0.0, hinten=True):
    """Schraubstock auf Rollständer, Boden mittig bei (x, y). Die feste Backe innen bei x - 46,
    die bewegliche bei x - 46 + spalt. hinten=True: Ständer und Bahn, False: die Backen davor."""
    p.setPen(KEIN_STIFT)
    p.save()
    p.translate(x, y)
    links = -46
    rechts = links + spalt
    if hinten:
        p.setBrush(QColor(0, 0, 0, 45))
        p.drawEllipse(QRectF(-44, -3, 88, 6))
        p.setBrush(linear(-30, 0, 30, 0, METALL_DUNKEL, QColor('#3E444C')))
        p.drawRoundedRect(QRectF(-34, -12, 68, 6), 2, 2)
        for rx in (-28, 28):
            p.setBrush(QColor('#26292E'))
            kreis(p, rx, -4, 4)
            p.setBrush(METALL)
            kreis(p, rx, -4, 1.5)
        p.setBrush(linear(-5, 0, 5, 0, METALL, METALL_DUNKEL))
        p.drawRect(QRectF(-5, -72, 10, 62))
        p.setBrush(linear(0, SCHRAUB_OBEN, 0, SCHRAUB_OBEN + 12, SCHRAUB_BLAU.lighter(120), SCHRAUB_BLAU_DUNKEL))
        p.drawRoundedRect(QRectF(links - 14, SCHRAUB_OBEN, 118, 12), 3, 3)
        p.restore()
        return
    # feste Backe
    for bx, seite in ((links, -1), (rechts, 1)):
        x0 = bx - 13 if seite < 0 else bx
        p.setBrush(linear(x0, 0, x0 + 13, 0, SCHRAUB_BLAU.lighter(115), SCHRAUB_BLAU_DUNKEL))
        p.drawRoundedRect(QRectF(x0, SCHRAUB_OBEN - 30, 13, 32), 3, 3)
        p.setBrush(METALL)
        bk = QRectF(bx - 3 if seite < 0 else bx, SCHRAUB_OBEN - 28, 3, 24)
        p.drawRect(bk)
        p.setBrush(METALL_DUNKEL)
        for k in range(6):
            p.drawRect(QRectF(bk.left(), bk.top() + 2 + k * 4, 3, 1))
    # Spindel und Knebel an der beweglichen Backe
    sx = rechts + 13
    p.setBrush(linear(0, SCHRAUB_OBEN - 18, 0, SCHRAUB_OBEN - 12, METALL.lighter(110), METALL_DUNKEL))
    p.drawRect(QRectF(sx, SCHRAUB_OBEN - 18, 22, 6))
    p.setPen(stift(METALL_DUNKEL, 0.8))
    for k in range(5):
        gx = sx + 2 + k * 4 + (kurbel * 4 / (2 * math.pi)) % 4
        p.drawLine(QPointF(gx, SCHRAUB_OBEN - 18), QPointF(gx + 1.5, SCHRAUB_OBEN - 12))
    p.setPen(KEIN_STIFT)
    kx = sx + 24
    ky = SCHRAUB_OBEN - 15
    lang = 16 * math.cos(kurbel)
    p.setBrush(linear(kx - 3, 0, kx + 3, 0, METALL.lighter(115), METALL_DUNKEL))
    p.drawRoundedRect(QRectF(kx - 3, ky - 6, 6, 12), 2, 2)
    p.setPen(stift(METALL_DUNKEL, 3.2))
    p.drawLine(QPointF(kx, ky - lang), QPointF(kx, ky + lang))
    p.setPen(KEIN_STIFT)
    p.setBrush(QColor('#C0392B'))
    kreis(p, kx, ky - lang, 3.2)
    kreis(p, kx, ky + lang, 3.2)
    p.restore()


def kurbel_griff(x, y, spalt, kurbel, s):
    """Weltpunkt des oberen Knebelknaufs zu zeichne_schraubstock bei (x, y) in Weltkoordinaten."""
    kx = -46 + spalt + 13 + 24
    return x + kx * s, y + (SCHRAUB_OBEN - 15 - 16 * math.cos(kurbel)) * s


def zeichne_harmonika(p, x_links, y, quetsch=0.0, t=0.0, bild=1.0, flackern=True, falten=6, kaputt=0.0):
    """Röhrenmonitor, quer zur Ziehharmonika zusammengedrückt. Linke Gehäusekante bei x_links,
    Fuß bei y; quetsch 0 = normal, 1 = auf ein Drittel gefaltet. Ein heller Flimmerbalken läuft
    über alle Falten weiter."""
    breite0 = 68.0
    w0 = breite0 / falten
    faktor = 1 - 0.55 * quetsch
    w = w0 * faktor
    tief = 6 * quetsch
    band = (t * 0.9) % 1
    for k in range(falten):
        a0 = -34 + k * w0
        p.save()
        p.translate(x_links + k * w, y)
        tr = QTransform()
        if k % 2 == 0:
            tr.shear(0, tief / w)
        else:
            tr.translate(0, tief)
            tr.shear(0, -tief / w)
        p.setTransform(tr, True)
        p.scale(faktor, 1)
        p.translate(-a0, 0)
        p.setClipRect(QRectF(a0, -82, w0, 84))
        zeichne_monitor(p, 0, 0, bild=bild, t=t, kaputt=kaputt, flackern=flackern)
        if bild > 0:
            p.setPen(KEIN_STIFT)
            yb = -72 + band * 44
            p.setBrush(QColor(235, 255, 245, 170))
            p.drawRect(QRectF(a0, yb, w0, 6))
            p.setBrush(QColor(235, 255, 245, 60))
            p.drawRect(QRectF(a0, yb - 7, w0, 7))
        if quetsch > 0:
            p.setPen(KEIN_STIFT)
            if k % 2:
                p.setBrush(linear(a0, 0, a0 + w0, 0, QColor(0, 0, 0, int(110 * quetsch)), QColor(0, 0, 0, int(30 * quetsch))))
            else:
                p.setBrush(linear(a0, 0, a0 + w0, 0, QColor(255, 255, 255, int(10 * quetsch)), QColor(255, 255, 255, int(70 * quetsch))))
            p.drawRect(QRectF(a0, -82, w0, 84))
            p.setBrush(QColor(60, 50, 40, int(120 * quetsch)))
            p.drawRect(QRectF(a0 + (w0 - 1.5 if k % 2 == 0 else 0), -80, 1.5, 80))
        p.restore()


def harmonika_breite(quetsch):
    return 68.0 * (1 - 0.55 * quetsch)
