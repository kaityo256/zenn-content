---
title: "Postscript言語を触ってみる"
emoji: "🤖"
type: "tech" # tech: 技術記事 / idea: アイデア
topics: ["PostScript", "Ghostscript","Python"]
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

この`GS>`がPostScriptのREPLになっており、ここにいろいろ入力できます。やはり最初は「Hello World!」からいきましょうか。PostScript言語では`(Hello World\n) print`と入力すると、画面に「Hello World!」と出力できます。

```sh
GS>(Hello World\n) print
Hello World
GS>
```

さて、PostScript言語はページ記述言語であり、図形を描画できるのが強みです。しかし、画面が大きいとやりづらいので、一度`quit`と入力して終了しましょう。

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

### スタックの表示と計算

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

スタックをクリアするには`clear`を使います。

```sh
GS<1>clear
GS>
```

また、データや命令は空白で区切っていくつも並べることができます。従って、以下のように「`2`と`3`を積んで、`2+3`を実行して、スタックの中身を表示してスタックを全てクリアする」という命令列を一度に指定することができます。

```sh
GS>2 3 add stack clear
5
GS>
```

せっかくなので逆ポーランド記法でいくつか計算してみましょう。例えば「`1 + 2 * 3`」は、逆ポーランド記法では「`1 2 3 * +`」です。PostScriptでは`1 2 3 mul add`と書きます。

```sh
GS>1 2 3 mul add stack clear
7
GS>
```

`(1+2)*(3+4)`は、逆ポーランド記法では`1 2 + 3 4 + *`なので、PostScriptでは`1 2 add 3 4 add mul`となります。

```sh
GS>1 2 add 3 4 add mul stack clear
21
GS>
```

コンピュータサイエンスの講義でスタックマシンについて教わり、その例として逆ポーランド記法が出てきて「は？」と思ったかもしれませんが、こうやって実際に現役(?)で使える処理系で遊んでみると、スタックマシンや逆ポーランド記法を少し身近に感じるかもしれません。

### スタック操作

PostScriptはスタックマシンなので、スタック操作系の命令が多数あります。その一部を紹介しておきましょう。

#### `pop`

スタックの一番上のデータを取り除きます。以下は`1 2 3`をスタックに積んだあと、最後に積んだ`3`を`pop`で取り除いた例です。

```sh
GS>1 2 3
GS<3>stack
3
2
1
GS<3>pop
GS<2>stack
2
1
GS<2>
```

#### `==`

スタックの一番上のデータを表示してから取り除きます。主に、後に述べるマクロの表示に使います。

```sh
GS>1 2 3
GS<3>==
3
GS<2>==
2
GS<1>==
1
GS>
```

#### `clear`

スタックの中身を全て消去します。

```sh
GS>1 2 3 stack
3
2
1
GS<3>clear stack
GS>
```

以下の例では、適宜最後に`clear`をつけて、スタックにゴミが残らないようにしています。

#### `exch`

スタックの一番上と、二番目のデータを入れ替えます(exchange)。`1 2 3 4`と積んでから`exch`を実行すると`1 2 4 3`となります。

```sh
GS>1 2 3 4 exch stack clear
3
4
2
1
GS>
```

#### `dup`

スタックの一番上のデータを複製します(duplicate)。スタックに`1 2`を積んでから`dup`を実行すると、`1 2 2`になります。

```sh
GS>1 2 dup stack clear
2
2
1
GS>
```

#### `index`

`n index`の形で使い、スタックの上から`n`個目を複製してスタックに積みます。ただし、一番上を0番目と数えます。`1 2 3 4`と積んである状態で`1 index`を実行すると、上から2番目のデータである`3`が複製され、一番上に積まれます。

```sh
GS>1 2 3 4 stack
4
3
2
1
GS<4>1 index stack clear
3
4
3
2
1
GS>
```

#### `copy`

`n copy`の形で使い、スタックの上から`n`個を複製します。例えば`1 2 3 4`が積まれた状態で`2 copy`を実行すると、`1 2 3 4 3 4`になります。

```sh
GS>1 2 3 4 stack
4
3
2
1
GS<4>2 copy stack
4
3
4
3
2
1
GS<6>clear
GS>
```

#### `roll`

`n d roll`の形で使います。スタックの上から`n`個を`d`だけ回します。例えばスタックに`1 2 3`が積まれている時、`3 1 roll`を実行すると`2 1 3`になります。

```sh
GS>1 2 3 stack
3
2
1
GS<3>3 1 roll stack clear
2
1
3
GS>
```

`d`には負の値も指定できます。すると逆方向に回すことができます。例えばスタックに`1 2 3`が積まれている時、`3 -1 roll`を実行すると`1 3 2`になります。

```sh
GS>1 2 3 stack
3
2
1
GS<3>3 -1 roll stack clear
1
3
2
GS>
```

### 描画命令

PostScriptには、他の多くの処理系における描画系のコマンドと同様にカレントポイントという概念があり、描画命令はカレントポイントを基準に実行されます。以下、よく使う描画関連の命令をいくつか紹介します。

#### `moveto`

`x y moveto`の形で使い、カレントポイントを(x,y)に移動します。次の直線描画と一緒に使うとわかりやすいと思います。

#### `lineto`

`x y lineto`の形で使い、カレントポイントから(x, y)まで直線のパスを生成します。また、カレントポイントが(x,y)にに移動します。

#### `stroke`

`lineto`はパスを生成するだけで、そのパスに実体を与えるのは`stroke`です。`stroke`により、現在の線、線幅、色でパスを描画します。

以上から、(0, 0)から(100, 100)に直線をひきたければ

```txt
0 0 moveto
100 100 lineto
stroke
```

を実行する必要があります。わかりやすさのために改行していますが、一行で指定してもかまいません。

```sh
GS>0 0 moveto 100 100 lineto stroke
GS>
```

#### `showpage`

現在までに描画されたデータをデバイス(主にプリンタ)に送ります。GhostscriptのREPLを使ってる時には、画面のクリアに使えます。以下、何か描画するたびに`showpage`とすると画面がクリアされます。

#### `arc`

`cx cy r angle1 angle2 arc`の形で使います。中心が(cx, cy)、半径がr、角度がangle1からangle2まで反時計周りに円を描画します。

```sh
GS>100 100 50 0 360 arc stroke
GS>
```

![arc](/images/ghostscript_sample/arc.png)

描画の開始点は「下」なので、0から270度まで描画するとこうなります。

```sh
GS>100 100 50 0 270 arc stroke
GS>
```

![arc_3_4](/images/ghostscript_sample/arc_3_4.png)

描画が真下からスタートして反時計周りに3/4円を描いていることがわかります。

時計回りバージョンの`arcn`というコマンドもあります。

#### `closepath`

いま描画中のパスの始点と終点をつなげます。例えば、(50,50)から(150,50)に直線を引き、(50,150)に直線を引いてから、`closepath`すると直角三角形を描画できます。

```sh
GS>50 50 moveto
GS>150 50 lineto
GS>50 150 lineto
GS>closepath
GS>stroke
GS>
```

![triangle](/images/ghostscript_sample/triangle.png)

このように、直線は連続して描画できます。

#### `fill`

閉じたパスの中身を塗りつぶします。`closepath`の後に使います。

```sh
GS>50 50 moveto
GS>150 50 lineto
GS>50 150 lineto
GS>closepath
GS>fill
GS>
```

![triangle_fill](/images/ghostscript_sample/triangle_fill.png)

円を塗りつぶすこともできます。

```sh
GS>100 100 50 0 360 arc fill
GS>
```

![arc_fill](/images/ghostscript_sample/arc_fill.png)

#### `setlinewidth`

`w setlinewidth`の形で使い、線幅を`w`にします。

```sh
GS>5 setlinewidth
GS>0 0 moveto 100 100 lineto stroke
GS>
```

![line_w](/images/ghostscript_sample/line_w.png)

#### `setrgbcolor`

`r g b setrgbcolor`の形で使い、色を指定します。三原色の輝度を0から1までで指定できます。小数による指定も可能です。

```sh
GS>1 0 0 setrgbcolor
GS>100 100 50 0 360 arc fill
GS>
```

![arc_red](/images/ghostscript_sample/arc_red.png)

```sh
GS>0.8 0.9 1.0 setrgbcolor
GS>100 100 50 0 360 arc fill
GS>
```

![arc_color](/images/ghostscript_sample/arc_color.png)

#### `findfont`,`scalefont`,`setfont`

`fontname findfont fontsize scalefont setfont`の形で使い、カレントフォントを指定します。例えば`/Helvetica findfont 14 scalefont setfont`により、Helveticaの14ポイントのフォントを指定できます。

#### `show`

カレントポイントにスタックの一番上に積まれた文字列を表示します。文字列をスタックに積むには`()`で囲む必要があります。`(string) show`の形で使うことが多いです。

```sh
GS>/Helvetica findfont 14 scalefont setfont
Loading NimbusSans-Regular font from /usr/share/ghostscript/9.50/Resource/Font/NimbusSans-Regular... 4331112 2813464 3833824 2542916 1 done.
GS>50 100 moveto
GS>(Hello World) show
```

![hello world](/images/ghostscript_sample/helloworld.png)

### 画面操作系

#### `translate`

`x y translate`の形で使い、原点を(x,y)方向にずらします。現在の原点をずらすため、二度実行すると二回ずれます。

#### `rotate`

`angle rotate`の形で使います。現在の座標軸を`angle`度だけ回転させます。

#### `scale`

`sx sy scale`の形で使います。現在の座標軸をx方向にsx倍、y方向にsy倍だけ拡大/縮小します。

#### `gsave`,`grestore`

`gsave`で現在の画面の状態を保存し、`grestore`で復帰します。`translate`や`rotate`などの情報を保存、復帰できます。EPSファイルなどで座標をいじっている時、正しく元に戻さないとその後のLaTeXの表示がおかしくなる時があります。ファイルの最初に`gsave`、最後に`grestore`をつけるのが一般的です。

### マクロ定義

PostScriptでは、マクロ定義のようなことができ、変数のように使えます、

マクロの定義の文法は

```txt
/name 定義 def
```

です。例えば

```txt
/R 50 def
```

とすると、以後は`50`の代わりに`R`と書くことができます。マクロを定義する時には`/`が必要ですが、参照する時には`/`を外します。

また、複数の文字列をマクロとして定義したければ中括弧で囲みます。以下は原点に半径50の円を書くマクロです。

```txt
/C {0 0 50 0 360 arc stroke} def
```

この後、

```txt
C
```

と書くと、

```txt
0 0 50 0 360 arc stroke
```

と書いたのと同じことになります。

マクロは「入れ子」にできます。例えば、マクロ定義にマクロを使うことができます。

```txt
/R 50 def
/C {0 0 R 0 360 arc stroke} def
```

また、マクロ定義時に、そのマクロが定義されている必要はありません。

```txt
/C {0 0 R 0 360 arc stroke} def 
/R 50 def
```

マクロは再定義(上書き)できます。なので、こんなことができます。

```sh
GS>/C {0 0 R 0 360 arc stroke} def
GS>/R 50 def C
GS>/R 100 def C
GS>/R 150 def C
GS>
```

![manyarc](/images/ghostscript_sample/manyarc.png)

これは、半径を50,100,150と変えながら表示したものです。

### 繰り返し

PostScriptにもfor文やif文があります。神代のプログラマは、PostScriptに複雑なコードを書いて、例えばマンデルブロ集合だのローレンツアトラクタだのをプリンタに計算させて出力する、みたいなことをして遊んでいたようですが、現在はEPSを別のプログラミング言語から出力することがほとんどであるため、制御構造はホスト側のプログラミング言語に任せ、PostScriptの高度なプログラミングは必要ないと思います。ここでは、for文の例を挙げておくにとどめます。

for文の文法は`start step end {proc} for`です。Cで言うと

```c
for (i = start; i <= end; i+= step){
  proc;
}
```

に対応します。終了条件に等号が含まれていることに注意してください。たとえば0から10までを表示させるには`0 1 10 {==} for`とします。

```sh
GS>0 1 10 {==} for
0
1
2
3
4
5
6
7
8
9
10
GS>
```

処理で何もしなければ、for文のループカウンタがスタックに積まれます。

```sh
GS>0 1 10 {} for stack
10
9
8
7
6
5
4
3
2
1
0
GS<11>
```

PostScriptはスタックマシンなので、ループカウンタがスタックの一番上に積まれることを利用して処理を書きます。

例えばこんなコードを書いてみましょう。

```txt
/M {moveto} def
/L {lineto} def
100 100 translate
0 5 50 {0 0 3 2 roll 0 360 arc stroke} for
50 0 M 0 50 L -50 0 L 0 -50 L closepath stroke
```

for文で、半径を0から50まで5ずつ増やしながら円を描いています。実行結果はこんな感じになります。

![for](/images/ghostscript_sample/for.png)

正方形が歪んで見えるというアレです。

ループカウンタを半径として使うために、座標をプッシュしてから`roll`で回していますが、マクロを使った方がわかりやすいでしょうか。

```txt
/M {moveto} def
/L {lineto} def
100 100 translate
0 5 50 {/R exch def 0 0 R 0 360 arc stroke} for
50 0 M 0 50 L -50 0 L 0 -50 L closepath stroke
```

スタックの一番上に積まれたループカウンタの値を`/R`としてマクロで受け取り、それを円の描画に利用しています。

## EPS

### EPSヘッダ

EPSはEncapsulated PostScriptの略で、もともとプリンタに送られるために作られたデータをうまく切り取って別のファイルに貼り込むために作られました。

例えば、gnuplotが出力するEPSファイルを見てみましょう。以下のような内容の`test.plt`をgnuplotに食わせると、`test.eps`ができます。

```txt
set term postscript eps
set out "test.eps"
p x
```

作成された`test.eps`の冒頭はこうなっています。

```txt
%!PS-Adobe-2.0 EPSF-2.0
%%Title: test.eps
%%Creator: gnuplot 5.2 patchlevel 8
%%CreationDate: Sat Feb 18 19:14:18 2023
%%DocumentFonts: (atend)
%%BoundingBox: 50 50 410 302
%%EndComments
%%BeginProlog
/gnudict 256 dict def
gnudict begin
```

PostScript言語では、`%`から行末まではコメント扱いです。EPSでは、ファイルのヘッダに`%%`を特別なコメントとして、そのコメントに付加情報をつけます。いろいろ書いてありますが、もっとも重要なのは冒頭の``BoundingBox`です。ここで、全体のどこを切り取るかを指定します。

例えば、(100, 100)に半径50の円を描画しましょう。

```txt
100 100 50 0 360 arc fill
```

これをGhostScriptで実行すると円が見えます。

![arc_fill](/images/ghostscript_sample/arc_fill.png)

これを(100,100)から(200,200)を対角線とする長方形で切り取って画像とするEPSファイルを作ってみましょう。

```txt
%!PS-Adobe-2.0 EPSF-2.0
%%BoundingBox: 100 100 200 200
%%DocumentFonts: Helvetica
%%Orientation: Landscape
%%Pages: 1
%%EndComments
/mydict 120 dict def
mydict begin
gsave
100 100 50 0 360 arc fill
end
grestore
showpage
```

これを`test2.eps`という名前で保存し、例えば`evince`などで表示するとこうなります。

![evince](/images/ghostscript_sample/evince.png)

中央から1/4だけ切り取られていることがわかります。なお、OrientationをLandscapeにすると、原点が左上になるために向きが変わります。原点を左下にしたければPortraitを指定します。

先程のEPSファイルには`%%BoundingBox:`の他にもいろいろ書いてありました。基本的には「おまじない」と思えばOKですが、ちょっとだけ説明します。

* `%%DocumentFonts: Helvetica` フォントの指定をしています。
* `/mydict 120 dict def` ユーザー辞書の指定です。マクロ定義はユーザの辞書に格納されますが、これが別の名前空間(たとえばLaTeXが出力するPostScript)とぶつかるとややこしいことになります(例えば次のEPSファイルが表示されなくなる)。そこで、ここで個別の辞書を定義しています。ローカル変数みたいなノリです。
* `gsave`,`grestore` 座標などの情報を最初に保存し、最後に復旧しています。PostScriptでは座標の原点をずらしたり傾けたり拡大縮小したりするため、それが次のPostScript命令に影響を与えるのを避けるためです。

### EPSファイルの出力例

#### スピン系

たとえばモンテカルロシミュレーションをしていて、スピン状態を可視化したくなったとします。イジングスピンを可視化するコードを書いてみましょう。

```py
import random


def save_eps(spins, filename):
    with open(filename, "w") as f:
        f.write("""
%!PS-Adobe-2.0 EPSF-2.0
%%BoundingBox: 0 0 200 200
%%DocumentFonts: Helvetica
%%Orientation: Portrait
%%Pages: 1
%%EndComments
/mydict 120 dict def
mydict begin
gsave
/M {moveto} def /L {lineto} def /S {stroke} def
/R {25 0 translate} def
/U {10 0 M 10 20 L S 5 15 M 10 20 L 15 15 L S R} def
/D {10 0 M 10 20 L S 5 5 M 10 0 L 15 5 L S R} def
/LF {-200 25 translate} def
""")
        for i in range(64):
            if i != 0 and i % 8 == 0:
                f.write("LF\n")
            if spins[i] == 0:
                f.write("U ")
            else:
                f.write("D ")
        f.write("""
end
grestore
showpage
""")


spins = [random.randint(0, 1) for _ in range(64)]
save_eps(spins, "sample1.eps")
```

実行すると`sample1.eps`ができます。こんな感じです。

![spins](/images/ghostscript_sample/spins.png)

#### 粒子系

分子動力学シミュレーションをしていて、粒子の位置と速度ベクトルの向きを描画したい、なんてこともあるでしょう。

```py
import random


class Atom:
    def __init__(self, x, y, theta):
        self.x = x
        self.y = y
        self.theta = theta


def save_eps(atoms, filename):
    with open(filename, "w") as f:
        f.write("""
%!PS-Adobe-2.0 EPSF-2.0
%%BoundingBox: 0 0 200 200
%%DocumentFonts: Helvetica
%%Orientation: Portrait
%%Pages: 1
%%EndComments
/mydict 120 dict def
mydict begin
gsave
/C {0 0 10 0 360 arc stroke} def
/V {rotate 0 0 moveto 0 10 lineto stroke} def
/P {gsave translate C V grestore} def
""")
        for a in atoms:
            f.write(f"{a.theta} {a.x} {a.y} P\n")
        f.write("""
end
grestore
showpage
""")


atoms = []

for _ in range(50):
    x = random.random() * 200
    y = random.random() * 200
    theta = random.random() * 360
    atoms.append(Atom(x, y, theta))
save_eps(atoms, "sample2.eps")
```

実行すると`sample2.eps`ができます。こんな感じです。

![atoms](/images/ghostscript_sample/atoms.png)

ベクタ画像なので、拡大してもきれいです。

![atoms_enlarge](/images/ghostscript_sample/atoms_enlarge.png)

イベントドリブン型のMDを書いていた時、こうして拡大して衝突判定のデバッグをしていました。

## まとめ

PostScript言語を紹介してみました。Ghostscriptを使ってインタラクティブに画像を描画するのは結構楽しいですし、スタックマシンでマクロを駆使しながらプログラミングをするのもパズルっぽくて面白いです。

また、コードからEPSを吐けるとたまに便利だったりしますPostScriptの知識があると、例えばPDFの中身も理解しやすかったりします。慣れれば速度場も三次元プロットも色つけたりも簡単にできます。

この「失われつつある知識」が、誰かの参考になれば幸いです。
