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

from PyQt6.QtCore import QRectF, Qt
from PyQt6.QtGui import QColor, QGuiApplication, QImage, QPainter, QPen

from szenen import finde_szenen
from zeichnen.grundlagen import FIGUR_HOEHE

BREITE, HOEHE = 1920, 1080
TAKT = 1 / 60


def lauf(klasse, s, schreck_bei=None, momente=(), bild=None):
    """Lässt eine Szene laufen; gibt (Dauer, Dauer nach Schreck, Bilder) zurück."""
    geo = QRectF(0, 0, BREITE, HOEHE)
    sz = klasse(geo, s)
    bilder = []
    momente = sorted(momente)
    while not sz.fertig and sz.t < 60:
        sz.schritt(TAKT)
        if schreck_bei is not None and not sz.erschreckt and sz.t >= schreck_bei:
            sz.erschrecken()
        while momente and sz.t >= momente[0]:
            momente.pop(0)
            bilder.append(schnappschuss(sz, geo))
    nach = sz.t - sz.te if sz.erschreckt else None
    return sz.t, sz.fertig, nach, bilder


def schnappschuss(sz, geo):
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
