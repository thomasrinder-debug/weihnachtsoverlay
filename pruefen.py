"""Prüft alle Szenen ohne Fenster: Vorschaubilder und Schreck-Test.

    python pruefen.py                    alle Szenen
    python pruefen.py spaehen fahrrad    nur diese
    python pruefen.py --ordner vorschau  Bilder dorthin (Standard: vorschau/)

Je Szene entsteht ein Bild mit vier Momenten (rot: neu gezeichneter Bereich).
Danach wird jede Szene zu mehreren Zeitpunkten erschreckt; sie muss dann
rasch und ohne Hänger enden.
"""
import argparse
import pathlib
import random

from PyQt6.QtCore import QRect, QRectF, Qt
from PyQt6.QtGui import QColor, QFont, QGuiApplication, QImage, QLinearGradient, QPainter, QPen

import bildanalyse
from szenen import finde_szenen
from zeichnen.grundlagen import FIGUR_HOEHE

BREITE, HOEHE = 1920, 1080
TAKT = 1 / 60


def testbildschirm():
    """Erfundener Bildschirm für Szenen, die mit dem echten Bildschirm spielen: ein Textfeld
    mit Schreibmarke und eine Taskleiste. Gibt (Bild, Schreibmarke, Leiste)."""
    bild = QImage(BREITE, HOEHE, QImage.Format.Format_RGB32)
    p = QPainter(bild)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    g = QLinearGradient(0, 0, BREITE, HOEHE)
    g.setColorAt(0, QColor('#3E6E5A'))
    g.setColorAt(1, QColor('#5A7FA8'))
    p.fillRect(bild.rect(), g)
    p.setPen(Qt.PenStyle.NoPen)
    farben = ['#E8B33A', '#3A8EE8', '#D9443B', '#4CB050', '#9C5BD9', '#F08A24', '#2BB3C0', '#555555']
    p.fillRect(QRect(380, 420, 1160, 300), QColor('white'))
    p.setPen(QColor('#202020'))
    p.setFont(QFont('Consolas', 13))
    text = 'Frohe Weihnachten und ein gutes neues Jahr'
    p.drawText(400, 520, text)
    x1 = 400 + p.fontMetrics().horizontalAdvance(text)
    marke = (x1 + 1, 503, x1 + 2, 526)
    p.fillRect(QRect(marke[0], marke[1], 1, marke[3] - marke[1]), QColor('black'))
    leiste = (0, HOEHE - 48, BREITE, HOEHE)
    p.fillRect(QRect(0, leiste[1], BREITE, 48), QColor(228, 229, 222))
    for i, f in enumerate(farben):
        x = 760 + i * 44
        p.setBrush(QColor(f))
        p.drawRoundedRect(QRectF(x, leiste[1] + 12, 24, 24), 5, 5)
        p.setBrush(QColor('white'))
        p.drawEllipse(QRectF(x + 7, leiste[1] + 19, 10, 10))
    p.end()
    return bild, marke, leiste


def testdaten(art):
    bild, marke, leiste = testbildschirm()
    um = bildanalyse.Umrechnung(QRect(0, 0, BREITE, HOEHE), 1.0)
    if art == 'taskleiste':
        return bildanalyse.taskleiste_daten(bild, leiste, (700, leiste[1], 1200, leiste[3]), um)
    return bildanalyse.tippzeile_daten(bild, marke, um, 380)


def lauf(klasse, s, schreck_bei=None, momente=(), bild=None):
    """Lässt eine Szene laufen; gibt (Dauer, Dauer nach Schreck, Bilder) zurück."""
    geo = QRectF(0, 0, BREITE, HOEHE)
    sz = klasse(geo, s, testdaten(klasse.braucht) if klasse.braucht else None)
    bilder = []
    momente = sorted(momente)
    while not sz.fertig and sz.t < 60:
        sz.schritt(TAKT)
        if schreck_bei is not None and not sz.erschreckt and sz.t >= schreck_bei:
            sz.erschrecken()
        while momente and sz.t >= momente[0]:
            momente.pop(0)
            bilder.append(schnappschuss(sz, geo, klasse.braucht))
    nach = sz.t - sz.te if sz.erschreckt else None
    return sz.t, sz.fertig, nach, bilder


def schnappschuss(sz, geo, braucht=None):
    if braucht:
        f = testbildschirm()[0].convertToFormat(QImage.Format.Format_ARGB32)
    else:
        f = QImage(BREITE, HOEHE, QImage.Format.Format_ARGB32)
        f.fill(QColor('#5A7FA8'))
    p = QPainter(f)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    if not sz.fertig:
        sz.zeichne(p)
        p.setPen(QPen(QColor('red'), 2))
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawRect(sz.grenzen())
    p.setPen(QColor('white'))
    p.drawText(12, 28, f'{sz.name}  t={sz.t:.1f}s  {"erschreckt" if sz.erschreckt else ""}')
    p.end()
    return f


def tafel(bilder, pfad):
    w, h = BREITE // 2, HOEHE // 2
    out = QImage(w * 2, h * 2, QImage.Format.Format_ARGB32)
    out.fill(QColor('#222222'))
    p = QPainter(out)
    for i, b in enumerate(bilder[:4]):
        p.drawImage(QRectF((i % 2) * w, (i // 2) * h, w, h), b)
    p.end()
    out.save(str(pfad))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('namen', nargs='*')
    ap.add_argument('--ordner', default='vorschau')
    ap.add_argument('--groesse', type=float, default=0.15)
    a = ap.parse_args()
    app = QGuiApplication([])  # noqa: F841  wird für Schriften und Zeichnen gebraucht
    szenen = finde_szenen()
    ordner = pathlib.Path(a.ordner)
    ordner.mkdir(exist_ok=True)
    s = HOEHE * a.groesse / FIGUR_HOEHE
    fehler = 0
    for name in a.namen or szenen:
        klasse = szenen[name]
        random.seed(3)
        dauer, fertig, _, _ = lauf(klasse, s)
        random.seed(3)
        momente = [dauer * f for f in (0.15, 0.4, 0.6, 0.85)]
        _, _, _, bilder = lauf(klasse, s, momente=momente)
        tafel(bilder, ordner / f'{name}.png')
        zeile = f'{name:12s} {dauer:5.1f}s {"ok" if fertig else "HÄNGT"}  Schreck:'
        fehler += not fertig
        for bei in (1.0, 2.5, 4.5, 7.5):
            random.seed(3)
            _, fertig, nach, _ = lauf(klasse, s, schreck_bei=bei)
            if nach is None:
                zeile += f'  {bei}s –'
            else:
                ok = fertig and nach < 3.0
                fehler += not ok
                zeile += f'  {bei}s→{nach:.1f}s{"" if ok else "!"}'
        print(zeile)
    print(f'Vorschaubilder in {ordner.resolve()}')
    print('Alles in Ordnung.' if not fehler else f'{fehler} Auffälligkeiten (! = zu langsam weg oder hängt).')


if __name__ == '__main__':
    main()
