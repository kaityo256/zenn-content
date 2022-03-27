$WshShell = New-Object -comObject WScript.Shell
$filename = "test.txt"
$shortcutfile = "$Home\Desktop\" + $filename + ".lnk"
$Shortcut = $WshShell.CreateShortcut($shortcutfile)
$targetpath= "\\wsl.localhost\Ubuntu\home\watanabe\test.txt"
$Shortcut.TargetPath = $targetpath
$Shortcut.Save()

