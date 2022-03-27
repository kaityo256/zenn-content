function wln() {
  temp_ps1=`mktemp`.ps1
cat <<'EOD' > $temp_ps1
Param($targetfile)
$filename = [System.IO.Path]::GetFileName($targetfile)
$WshShell = New-Object -comObject WScript.Shell
$shortcutfile = "$Home\Desktop\" + $filename + ".lnk"
$Shortcut = $WshShell.CreateShortcut($shortcutfile)
$Shortcut.TargetPath = $targetfile
$Shortcut.Save()
EOD

targetfile=$(wslpath -w $1)
ps1file=$(wslpath -w $temp_ps1)
powershell.exe $ps1file $targetfile
rm -f $temp_ps1
}

