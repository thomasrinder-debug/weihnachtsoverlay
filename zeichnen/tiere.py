"""Wintertiere: Fuchs, Elch, Robbe, Schneeeule, Dachs, Schneehase, Rotkehlchen, Murmeltier,
dazu ihre Requisiten (Ast, Eisloch, Schneedecke, Stiefel).

Wie in figuren.py: KASTEN (Umriss in Einheiten, Fuß im Ursprung, Blick nach rechts),
KOPF (Punkt über dem Kopf) und zeichne(p, d) mit d.pose, d.t und eigenen Merkmalen.
"""
import math

from PyQt6.QtCore import QPointF, QRectF
from PyQt6.QtGui import QColor, QPainterPath

from .grundlagen import *  # noqa: F401,F403  Farben und Hilfen
from .figuren import augen, blick_x, brauen, mund, wangen
from .requisiten import zeichne_schneehaufen

MAUL = QColor('#5A1A1A')


def _bein(p, x, y, laenge, breite, winkel, hell, dunkel, pfote=None):
    """Bein, im Hüftpunkt (x, y) drehbar, hängt nach unten."""
    p.save()
    p.translate(x, y)
    p.rotate(winkel)
    p.setBrush(linear(-breite / 2, 0, breite / 2, 0, hell, dunkel))
    p.drawRoundedRect(QRectF(-breite / 2, -breite / 2, breite, laenge + breite / 2), breite / 2, breite / 2)
    if pfote is not None:
        p.setBrush(pfote)
        p.drawEllipse(QPointF(breite * 0.2, laenge - 1), breite * 0.7, breite * 0.45)
    p.restore()


def _schnurrhaare(p, x, y, laenge, farbe=QColor(60, 60, 60, 200)):
    p.setPen(stift(farbe, 0.9))
    for dy, w in ((-2, -0.15), (1, 0.05), (4, 0.25)):
        p.drawLine(QPointF(x, y + dy), QPointF(x + laenge, y + dy + laenge * w))
    p.setPen(KEIN_STIFT)


def _gesicht_vorn(p, x, y, r, pose, braue, abstand=0.42, augen_r=0.17):
    """Zwei Augen und Brauen für einen Tierkopf von vorn."""
    xs = (x - r * abstand, x + r * abstand)
    augen(p, xs, y, r * augen_r, r * augen_r * 1.15, pose, (pose.blick_x, pose.blick_y), 0.7)
    brauen(p, xs, y - r * 0.32, r * 0.3, pose, braue)


# ---------------------------------------------------------------- Fuchs

FUCHS = QColor('#E8742C')
FUCHS_DUNKEL = QColor('#A9481A')
FUCHS_HELL = QColor('#FFF4E6')
FUCHS_PFOTE = QColor('#3B2A22')


def zeichne_fuchsschwanz(p, x, y, wedel=0.0, hoch=0.0):
    """Buschiger Schwanz, Ansatz in (x, y), zeigt nach hinten (links)."""
    p.save()
    p.translate(x, y)
    p.rotate(-25 * hoch + wedel)
    pfad = QPainterPath()
    pfad.moveTo(0, -8)
    pfad.cubicTo(-30, -26, -70, -20, -92, 4)
    pfad.cubicTo(-80, 22, -40, 24, 0, 8)
    pfad.closeSubpath()
    p.setBrush(radial(-40, -2, 60, FUCHS.lighter(115), FUCHS_DUNKEL))
    p.drawPath(pfad)
    spitze = QPainterPath()
    spitze.moveTo(-70, -12)
    spitze.cubicTo(-84, -10, -96, -2, -92, 4)
    spitze.cubicTo(-86, 14, -76, 16, -66, 12)
    spitze.cubicTo(-72, 4, -74, -4, -70, -12)
    p.setBrush(FUCHS_HELL)
    p.drawPath(spitze)
    p.setPen(stift(FUCHS.lighter(140), 1.3))
    for k in range(4):
        p.drawLine(QPointF(-18 - k * 13, -6 + k), QPointF(-26 - k * 13, -3 + k))
    p.setPen(KEIN_STIFT)
    p.restore()


def zeichne_fuchsbein(p, x, y, winkel, hinten=False, laenge=48):
    k = 125 if hinten else 100
    _bein(p, x, y, laenge, 13, winkel, FUCHS.darker(k), FUCHS_DUNKEL.darker(k))
    p.save()
    p.translate(x, y)
    p.rotate(winkel)
    p.setBrush(FUCHS_PFOTE.darker(k))
    p.drawRoundedRect(QRectF(-6.5, laenge * 0.55, 13, laenge * 0.45 + 2), 6, 6)
    p.drawEllipse(QPointF(3, laenge), 8, 5)
    p.restore()


def zeichne_fuchskopf(p, hx, hy, pose, schnee=0.0):
    """Fuchskopf mit Mitte (hx, hy); schnee (0..1): Schneebart an der Schnauze."""
    for dx, dunkel in ((-12, True), (6, False)):
        ohr = QPainterPath()
        ohr.moveTo(hx + dx - 10, hy - 12)
        ohr.lineTo(hx + dx - 2, hy - 46)
        ohr.lineTo(hx + dx + 10, hy - 12)
        ohr.closeSubpath()
        p.setBrush(FUCHS_DUNKEL if dunkel else FUCHS)
        p.drawPath(ohr)
        innen = QPainterPath()
        innen.moveTo(hx + dx - 5, hy - 14)
        innen.lineTo(hx + dx - 2, hy - 36)
        innen.lineTo(hx + dx + 5, hy - 14)
        p.setBrush(FUCHS_PFOTE)
        p.drawPath(innen)
    if pose.kopf_vorn:
        p.setBrush(radial(hx - 6, hy - 6, 32, FUCHS.lighter(120), FUCHS_DUNKEL))
        p.drawEllipse(QPointF(hx, hy), 25, 22)
        for s in (-1, 1):
            backe = QPainterPath()
            backe.moveTo(hx + s * 24, hy - 2)
            backe.quadTo(hx + s * 30, hy + 14, hx + s * 6, hy + 18)
            backe.lineTo(hx, hy + 6)
            p.setBrush(FUCHS_HELL)
            p.drawPath(backe)
        p.setBrush(FUCHS_HELL)
        p.drawEllipse(QPointF(hx, hy + 12), 9, 9)
        p.setBrush(SCHWARZ)
        p.drawEllipse(QPointF(hx, hy + 7), 4.5, 3.5)
        _gesicht_vorn(p, hx, hy - 4, 24, pose, FUCHS_DUNKEL.darker(130))
        if pose.schreck > 0.2 or pose.mund_offen:
            mund(p, hx, hy + 14, 9, pose, MAUL)
        mx, my = hx, hy + 12
    else:
        p.setBrush(radial(hx - 4, hy - 6, 30, FUCHS.lighter(120), FUCHS_DUNKEL))
        p.drawEllipse(QPointF(hx, hy), 22, 20)
        schnauze = QPainterPath()
        schnauze.moveTo(hx + 8, hy - 10)
        schnauze.quadTo(hx + 30, hy - 4, hx + 40, hy + 2)
        schnauze.quadTo(hx + 30, hy + 14, hx + 4, hy + 16)
        schnauze.closeSubpath()
        p.setBrush(FUCHS)
        p.drawPath(schnauze)
        kinn = QPainterPath()
        kinn.moveTo(hx - 16, hy + 6)
        kinn.quadTo(hx + 10, hy + 22, hx + 36, hy + 6)
        kinn.quadTo(hx + 20, hy + 10, hx - 16, hy + 6)
        p.setBrush(FUCHS_HELL)
        p.drawPath(kinn)
        p.setBrush(SCHWARZ)
        p.drawEllipse(QPointF(hx + 39, hy + 1), 4.5, 3.5)
        augen(p, (hx + 10,), hy - 5, 3.8, 4.4, pose, (blick_x(pose), pose.blick_y), 0.75)
        brauen(p, (hx + 10,), hy - 12, 6, pose, FUCHS_DUNKEL.darker(130))
        if pose.schreck > 0.2 or pose.mund_offen:
            mund(p, hx + 26, hy + 10, 9, pose, MAUL)
        mx, my = hx + 32, hy + 6
    if schnee > 0:
        c = QColor(WEISS)
        c.setAlphaF(min(1.0, schnee))
        p.setBrush(c)
        for dx, dy, r in ((-4, 0, 9), (4, 4, 8), (-10, 6, 7), (8, -4, 7), (0, 9, 6)):
            kreis(p, mx + dx, my + dy, r * (0.6 + 0.4 * schnee))


class Fuchs:
    """Rotfuchs auf vier Pfoten. d.lauer (0..1): geduckt, lauschend; d.schnee: Schneebart;
    d.schwanz_hoch (0..1) hebt den Schwanz."""
    KASTEN = QRectF(-130, -150, 270, 156)
    KOPF = (58, -140)

    @staticmethod
    def zeichne(p, d):
        pose, t = d.pose, d.t
        lauer = getattr(d, 'lauer', 0.0)
        tief = 14 * lauer
        wedel = math.sin(t * 4) * 5
        zeichne_fuchsschwanz(p, -52, -66 + tief, wedel, getattr(d, 'schwanz_hoch', 0.0))
        zeichne_fuchsbein(p, -36, -54 + tief, pose.bein_h - 15 * lauer, True, 52 - tief)
        zeichne_fuchsbein(p, 32, -54 + tief, pose.bein_v + 15 * lauer, True, 52 - tief)
        p.setBrush(radial(-4, -78 + tief, 70, FUCHS.lighter(118), FUCHS_DUNKEL))
        p.drawEllipse(QRectF(-58, -90 + tief, 112, 48))
        p.setBrush(FUCHS_HELL)
        p.drawEllipse(QRectF(22, -78 + tief, 34, 30))
        zeichne_fuchsbein(p, -26, -54 + tief, pose.bein_v - 15 * lauer, False, 52 - tief)
        zeichne_fuchsbein(p, 42, -54 + tief, pose.bein_h + 15 * lauer, False, 52 - tief)
        zeichne_fuchskopf(p, 58, -96 + tief * 1.6, pose, getattr(d, 'schnee', 0.0))


# ---------------------------------------------------------------- Elch

ELCH = QColor('#7C4F2E')
ELCH_DUNKEL = QColor('#45291A')
ELCH_HELL = QColor('#A9784F')
GEWEIH = QColor('#E3D0A6')
GEWEIH_DUNKEL = QColor('#A68A5A')


def zeichne_schaufel(p, x, y, dunkel=False):
    """Schaufelgeweih, Ansatz in (x, y), breitet sich nach oben und hinten aus."""
    a, b = (GEWEIH.darker(118), GEWEIH_DUNKEL.darker(118)) if dunkel else (GEWEIH, GEWEIH_DUNKEL)
    p.save()
    p.translate(x, y)
    p.rotate(-28)
    p.translate(-x, -y)
    p.setBrush(linear(x, y - 60, x, y, a, b))
    p.drawRoundedRect(QRectF(x - 4, y - 18, 9, 20), 4, 4)
    pfad = QPainterPath()
    pfad.moveTo(x - 2, y - 14)
    pfad.cubicTo(x - 30, y - 18, x - 60, y - 34, x - 66, y - 56)
    zacken = [(-66, -56), (-58, -74), (-48, -60), (-40, -80), (-30, -62), (-20, -84), (-10, -62),
              (0, -82), (8, -58), (18, -72), (16, -44)]
    for dx, dy in zacken[1:]:
        pfad.lineTo(x + dx, y + dy)
    pfad.cubicTo(x + 10, y - 30, x + 4, y - 18, x - 2, y - 14)
    p.drawPath(pfad)
    p.setPen(stift(b.darker(110), 1.2))
    p.drawLine(QPointF(x - 50, y - 46), QPointF(x - 8, y - 30))
    p.setPen(KEIN_STIFT)
    p.restore()


class Elch:
    """Großer Elch mit Schaufelgeweih. d.spreiz (0..1): Beine gespreizt gegen eine Last;
    d.nicken (Grad): Kopf und Geweih nach vorn unten; d.kipp (Grad): ganzer Elch kippt um
    den Punkt d.drehpunkt (Einheiten) nach vorn, bei etwa 105 steht er auf dem Geweih."""
    KASTEN = QRectF(-110, -330, 300, 336)
    KOPF = (96, -300)
    GEWEIH_SPITZE = (70, -282)     # Sitzplatz oben auf dem Geweih (ohne Nicken)

    @staticmethod
    def zeichne(p, d):
        pose, t = d.pose, d.t
        spreiz = getattr(d, 'spreiz', 0.0)
        nicken = getattr(d, 'nicken', 0.0)
        kipp = getattr(d, 'kipp', 0.0)
        if kipp:
            px, py = getattr(d, 'drehpunkt', (150, 0))
            p.translate(px, py)
            p.rotate(kipp)
            p.translate(-px, -py)
        zitter = math.sin(t * 50) * 1.5 * spreiz
        def beine(hinten):
            k = 125 if hinten else 100
            paar = ((-62, pose.bein_h, 1), (44, pose.bein_v, -1)) if hinten else ((-50, pose.bein_v, 1), (56, pose.bein_h, -1))
            for x, w, seite in paar:
                winkel = w + seite * 24 * spreiz
                _bein(p, x, -128, 126 - 8 * spreiz, 15, winkel, ELCH.darker(k), ELCH_DUNKEL.darker(k))
                p.save()
                p.translate(x, -128)
                p.rotate(winkel)
                p.setBrush(SCHWARZ.lighter(130).darker(k))
                p.drawRoundedRect(QRectF(-9, 116 - 8 * spreiz, 19, 12), 4, 4)
                p.restore()
        beine(True)
        # Rumpf mit Widerrist-Buckel
        p.setBrush(radial(-10, -170, 120, ELCH_HELL, ELCH_DUNKEL))
        p.drawEllipse(QRectF(-86, -196 + zitter, 160, 80))
        p.drawEllipse(QPointF(36, -186 + zitter), 42, 38)
        p.setBrush(ELCH_DUNKEL)
        p.drawEllipse(QPointF(-84, -172 + zitter), 9, 7)
        p.setPen(stift(ELCH_DUNKEL.lighter(120), 1.5))
        for k in range(5):
            x = -60 + k * 22
            p.drawLine(QPointF(x, -190 + zitter), QPointF(x + 4, -182 + zitter))
        p.setPen(KEIN_STIFT)
        beine(False)
        # Hals und Kopf, drehen sich ums Halsende
        p.save()
        p.translate(56, -200 + zitter)
        p.rotate(nicken)
        hx, hy = 40, -36
        hals = QPainterPath()
        hals.moveTo(-18, 16)
        hals.quadTo(4, -40, hx, hy - 10)
        hals.lineTo(hx + 8, hy + 20)
        hals.quadTo(14, 10, 22, 30)
        hals.closeSubpath()
        p.setBrush(radial(10, -10, 60, ELCH_HELL, ELCH_DUNKEL))
        p.drawPath(hals)
        zeichne_schaufel(p, hx - 10, hy - 18, True)
        # Ohr
        ohr = QPainterPath()
        ohr.moveTo(hx - 12, hy - 14)
        ohr.quadTo(hx - 34, hy - 26, hx - 30, hy - 10)
        ohr.quadTo(hx - 22, hy - 6, hx - 10, hy - 6)
        p.setBrush(ELCH.darker(110))
        p.drawPath(ohr)
        # Kopf mit überhängender Nase und Bart
        kopf = QPainterPath()
        kopf.moveTo(hx - 14, hy - 16)
        kopf.cubicTo(hx + 10, hy - 22, hx + 40, hy - 6, hx + 54, hy + 8)
        kopf.cubicTo(hx + 62, hy + 18, hx + 58, hy + 34, hx + 44, hy + 34)
        kopf.cubicTo(hx + 26, hy + 34, hx + 6, hy + 26, hx - 10, hy + 16)
        kopf.closeSubpath()
        p.setBrush(radial(hx + 10, hy, 50, ELCH_HELL.lighter(105), ELCH))
        p.drawPath(kopf)
        p.setBrush(ELCH_DUNKEL.lighter(110))
        bart = QPainterPath()
        bart.moveTo(hx + 4, hy + 22)
        bart.quadTo(hx + 4, hy + 50, hx + 12, hy + 56)
        bart.quadTo(hx + 18, hy + 40, hx + 22, hy + 28)
        p.drawPath(bart)
        p.setBrush(ELCH_DUNKEL)
        p.drawEllipse(QPointF(hx + 52, hy + 20), 4, 3)
        zeichne_schaufel(p, hx - 2, hy - 16)
        augen(p, (hx + 10,), hy - 2, 4.2, 5, pose, (blick_x(pose) if not pose.kopf_vorn else pose.blick_x,
                                                    pose.blick_y), 0.75)
        brauen(p, (hx + 10,), hy - 10, 7, pose, ELCH_DUNKEL.darker(120))
        if pose.schreck > 0.2 or pose.mund_offen:
            mund(p, hx + 44, hy + 30, 10, pose, MAUL)
        p.restore()


def elch_punkt(d, x, y, kopf=False):
    """Bildpunkt zu (x, y) in Elch-Einheiten; kopf=True: Punkt am Kopf (dreht mit dem Nicken)."""
    if kopf:
        n = math.radians(getattr(d, 'nicken', 0.0))
        x, y = 56 + x * math.cos(n) - y * math.sin(n), -200 + x * math.sin(n) + y * math.cos(n)
    k = math.radians(getattr(d, 'kipp', 0.0))
    if k:
        px, py = getattr(d, 'drehpunkt', (150, 0))
        x, y = px + (x - px) * math.cos(k) - (y - py) * math.sin(k), py + (x - px) * math.sin(k) + (y - py) * math.cos(k)
    return d.trafo().map(QPointF(x, y))


def elch_geweih_punkt(d):
    """Sitzplatz oben auf dem Geweih."""
    return elch_punkt(d, -14, -106, kopf=True)


# ---------------------------------------------------------------- Rotkehlchen

KEHLCHEN_BRAUN = QColor('#8A6A4A')
KEHLCHEN_ROT = QColor('#F0662E')


class Rotkehlchen:
    """Kleines Rotkehlchen. d.plustern (1 = normal, 4 = Riesenkugel), d.fluegel (Grad), d.zittern,
    d.roll (Grad) dreht die Kugel um ihre Mitte."""
    KASTEN = QRectF(-90, -190, 180, 196)
    KOPF = (4, -40)

    @staticmethod
    def kasten_fuer(d):
        k = getattr(d, 'plustern', 1.0)
        r = 17 * k
        return QRectF(-r - 14, -14 - 2 * r - 10, 2 * r + 28, 2 * r + 30)

    @staticmethod
    def zeichne(p, d):
        pose, t = d.pose, d.t
        k = getattr(d, 'plustern', 1.0)
        r = 17 * k
        cy = -14 - r
        zit = math.sin(t * 60) * 1.2 * getattr(d, 'zittern', 0.0)
        p.translate(zit, 0)
        duenn = getattr(d, 'duenn', 1.0)
        if duenn != 1.0:
            p.scale(duenn, 2 - duenn)
        roll = getattr(d, 'roll', 0.0)
        if roll:
            p.translate(0, 14 * (1 - math.cos(math.radians(roll))) / 2)
            p.translate(0, cy)
            p.rotate(roll)
            p.translate(0, -cy)
        # Beinchen
        p.setPen(stift(QColor('#6B4A2E'), 2))
        for dx in (-4, 4):
            bx = dx + pose.bein_v * 0.1
            p.drawLine(QPointF(dx, cy + r * 0.85), QPointF(bx, -1))
            p.drawLine(QPointF(bx, -1), QPointF(bx + 5, 0))
        p.setPen(KEIN_STIFT)
        # Schwanz
        p.setBrush(KEHLCHEN_BRAUN.darker(120))
        schwanz = QPainterPath()
        schwanz.moveTo(-r * 0.7, cy)
        schwanz.lineTo(-r * 0.7 - 18, cy - 10 - 4 * k)
        schwanz.lineTo(-r * 0.7 - 12, cy + 4)
        p.drawPath(schwanz)
        # Körper: Federkugel mit Flaumrand
        if k > 1.2:
            p.setBrush(KEHLCHEN_BRAUN.lighter(110))
            n = int(10 + 6 * k)
            for i in range(n):
                w = 2 * math.pi * i / n + t * 0.4
                kreis(p, math.cos(w) * r * 0.95, cy + math.sin(w) * r * 0.95, 3 + 1.2 * k)
        p.setBrush(radial(-r * 0.3, cy - r * 0.4, r * 1.6, KEHLCHEN_BRAUN.lighter(125), KEHLCHEN_BRAUN.darker(120)))
        kreis(p, 0, cy, r)
        p.setBrush(radial(r * 0.3, cy + r * 0.1, r * 1.0, KEHLCHEN_ROT.lighter(115), KEHLCHEN_ROT.darker(110)))
        p.drawEllipse(QPointF(r * 0.32, cy + r * 0.05), r * 0.62, r * 0.7)
        p.setBrush(QColor('#F4ECE0'))
        p.drawEllipse(QPointF(r * 0.1, cy + r * 0.72), r * 0.45, r * 0.22)
        # Flügel
        p.save()
        p.translate(-r * 0.15, cy - r * 0.1)
        p.rotate(getattr(d, 'fluegel', 0.0))
        p.setBrush(KEHLCHEN_BRAUN.darker(135))
        p.drawEllipse(QRectF(-r * 0.2 - 9, -6, 22, 12))
        p.restore()
        # Kopf ist Teil der Kugel: Auge und Schnabel
        sx = r * 0.98
        p.setBrush(QColor('#3A2A1E'))
        schnabel = QPainterPath()
        schnabel.moveTo(sx - 2, cy - r * 0.35 - 3)
        schnabel.lineTo(sx + 9, cy - r * 0.35)
        schnabel.lineTo(sx - 2, cy - r * 0.35 + 3)
        p.drawPath(schnabel)
        if pose.mund_offen or pose.schreck > 0.2:
            schnabel = QPainterPath()
            schnabel.moveTo(sx - 2, cy - r * 0.35)
            schnabel.lineTo(sx + 8, cy - r * 0.35 + 6)
            schnabel.lineTo(sx - 2, cy - r * 0.35 + 3)
            p.drawPath(schnabel)
        augen(p, (r * 0.55,), cy - r * 0.5, 3.0, 3.4, pose, (blick_x(pose), pose.blick_y), 0.8)
        brauen(p, (r * 0.55,), cy - r * 0.5 - 6, 5, pose, KEHLCHEN_BRAUN.darker(160))


# ---------------------------------------------------------------- Schneeeule

EULE = QColor('#FBFBF8')
EULE_SCHATTEN = QColor('#C9D2DE')
EULE_TUPFEN = QColor('#4A4A52')


def _tupfen(p, punkte, g=2.6):
    p.setBrush(EULE_TUPFEN)
    for x, y in punkte:
        p.drawEllipse(QPointF(x, y), g, g * 0.6)


class Schneeeule:
    """Schneeeule, sitzend, schaut meist nach vorn. d.fluegel (0..1) breitet die Flügel aus,
    d.zerzaust (0..1) sträubt die Federn, d.flattern (Grad) schlägt die Flügel."""
    KASTEN = QRectF(-110, -132, 220, 138)
    KOPF = (0, -126)

    @staticmethod
    def zeichne(p, d):
        pose, t = d.pose, d.t
        f = getattr(d, 'fluegel', 0.0)
        zz = getattr(d, 'zerzaust', 0.0)
        fl = getattr(d, 'flattern', 0.0)
        # Flügel
        for s in (-1, 1):
            p.save()
            p.translate(s * 26, -66)
            p.rotate(s * (-100 * f - fl))
            p.setBrush(radial(0, 20, 50, EULE, EULE_SCHATTEN))
            fluegel = QPainterPath()
            fluegel.moveTo(-10, -6)
            fluegel.cubicTo(-14 * s + s * 8, 30, s * 4, 56, s * 6, 64)
            fluegel.cubicTo(s * 18, 50, s * 18, 20, 10 * s, -6)
            fluegel.closeSubpath()
            p.drawPath(fluegel)
            _tupfen(p, [(s * 4, 20), (s * 8, 34), (s * 2, 44), (s * 10, 50)], 2.2)
            p.restore()
        # Körper
        p.setBrush(radial(-8, -60, 70, EULE, EULE_SCHATTEN))
        p.drawEllipse(QRectF(-36, -104, 72, 102))
        _tupfen(p, [(-14, -46), (6, -40), (-4, -30), (16, -54), (-20, -24), (12, -22), (0, -56)])
        # Füße
        p.setBrush(EULE_SCHATTEN)
        for s in (-1, 1):
            p.drawEllipse(QPointF(s * 12, -3), 10, 6)
            p.setPen(stift(SCHWARZ, 1.6))
            for k in (-5, 0, 5):
                p.drawLine(QPointF(s * 12 + k, 1), QPointF(s * 12 + k + 1, 5))
            p.setPen(KEIN_STIFT)
        # Kopf
        hy = -104
        p.setBrush(radial(-6, hy - 8, 42, EULE, EULE_SCHATTEN))
        p.drawEllipse(QPointF(0, hy), 34, 28)
        _tupfen(p, [(-18, hy - 18), (-6, hy - 22), (8, hy - 21), (20, hy - 16)], 2.0)
        if zz > 0:
            p.setBrush(EULE)
            for k in range(7):
                w = math.radians(-150 + k * 20)
                fx, fy = math.cos(w) * 30, hy + math.sin(w) * 26
                feder = QPainterPath()
                feder.moveTo(fx - 4, fy)
                feder.lineTo(fx + math.cos(w) * 14 * zz, fy + math.sin(w) * 14 * zz)
                feder.lineTo(fx + 4, fy)
                p.drawPath(feder)
        # Gesichtsschleier
        p.setBrush(QColor(255, 255, 255))
        for s in (-1, 1):
            kreis(p, s * 12, hy + 2, 13)
        for x in (-12, 12):
            g = 1 + 0.35 * pose.schreck
            if pose.auge_zu:
                p.setPen(stift(SCHWARZ, 2))
                p.drawLine(QPointF(x - 6, hy + 1), QPointF(x + 6, hy + 1))
                p.setPen(KEIN_STIFT)
                continue
            p.setBrush(radial(x, hy + 1, 9 * g, QColor('#FFE24A'), QColor('#E9A814')))
            kreis(p, x, hy + 1, 8 * g)
            p.setBrush(SCHWARZ)
            kreis(p, x + pose.blick_x * 3, hy + 1 + pose.blick_y * 3, 4.6 * g * (1 - 0.3 * pose.schreck))
            p.setBrush(WEISS)
            kreis(p, x + pose.blick_x * 3 + 1.6, hy - 1 + pose.blick_y * 3, 1.4)
        # Lider (halb zu = trockener Blick)
        if getattr(d, 'muede', 0.0) > 0:
            p.setBrush(EULE)
            for x in (-12, 12):
                p.drawChord(QRectF(x - 9, hy - 8, 18, 18 * getattr(d, 'muede', 0.0)), 0, 180 * 16)
                p.drawRect(QRectF(x - 9, hy - 8, 18, 9 * getattr(d, 'muede', 0.0)))
        brauen(p, (-12, 12), hy - 10, 9, pose, EULE_TUPFEN)
        p.setBrush(QColor('#3A3A3A'))
        schnabel = QPainterPath()
        schnabel.moveTo(-4, hy + 8)
        schnabel.quadTo(0, hy + 20 + (5 if pose.mund_offen or pose.schreck > 0.2 else 0), 4, hy + 8)
        schnabel.closeSubpath()
        p.drawPath(schnabel)


def zeichne_ast(p, laenge, biegung, zweige=True):
    """Kahler Ast aus der Wand (Ursprung) nach rechts, Spitze biegt sich um 'biegung' Einheiten nach unten."""
    pfad = QPainterPath()
    pfad.moveTo(-10, -9)
    pfad.cubicTo(laenge * 0.4, -8, laenge * 0.75, -3 + biegung * 0.45, laenge, biegung - 1)
    pfad.lineTo(laenge, biegung + 2)
    pfad.cubicTo(laenge * 0.75, 4 + biegung * 0.45, laenge * 0.4, 9, -10, 11)
    pfad.closeSubpath()
    p.setBrush(linear(0, -10, 0, 12, QColor('#7B5A3E'), QColor('#3E2A1B')))
    p.drawPath(pfad)
    p.setBrush(WEISS)
    schnee = QPainterPath()
    schnee.moveTo(0, -8)
    schnee.cubicTo(laenge * 0.4, -14, laenge * 0.7, -8 + biegung * 0.4, laenge * 0.8, ast_y(laenge * 0.8, laenge, biegung) - 6)
    schnee.cubicTo(laenge * 0.6, -4 + biegung * 0.3, laenge * 0.3, -6, 0, -4)
    p.drawPath(schnee)
    if zweige:
        p.setPen(stift(QColor('#4E3826'), 3))
        for f, w in ((0.35, -50), (0.6, 40), (0.8, -35)):
            x = laenge * f
            y = ast_y(x, laenge, biegung)
            p.drawLine(QPointF(x, y), QPointF(x + 22 * math.cos(math.radians(w)), y + 22 * math.sin(math.radians(w))))
        p.setPen(KEIN_STIFT)


def ast_y(x, laenge, biegung):
    """Höhe der Astoberkante bei x (Einheiten)."""
    u = max(0.0, min(1.0, x / laenge))
    return -9 + biegung * u * u


# ---------------------------------------------------------------- Robbe

ROBBE = QColor('#9AA3AE')
ROBBE_DUNKEL = QColor('#5D6672')
ROBBE_BAUCH = QColor('#D5DAE0')


class Robbe:
    """Robbe, aufgerichtet; Ursprung tief im Körper (für das Eisloch). d.zieh (1..2): wird
    länger wie eine Ziehharmonika, d.verschraenkt: Flossen vor der Brust gekreuzt,
    d.flosse (Grad) bewegt die Vorderflossen, d.schwanz: Schwanzflosse sichtbar (liegend)."""
    KASTEN = QRectF(-60, -290, 120, 345)
    KOPF = (0, -170)

    @staticmethod
    def zeichne(p, d):
        pose, t = d.pose, d.t
        zieh = getattr(d, 'zieh', 1.0)
        laenge = 130 * zieh
        top = -laenge
        if getattr(d, 'schwanz', False):
            for s in (-1, 1):
                flosse = QPainterPath()
                flosse.moveTo(0, 30)
                flosse.cubicTo(s * 10, 46, s * 26, 52, s * 30, 50)
                flosse.cubicTo(s * 22, 40, s * 10, 34, 0, 24)
                p.setBrush(ROBBE_DUNKEL)
                p.drawPath(flosse)
        rumpf = QPainterPath()
        rumpf.moveTo(-30, 40)
        rumpf.cubicTo(-38, top * 0.4, -30, top + 30, -22, top + 18)
        rumpf.lineTo(22, top + 18)
        rumpf.cubicTo(30, top + 30, 38, top * 0.4, 30, 40)
        rumpf.closeSubpath()
        p.setBrush(linear(-34, 0, 34, 0, ROBBE.lighter(112), ROBBE_DUNKEL))
        p.drawPath(rumpf)
        p.setBrush(ROBBE_BAUCH)
        p.drawEllipse(QRectF(-14, top + 30, 30, laenge + 10))
        if zieh > 1.05:
            p.setPen(stift(ROBBE_DUNKEL.darker(115), 1.6))
            n = 5
            for i in range(n):
                y = top + 40 + (laenge - 40) * (i + 0.5) / n
                p.drawArc(QRectF(-32, y - 4, 64, 8), 200 * 16, 140 * 16)
            p.setPen(KEIN_STIFT)
        p.setBrush(ROBBE_DUNKEL.lighter(110))
        for x, y in ((-20, top + 60), (18, top + 80), (-14, top + 100)):
            kreis(p, x, y, 2.5)
        # Kopf
        hy = top - 4
        p.setBrush(radial(-6, hy - 8, 40, ROBBE.lighter(115), ROBBE_DUNKEL))
        p.drawEllipse(QPointF(0, hy), 27, 25)
        p.setBrush(ROBBE_BAUCH)
        p.drawEllipse(QPointF(0, hy + 12), 14, 10)
        p.setBrush(SCHWARZ)
        p.drawEllipse(QPointF(0, hy + 6), 5, 3.6)
        _schnurrhaare(p, 8, hy + 12, 18)
        p.save()
        p.translate(0, 0)
        p.scale(-1, 1)
        _schnurrhaare(p, 8, hy + 12, 18)
        p.restore()
        xs = (-11, 11)
        g = 1 + 0.35 * pose.schreck
        for x in xs:
            if pose.auge_zu:
                p.setPen(stift(SCHWARZ, 2))
                p.drawArc(QRectF(x - 5, hy - 10, 10, 8), 200 * 16, 140 * 16)
                p.setPen(KEIN_STIFT)
                continue
            p.setBrush(SCHWARZ)
            p.drawEllipse(QPointF(x + pose.blick_x * 1.5, hy - 5 + pose.blick_y * 1.5), 6 * g, 7 * g)
            p.setBrush(WEISS)
            kreis(p, x + pose.blick_x * 1.5 + 2, hy - 8 + pose.blick_y * 1.5, 2)
        brauen(p, xs, hy - 15, 8, pose, ROBBE_DUNKEL.darker(130))
        if pose.schreck > 0.2 or pose.mund_offen:
            mund(p, 0, hy + 17, 9, pose, MAUL)
        # Vorderflossen
        if getattr(d, 'verschraenkt', False):
            for s in (-1, 1):
                p.save()
                p.translate(s * 24, top + 50)
                p.rotate(s * 70)
                p.setBrush(ROBBE_DUNKEL.lighter(105 + 15 * (s > 0)))
                p.drawEllipse(QRectF(-8, -4, 16, 36))
                p.restore()
        else:
            for s in (-1, 1):
                p.save()
                p.translate(s * 26, top + 52)
                p.rotate(s * (20 + getattr(d, 'flosse', 0.0)))
                p.setBrush(ROBBE_DUNKEL)
                p.drawEllipse(QRectF(-7, -4, 14, 38))
                p.restore()


def zeichne_eisloch_hinten(p, b):
    """Dunkles Wasserloch am Boden, Mitte im Ursprung, Breite b (Einheiten)."""
    p.setBrush(radial(0, 0, b * 0.5, QColor('#1E3A5A'), QColor('#0E1E30')))
    p.drawEllipse(QPointF(0, 0), b / 2, b * 0.14)


def zeichne_eisloch_vorn(p, b, rand):
    """Eisrand vor der Robbe; rand (0..1) friert das Loch zu."""
    innen = b / 2 * (1 - 0.55 * rand)
    pfad = QPainterPath()
    pfad.addEllipse(QPointF(0, 0), b / 2 + 34, b * 0.14 + 16)
    loch = QPainterPath()
    loch.addEllipse(QPointF(0, -2), innen, b * 0.14 * (1 - 0.4 * rand))
    oben = QPainterPath()
    oben.addRect(QRectF(-b, -b, 2 * b, b - 2))
    vorn = pfad.subtracted(loch).subtracted(oben)
    p.setBrush(linear(0, -10, 0, 30, QColor('#F4FAFF'), QColor('#9CC3E4')))
    p.drawPath(vorn)
    hinten = pfad.subtracted(loch).intersected(oben)
    p.setBrush(linear(0, -30, 0, 0, QColor('#E6F2FC'), QColor('#B5D4EE')))
    p.drawPath(hinten)
    p.setPen(stift(QColor(255, 255, 255, 220), 1.5))
    p.setBrush(KEIN_PINSEL)
    p.drawArc(QRectF(-innen, -b * 0.14 - 2, 2 * innen, b * 0.28), 200 * 16, 140 * 16)
    p.setPen(KEIN_STIFT)


# ---------------------------------------------------------------- Dachs

DACHS = QColor('#8C8D93')
DACHS_DUNKEL = QColor('#4E4F56')


def zeichne_dachskopf(p, hx, hy, pose, muetze=False):
    """Dachskopf mit Streifen, Schnauze nach rechts, Mitte (hx, hy)."""
    p.setBrush(DACHS_DUNKEL)
    kreis(p, hx - 14, hy - 16, 6)
    p.setBrush(radial(hx, hy - 4, 30, WEISS, QColor('#D8D8DC')))
    kopf = QPainterPath()
    kopf.moveTo(hx - 20, hy - 14)
    kopf.cubicTo(hx, hy - 22, hx + 30, hy - 6, hx + 40, hy + 4)
    kopf.cubicTo(hx + 30, hy + 16, hx - 6, hy + 20, hx - 22, hy + 10)
    kopf.closeSubpath()
    p.drawPath(kopf)
    p.setBrush(SCHWARZ.lighter(140))
    streifen = QPainterPath()
    streifen.moveTo(hx - 20, hy - 10)
    streifen.cubicTo(hx, hy - 14, hx + 20, hy - 6, hx + 32, hy)
    streifen.cubicTo(hx + 20, hy + 2, hx, hy + 2, hx - 20, hy + 2)
    streifen.closeSubpath()
    p.drawPath(streifen)
    p.setBrush(SCHWARZ)
    p.drawEllipse(QPointF(hx + 40, hy + 3), 4.5, 3.5)
    augen(p, (hx + 10,), hy - 3, 3.2, 3.6, pose, (blick_x(pose), pose.blick_y), 0.75)
    brauen(p, (hx + 10,), hy - 10, 5, pose, QColor('#222222'))
    if pose.schreck > 0.2 or pose.mund_offen:
        mund(p, hx + 28, hy + 10, 8, pose, MAUL)
    if muetze:
        p.save()
        p.translate(hx - 4, hy - 16)
        p.rotate(-10)
        p.scale(0.6, 0.6)
        from .requisiten import zeichne_muetze_lose
        zeichne_muetze_lose(p)
        p.restore()


class Dachs:
    """Dachs, flach und breit. d.muetze: trägt die Mütze des Weihnachtsmanns."""
    KASTEN = QRectF(-90, -96, 190, 102)
    KOPF = (64, -80)

    @staticmethod
    def zeichne(p, d):
        pose = d.pose
        for x, w, k in ((-46, pose.bein_h, 125), (34, pose.bein_v, 125), (-36, pose.bein_v, 100),
                        (44, pose.bein_h, 100)):
            if k == 100:
                p.setBrush(radial(-10, -50, 80, DACHS.lighter(115), DACHS_DUNKEL))
                if x == -36:
                    p.drawEllipse(QRectF(-76, -70, 140, 52))
                    p.setPen(stift(DACHS_DUNKEL, 1.3))
                    for i in range(6):
                        p.drawLine(QPointF(-60 + i * 18, -66), QPointF(-56 + i * 18, -58))
                    p.setPen(KEIN_STIFT)
            _bein(p, x, -34, 30, 14, w, SCHWARZ.lighter(150 if k == 100 else 120), SCHWARZ, SCHWARZ)
        zeichne_dachskopf(p, 62, -48, pose, getattr(d, 'muetze', False))


# ---------------------------------------------------------------- Schneehase

HASE = QColor('#FDFDFD')
HASE_SCHATTEN = QColor('#C8D6E8')


class Schneehase:
    """Weißer Schneehase, sitzend. d.haufen (0..1): reglos wie ein Schneehaufen getarnt,
    d.sprung (0..1): gestreckt im Sprung."""
    KASTEN = QRectF(-70, -150, 150, 156)
    KOPF = (24, -140)

    @staticmethod
    def zeichne(p, d):
        pose, t = d.pose, d.t
        haufen = getattr(d, 'haufen', 0.0)
        sprung = max(getattr(d, 'sprung', 0.0), min(1.0, abs(pose.bein_v) / 40))
        if haufen < 1:
            p.save()
            p.setOpacity(p.opacity() * (1 - haufen * 0.0))
            # Hinterlauf, lang beim Sprung
            p.save()
            p.translate(-14, -20)
            p.rotate(-50 * sprung)
            p.setBrush(radial(-6, -6, 40, HASE, HASE_SCHATTEN))
            p.drawEllipse(QRectF(-26, -24, 46, 36))
            p.drawRoundedRect(QRectF(-30 - 20 * sprung, 8, 56, 13), 6, 6)
            p.restore()
            # Körper
            p.setBrush(radial(-10, -60, 70, HASE, HASE_SCHATTEN))
            p.save()
            p.translate(4, -46)
            p.rotate(30 * sprung)
            p.drawEllipse(QRectF(-38, -34, 72, 66))
            p.restore()
            p.drawRoundedRect(QRectF(20 + 14 * sprung, -16 - 10 * sprung, 13, 18), 6, 6)
            kreis(p, -40, -40, 10)
            # Kopf und Ohren
            hx, hy = 26 + 12 * sprung, -88 + 10 * sprung
            for dx, w, dunkel in ((-12, -28, True), (-2, -14, False)):
                p.save()
                p.translate(hx + dx, hy - 14)
                p.rotate(w - 50 * sprung)
                p.setBrush(HASE_SCHATTEN if dunkel else HASE)
                p.drawEllipse(QRectF(-7, -50, 14, 52))
                p.setBrush(QColor('#F5C8CF'))
                p.drawEllipse(QRectF(-3.5, -42, 7, 36))
                p.setBrush(SCHWARZ)
                p.drawChord(QRectF(-7, -50, 14, 16), 0, 180 * 16)
                p.restore()
            p.setBrush(radial(hx - 4, hy - 6, 30, HASE, HASE_SCHATTEN))
            p.drawEllipse(QPointF(hx, hy), 22, 19)
            p.drawEllipse(QPointF(hx + 16, hy + 6), 10, 8)
            p.setBrush(QColor('#E58A9A'))
            p.drawEllipse(QPointF(hx + 25, hy + 3), 3, 2.5)
            _schnurrhaare(p, hx + 24, hy + 8, 14, QColor(120, 120, 140, 200))
            augen(p, (hx + 8,), hy - 4, 4, 4.8, pose, (blick_x(pose), pose.blick_y), 0.78)
            brauen(p, (hx + 8,), hy - 12, 6, pose, HASE_SCHATTEN.darker(150))
            wangen(p, (hx + 10,), hy + 8, 5)
            if pose.schreck > 0.2 or pose.mund_offen:
                mund(p, hx + 18, hy + 12, 7, pose, MAUL)
            p.restore()
        if haufen > 0:
            p.save()
            p.setOpacity(p.opacity() * haufen)
            zeichne_schneehaufen(p, 0, 0, 130, 82)
            p.restore()


# ---------------------------------------------------------------- Murmeltier

MURMEL = QColor('#A47A50')
MURMEL_DUNKEL = QColor('#5E4127')
MURMEL_HELL = QColor('#E6CBA4')


class Murmeltier:
    """Murmeltier. d.schlaf (0..1): eingerollt schlafend, d.pfiff (0..1): aufgerichtet mit
    riesig offenem Maul, d.recken (Einheiten): streckt sich in die Höhe."""
    KASTEN = QRectF(-70, -220, 150, 226)
    KOPF = (6, -200)

    @staticmethod
    def zeichne(p, d):
        pose, t = d.pose, d.t
        schlaf = getattr(d, 'schlaf', 0.0)
        pfiff = getattr(d, 'pfiff', 0.0)
        if schlaf > 0.5:
            atmen = math.sin(t * 2.0) * 3
            p.setBrush(radial(-10, -40, 70, MURMEL.lighter(115), MURMEL_DUNKEL))
            p.drawEllipse(QRectF(-56, -66 - atmen, 112, 66 + atmen))
            p.setBrush(MURMEL_DUNKEL)
            schwanz = QPainterPath()
            schwanz.moveTo(-50, -16)
            schwanz.cubicTo(-70, -10, -66, 4, -40, 0)
            p.drawPath(schwanz)
            hx, hy = 30, -26
            p.setBrush(radial(hx - 4, hy - 4, 30, MURMEL.lighter(120), MURMEL_DUNKEL))
            p.drawEllipse(QPointF(hx, hy), 24, 20)
            p.setBrush(MURMEL_HELL)
            p.drawEllipse(QPointF(hx + 14, hy + 6), 11, 8)
            p.setBrush(SCHWARZ)
            p.drawEllipse(QPointF(hx + 22, hy + 3), 3.5, 2.8)
            p.setPen(stift(SCHWARZ, 1.8))
            p.setBrush(KEIN_PINSEL)
            p.drawArc(QRectF(hx + 2, hy - 10, 10, 7), 200 * 16, 140 * 16)
            p.setPen(KEIN_STIFT)
            p.setBrush(MURMEL_DUNKEL)
            kreis(p, hx - 10, hy - 16, 5)
            return
        recken = getattr(d, 'recken', 0.0)
        top = -150 - recken
        hupf = 0.0
        p.translate(0, -hupf)
        # Füße und Schwanz
        p.setBrush(MURMEL_DUNKEL)
        p.drawEllipse(QRectF(-34, -10, 26, 12))
        p.drawEllipse(QRectF(8, -10, 26, 12))
        schwanz = QPainterPath()
        schwanz.moveTo(-30, -20)
        schwanz.cubicTo(-60, -16, -62, 0, -40, 2)
        schwanz.cubicTo(-36, -6, -30, -10, -24, -12)
        p.drawPath(schwanz)
        # Rumpf (birnenförmig)
        rumpf = QPainterPath()
        rumpf.moveTo(-40, -6)
        rumpf.cubicTo(-52, -60, -30, top + 30, 0, top + 20)
        rumpf.cubicTo(30, top + 30, 52, -60, 40, -6)
        rumpf.closeSubpath()
        p.setBrush(radial(-10, -80, 110, MURMEL.lighter(118), MURMEL_DUNKEL))
        p.drawPath(rumpf)
        p.setBrush(MURMEL_HELL)
        p.drawEllipse(QRectF(-22, top + 50, 44, -top - 56))
        # Ärmchen
        for s in (-1, 1):
            p.save()
            p.translate(s * 22, top + 56)
            p.rotate(s * 15 + (pose.arm_v if s > 0 else pose.arm_h) * 0.6 * s * -1 + 70 * pfiff * s)
            p.setBrush(MURMEL.darker(110))
            p.drawRoundedRect(QRectF(-6, -2, 12, 30), 6, 6)
            p.restore()
        # Kopf von vorn
        hy = top + 4
        g = 1 + 0.25 * pfiff
        for s in (-1, 1):
            p.setBrush(MURMEL_DUNKEL)
            kreis(p, s * 22 * g, hy - 20 * g, 7)
        p.setBrush(radial(-6, hy - 8, 40, MURMEL.lighter(120), MURMEL_DUNKEL))
        p.drawEllipse(QPointF(0, hy), 30 * g, 27 * g)
        p.setBrush(MURMEL_HELL)
        p.drawEllipse(QPointF(0, hy + 12 * g), 16 * g, 11 * g)
        if pfiff > 0.05:
            p.setBrush(MAUL)
            p.drawEllipse(QPointF(0, hy + 16 * g), 13 * pfiff * g, 15 * pfiff * g)
            p.setBrush(QColor('#FFF4D0'))
            p.drawRect(QRectF(-5, hy + 16 * g - 15 * pfiff * g - 1, 4.5, 8))
            p.drawRect(QRectF(0.5, hy + 16 * g - 15 * pfiff * g - 1, 4.5, 8))
            p.setBrush(SCHWARZ)
            p.drawEllipse(QPointF(0, hy + 2 * g), 5, 3.5)
        else:
            p.setBrush(SCHWARZ)
            p.drawEllipse(QPointF(0, hy + 6), 5, 3.5)
            p.setBrush(QColor('#FFF4D0'))
            p.drawRect(QRectF(-4, hy + 14, 3.6, 6))
            p.drawRect(QRectF(0.4, hy + 14, 3.6, 6))
        _schnurrhaare(p, 10, hy + 10, 16)
        p.save()
        p.scale(-1, 1)
        _schnurrhaare(p, 10, hy + 10, 16)
        p.restore()
        _gesicht_vorn(p, 0, hy - 6 * g, 28, pose, MURMEL_DUNKEL.darker(130))


def zeichne_schneedecke(p, b, h, zug=0.0):
    """Schneedecke über dem schlafenden Murmeltier, Mitte unten im Ursprung; zug verschiebt
    sie nach rechts (Einheiten), als zöge jemand daran."""
    pfad = QPainterPath()
    pfad.moveTo(-b / 2 + zug * 0.3, 2)
    pfad.cubicTo(-b * 0.45 + zug * 0.4, -h * 1.1, b * 0.2 + zug * 0.7, -h * 1.15, b / 2 + zug, -h * 0.4)
    pfad.quadTo(b / 2 + zug + 10, 0, b / 2 + zug - 4, 2)
    pfad.closeSubpath()
    p.setBrush(linear(0, -h, 0, 0, WEISS, QColor('#C7D8EC')))
    p.drawPath(pfad)
    p.setPen(stift(QColor('#B4C8E0'), 1.4))
    p.setBrush(KEIN_PINSEL)
    p.drawArc(QRectF(-b * 0.3 + zug * 0.5, -h * 0.9, b * 0.5, h * 0.5), 200 * 16, 120 * 16)
    p.setPen(KEIN_STIFT)


def zeichne_stiefel(p, x, y):
    """Ein Paar leere Stiefel des Weihnachtsmanns, Sohlen bei y."""
    for dx, k in ((-10, 125), (14, 100)):
        bx = x + dx
        p.setBrush(linear(0, y - 40, 0, y, QColor('#444444').darker(k), SCHWARZ.darker(k)))
        p.drawRoundedRect(QRectF(bx - 11, y - 40, 22, 40), 6, 6)
        p.drawRoundedRect(QRectF(bx - 11, y - 14, 32, 14), 6, 6)
        p.setBrush(QColor('#4A3426').darker(k))
        p.drawRoundedRect(QRectF(bx - 12, y - 3, 34, 4), 2, 2)
        flausch(p, [(bx - 9, y - 40), (bx - 3, y - 41), (bx + 3, y - 41), (bx + 9, y - 40)], 5, k == 100)


def zeichne_einzelfeder(p, x, y, winkel=0.0, laenge=22):
    """Eine einzelne weiße Feder, Mitte in (x, y)."""
    p.save()
    p.translate(x, y)
    p.rotate(winkel)
    p.setBrush(radial(0, 0, laenge * 0.6, EULE, EULE_SCHATTEN))
    feder = QPainterPath()
    feder.moveTo(-laenge / 2, 0)
    feder.cubicTo(-laenge / 4, -laenge * 0.28, laenge / 4, -laenge * 0.3, laenge / 2, 0)
    feder.cubicTo(laenge / 4, laenge * 0.2, -laenge / 4, laenge * 0.22, -laenge / 2, 0)
    p.drawPath(feder)
    p.setPen(stift(EULE_SCHATTEN.darker(130), 1.0))
    p.drawLine(QPointF(-laenge * 0.62, 1), QPointF(laenge * 0.45, -1))
    p.setPen(KEIN_STIFT)
    p.restore()
