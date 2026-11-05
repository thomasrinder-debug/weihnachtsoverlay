# Installiert das Weihnachtsmann-Overlay für den angemeldeten Benutzer (ohne Adminrechte).
# Wird vom Setup (IExpress) aus dem Entpackordner gestartet; app.zip liegt daneben.
param(
    [string]$Ziel = (Join-Path $env:LOCALAPPDATA 'Programs\Weihnachtsmann'),
    [switch]$Test       # nur entpacken, keine Verknüpfungen, kein Registry-Eintrag, keine Meldung
)
$ErrorActionPreference = 'Stop'
$quelle = Split-Path -Parent $MyInvocation.MyCommand.Path

Get-Process -Name 'Weihnachtsmann' -ErrorAction SilentlyContinue | Stop-Process -Force
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
