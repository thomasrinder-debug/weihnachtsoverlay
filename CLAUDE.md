# Weihnachtsmann-Overlay

Animierter Weihnachtsmann als durchsichtiges Overlay für Windows 11, gedacht für Thomas Rinders Weihnachtsvorlesung (HAW Kiel). Er läuft über PowerPoint/PDF im Vollbild, kommt von selbst mit zufälligen Pausen und erschrickt, sobald jemand die Maus bewegt oder eine Taste drückt.

## Aufbau

- `weihnachtsmann.py`: Fenster, Tastenkürzel, Infobereich, Automatik. Nur unter Windows lauffähig (ctypes.windll).
- `szenen/`: eine Datei pro Szene, wird automatisch gefunden. `szenen/basis.py` enthält `Szene` und die Bausteine (Schritte).
- `zeichnen/`: `grundlagen.py` (Farben, Pelz, Teilchen), `figur.py` (Weihnachtsmann, Posen, Kopf von vorn), `figuren.py` (weitere Figuren: Schneemann, Wichtel, Lebkuchenmann, Pinguin, Nussknacker, Tannenbaum, Eisbär, Rentier), `requisiten.py` (Rentier, Schlitten, Fahrrad, Schornstein, Seil, Geschenk, Lichterkette, Strumpf und anderes).
- Der verrückte Professor: Figur in `zeichnen/professor.py`, Laborrequisiten und Kreideschrift in `zeichnen/labor.py` (weitere in `labor_a.py` bis `labor_f.py`), gemeinsame Bausteine in `szenen/professor.py` (`ProfSzene` mit dem Professor als Hauptfigur, `TafelSzene`, Schreck-Varianten, Triumph-Pose, `Knall`, `Publikumsblick`, `Umkippen`), Computer-Grundlage in `szenen/geraet.py`. Jede Professor-Szene folgt Aufbau – Steigerung – Knall – Reaktion in 8–12 s, mit großen, körperlichen Pointen (siehe `szenen/IDEEN.md`). Seine Szenen heißen `szenen/prof_*.py`. Auf seiner Tafel sind Ziffern, Rechenzeichen und einfache Gleichungen erlaubt, keine Wörter.
- `pruefen.py`: rendert jede Szene ohne Fenster als Vorschaubild (`vorschau/<name>.png`) und testet den Schreck.
- `abgreifen.py` (nur Windows) und `bildanalyse.py`: für Szenen mit `braucht = 'schreibmarke'`. Bildschirmfoto und Schreibmarke werden ermittelt, die Szene bekommt Ausschnitt, Rechtecke (logische Pixel) und Flicken als `self.daten`. `pruefen.py` erzeugt dafür einen Testbildschirm. Szenen mit `nur_ausloeser = True` kommen nicht in der Zufallsreihe; die Tippkatze startet die Automatik, wenn nach dem Tippen 2–4 s Ruhe ist.

`szenen/` und `zeichnen/` dürfen nichts Windows-Spezifisches importieren, damit `pruefen.py` überall läuft.

## Eine neue Szene

Neue Datei in `szenen/`, Klasse von `Szene`, mit `name`, `titel`, `reihenfolge`. Der `name` muss eindeutig sein, sonst verdrängt die Szene stillschweigend eine andere. In `ablauf()` die Schrittliste zurückgeben, Beispiel `szenen/spaziergang.py`. Eigener Zustand gehört in `vorbereiten()`, eigenes Zeichnen in `zeichne_hinten`/`zeichne_vorn`, zusätzlicher Bereich in `grenzen_extra()`. Neue Zeichnungen (Requisiten) kommen nach `zeichnen/requisiten.py`. Fehlt ein Baustein, ihn allgemein in `szenen/basis.py` ergänzen, nicht in der Szene nachbauen.

Weitere Figuren sind Darsteller: in `vorbereiten()` mit `self.dazu('wichtel', Wichtel, groesse=0.7)` anlegen, dann laufen alle Schritte auch mit ihnen, etwa `Mit('wichtel', Gehe(bis=...))` oder im Hintergrund `Nebenbei(Mit(...))`. Bei mehreren Figuren liefert `self.schreck_alle()` den Standardschreck für alle. Staub, Schnee und Krümel über `self.streue(...)`. Ideen und bereits umgesetzte Gags stehen in `szenen/IDEEN.md`.

Vorgaben von Thomas:
- **Nur an den Bildschirmrändern** (oben, unten, links, rechts); die Mitte mit den Folien bleibt frei. Ausnahme: die Tippkatze sitzt im getippten Text.
- **Schreckhaft:** `schreck_ablauf()` muss die Szene nach Maus/Taste schnell beenden (unter 3 s, besser ~1 s), mit sichtbarem großem Schreck. Standard: Erschrecke + Renne zum nächsten Rand.
- **Kein Text**, keine Sprechblasen.
- **Klein** (Standardgröße 15 % der Bildschirmhöhe) und liebevoll detailliert gezeichnet (Verläufe, Pelz, Blinzeln).
- Eigene, freie Gestaltung: keine bekannten Figuren oder Marken nachbauen.
- Höchstens 9 Szenen bekommen ein Tastenkürzel (Strg+Alt+1..9); weitere laufen über Automatik und Menü.

## Prüfen

```
pip install -r requirements.txt
QT_QPA_PLATFORM=offscreen python pruefen.py            # Linux/Cloud
python pruefen.py                                       # Windows
```

`pruefen.py` muss „Alles in Ordnung.“ melden. Die Vorschaubilder ansehen, bevor eine Szene als fertig gilt (Figur verdeckt nichts Falsches, roter Rahmen umschließt alles Gezeichnete).

## Stil

Deutsch in Namen, Kommentaren und Texten, wie im vorhandenen Code. Kommentare sparsam. Commit-Nachrichten auf Deutsch.
