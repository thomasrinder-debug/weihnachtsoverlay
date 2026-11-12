"""Die Szenen als Windows-Bildschirmschoner (Weihnachtsmann.scr).

Windows ruft einen Bildschirmschoner so auf (groß/klein, auch mit Doppelpunkt):
  /s            Vollbild auf allen Bildschirmen
  /p <hwnd>     kleine Vorschau im Einstellungsdialog, als Kindfenster von hwnd
  /c[:<hwnd>]   Einstellungen; ohne Argument ebenso

Im Vollbild laufen die Szenen nacheinander vor einem Winterhimmel. Bewegt jemand
die Maus, klickt oder drückt eine Taste, erschrecken die Figuren kurz, dann ist
der Schoner weg. Ein Wächter-Thread beendet den Prozess hart, falls das hängt.
"""
import configparser
import ctypes
import os
import pathlib
import random
import sys
import threading
import time
from ctypes import wintypes

from PyQt6.QtCore import QElapsedTimer, QPointF, QRectF, Qt, QTimer
from PyQt6.QtGui import QColor, QLinearGradient, QPainter, QPixmap, QRadialGradient, QWindow
from PyQt6.QtWidgets import (QApplication, QCheckBox, QDialog, QDialogButtonBox, QDoubleSpinBox,
                             QFormLayout, QSpinBox, QWidget)

from szenen import finde_szenen
from zeichnen.grundlagen import FIGUR_HOEHE

user32 = ctypes.windll.user32
user32.IsWindow.argtypes = [wintypes.HWND]
user32.GetClientRect.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.RECT)]
user32.SetParent.argtypes = [wintypes.HWND, wintypes.HWND]
user32.GetWindowLongW.argtypes = [wintypes.HWND, ctypes.c_int]
user32.SetWindowLongW.argtypes = [wintypes.HWND, ctypes.c_int, wintypes.LONG]
user32.MoveWindow.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, wintypes.BOOL]
GWL_STYLE, WS_CHILD, WS_POPUP = -16, 0x40000000, -0x80000000
dwmapi = ctypes.windll.dwmapi

INI = pathlib.Path(os.environ.get('APPDATA', pathlib.Path.home())) / 'Weihnachtsmann' / 'schoner.ini'
STANDARD = {'groesse': 18, 'pause': 1.0, 'schnee': True}
SCHRECK_DAUER = 0.8     # so lange dürfen die Figuren nach einer Eingabe noch erschrecken
MAUS_SCHWELLE = 12      # Pixel, ab denen eine Mausbewegung zählt
WAECHTER = 1.5          # spätestens so lange nach einer Eingabe ist der Prozess weg


# ---------------------------------------------------------------- Aufruf und Einstellungen

def ist_schoner(argv):
    """True, wenn das Programm als Bildschirmschoner gestartet wurde."""
    if argv[0].lower().endswith('.scr'):
        return True
    return len(argv) > 1 and argv[1][:2].lower() in ('/s', '/p', '/c', '-s', '-p', '-c')


def aufruf(argv):
    """('s'|'p'|'c', hwnd oder None) aus den Argumenten, wie Windows sie übergibt."""
    if len(argv) < 2:
        return 'c', None
    a = argv[1].strip().lower()
    art = a[1:2] if a[:1] in '/-' else ''
    rest = a[2:].lstrip(':').strip()
    if not rest and len(argv) > 2:
        rest = argv[2].strip()
    hwnd = int(rest) if rest.isdigit() else None
    if art not in ('s', 'p', 'c'):
        art = 'c'
    return art, hwnd


def lade():
    werte = dict(STANDARD)
    ini = configparser.ConfigParser()
    try:
        ini.read(INI, encoding='utf-8')
        g = ini['schoner']
        werte['groesse'] = max(5, min(40, g.getint('groesse', STANDARD['groesse'])))
        werte['pause'] = max(0.0, min(60.0, g.getfloat('pause', STANDARD['pause'])))
        werte['schnee'] = g.getboolean('schnee', STANDARD['schnee'])
    except (KeyError, ValueError, configparser.Error):
        pass
    return werte


def speichere(werte):
    ini = configparser.ConfigParser()
    ini['schoner'] = {k: str(v) for k, v in werte.items()}
    INI.parent.mkdir(parents=True, exist_ok=True)
    with open(INI, 'w', encoding='utf-8') as f:
        ini.write(f)


class Einstellungen(QDialog):
    def __init__(self, werte):
        super().__init__()
        self.setWindowTitle('Weihnachtsmann – Bildschirmschoner')
        self.groesse = QSpinBox()
        self.groesse.setRange(5, 40)
        self.groesse.setSuffix(' % der Bildschirmhöhe')
        self.groesse.setValue(werte['groesse'])
        self.pause = QDoubleSpinBox()
        self.pause.setRange(0, 60)
        self.pause.setDecimals(1)
        self.pause.setSingleStep(0.5)
        self.pause.setSuffix(' s')
        self.pause.setValue(werte['pause'])
        self.schnee = QCheckBox('Schneefall im Hintergrund')
        self.schnee.setChecked(werte['schnee'])
        knoepfe = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        knoepfe.button(QDialogButtonBox.StandardButton.Cancel).setText('Abbrechen')
        knoepfe.accepted.connect(self.accept)
        knoepfe.rejected.connect(self.reject)
        form = QFormLayout(self)
        form.addRow('Figurgröße', self.groesse)
        form.addRow('Pause zwischen Szenen', self.pause)
        form.addRow('', self.schnee)
        form.addRow(knoepfe)

    def werte(self):
        return {'groesse': self.groesse.value(), 'pause': round(self.pause.value(), 1),
                'schnee': self.schnee.isChecked()}


# ---------------------------------------------------------------- Bild

def schoner_szenen():
    """Alle Szenen, die ohne Bildschirmfoto und ohne eigenen Auslöser auskommen."""
    return [k for k in finde_szenen().values() if not k.braucht and not k.nur_ausloeser]


class Himmel:
    """Dunkler Winterhimmel mit Sternen, Schneehang und leisem Schneefall."""

    def __init__(self, w, h, schnee):
        self.w, self.h = w, h
        self.bild = QPixmap(max(1, w), max(1, h))
        p = QPainter(self.bild)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        g = QLinearGradient(0, 0, 0, h)
        g.setColorAt(0, QColor('#050A16'))
        g.setColorAt(0.65, QColor('#0E1C36'))
        g.setColorAt(1, QColor('#1B2D4C'))
        p.fillRect(0, 0, w, h, g)
        zufall = random.Random(7)
        p.setPen(Qt.PenStyle.NoPen)
        for _ in range(int(w * h / 9000)):
            x, y = zufall.uniform(0, w), zufall.uniform(0, h * 0.7) ** 1.15 / (h * 0.7) ** 0.15
            c = QColor(255, 255, 240, zufall.randint(40, 170))
            p.setBrush(c)
            r = zufall.uniform(0.5, 1.6) * h / 1080
            p.drawEllipse(QPointF(x, y), r, r)
        mond = QRadialGradient(w * 0.82, h * 0.16, h * 0.12)
        mond.setColorAt(0, QColor(220, 230, 255, 60))
        mond.setColorAt(1, QColor(220, 230, 255, 0))
        p.setBrush(mond)
        p.drawEllipse(QPointF(w * 0.82, h * 0.16), h * 0.12, h * 0.12)
        p.end()
        self.flocken = []
        if schnee:
            for _ in range(int(w * h / 14000)):
                self.flocken.append(self.flocke(zufall, zufall.uniform(0, h)))

    def flocke(self, zufall, y):
        r = zufall.uniform(0.8, 2.6) * self.h / 1080
        return [zufall.uniform(0, self.w), y, r, r * 22 + 10, zufall.uniform(0, 6.3)]

    def schritt(self, dt, t):
        for f in self.flocken:
            f[1] += f[3] * dt
            f[0] += 12 * dt * (1 if (t * 0.4 + f[4]) % 6.3 < 3.15 else -1)
            if f[1] > self.h + 5:
                f[:] = self.flocke(random, -5)

    def zeichne(self, p):
        p.drawPixmap(0, 0, self.bild)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor(235, 240, 255, 150))
        for x, y, r, *_ in self.flocken:
            p.drawEllipse(QPointF(x, y), r, r)


class Buehne(QWidget):
    """Ein Fenster mit Himmel, in dem die Szenen nacheinander laufen."""

    def __init__(self, werte, klassen, groesse, parent=None):
        super().__init__(parent)
        self.werte, self.klassen = werte, klassen
        self.groesse = groesse
        self.reihe = []
        self.szene = None
        self.himmel = None
        self.naechste_ab = 0.3
        self.ende = False

    def resizeEvent(self, _):
        self.himmel = Himmel(self.width(), self.height(), self.werte['schnee'])

    def neue_szene(self):
        if not self.reihe:
            self.reihe = list(self.klassen)
            random.shuffle(self.reihe)
        geo = QRectF(0, 0, self.width(), self.height())
        s = geo.height() * self.groesse / FIGUR_HOEHE
        try:
            self.szene = self.reihe.pop()(geo, s, None)
        except Exception:       # eine kaputte Szene soll den Schoner nicht anhalten
            self.szene = None

    def schritt(self, dt, t):
        if self.himmel:
            self.himmel.schritt(dt, t)
        if self.szene:
            try:
                self.szene.schritt(dt)
            except Exception:
                self.szene = None
            if self.szene is None or self.szene.fertig:
                self.szene = None
                self.naechste_ab = t + self.werte['pause']
        elif not self.ende and t >= self.naechste_ab:
            self.neue_szene()
        self.update()

    def erschrecken(self):
        self.ende = True
        if self.szene:
            self.szene.erschrecken()

    def fertig(self):
        return self.szene is None

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        if self.himmel:
            self.himmel.zeichne(p)
        else:
            p.fillRect(self.rect(), QColor('black'))
        if self.szene:
            try:
                self.szene.zeichne(p)
            except Exception:
                pass
        p.end()


class Takt:
    """Gemeinsamer Takt für alle Bühnen, im Rhythmus der Bildwiederholung."""

    def __init__(self, buehnen, pruefe=None):
        self.buehnen, self.pruefe = buehnen, pruefe
        self.uhr = QElapsedTimer()
        self.uhr.start()
        self.zuletzt = 0.0
        self.puls = time.monotonic()    # letzter Takt, für den Wächter
        self.zeit = QTimer()
        self.zeit.setTimerType(Qt.TimerType.PreciseTimer)
        self.zeit.setInterval(0)
        self.zeit.timeout.connect(self.schritt)
        self.zeit.start()

    def jetzt(self):
        return self.uhr.elapsed() / 1000

    def schritt(self):
        self.puls = time.monotonic()
        dwmapi.DwmFlush()
        t = self.jetzt()
        dt = min(t - self.zuletzt, 0.05)
        if dt <= 0.001:
            time.sleep(0.004)       # ohne Komposition (z. B. Remote) nicht im Kreis drehen
            return
        self.zuletzt = t
        for b in self.buehnen:
            b.schritt(dt, t)
        if self.pruefe:
            self.pruefe(t)


# ---------------------------------------------------------------- Vollbild

def protokoll(text):
    if os.environ.get('SCHONER_PROTOKOLL'):
        print(f'{time.perf_counter():.3f} {text}', flush=True)


class LASTINPUTINFO(ctypes.Structure):
    _fields_ = [('cbSize', ctypes.c_uint), ('dwTime', ctypes.c_uint)]


def letzte_eingabe():
    info = LASTINPUTINFO(ctypes.sizeof(LASTINPUTINFO), 0)
    user32.GetLastInputInfo(ctypes.byref(info))
    return info.dwTime


def mauslage():
    pt = wintypes.POINT()
    user32.GetCursorPos(ctypes.byref(pt))
    return pt.x, pt.y


class Vollbild(Buehne):
    def __init__(self, werte, klassen, bildschirm, melde):
        super().__init__(werte, klassen, werte['groesse'] / 100)
        self.melde = melde
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent)
        self.setCursor(Qt.CursorShape.BlankCursor)
        self.setMouseTracking(True)
        self.setScreen(bildschirm)
        self.setGeometry(bildschirm.geometry())

    def keyPressEvent(self, _):
        self.melde()

    def mousePressEvent(self, _):
        self.melde()

    def wheelEvent(self, _):
        self.melde()

    def closeEvent(self, e):
        self.melde()
        e.ignore()


def vollbild(app, werte):
    klassen = schoner_szenen()
    start_maus, start_eingabe = mauslage(), letzte_eingabe()
    z = {'ende': None, 'eingabe': start_eingabe, 'maus': start_maus}
    beginn = time.monotonic()

    def melde():
        if z['ende'] is None:
            z['ende'] = time.monotonic()
            protokoll('Eingabe erkannt')
            for b in buehnen:
                b.erschrecken()

    buehnen = [Vollbild(werte, klassen, b, melde) for b in app.screens()]
    for b in buehnen:
        b.showFullScreen()
    buehnen[0].activateWindow()
    buehnen[0].raise_()
    user32.SetForegroundWindow(int(buehnen[0].winId()))
    app.setOverrideCursor(Qt.CursorShape.BlankCursor)

    def pruefe(_t):
        if z['ende'] is not None:
            if time.monotonic() - z['ende'] > SCHRECK_DAUER or all(b.fertig() for b in buehnen):
                protokoll('Ende')
                app.exit(0)     # nicht quit(): das bricht ab, weil die Fenster Schließen ablehnen
            return
        # Auch ohne Fokus (Tasten, die an ein anderes Fenster gehen): Jede Eingabe, bei der
        # die Maus stillsteht, ist Taste oder Klick. Leichtes Zittern der Maus zählt nicht.
        e, m = letzte_eingabe(), mauslage()
        if abs(m[0] - start_maus[0]) + abs(m[1] - start_maus[1]) > MAUS_SCHWELLE:
            melde()
        elif e != z['eingabe']:
            if m == z['maus'] and time.monotonic() - beginn > 0.3:
                melde()
            z['eingabe'] = e
        z['maus'] = m

    takt = Takt(buehnen, pruefe)

    def waechter():
        while True:
            time.sleep(0.05)
            ende = z['ende']
            if ende is not None and time.monotonic() - ende > WAECHTER:
                os._exit(0)
            if ende is None and time.monotonic() - takt.puls > 2.0 and letzte_eingabe() != start_eingabe:
                os._exit(0)     # die Oberfläche hängt, und jemand will an den Rechner

    threading.Thread(target=waechter, daemon=True).start()
    protokoll('läuft')
    app.exec()
    protokoll('exec zurück')


# ---------------------------------------------------------------- Vorschau

def vorschau(app, werte, hwnd):
    """Kleine Vorschau als Kindfenster des Einstellungsdialogs von Windows."""
    if not hwnd or not user32.IsWindow(hwnd):
        return
    r = wintypes.RECT()
    user32.GetClientRect(hwnd, ctypes.byref(r))
    w = Buehne(dict(werte, pause=min(werte['pause'], 0.5)), schoner_szenen(), 0.42)
    w.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool)
    w.setAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent)
    eigen = int(w.winId())
    stil = user32.GetWindowLongW(eigen, GWL_STYLE)
    user32.SetWindowLongW(eigen, GWL_STYLE, (stil & ~WS_POPUP) | WS_CHILD)
    user32.SetParent(eigen, hwnd)
    dpr = w.devicePixelRatioF() or 1.0
    w.resize(max(1, round(r.right / dpr)), max(1, round(r.bottom / dpr)))
    w.show()
    user32.MoveWindow(eigen, 0, 0, r.right, r.bottom, True)
    takt = Takt([w])  # noqa: F841  muss bis zum Ende leben
    pruefen = QTimer()
    pruefen.timeout.connect(lambda: None if user32.IsWindow(hwnd) else app.exit(0))
    pruefen.start(300)
    app.exec()


# ---------------------------------------------------------------- Sperren mit Weihnachtsmann

def langer_pfad(pfad):
    puffer = ctypes.create_unicode_buffer(1024)
    if ctypes.windll.kernel32.GetLongPathNameW(pfad, puffer, 1024):
        return puffer.value
    return pfad


def schoner_einstellung():
    """(ist unser Schoner gewählt und aktiv, ist „Anmeldeseite bei Reaktivierung“ an)"""
    import winreg
    werte = {}
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Control Panel\Desktop') as k:
            for n in ('SCRNSAVE.EXE', 'ScreenSaveActive', 'ScreenSaverIsSecure'):
                try:
                    werte[n] = str(winreg.QueryValueEx(k, n)[0])
                except FileNotFoundError:
                    werte[n] = ''
    except OSError:
        return False, False
    pfad = werte['SCRNSAVE.EXE']
    unser = bool(pfad) and pathlib.Path(langer_pfad(pfad)).name.lower() == 'weihnachtsmann.scr'
    return unser and werte['ScreenSaveActive'] != '0', werte['ScreenSaverIsSecure'] == '1'


def sperren():
    """Lässt Windows den eingerichteten Schoner sofort starten. Weil Windows ihn startet, gilt
    „Anmeldeseite bei Reaktivierung“: nach dem Schreck kommt der Sperrbildschirm. False, wenn
    dafür etwas nicht eingerichtet ist."""
    unser, sicher = schoner_einstellung()
    if not (unser and sicher):
        return False
    user32.SendMessageW.argtypes = [wintypes.HWND, ctypes.c_uint, wintypes.WPARAM, wintypes.LPARAM]
    user32.SendMessageW(user32.GetDesktopWindow(), 0x0112, 0xF140, 0)     # WM_SYSCOMMAND, SC_SCREENSAVE
    # Startet Windows den Schoner nicht (etwa weil ein Programm den Bildschirm wachhält),
    # trotzdem sperren: Wer „Sperren“ wählt, soll nie einen offenen Rechner zurücklassen.
    ende = time.monotonic() + 3.0
    while time.monotonic() < ende:
        if schoner_laeuft():
            return True
        time.sleep(0.1)
    user32.LockWorkStation()
    return True


def schoner_laeuft():
    an = wintypes.BOOL()
    user32.SystemParametersInfoW(0x0072, 0, ctypes.byref(an), 0)    # SPI_GETSCREENSAVERRUNNING
    if an.value:
        return True
    import subprocess
    aus = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq Weihnachtsmann.scr', '/NH'], capture_output=True,
                         encoding='mbcs', errors='replace', creationflags=0x08000000).stdout or ''
    return 'weihnachtsmann.scr' in aus.lower()


def sperren_oder_hinweis(eltern=None):
    """Für Verknüpfung und Menü: sperren, sonst erklären, was fehlt, und beim Einrichten helfen."""
    from PyQt6.QtWidgets import QMessageBox
    if sperren():
        return
    unser, _ = schoner_einstellung()
    text = ('„Sperren mit Weihnachtsmann“ startet den Bildschirmschoner sofort; nach dem Schreck '
            'kommt der Sperrbildschirm.\n\nDafür in den Bildschirmschoner-Einstellungen '
            + ('„Anmeldeseite bei Reaktivierung“ ankreuzen.' if unser else
               '„Weihnachtsmann“ auswählen und „Anmeldeseite bei Reaktivierung“ ankreuzen.'))
    box = QMessageBox(QMessageBox.Icon.Information, 'Weihnachtsmann', text, parent=eltern)
    einrichten = box.addButton('Einstellungen öffnen', QMessageBox.ButtonRole.AcceptRole)
    box.addButton('Abbrechen', QMessageBox.ButtonRole.RejectRole)
    box.exec()
    if box.clickedButton() is einrichten:
        import subprocess
        scr = pathlib.Path(sys.executable).with_name('Weihnachtsmann.scr')
        rundll = pathlib.Path(os.environ.get('SystemRoot', r'C:\Windows')) / 'System32' / 'rundll32.exe'
        if scr.exists():
            subprocess.Popen(f'"{rundll}" desk.cpl,InstallScreenSaver {scr}')     # Pfad ohne Anführungszeichen
        else:
            subprocess.Popen(['control.exe', 'desk.cpl,,@screensaver'])


# ---------------------------------------------------------------- Start

def main(argv):
    art, hwnd = aufruf(argv)
    app = QApplication(argv[:1])
    werte = lade()
    if art == 's':
        vollbild(app, werte)
    elif art == 'p':
        vorschau(app, werte, hwnd)
    else:
        d = Einstellungen(werte)
        if hwnd and user32.IsWindow(hwnd):
            d.winId()
            d.windowHandle().setTransientParent(QWindow.fromWinId(hwnd))
        if d.exec() == QDialog.DialogCode.Accepted:
            speichere(d.werte())
    os._exit(0)     # ohne langes Aufräumen von Qt sofort weg
