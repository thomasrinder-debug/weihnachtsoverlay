# Entfernt das Weihnachtsmann-Overlay wieder (Programmordner, Verknüpfungen, Eintrag in „Apps“).
$ErrorActionPreference = 'SilentlyContinue'
$ziel = Split-Path -Parent $MyInvocation.MyCommand.Path
Get-Process -Name 'Weihnachtsmann', 'Weihnachtsmann.scr' | Stop-Process -Force
Start-Sleep -Milliseconds 500
Remove-Item (Join-Path ([Environment]::GetFolderPath('Programs')) 'Weihnachtsmann.lnk') -Force
Remove-Item (Join-Path ([Environment]::GetFolderPath('Desktop')) 'Weihnachtsmann.lnk') -Force
Remove-Item (Join-Path ([Environment]::GetFolderPath('Programs')) 'Weihnachtsmann als Bildschirmschoner einrichten.lnk') -Force
Remove-Item (Join-Path ([Environment]::GetFolderPath('Programs')) 'Sperren mit Weihnachtsmann.lnk') -Force
# War er als Bildschirmschoner gewählt, die Auswahl entfernen (sonst zeigt Windows einen toten Eintrag).
$desk = 'HKCU:\Control Panel\Desktop'
$gewaehlt = (Get-ItemProperty $desk -Name 'SCRNSAVE.EXE').'SCRNSAVE.EXE'
if ($gewaehlt -and ((Split-Path -Leaf $gewaehlt) -ieq 'Weihnachtsmann.scr' -or $gewaehlt -like "$ziel*")) {
    Remove-ItemProperty $desk -Name 'SCRNSAVE.EXE' -Force
}
Remove-Item (Join-Path $env:APPDATA 'Weihnachtsmann') -Recurse -Force
Remove-Item 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\Weihnachtsmann' -Recurse -Force
# den eigenen Ordner erst nach dem Ende dieses Skripts löschen
Start-Process cmd.exe -ArgumentList "/c timeout /t 2 /nobreak >nul & rmdir /s /q `"$ziel`"" -WindowStyle Hidden
