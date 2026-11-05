"""Was auf dem Bildschirm zu sehen ist: die Schreibmarke mit der Zeile davor.
Nur unter Windows.

Das Overlay ändert nichts an anderen Programmen. Es macht ein Bildschirmfoto,
schneidet die Zeile aus und gibt sie den Szenen als Daten: Bildausschnitte,
Rechtecke in logischen Pixeln (wie die Szene zeichnet) und Flicken, mit denen
die Szene das Original abdeckt, solange die Kopie durcheinandergerät. Die Auswertung
der Bilder steht in bildanalyse.py.
"""
import ctypes
from ctypes import wintypes

from bildanalyse import Umrechnung, tippzeile_daten

# ---------------------------------------------------------------- Windows-Abfragen

class GUITHREADINFO(ctypes.Structure):
    _fields_ = [('cbSize', wintypes.DWORD), ('flags', wintypes.DWORD), ('hwndActive', wintypes.HWND),
                ('hwndFocus', wintypes.HWND), ('hwndCapture', wintypes.HWND), ('hwndMenuOwner', wintypes.HWND),
                ('hwndMoveSize', wintypes.HWND), ('hwndCaret', wintypes.HWND), ('rcCaret', wintypes.RECT)]


class VARIANT(ctypes.Structure):
    _fields_ = [('vt', ctypes.c_ushort), ('r1', ctypes.c_ushort), ('r2', ctypes.c_ushort), ('r3', ctypes.c_ushort),
                ('wert', ctypes.c_longlong), ('rest', ctypes.c_longlong)]


class GUID(ctypes.Structure):
    _fields_ = [('a', ctypes.c_uint32), ('b', ctypes.c_uint16), ('c', ctypes.c_uint16), ('d', ctypes.c_ubyte * 8)]


IID_IAccessible = GUID(0x618736E0, 0x3C3D, 0x11CF, (ctypes.c_ubyte * 8)(0x81, 0x0C, 0x00, 0xAA, 0x00, 0x38, 0x9B, 0x71))
OBJID_CARET = -8


def _user32():
    u = ctypes.windll.user32
    u.GetWindowRect.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.RECT)]
    u.ClientToScreen.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.POINT)]
    u.FindWindowW.restype = wintypes.HWND
    u.GetForegroundWindow.restype = wintypes.HWND
    u.GetAncestor.argtypes = [wintypes.HWND, ctypes.c_uint]
    u.GetAncestor.restype = wintypes.HWND
    return u


def fensterrechteck(hwnd):
    r = wintypes.RECT()
    _user32().GetWindowRect(hwnd, ctypes.byref(r))
    return r.left, r.top, r.right, r.bottom


def physisch(screen):
    g, d = screen.geometry(), screen.devicePixelRatio()
    return g.x(), g.y(), g.x() + round(g.width() * d), g.y() + round(g.height() * d)


def bildschirmfoto(screen):
    """(Bild in physischen Pixeln, Umrechnung) für einen Bildschirm."""
    bild = screen.grabWindow(0).toImage()
    return bild, Umrechnung(screen.geometry(), screen.devicePixelRatio())


def _caret_msaa(hwnd):
    """Schreibmarke über MSAA (OBJID_CARET); klappt in Browsern und vielen anderen Programmen."""
    oleacc = ctypes.windll.oleacc
    zeiger = ctypes.c_void_p()
    if oleacc.AccessibleObjectFromWindow(wintypes.HWND(hwnd), ctypes.c_long(OBJID_CARET),
                                         ctypes.byref(IID_IAccessible), ctypes.byref(zeiger)) != 0 or not zeiger:
        return None
    vtab = ctypes.cast(ctypes.cast(zeiger, ctypes.POINTER(ctypes.c_void_p))[0], ctypes.POINTER(ctypes.c_void_p))
    lage = ctypes.WINFUNCTYPE(ctypes.c_long, ctypes.c_void_p, ctypes.POINTER(ctypes.c_long),
                              ctypes.POINTER(ctypes.c_long), ctypes.POINTER(ctypes.c_long),
                              ctypes.POINTER(ctypes.c_long), VARIANT)(vtab[22])
    freigabe = ctypes.WINFUNCTYPE(ctypes.c_ulong, ctypes.c_void_p)(vtab[2])
    x, y, w, h = ctypes.c_long(), ctypes.c_long(), ctypes.c_long(), ctypes.c_long()
    try:
        ok = lage(zeiger, ctypes.byref(x), ctypes.byref(y), ctypes.byref(w), ctypes.byref(h), VARIANT(3)) == 0
    finally:
        freigabe(zeiger)
    if not ok or h.value <= 0:
        return None
    return x.value, y.value, x.value + max(1, w.value), y.value + h.value


def schreibmarke():
    """Schreibmarke im Vordergrundfenster als physisches Rechteck und Fenster, oder (None, None)."""
    u = _user32()
    vorn = u.GetForegroundWindow()
    if not vorn:
        return None, None
    faden = u.GetWindowThreadProcessId(vorn, None)
    info = GUITHREADINFO(cbSize=ctypes.sizeof(GUITHREADINFO))
    if u.GetGUIThreadInfo(faden, ctypes.byref(info)) and info.hwndCaret:
        r = info.rcCaret
        if r.bottom > r.top:
            pt = wintypes.POINT(r.left, r.top)
            u.ClientToScreen(info.hwndCaret, ctypes.byref(pt))
            return (pt.x, pt.y, pt.x + max(1, r.right - r.left), pt.y + r.bottom - r.top), info.hwndCaret
    fenster = info.hwndFocus or vorn
    try:
        marke = _caret_msaa(fenster)
    except OSError:
        marke = None
    if marke and marke[0] == marke[1] == 0:
        marke = None
    return marke, fenster if marke else None


def tippzeile(screen):
    """Daten für die Tippkatze oder None (keine Schreibmarke, nichts getippt, anderer Bildschirm)."""
    marke, fenster = schreibmarke()
    if not marke:
        return None
    sx0, sy0, sx1, sy1 = physisch(screen)
    if not (sx0 <= marke[0] < sx1 and sy0 <= marke[1] < sy1):
        return None
    if _user32().GetAncestor(fenster, 2) == _user32().FindWindowW('Shell_TrayWnd', None):
        return None
    links = fensterrechteck(fenster)[0]
    bild, um = bildschirmfoto(screen)
    m = (*um.im_bild(marke[0], marke[1]), *um.im_bild(marke[2], marke[3]))
    return tippzeile_daten(bild, m, um, um.im_bild(links, 0)[0])


def fuer(art, screen):
    """Daten für eine Szene, die etwas vom Bildschirm braucht (Szene.braucht)."""
    try:
        return {'schreibmarke': tippzeile}[art](screen)
    except (OSError, ValueError, KeyError):
        return None
