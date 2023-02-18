---
title: "Postscript言語を触ってみる"
emoji: "🤖"
type: "tech" # tech: 技術記事 / idea: アイデア
topics: []
published: false
---

## はじめに

EPSというファイルを見かけたことがあるかもしれません。一昔前のLaTeXなどではEPSが標準のグラフィックファイルでした。なので、EPSを画像フォーマットだと思っている人がいるかもしれませんが、EPSはEncapsulated PostScriptと呼ばれるPostScript言語に付加情報をつけたもので、PostScriptとは、Adobeが開発しているプログラミング言語です。プログラミング言語なので、テキストファイルで編集したり、何か計算したりできます。

昔話になりますが、今ほどデータの可視化手法が充実していなかったため、一部の数値計算屋は自作のコードからPostScriptファイルを出力することでデータの可視化をしていました。EPSを出力すればLaTeXに直接貼り込めるし、ファイルサイズは小さいし、ベクタなので拡大してもきれいと、わりと優れた可視化手法でした。僕が大学で所属していた研究室でも、それまでCUIをほとんど触ったことがなかったいたいけな学生が、配属されてしばらくしたらVimでEPSファイルを直接いじりだす、心温まる光景が見られたものです。

PostScript言語はページ記述言語と呼ばれる、描画命令に特化した言語です。そういう意味で、Processingの遠い祖先といえなくもありません。また、PDFはPostScriptの直系の子孫であり、PostScriptの知識があると、わりとPDFフォーマットが理解できたりします。

現在では論文に図を貼り込むのはPDFが標準となり、PSやEPSファイルを直接見たり編集したりする機会はほとんどなくなりました。この、失われつつあるPostScriptの知識を後世に残すのも年寄りの役目かな、と思ってこの記事として埋葬しておきます。

## GhostScriptの起動

PostScriptはプログラミング言語ですから、その言語処理系があります。それがGhostScriptです。X Window Systemが使えるLinux環境があるとそのまま使えますが、WindowsやMacの場合は、WindowsならVcXsrv、MacならXQuartzをインストールし、Dockerで適当なLinux環境を作ると良いでしょう。

例えば、以下を実行すればGhostScriptが使えるようになります。

```sh
git clone https://github.com/kaityo256/gs_sample.git
cd gs_sample
cd docker
make
make run
```

なお、Dockerが走っていることと、X Window Systemが適切な許可を持っていることが前提です。

GhostScriptがインストールされている環境が手に入ったら、`gs`を入力しましょう。

```sh
$ gs
gs
GPL Ghostscript 9.50 (2019-10-15)
Copyright (C) 2019 Artifex Software, Inc.  All rights reserved.
This software is supplied under the GNU AGPLv3 and comes with NO WARRANTY:
see the file COPYING for details.
GS>
```

このように`GS>`というプロンプトが出てきて入力待ちになり、かつ以下のようなウィンドウが出てくるはずです。

![gs.png](/images/ghostscript_sample/gs.png)

この`GS>`がPostScriptのREPLになっており、ここにいろいろ入力できるのですが、画面が大きいとやりづらいので、一度`quit`と入力して修了しましょう。

```sh
GS>quit
$
```

そして、今度はウィンドウサイズを指定して起動します。

```sh
gs -dDEVICEWIDTHPOINTS=200 -dDEVICEHEIGHTPOINTS=200
```

こうすると、200ピクセル x 200ピクセルのウィンドウが出てきたはずです。

![gs_200](/images/ghostscript_sample/gs_200.png)

この状態で、プロンプトに`0 0 moveto 100 100 lineto stroke`と入力します。

```sh
GS>0 0 moveto 100 100 lineto stroke
GS>
```

以下のように、直線が描画されたはずです。

![line](/images/ghostscript_sample/line.png)

これは座標(0,0)から(100,100)に直線を引く命令です。原点は左下であり、ウィンドウサイズが(200, 200)なので、左下から中央に向けて線が引かれています。

先程入力した`0 0 moveto 100 100 lineto stroke`という命令は

* `0 0 moveto` カレントポイントを(0,0)に移動し、
* `100 100 lineto` カレントポイントから(100,100)に直線のパスを作成し
* `stroke` これまでのパスを描画せよ

というPostScriptの命令であり、GhostScriptはそれを解釈して線を描画した、という流れになります。

## PostScriptの概要

PostScriptはスタックマシンを採用しています。言語仕様は非常に単純であり、基本は「数字が入力されたらスタックに積む」「文字列が入力されたら命令として実行する」の二種類だけです。それを見てみましょう。

まず、まっさらな状態から始めます。

```sh
GS>
```

ここで、`2`を入力し、エンターを押します。

```sh
GS>2
GS<1>
```

プロンプトが`GS>`から`GS<1>`に変化しました。これはスタックにデータが1つ積まれていることを表しています。さらに3を積んでみましょう。

```sh
GS<1>3
GS<2>
```

スタックにデータが2つ積まれています。この状態で`stack`と入力しましょう。

```sh
GS<2>stack
3
2
GS<2>
```

下から順番に「2」「3」と積まれていることがわかります。これらを足してみましょう。`add`と入力します。

```sh
GS<2>add
GS<1>
```

スタックに積まれたデータが1つに減りました。`stack`で中身を見てみましょう。

```sh
GS<1>stack
5
GS<1>
```

「2」「3」の代わりに、「2+3」の結果である「5」が積まれています。

すなわち、Ghostscriptは、自然に逆ポーランド記法の電卓になっています。

PostScriptには、他の多くの描画系の言語と同様に「カレントポイント」という概念があります。カレントポイントは、今の筆の位置であり、「どこそこに線をひけ」と命令すると、カレントポイントからその場所に線がひかれます。