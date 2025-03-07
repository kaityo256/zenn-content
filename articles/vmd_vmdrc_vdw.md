---
title: "VMDで描画方法としてVDWをデフォルトにする"
emoji: "🤖"
type: "tech" # tech: 技術記事 / idea: アイデア
topics: ["VMD","Visualization","MD"]
published: true
---

## TL;DR

VMDの可視化方法でVDW(van der Waals)をデフォルトにしたい場合は、ホームディレクトリに以下の内容の`.vmdrc`を作成すれば良い。

```tck
mol default style VDW
menu main on
```

ただし、Windows版などではホームディレクトリが書き込み不可の場所であったりするので、ショートカットを作成し、リンク先を

```txt
"C:\Program Files (x86)\VMD\vmd.exe" -e "C:\Users\username\.vmdrc"
```

などとしてやる必要がある。

なお、粒子の大きさも同時に指定したい場合は、

```tck
mol default style "VDW 0.8"
menu main on
```

などと、`style`の後をダブルクオーテーションマークで囲む必要がある。

## VMDの可視化方法

VMD (Visual molecular dynamics)は、イリノイ大学及びベックマン研究所のグループにより開発されている、分子シミュレーションの可視化ソフトである。様々なアプリケーションに対応しているが、例えばLAMMPS (LAMMPS Molecular Dynamics Simulator)が吐くような軌跡ファイル(LAMMPS trajectory)を可視化するのに便利だ。

しかし、様々な可視化手法に対応しているからか、LAMMPS TrajectoryでMoleculesを読み込んだ時、デフォルトで原子の可視化タイプが「Lines」になっている。

![lines](/images/vmd_vmdrc_vdw/lines.png)

メニューのGraphics→Representationsで設定画面を開き、Drawing MethodをLinesからVDWにすると、つぶつぶとして可視化できる。

![lines](/images/vmd_vmdrc_vdw/menu.png)

![vdw](/images/vmd_vmdrc_vdw/vdw.png)

多くのLAMMPSユーザにとって、これが所望の表示方法であろう。なのに毎回ファイルを読み込んではメニューから可視化手法を変更するのは面倒だ。そこで、最初から可視化手法(Drawing Method)をLinesではなくVDWにしたくなる。

そのためには、`.vmdrc`に記述すればよいのだが、ここでVMD scriptの知識が必要になる。

## VMD Scriptと.vmdrc

VMDを起動すると、同時にVMDのコマンドラインインタフェースが表示される。

![vdw](/images/vmd_vmdrc_vdw/vmd_cmdline.png)

このコマンドラインで`vmd >`となっているプロンプトにコマンドを入力することで、ほぼすべてのVMDの制御が可能だ。

例えば定番の`Hello World`もできる。

```txt
vmd > puts "Hello VMD World!"
Hello VMD World!
```

ここで重要なのが、VMDのホームディレクトリだ。VMDが起動時にどこをカレントディレクトリにしているかは、起動直後に`pwd`コマンドで調べることができる。

```txt
vmd > pwd
/Users/watanabe
```


上記は、LinuxやMacならホームディレクトリ`$HOME`になっているだろう。VMDは起動時にホームディレクトリにある`.vmdrc`を読み込んで実行してくれるため、デフォルトで設定したい動作をVMDコマンドラインで動作確認した後で、`~/.vmdrc`に記述すれば良い。

例えば、分子の可視化方法のデフォルトを確認するには`mol default style`と入力する。

```txt
vmd > mol default style
Lines
```

現在は`Lines`になっている。これをVDWに変更しよう。

```txt
vmd > mol default style VDW
vmd > mol default style 
VDW
```

正しく変更された。この後でLAMMPSのTrajectoryファイルを読み込んでみて、つぶつぶで表示されれば成功だ。ただ、注意点として`.vmdrc`になにかコマンドを書くと、デフォルトでメインメニューが非表示になってしまうようだ。そこで`.vmdrc`には、

```txt
mol default style VDW
menu main on
```

と書けば、初期設定でDrawing MethodがVDWになった上に、メインメニュー(VMD Main)も表示される。

## Windowsの場合

Windowsの場合はちょっと面倒だ。デフォルトでVMDのホームディレクトリが`C:/Program Files (x86)/VMD`などになっており、そこには一般ユーザ権限でファイルを置けないし、そもそも個人設定をシステムディレクトリに置きたくない。

```txt
vmd > pwd
C:/Program Files (x86)/VMD
```

そこで、VMDに起動時スクリプトを指定することで対応する。VMDは`-e`オプションにより、起動時スクリプトを指定できる。

まずエクスプローラで`C:/Program Files (x86)/VMD`を表示し`vmd.exe`のショートカットを作成する。右クリックメニューで表示されない場合は「その他のオプションを確認」を選ぶと「ショートカットの作成(S)」が出てくるのでそれを選ぶ。

![vdw](/images/vmd_vmdrc_vdw/vmd_win.png)

すると、「ここにショートカットを作成することはできません。デスクトップ上に作成しますか？」と聞かれるので「はい」を選ぶ。

デスクトップ上に作成された「vmd.exe - ショートカット」を右クリックし、「プロパティ」から「ショートカット」メニューの「リンク先」を編集する。

![vdw](/images/vmd_vmdrc_vdw/vmd_shortcut.png)

最初は

```txt
"C:\Program Files (x86)\VMD\vmd.exe"
```

となっているため、

```txt
"C:\Program Files (x86)\VMD\vmd.exe" -e "C:\Users\username\.vmdrc"
```

などとすればよい(usernameは適宜修正すること)。

これによりWindowsでもデフォルト設定を指定できる。

## まとめ

VMDの初期設定を指定する方法をまとめた。最初にWindowsで作業したため、`.vmdrc`ファイルが読み込まれていなかったことに気づかなかった。また、`.vmdrc`を修正してはVMDを再起動とかすると非効率なので、まずはVMDコマンドラインで作業し、うまくいくことを確認してからファイルに書き込むと良い。

この覚書が他の誰かの助けとなることを祈っている。
