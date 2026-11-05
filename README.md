# Weihnachtsmann-Overlay

Ein kleiner, schreckhafter Weihnachtsmann, der unter Windows 11 am Bildschirmrand auftaucht, auch über Präsentationen im Vollbild. Bewegt jemand die Maus oder drückt eine Taste, erschrickt er und verschwindet.

## Starten

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

## Szenen prüfen

`python pruefen.py` rendert alle Szenen als Vorschaubilder nach `vorschau/` und testet den Schreck. Wie neue Szenen entstehen, steht in `CLAUDE.md`.
