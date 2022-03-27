Param($targetfile)
$filename = [System.IO.Path]::GetFileName($targetfile)
$WshShell = New-Object -comObject WScript.Shell
$shortcutfile = "$Home\Desktop\" + $filename + ".lnk"
$Shortcut = $WshShell.CreateShortcut($shortcutfile)
$Shortcut.TargetPath = $targetfile
$Shortcut.Save()

