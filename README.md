# Weihnachtsmann-Overlay

Ein kleiner, schreckhafter Weihnachtsmann, der unter Windows 11 am Bildschirmrand auftaucht, auch über Präsentationen im Vollbild. Bewegt jemand die Maus oder drückt eine Taste, erschrickt er und verschwindet.

## Installieren (ohne Python)

Unter „Releases“ auf GitHub `Weihnachtsmann-Setup-<version>.exe` herunterladen und starten. Das Setup braucht keine Adminrechte; es installiert nach `%LOCALAPPDATA%\Programs\Weihnachtsmann`, legt Verknüpfungen im Startmenü und auf dem Desktop an und startet das Overlay. Entfernen über Windows-Einstellungen → Apps → „Weihnachtsmann-Overlay“. Das Setup ist nicht signiert, Windows SmartScreen fragt deshalb beim ersten Start nach („Weitere Informationen“ → „Trotzdem ausführen“).

Setup selbst bauen: `.venv\Scripts\python.exe -m pip install pyinstaller`, dann `.venv\Scripts\python.exe installer\bauen.py 1.0.0`; das Ergebnis liegt in `dist/`.

## Starten aus dem Quellcode

```
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
weihnachtsmann.cmd
```

Beim Start erscheint ein Symbol im Infobereich mit Menü.

| Tasten | Wirkung |
|---|---|
| Strg+Alt+A | Automatik an/aus (Szenen von selbst, zufällige Pausen) |
| Strg+Alt+W | zufällige Szene |
| Strg+Alt+1 … 9 | bestimmte Szene |
| Strg+Alt+Q | beenden |

Optionen: `--monitor 2` (Beamer), `--groesse 0.2`, `--pause 10 60`, `--manuell`, `--mutig` (erschrickt nicht), `--sofort [szene]`, `--liste`.

## Als Bildschirmschoner

Das Setup legt neben `Weihnachtsmann.exe` auch `Weihnachtsmann.scr` ab, schaltet den Bildschirmschoner aber nicht ein. Einrichten: im Startmenü „Weihnachtsmann als Bildschirmschoner einrichten“ (oder Rechtsklick auf die `.scr` → „Installieren“). Danach öffnen sich die Bildschirmschoner-Einstellungen von Windows, dort Wartezeit und „Anmeldeseite bei Reaktivierung“ wählen. „Einstellungen“ öffnet Figurgröße, Pause zwischen den Szenen und Schneefall (gespeichert in `%APPDATA%\Weihnachtsmann\schoner.ini`).

Im Schoner laufen die Szenen ohne Pause nacheinander vor einem Winterhimmel, auf allen Bildschirmen. Bewegt jemand die Maus, klickt oder drückt eine Taste, erschrecken die Figuren kurz, dann ist der Schoner nach höchstens etwa einer Sekunde weg. Die Tippkatze und Szenen, die Bildschirmfotos brauchen, laufen dort nicht. Aus dem Quellcode: `python weihnachtsmann.py /s` (Vollbild), `/p <hwnd>` (Vorschau), `/c` (Einstellungen).

## Szenen prüfen

`python pruefen.py` rendert alle Szenen als Vorschaubilder nach `vorschau/` und testet den Schreck. Wie neue Szenen entstehen, steht in `CLAUDE.md`.

## Lizenz

Copyright © 2026 Thomas Rinder. Freie Software unter der GNU General Public License v3.0, siehe `LICENSE`. Du darfst sie nutzen, verändern und weitergeben, auch veränderte Fassungen weitergeben, solange diese ebenfalls unter der GPL-3.0 stehen und ihr Quelltext offen ist. Das Setup enthält PyQt6 (GPL-3.0) und Qt (LGPL-3.0).
