---
title: "WSLからWindows側にショートカットファイルを作る"
emoji: "🤖"
type: "tech" # tech: 技術記事 / idea: アイデア
topics: ["wsl","zsh"]
published: true
---

## TL;DR

WSLのUbuntu側でファイルを指定して、Windowsのデスクトップにショートカットファイルを作るシェルスクリプト関数`wln`を作った。`wln filename`として実行すると、そのファイルのショートカットがWindowsデスクトップに作成される。

```sh
wln test.txt
```

実装は以下の通り。

```sh
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
```

Zshでしか確認していないが、Bash系なら動くと思う。

これを実行する前に、PowerShell側でスクリプトのセキュリティポリシーを`Bypass`か`Unrestricted`にしておく必要がある。

```sh
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope CurrentUser
```

もしくは

```sh
Set-ExecutionPolicy -ExecutionPolicy Unrestricted -Scope CurrentUser
```

:::message alert
`Bypass`にすると、全てのPowerShellスクリプトが無条件で実行できるようになってしまうため、よくわからない場合は設定しないこと。
:::


## はじめに

Windowsを使っていて、ほぼ全ての作業をWSLのUbuntuで行っている人は多いのではないかと思う。特に、Ubuntu上のGitでファイルを管理していると、必要なファイルが全てWSL側にあることになる。そのファイルをWindows側で開きたい時、例えば[openコマンドを用意](https://zenn.dev/kaityo256/articles/open_command_on_wsl)して開いても良いが、たまにショートカットファイルをデスクトップに作りたい時がある(例えばウェブ会議していて、複数のPDFファイルを順番に共有したいときとか)。というわけで、そんなコマンド`wln`を作りたい。

## ショートカットの作成

Windowsのショートカットファイルを作るのにはいくつか方法があるが、一番簡単なのはCOMで`WScript.Shell`オブジェクトを作って`CreateShortcut`メソッドを叩くことだ。

例えばPowerShell上で以下を実行すると、`$HOME\test.txt`へのショートカットをデスクトップ上に作ることができる。

```sh
$WshShell = New-Object -comObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("$Home\Desktop\test.txt.lnk")
$Shortcut.TargetPath = "$Home\test.txt"
$Shortcut.Save()
```

順番に

* COMを叩いて`WScript.Shell`オブジェクトを作り
* ショートカットファイル名を指定してショートカットオブジェクトを作り
* ショートカットオブジェクトにターゲットパスを指定して* 保存する

ということをしているだけだ。

## スクリプトのセキュリティポリシー

上記はPowerShell上で一行ずつ実行したが、これを例えば`test.ps1`というファイルに保存してスクリプトファイルとして実行すると怒られる。

```sh
$ ./test.ps1
./test.ps1 : このシステムではスクリプトの実行が無効になっているため、ファイル C:\Users\username\test.ps1 を読み込むこと
ができません。詳細については、「about_Execution_Policies」(https://go.microsoft.com/fwlink/?LinkID=135170) を参照してく
ださい。
発生場所 行:1 文字:1
+ ./test.ps1
+ ~~~~~~~~~~
    + CategoryInfo          : セキュリティ エラー: (: ) []、PSSecurityException
    + FullyQualifiedErrorId : UnauthorizedAccess
```

これは、デフォルトでPowerShellスクリプトの実行ポリシーが「Restricted(禁止)」になっているからだ。現在の実行ポリシーは`Get-ExecutionPolicy -List`で得ることができる。

```sh
$ Get-ExecutionPolicy -List

        Scope ExecutionPolicy
        ----- ---------------
MachinePolicy       Undefined
   UserPolicy       Undefined
      Process       Undefined
  CurrentUser       Undefined
 LocalMachine       Undefined
```

過去に何も設定していなければ`Undefined`になっているはず。そして`Undefined`の場合はデフォルトで`Restricted`が適用され、スクリプトの実行ができない。

セキュリティポリシーにはいくつか種類があるが、例えば`RemoteSigned`にすると、リモートのスクリプトは署名付きのみ、ローカルはそのまま実行できるようになる。

```sh
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

これで先ほどのスクリプトはそのまま実行できるようになる。

後はこれをWSLのUbuntu側でPowerShellに食わせて実行すればよいのだが、セキュリティポリシー`RemoteSigned`では実行できない。

以下をUbuntu側で実行してみる。

```sh
$ echo "echo Hello" > test.ps1
$ powershell.exe ./test.ps1
./test.ps1 : ファイル \\wsl.localhost\Ubuntu\home\username\test.ps1 を読み込めません。ファイル \\wsl.localhost\Ubuntu\home\username\test.ps1 はデ
ジタル署名されていません。このスクリプトは現在のシステムでは実行できません。スクリプトの実行および実行ポリシーの設定の詳細については、「about_Exe
cution_Policies」(https://go.microsoft.com/fwlink/?LinkID=135170) を参照してください。
発生場所 行:1 文字:1
+ ./test.ps1
+ ~~~~~~~~~~
    + CategoryInfo          : セキュリティ エラー: (: ) []、PSSecurityException
    + FullyQualifiedErrorId : UnauthorizedAccess
```

これはWSLがリモート扱いだからだ。セキュリティポリシーを`Bypass`にすると、全てのスクリプトを確認なしで実行できるようにする。

以下をPowerShell側で実行する。

```sh
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope CurrentUser
```

すると、WSL側でPowerShellスクリプトを実行できるようになる。

```sh
$ powershell.exe ./test.ps1
Hello
```

セキュリティポリシー`Unrestricted`にすると、毎回確認が入る。

```sh
$ powershell.exe ./test.ps1

セキュリティ警告
信頼するスクリプトのみを実行してください。インターネットから入手したスクリプトは便利ですが、コンピューターに危害を及ぼす可能性があります。このス
クリプトを信頼する場合は、この警告メッセージが表示されないように、Unblock-File
コマンドレットを使用して、スクリプトの実行を許可してください。\\wsl.localhost\Ubuntu\home\watanabe\test.ps1 を実行しますか?
[D] 実行しない(D)  [R] 一度だけ実行する(R)  [S] 中断(S)  [?] ヘルプ (既定値は "D"): r
Hello
```

こっちの方が安全。

## ファイル名の処理

WSL側からPowerShellスクリプトが実行できるようになれば、あとはショートカットを作りたいファイルをPowerShellスクリプトに渡すだけだ。

使い方としては

```sh
wln filename
```

としよう。この`filename`はWSL側のパスになっているので`wslpath -w`でWindows側のパスに修正して渡してやればよい。ショートカットファイル作成スクリプトを`makelnk.ps1`とすると、`wln`は内部で

```sh
powershell.exe makelnk.ps1 $(wslpath -w $1)
```

としてPowerShellを呼び出せば良い。

PowerShell側で引数の受け取り方はいくつかあるが、`Param`で受け取るのが良いと思う。

```sh
Param($targetfile)
```

ショートカットファイル名を作るために、まずはフルパスからファイル名を分離する。

```sh
$filename = [System.IO.Path]::GetFileName($targetfile)
```

デスクトップにファイルを作りたいので、`$HOME\Desktop\`を追加。さらに、拡張子は`.lnk`でなくてはならないので、それも追加する。

```sh
$shortcutfile = "$Home\Desktop\" + $filename + ".lnk"
```

あとは先ほどの例と同様にショートカットオブジェクトを作って保存すればよい。以上から、引数を受け取ってデスクトップにショートカットファイルを作成するPowerShellスクリプト`makelnk.ps1`はこうなる。

```sh
Param($targetfile)
$filename = [System.IO.Path]::GetFileName($targetfile)
$WshShell = New-Object -comObject WScript.Shell
$shortcutfile = "$Home\Desktop\" + $filename + ".lnk"
$Shortcut = $WshShell.CreateShortcut($shortcutfile)
$Shortcut.TargetPath = $targetfile
$Shortcut.Save()
```

この`makelnk.ps1`をどこかパスが通った場所においても良いのだが、対して大きくないので毎回テンポラリファイルとして作ってしまおう。`mktemp`でファイル名を作成し、拡張子`.ps1`をつけて保存する。

```sh
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
```

テンポラリファイル名はWSL側のパスなので、Windows側のパスに直して食わせる必要がある。ターゲットファイルも同様なので、

```sh
targetfile=$(wslpath -w $1)
ps1file=$(wslpath -w $temp_ps1)
powershell.exe $ps1file $targetfile
rm -f $temp_ps1
```

以上をまとめると冒頭のスクリプトになる。

## まとめ

WSL側からPowerShellスクリプトを介してWindowsのデスクトップショートカットファイルを作る方法を紹介した。デフォルトではPowerShellスクリプトがそのまま実行できないので、セキュリティポリシーを変更する必要がある。他にもWindows側にRubyなりなんなりを入れて、そちらからCOMを叩くというのも考えたが、やりたいことのわりに面倒な気がする。

PowerShellスクリプトを使うなら、本当はちゃんと署名して、`Allsigned`もしくは`RemoteSigned`ポリシーで実行できるようにしたほうが良いのだが、署名しようとしてなかなかうまくいかなかった(今後の課題)。`wln`を実行するたびにスクリプトの許可の実行を求められるが、あまり利用頻度は高くないし、とりあえず`Unrestricted`ポリシーで運用しようと思う。