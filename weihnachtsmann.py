"""Weihnachtsmann-Overlay: kleine Szenen am Bildschirmrand, auch über
Vollbild-Präsentationen (PowerPoint, PDF, Browser F11).

Das Fenster ist durchsichtig, liegt immer oben und lässt Maus und Tastatur
durch. Es bedeckt während einer Szene den ganzen Bildschirm und bewegt sich
nicht; neu gezeichnet wird nur der Bereich, in dem sich etwas ändert, im Takt
der Bildwiederholung. Bewegt jemand die Maus oder drückt eine Taste,
erschrickt der Weihnachtsmann und verschwindet.

Die Szenen liegen einzeln im Ordner szenen/, das Zeichnen in zeichnen/.

Einige Szenen spielen mit dem, was gerade zu sehen ist (getippter
Text). Dafür holt abgreifen.py ein Bildschirmfoto und die Lage der
Symbole bzw. der Schreibmarke; ohne passende Stelle fällt die Szene aus. Die
Tippkatze kommt in der Automatik, wenn nach dem Tippen kurz Ruhe ist.

Tastenkürzel (global):
  Strg+Alt+A      Automatik an/aus (Szenen von selbst, zufällige Pausen)
  Strg+Alt+W      nächste Szene (zufällige Reihenfolge)
  Strg+Alt+1..9   eine bestimmte Szene
  Strg+Alt+Q      Programm beenden
"""
import argparse
import ctypes
import math
import random
import sys
from ctypes import wintypes

from PyQt6.QtCore import QAbstractNativeEventFilter, QElapsedTimer, QRectF, Qt, QTimer
from PyQt6.QtGui import QIcon, QPainter, QPixmap
from PyQt6.QtWidgets import QApplication, QMenu, QMessageBox, QSystemTrayIcon, QWidget

import abgreifen
from szenen import finde_szenen
from zeichnen.figur import zeichne_kopf_vorn
from zeichnen.grundlagen import FIGUR_HOEHE

SZENEN = finde_szenen()


# ---------------------------------------------------------------- Fenster und Tastenkürzel

user32 = ctypes.windll.user32
user32.SetWindowPos.argtypes = [ctypes.c_ssize_t, ctypes.c_ssize_t, ctypes.c_int, ctypes.c_int,
                                ctypes.c_int, ctypes.c_int, ctypes.c_uint]
user32.RegisterHotKey.argtypes = [ctypes.c_ssize_t, ctypes.c_int, ctypes.c_uint, ctypes.c_uint]
HWND_TOPMOST = -1
SWP_NOSIZE, SWP_NOMOVE, SWP_NOACTIVATE = 0x1, 0x2, 0x10
WM_HOTKEY = 0x0312
MOD_ALT, MOD_CONTROL, MOD_NOREPEAT = 0x1, 0x2, 0x4000
HK_WEITER, HK_ENDE, HK_AUTO = 1, 2, 3      # ab 11: Szenen einzeln
dwmapi = ctypes.windll.dwmapi
SCHONZEIT = 0.8     # Sekunden nach dem Start, in denen Eingaben (das Tastenkürzel selbst) nicht erschrecken


class LASTINPUTINFO(ctypes.Structure):
    _fields_ = [('cbSize', ctypes.c_uint), ('dwTime', ctypes.c_uint)]


def letzte_eingabe():
    """Zeitstempel der letzten Maus- oder Tastatureingabe irgendwo im System."""
    info = LASTINPUTINFO(ctypes.sizeof(LASTINPUTINFO), 0)
    user32.GetLastInputInfo(ctypes.byref(info))
    return info.dwTime


def ruhe_seit(zeitstempel):
    """Sekunden seit einem Zeitstempel von letzte_eingabe()."""
    return ((ctypes.windll.kernel32.GetTickCount() - zeitstempel) & 0xFFFFFFFF) / 1000


def mauslage():
    pt = wintypes.POINT()
    user32.GetCursorPos(ctypes.byref(pt))
    return pt.x, pt.y


class Overlay(QWidget):
    def __init__(self, bildschirm, groesse, einmal, schreckhaft=True):
        super().__init__(None, Qt.WindowType.FramelessWindowHint
                         | Qt.WindowType.WindowStaysOnTopHint
                         | Qt.WindowType.Tool
                         | Qt.WindowType.WindowTransparentForInput
                         | Qt.WindowType.WindowDoesNotAcceptFocus)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.setScreen(bildschirm)
        self.bildschirm = bildschirm
        self.geo = QRectF(bildschirm.geometry())
        self.s = self.geo.height() * groesse / FIGUR_HOEHE
        self.einmal = einmal
        self.szene = None
        self.reihe = []
        self.uhr = QElapsedTimer()
        self.uhr.start()
        self.zuletzt = 0.0
        self.alt = QRectF()
        self.schreckhaft = schreckhaft
        self.eingabe = 0
        # Der Takt wartet in schritt() per DwmFlush auf das nächste Bild des
        # Monitors, so passt jede Bewegung genau zur Bildwiederholung.
        self.takt = QTimer(self)
        self.takt.setTimerType(Qt.TimerType.PreciseTimer)
        self.takt.setInterval(0)
        self.takt.timeout.connect(self.schritt)
        # Manche Vollbildprogramme schieben sich beim Fokuswechsel nach oben,
        # deshalb holt sich das Fenster regelmäßig wieder nach vorn.
        self.vorn = QTimer(self)
        self.vorn.setInterval(250)
        self.vorn.timeout.connect(self.nach_vorn)
        # Automatik: Szenen kommen von selbst, mit zufällig langen Pausen
        self.automatik = False
        self.pause = (20.0, 180.0)
        self.wecker = QTimer(self)
        self.wecker.setSingleShot(True)
        self.wecker.timeout.connect(self.von_selbst)
        # Tippkatze: lauscht, ob getippt wird (Eingaben ohne Mausbewegung), und kommt,
        # wenn danach 2 bis 4 Sekunden Ruhe ist.
        self.katzenpause = (45.0, 240.0)
        self.lauscher = QTimer(self)
        self.lauscher.setInterval(150)
        self.lauscher.timeout.connect(self.lauschen)
        self.l_eingabe, self.l_maus = letzte_eingabe(), mauslage()
        self.tasten = 0
        self.katze_ab = 0.0
        self.katze_nach = random.uniform(2.0, 4.0)

    def automatik_setzen(self, an):
        self.automatik = an
        if an:
            self.planen()
            if 'tippkatze' in SZENEN:
                self.lauscher.start()
        else:
            self.wecker.stop()
            self.lauscher.stop()

    def planen(self):
        # logarithmisch verteilt: kurze Pausen kommen öfter vor, lange gibt es trotzdem
        kurz, lang = self.pause
        sekunden = math.exp(random.uniform(math.log(kurz), math.log(lang)))
        self.wecker.start(int(sekunden * 1000))

    def von_selbst(self):
        if self.szene:
            self.planen()
        else:
            self.start()

    def lauschen(self):
        e, maus = letzte_eingabe(), mauslage()
        if e != self.l_eingabe:
            self.l_eingabe = e
            if maus != self.l_maus:
                self.l_maus, self.tasten = maus, 0
            else:
                self.tasten += 1
            return
        if self.tasten < 4:
            return
        ruhe = ruhe_seit(e)
        if ruhe < self.katze_nach:
            return
        self.tasten = 0
        self.katze_nach = random.uniform(2.0, 4.0)
        jetzt = self.uhr.elapsed() / 1000
        if ruhe < 6 and jetzt >= self.katze_ab and not self.szene and self.start('tippkatze'):
            self.katze_ab = jetzt + random.uniform(*self.katzenpause)

    def start(self, name=None):
        """Startet eine Szene (ohne Namen: die nächste zufällige). False, wenn keine startet,
        etwa weil eine Szene, die mit dem Bildschirm spielt, nichts Passendes findet."""
        if self.szene:
            return False
        zufall = name is None
        for _ in range(len(SZENEN)):
            if zufall:
                if not self.reihe:
                    self.reihe = [n for n, k in SZENEN.items() if not k.nur_ausloeser]
                    random.shuffle(self.reihe)
                name = self.reihe.pop()
            klasse = SZENEN[name]
            daten = abgreifen.fuer(klasse.braucht, self.bildschirm) if klasse.braucht else None
            if not klasse.braucht or daten:
                break
            if not zufall:
                return False
        else:
            return False
        self.szene = klasse(self.geo, self.s, daten)
        self.zuletzt = self.uhr.elapsed() / 1000
        self.alt = QRectF()
        self.eingabe = letzte_eingabe()
        self.setGeometry(self.geo.toAlignedRect())
        self.show()
        self.nach_vorn()
        self.takt.start()
        self.vorn.start()
        return True

    def stop(self):
        self.takt.stop()
        self.vorn.stop()
        self.hide()
        self.szene = None
        if self.einmal:
            QApplication.quit()
        elif self.automatik:
            self.planen()

    def nach_vorn(self):
        if self.isVisible():
            user32.SetWindowPos(int(self.winId()), HWND_TOPMOST, 0, 0, 0, 0,
                                SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE)

    def schritt(self):
        dwmapi.DwmFlush()
        jetzt = self.uhr.elapsed() / 1000
        dt = min(jetzt - self.zuletzt, 0.05)
        self.zuletzt = jetzt
        self.szene.schritt(dt)
        if self.schreckhaft:
            e = letzte_eingabe()
            if e != self.eingabe:
                self.eingabe = e
                if self.szene.t > SCHONZEIT:
                    self.szene.erschrecken()
        if self.szene.fertig:
            self.stop()
            return
        # Nur den alten und den neuen Bereich der Szene neu zeichnen.
        neu = self.szene.grenzen()
        bereich = neu.united(self.alt) if not self.alt.isEmpty() else neu
        self.alt = neu
        if not bereich.isEmpty():
            r = bereich.translated(-self.geo.x(), -self.geo.y()).toAlignedRect().adjusted(-3, -3, 3, 3)
            self.update(r)

    def paintEvent(self, _):
        if not self.szene:
            return
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.translate(-self.geo.x(), -self.geo.y())
        self.szene.zeichne(p)
        p.end()


class TastenFilter(QAbstractNativeEventFilter):
    def __init__(self, aktion):
        super().__init__()
        self.aktion = aktion

    def nativeEventFilter(self, art, nachricht):
        if bytes(art) == b'windows_generic_MSG':
            msg = wintypes.MSG.from_address(int(nachricht))
            if msg.message == WM_HOTKEY:
                self.aktion(msg.wParam)
                return True, 0
        return False, 0


def main():
    ap = argparse.ArgumentParser(description='Weihnachtsmann-Szenen über dem Bildschirm.')
    ap.add_argument('--monitor', type=int, default=0, help='Bildschirm 1, 2, ... (Standard: Hauptbildschirm)')
    ap.add_argument('--liste', action='store_true', help='Bildschirme auflisten und beenden')
    ap.add_argument('--sofort', nargs='?', const='', metavar='SZENE',
                    help='gleich beim Start loslegen, optional mit Szene: ' + ', '.join(SZENEN))
    ap.add_argument('--einmal', action='store_true', help='nach einer Szene beenden')
    ap.add_argument('--groesse', type=float, default=0.15, help='Figurhöhe als Anteil der Bildschirmhöhe')
    ap.add_argument('--mutig', action='store_true', help='erschrickt nicht bei Maus- oder Tastatureingaben')
    ap.add_argument('--pause', type=float, nargs=2, default=(20, 180), metavar=('KURZ', 'LANG'),
                    help='Pausen der Automatik in Sekunden (Standard: 20 180)')
    ap.add_argument('--manuell', action='store_true', help='Automatik beim Start aus, nur Tastenkürzel')
    ap.add_argument('--katzenpause', type=float, nargs=2, default=(45, 240), metavar=('KURZ', 'LANG'),
                    help='Abstand zwischen zwei Besuchen der Tippkatze in Sekunden (Standard: 45 240)')
    a = ap.parse_args()

    app = QApplication(sys.argv[:1])
    app.setQuitOnLastWindowClosed(False)
    # Nur eine Kopie: ein zweiter Start meldet sich und beendet sich wieder.
    kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
    kernel32.CreateMutexW.restype = ctypes.c_void_p
    sperre = kernel32.CreateMutexW(None, False, 'WeihnachtsmannOverlay')
    if ctypes.get_last_error() == 183 and not a.liste:     # ERROR_ALREADY_EXISTS
        QMessageBox.information(None, 'Weihnachtsmann', 'Der Weihnachtsmann läuft schon.\n\n'
                                'Strg+Alt+W startet eine Szene, das Symbol unten rechts im '
                                'Infobereich hat ein Menü.')
        return
    bildschirme = app.screens()
    if a.liste:
        for i, b in enumerate(bildschirme, 1):
            g = b.geometry()
            haupt = ' (Haupt)' if b is app.primaryScreen() else ''
            print(f'{i}: {b.name()} {g.width()}x{g.height()} bei {g.x()},{g.y()}{haupt}')
        return
    bildschirm = bildschirme[a.monitor - 1] if a.monitor else app.primaryScreen()
    overlay = Overlay(bildschirm, a.groesse, a.einmal, not a.mutig)
    overlay.pause = (max(1.0, min(a.pause)), max(a.pause))
    overlay.katzenpause = (max(0.0, min(a.katzenpause)), max(a.katzenpause))
    namen = list(SZENEN)[:9]

    def taste(nr):
        if nr == HK_WEITER:
            overlay.start()
        elif nr == HK_ENDE:
            app.quit()
        elif nr == HK_AUTO:
            symbol.auto.setChecked(not overlay.automatik)      # löst automatik_setzen aus
            symbol.showMessage('Weihnachtsmann', 'Automatik an' if overlay.automatik else 'Automatik aus',
                               QSystemTrayIcon.MessageIcon.Information, 2000)
        elif 11 <= nr < 11 + len(namen):
            overlay.start(namen[nr - 11])

    filt = TastenFilter(taste)
    app.installNativeEventFilter(filt)
    hwnd = int(overlay.winId())
    mod = MOD_CONTROL | MOD_ALT | MOD_NOREPEAT
    ok = user32.RegisterHotKey(hwnd, HK_WEITER, mod, ord('W'))
    ok &= user32.RegisterHotKey(hwnd, HK_ENDE, mod, ord('Q'))
    ok &= user32.RegisterHotKey(hwnd, HK_AUTO, mod, ord('A'))
    for i in range(len(namen)):
        ok &= user32.RegisterHotKey(hwnd, 11 + i, mod, ord('1') + i)
    symbol = infobereich(app, overlay, namen)
    symbol.auto.setChecked(not a.manuell)
    if ok:
        zustand = 'kommt von selbst' if overlay.automatik else 'wartet auf Strg+Alt+W'
        symbol.showMessage(f'Weihnachtsmann ist bereit ({zustand})',
                           f'Strg+Alt+A: Automatik an/aus · Strg+Alt+W: Szene · '
                           f'Strg+Alt+1–{len(namen)}: bestimmte Szene · Strg+Alt+Q: beenden',
                           QSystemTrayIcon.MessageIcon.Information, 6000)
    else:
        symbol.showMessage('Weihnachtsmann', 'Einige Tastenkürzel sind schon von einem anderen Programm belegt. '
                           'Die Szenen lassen sich über dieses Symbol starten.',
                           QSystemTrayIcon.MessageIcon.Warning, 8000)
    if a.sofort is not None:
        def sofort():
            if not overlay.start(a.sofort or None) and a.einmal:
                app.quit()      # Szene fand nichts Passendes auf dem Bildschirm
        QTimer.singleShot(300, sofort)
    code = app.exec()
    kernel32.CloseHandle(ctypes.c_void_p(sperre))
    sys.exit(code)


def infobereich(app, overlay, namen):
    """Symbol mit Menü im Infobereich der Taskleiste."""
    bild = QPixmap(64, 64)
    bild.fill(Qt.GlobalColor.transparent)
    p = QPainter(bild)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.translate(30, 38)
    p.scale(0.42, 0.42)
    zeichne_kopf_vorn(p, 0, 0)
    p.end()
    symbol = QSystemTrayIcon(QIcon(bild), app)
    symbol.setToolTip('Weihnachtsmann – Strg+Alt+W startet eine Szene')
    menue = QMenu()
    symbol.auto = menue.addAction('Automatisch, zufällige Pausen\tStrg+Alt+A')
    symbol.auto.setCheckable(True)
    symbol.auto.toggled.connect(overlay.automatik_setzen)
    menue.addSeparator()
    menue.addAction('Zufällige Szene\tStrg+Alt+W', lambda: overlay.start())
    menue.addSeparator()
    for i, name in enumerate(namen):
        menue.addAction(f'{SZENEN[name].titel or name}\tStrg+Alt+{i + 1}', lambda n=name: overlay.start(n))
    menue.addSeparator()
    menue.addAction('Beenden\tStrg+Alt+Q', app.quit)
    symbol.setContextMenu(menue)
    symbol.activated.connect(lambda grund: overlay.start()
                             if grund == QSystemTrayIcon.ActivationReason.Trigger else None)
    symbol.show()
    symbol.menue = menue      # Menü am Leben halten
    return symbol


if __name__ == '__main__':
    main()
