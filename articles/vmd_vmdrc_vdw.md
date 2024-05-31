---
title: "VMDで描画方法としてVDWをデフォルトにする"
emoji: "🤖"
type: "tech" # tech: 技術記事 / idea: アイデア
topics: ["VMD","Visualization","MD"]
published: false
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

## VMDの可視化方法

VMD (Visual molecular dynamics)は、イリノイ大学及びベックマン研究所のグループにより開発されている、分子シミュレーションの可視化ソフトである。様々なアプリケーションに対応しているが、例えばLAMMPS (LAMMPS Molecular Dynamics Simulator)が吐くような軌跡ファイル(LAMMPS trajectory)を可視化するのに便利だ。

しかし、様々な可視化手法に対応しているからか、LAMMPS TrajectoryでMoleculesを読み込んだ時、デフォルトで原子の可視化タイプが「Lines」になっている。

![lines](/images/vmd_vmdrc_vdw/lines.png)

メニューのGraphics→Representationsで設定画面を開き、Drawing MethodをLinesからVDWにすると、つぶつぶとして可視化できる。

![lines](/images/vmd_vmdrc_vdw/menu.png)

![vdw](/images/vmd_vmdrc_vdw/vdw.png)

多くのLAMMPSユーザにとって、これが所望の表示方法であろう。なのに毎回ファイルを読み込んではメニューから可視化手法を変更するのは面倒だ。そこで、最初から可視化手法(Drawing Method)をLinesではなくVDWにしたくなる。

そのためには、`.vmdrc`に記述すればよいのだが、ここでVMD scriptの知識が必要になる。

## VMD Script

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

