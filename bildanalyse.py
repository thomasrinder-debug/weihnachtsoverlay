"""Bildauswertung für die Szenen, die mit dem echten Bildschirm spielen: Tintenspalten,
Buchstabenstücke einer Zeile, Flicken zum Abdecken.

Ohne Windows-Abhängigkeit, damit pruefen.py sie mit Testbildern prüfen kann. Was
Fenster und Schreibmarke abfragt, steht in abgreifen.py.
"""
from PyQt6.QtCore import QPointF, QRect, QRectF
from PyQt6.QtGui import QColor, QImage


class Pixel:
    """Schneller Lesezugriff auf ein QImage (32 Bit)."""

    def __init__(self, bild):
        self.bild = bild.convertToFormat(QImage.Format.Format_RGB32)
        self.w, self.h = self.bild.width(), self.bild.height()
        self.zeile = self.bild.bytesPerLine()
        b = self.bild.constBits()
        b.setsize(self.bild.sizeInBytes())
        self.daten = bytes(b)

    def rgb(self, x, y):
        i = y * self.zeile + 4 * x
        d = self.daten
        return d[i + 2], d[i + 1], d[i]


def abstand(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1]) + abs(a[2] - b[2])


def haeufigste_farbe(px, rechteck):
    """Häufigste (leicht vergröberte) Farbe im Rechteck, als (r, g, b)."""
    zaehler = {}
    x0, y0, x1, y1 = rechteck
    schritt = max(1, (x1 - x0) * (y1 - y0) // 4000)
    i = 0
    for y in range(y0, y1):
        for x in range(x0, x1):
            i += 1
            if i % schritt:
                continue
            c = px.rgb(x, y)
            k = (c[0] >> 3, c[1] >> 3, c[2] >> 3)
            zaehler.setdefault(k, [0, c])[0] += 1
    return max(zaehler.values())[1] if zaehler else (255, 255, 255)


def tintenspalten(px, rechteck, grund, schwelle=60):
    """Für jede Spalte im Rechteck: Anzahl der Pixel, die deutlich von grund abweichen."""
    x0, y0, x1, y1 = rechteck
    return [sum(abstand(px.rgb(x, y), grund) > schwelle for y in range(y0, y1)) for x in range(x0, x1)]


def laeufe(werte, luecke=1, mindest=1):
    """Zusammenhängende Bereiche mit werte > 0 als (anfang, ende), Lücken bis 'luecke' überbrückt."""
    bereiche = []
    start = None
    leer = 0
    for i, v in enumerate(werte):
        if v >= mindest:
            if start is None:
                start = i
            ende, leer = i + 1, 0
        elif start is not None:
            leer += 1
            if leer > luecke:
                bereiche.append((start, ende))
                start = None
    if start is not None:
        bereiche.append((start, ende))
    return bereiche


def tintenzeilen(px, x0, x1, y0, y1, grund, schwelle=60):
    zeilen = [y for y in range(y0, y1)
              if any(abstand(px.rgb(x, y), grund) > schwelle for x in range(x0, x1))]
    return (zeilen[0], zeilen[-1] + 1) if zeilen else None


def einfarbig(w, h, farbe):
    bild = QImage(w, h, QImage.Format.Format_RGB32)
    bild.fill(QColor(*farbe))
    return bild


class Umrechnung:
    """Physische Bildschirmpixel (Windows) in logische (Qt, Szenen) für einen Bildschirm.
    Qt behält den Ursprung jedes Bildschirms bei und teilt nur den Abstand dazu."""

    def __init__(self, geo, dpr):
        self.ox, self.oy, self.d = geo.x(), geo.y(), dpr

    def punkt(self, x, y):
        return QPointF(self.ox + (x - self.ox) / self.d, self.oy + (y - self.oy) / self.d)

    def rechteck(self, x0, y0, x1, y1):
        """Physisches Rechteck (absolute Koordinaten) logisch."""
        return QRectF(self.punkt(x0, y0), self.punkt(x1, y1))

    def im_bild(self, x, y):
        """Absolute physische Koordinaten -> Pixel im Bildschirmfoto."""
        return round(x - self.ox), round(y - self.oy)

    def bildrechteck(self, x0, y0, x1, y1):
        """Pixel im Bildschirmfoto -> logisches Rechteck."""
        return self.rechteck(x0 + self.ox, y0 + self.oy, x1 + self.ox, y1 + self.oy)


def ausschnitt(bild, x0, y0, x1, y1):
    return bild.copy(QRect(x0, y0, x1 - x0, y1 - y0))


# ---- Zeile an der Schreibmarke

def tippzeile_daten(bild, marke, um, links=None):
    """marke: Schreibmarke (x0, y0, x1, y1) in Bildpixeln. Schneidet die Zeile links davon aus
    und zerlegt sie in Buchstabenstücke. links: kleinstes x (Rand des Textfelds)."""
    px = Pixel(bild)
    mx0, my0, mx1, my1 = marke
    h = my1 - my0
    if h < 6:
        return None
    x0 = max(links if links is not None else 0, mx0 - 22 * h, 0)
    x1 = mx0 - 1
    if x1 - x0 < 3 * h:
        return None
    y0, y1 = max(0, my0), min(px.h, my1)
    grund = haeufigste_farbe(px, (x0, y0, x1, y1))
    spalten = tintenspalten(px, (x0, y0, x1, y1), grund)
    stuecke = []
    for a, b in laeufe(spalten, luecke=0):
        if b - a <= 3 and max(spalten[a:b]) >= 0.9 * (y1 - y0):
            stuecke.clear()             # Rahmenlinie eines Textfelds: davor gehört nicht mehr zur Zeile
            continue
        # sehr breite Stücke (zusammenhängende Schrift) in buchstabengroße Teile schneiden
        teile = max(1, round((b - a) / (0.65 * h)))
        for k in range(teile):
            stuecke.append((x0 + a + (b - a) * k // teile, x0 + a + (b - a) * (k + 1) // teile))
    # nur die letzten Wörter vor der Marke: ab einer großen Lücke abschneiden
    behalten = []
    for s in reversed(stuecke):
        if behalten and behalten[-1][0] - s[1] > 2.5 * h:
            break
        behalten.append(s)
    behalten.reverse()
    if len(behalten) < 3:
        return None
    x0 = max(x0, behalten[0][0] - h // 2)
    tinte = tintenzeilen(px, behalten[0][0], behalten[-1][1], y0, y1, grund) or (y0, y1)
    tinte = um.bildrechteck(x0, tinte[0], x1, tinte[1])
    return {
        'zeile': ausschnitt(bild, x0, y0, x1, y1),
        'flicken': einfarbig(x1 - x0, y1 - y0, grund),
        'rechteck': um.bildrechteck(x0, y0, x1, y1),
        'stuecke': [um.bildrechteck(a, y0, b, y1) for a, b in behalten],
        'marke': um.bildrechteck(mx0, my0, mx1, my1),
        'grund': QColor(*grund),
        'tinte': (tinte.top(), tinte.bottom()),       # oberste und unterste Pixelzeile mit Schrift
    }


