@echo off
rem Startet das Overlay ohne Konsolenfenster.
rem Strg+Alt+A: Automatik an/aus, Strg+Alt+W: naechste Szene, Strg+Alt+1..9: bestimmte Szene, Strg+Alt+Q: beenden.
rem Optionen werden durchgereicht, z. B.  weihnachtsmann.cmd --monitor 2
start "" "%~dp0.venv\Scripts\pythonw.exe" "%~dp0weihnachtsmann.py" %*
