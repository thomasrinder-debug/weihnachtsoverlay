# Entfernt das Weihnachtsmann-Overlay wieder (Programmordner, Verknüpfungen, Eintrag in „Apps“).
$ErrorActionPreference = 'SilentlyContinue'
$ziel = Split-Path -Parent $MyInvocation.MyCommand.Path
Get-Process -Name 'Weihnachtsmann' | Stop-Process -Force
Start-Sleep -Milliseconds 500
Remove-Item (Join-Path ([Environment]::GetFolderPath('Programs')) 'Weihnachtsmann.lnk') -Force
Remove-Item (Join-Path ([Environment]::GetFolderPath('Desktop')) 'Weihnachtsmann.lnk') -Force
Remove-Item 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\Weihnachtsmann' -Recurse -Force
# den eigenen Ordner erst nach dem Ende dieses Skripts löschen
Start-Process cmd.exe -ArgumentList "/c timeout /t 2 /nobreak >nul & rmdir /s /q `"$ziel`"" -WindowStyle Hidden
