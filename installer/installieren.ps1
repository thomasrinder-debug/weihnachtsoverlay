# Installiert das Weihnachtsmann-Overlay für den angemeldeten Benutzer (ohne Adminrechte).
# Wird vom Setup (IExpress) aus dem Entpackordner gestartet; app.zip liegt daneben.
param(
    [string]$Ziel = (Join-Path $env:LOCALAPPDATA 'Programs\Weihnachtsmann'),
    [switch]$Test       # nur entpacken, keine Verknüpfungen, kein Registry-Eintrag, keine Meldung
)
$ErrorActionPreference = 'Stop'
$quelle = Split-Path -Parent $MyInvocation.MyCommand.Path

Get-Process -Name 'Weihnachtsmann', 'Weihnachtsmann.scr' -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep -Milliseconds 300
if (Test-Path $Ziel) { Remove-Item $Ziel -Recurse -Force }
New-Item -ItemType Directory -Force -Path $Ziel | Out-Null
Expand-Archive -Path (Join-Path $quelle 'app.zip') -DestinationPath $Ziel -Force
Copy-Item (Join-Path $quelle 'deinstallieren.ps1') $Ziel -Force
if ($Test) { return }

$exe = Join-Path $Ziel 'Weihnachtsmann.exe'
$shell = New-Object -ComObject WScript.Shell
$startmenue = Join-Path ([Environment]::GetFolderPath('Programs')) 'Weihnachtsmann.lnk'
$desktop = Join-Path ([Environment]::GetFolderPath('Desktop')) 'Weihnachtsmann.lnk'
foreach ($pfad in @($startmenue, $desktop)) {
    $lnk = $shell.CreateShortcut($pfad)
    $lnk.TargetPath = $exe
    $lnk.WorkingDirectory = $Ziel
    $lnk.Description = 'Weihnachtsmann-Overlay (Strg+Alt+W: Szene, Strg+Alt+Q: beenden)'
    $lnk.Save()
}
# Bildschirmschoner: nicht ungefragt aktivieren, nur ein Eintrag zum Einrichten. Er wirkt wie
# „Installieren“ im Kontextmenü einer .scr: auswählen und die Bildschirmschoner-Einstellungen öffnen.
$scr = Join-Path $Ziel 'Weihnachtsmann.scr'
$lnk = $shell.CreateShortcut((Join-Path ([Environment]::GetFolderPath('Programs')) 'Weihnachtsmann als Bildschirmschoner einrichten.lnk'))
$lnk.TargetPath = Join-Path $env:SystemRoot 'System32\rundll32.exe'
$lnk.Arguments = "desk.cpl,InstallScreenSaver $scr"
$lnk.WorkingDirectory = $Ziel
$lnk.IconLocation = "$exe,0"
$lnk.Description = 'Weihnachtsmann als Bildschirmschoner auswaehlen (Windows-Einstellungen)'
$lnk.Save()
# Sperren mit Weihnachtsmann (Strg+Alt+L): Windows startet den Schoner sofort, nach dem Schreck
# kommt der Sperrbildschirm. Ist das nicht eingerichtet, erklärt ein Hinweis, was fehlt.
$lnk = $shell.CreateShortcut((Join-Path ([Environment]::GetFolderPath('Programs')) 'Sperren mit Weihnachtsmann.lnk'))
$lnk.TargetPath = $exe
$lnk.Arguments = '--sperren'
$lnk.WorkingDirectory = $Ziel
$lnk.Hotkey = 'CTRL+ALT+L'
$lnk.Description = 'Bildschirmschoner starten, danach Sperrbildschirm (Strg+Alt+L)'
$lnk.Save()

$schluessel = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\Weihnachtsmann'
New-Item -Path $schluessel -Force | Out-Null
$deinst = 'powershell.exe -NoProfile -ExecutionPolicy Bypass -File "' + (Join-Path $Ziel 'deinstallieren.ps1') + '"'
Set-ItemProperty $schluessel DisplayName 'Weihnachtsmann-Overlay'
Set-ItemProperty $schluessel DisplayVersion (Get-Content (Join-Path $Ziel 'VERSION.txt') -ErrorAction SilentlyContinue)
Set-ItemProperty $schluessel Publisher 'Thomas Rinder'
Set-ItemProperty $schluessel InstallLocation $Ziel
Set-ItemProperty $schluessel DisplayIcon $exe
Set-ItemProperty $schluessel UninstallString $deinst
Set-ItemProperty $schluessel NoModify 1 -Type DWord
Set-ItemProperty $schluessel NoRepair 1 -Type DWord

Start-Process $exe
