"""Baut das Setup: dist/Weihnachtsmann-Setup-<version>.exe

    .venv\\Scripts\\python.exe -m pip install pyinstaller
    .venv\\Scripts\\python.exe installer\\bauen.py 1.0.0

1. PyInstaller packt das Programm samt Python und Qt in einen Ordner (ohne Konsole).
2. Eine Konsolenfassung prüft, dass im gepackten Programm alle Szenen gefunden werden.
3. Der Ordner wird gezippt; IExpress (gehört zu Windows) baut daraus ein Setup, das
   installieren.ps1 ausführt: Installation nach %LOCALAPPDATA%\\Programs\\Weihnachtsmann,
   Verknüpfungen in Startmenü und auf dem Desktop, Eintrag unter „Apps“ zum Deinstallieren.
"""
import pathlib
import shutil
import subprocess
import sys

HIER = pathlib.Path(__file__).resolve().parent
PROJ = HIER.parent
BUILD = PROJ / 'build'
DIST = PROJ / 'dist'
PY = sys.executable


def pyinstaller(name, konsole):
    args = [PY, '-m', 'PyInstaller', '--noconfirm', '--clean', '--onedir', '--name', name,
            '--distpath', str(BUILD / 'dist'), '--workpath', str(BUILD / 'work'), '--specpath', str(BUILD),
            '--collect-submodules', 'szenen', '--collect-submodules', 'zeichnen',
            '--exclude-module', 'tkinter', '--exclude-module', 'PyQt6.QtWebEngineCore',
            '--exclude-module', 'PyQt6.QtQml', '--exclude-module', 'PyQt6.QtQuick',
            '--exclude-module', 'PyQt6.QtMultimedia', '--exclude-module', 'PyQt6.QtNetwork',
            '--exclude-module', 'PyQt6.QtPdf', '--exclude-module', 'PyQt6.QtSvg',
            '--exclude-module', 'PyQt6.QtOpenGL',
            '--console' if konsole else '--windowed', str(PROJ / 'weihnachtsmann.py')]
    subprocess.run(args, check=True, cwd=PROJ)
    return BUILD / 'dist' / name


def pruefen(ordner, erwartet):
    hilfe = subprocess.run([str(ordner / 'WeihnachtsmannTest.exe'), '--help'], capture_output=True, text=True,
                           encoding='cp1252', errors='replace', check=True).stdout
    fehlt = [n for n in erwartet if n not in hilfe]
    if fehlt:
        sys.exit(f'Im gepackten Programm fehlen Szenen: {fehlt}')
    print(f'Gepacktes Programm findet alle {len(erwartet)} Szenen.')


def setup(app, version):
    paket = BUILD / 'paket'
    shutil.rmtree(paket, ignore_errors=True)
    paket.mkdir(parents=True)
    (app / 'VERSION.txt').write_text(version, encoding='ascii')
    shutil.make_archive(str(paket / 'app'), 'zip', app)
    for datei in ('installieren.ps1', 'deinstallieren.ps1'):
        shutil.copy(HIER / datei, paket / datei)
    DIST.mkdir(exist_ok=True)
    ziel = DIST / f'Weihnachtsmann-Setup-{version}.exe'
    befehl = 'powershell.exe -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File installieren.ps1'
    sed = f"""[Version]
Class=IEXPRESS
SEDVersion=3
[Options]
PackagePurpose=InstallApp
ShowInstallProgramWindow=1
HideExtractAnimation=0
UseLongFileName=1
InsideCompressed=0
CAB_FixedSize=0
CAB_ResvCodeSigning=0
RebootMode=N
InstallPrompt=%InstallPrompt%
DisplayLicense=%DisplayLicense%
FinishMessage=%FinishMessage%
TargetName=%TargetName%
FriendlyName=%FriendlyName%
AppLaunched=%AppLaunched%
PostInstallCmd=%PostInstallCmd%
AdminQuietInstCmd=%AdminQuietInstCmd%
UserQuietInstCmd=%UserQuietInstCmd%
SourceFiles=SourceFiles
[Strings]
InstallPrompt=Weihnachtsmann-Overlay {version} installieren?
DisplayLicense=
FinishMessage=Fertig. Das Overlay läuft jetzt (Symbol im Infobereich). Strg+Alt+W startet eine Szene, Strg+Alt+A schaltet die Automatik, Strg+Alt+Q beendet.
TargetName={ziel}
FriendlyName=Weihnachtsmann-Overlay
AppLaunched={befehl}
PostInstallCmd=<None>
AdminQuietInstCmd={befehl}
UserQuietInstCmd={befehl}
FILE0="installieren.ps1"
FILE1="deinstallieren.ps1"
FILE2="app.zip"
[SourceFiles]
SourceFiles0={paket}\\
[SourceFiles0]
%FILE0%=
%FILE1%=
%FILE2%=
"""
    (paket / 'setup.sed').write_text(sed, encoding='mbcs')
    subprocess.run([r'C:\Windows\System32\iexpress.exe', '/N', '/Q', str(paket / 'setup.sed')], check=True)
    if not ziel.exists():
        sys.exit('IExpress hat kein Setup erzeugt.')
    print(f'{ziel}  ({ziel.stat().st_size / 1e6:.1f} MB)')
    return paket


def main():
    version = sys.argv[1] if len(sys.argv) > 1 else '1.0.0'
    sys.path.insert(0, str(PROJ))
    from szenen import finde_szenen
    erwartet = list(finde_szenen())
    test = pyinstaller('WeihnachtsmannTest', konsole=True)
    pruefen(test, erwartet)
    app = pyinstaller('Weihnachtsmann', konsole=False)
    setup(app, version)


if __name__ == '__main__':
    main()
