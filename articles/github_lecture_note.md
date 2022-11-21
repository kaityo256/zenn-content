---
title: "GitHubで講義ノートを書く"
emoji: "🤖"
type: "tech" # tech: 技術記事 / idea: アイデア
topics: [GitHub, Markdown, Pandoc]
published: false
---

## はじめに

大学の講義ノートをGitHubで執筆、公開しています。

@[card](https://github.com/kaityo256/python_zero)

@[card](https://github.com/kaityo256/github)

しばらく続けて見て、いろいろノウハウが溜まったので共有してみようと思います。

## 大学の講義ノートをどうするか問題

昔から大学の講義ノートを公開する人は結構多いです。最初期は、LaTeXで書いてPDFで公開することが多かったように思います。これはこれで良いのですが、基本的にはダウンロードして印刷して読む前提であり、ウェブで気軽に読める形ではありませんでした。その後、LaTeX2HTMLを使って、LaTeXファイルをHTMLに変換して公開するケースが増えました。これによりウェブで講義ノートが気軽に閲覧できるようになったのですが、いかにも「LaTeX2HTMLを使って変換しました」という外観になるのと、(少なくともデフォルトでは)レスポンシブではなく、スマホ非対応になるのが不便な点でした。また、ウェブで公開するならHTMLだけで良いですが、例えば学生に配る課題などはPDFで作りたくなります。HTML用とPDF用でファイルを分けたくありません。講義ノートの公開場所も問題です。大学のサーバにおいてあると、著者が退職したあとに消えてしまうことが多いです。

そこでいろいろ試行錯誤した結果、

* 講義ノートをMarkdown形式でVS Code上で書く
* MarkdownファイルをPandocでHTMLに変換してウェブ閲覧用とする
* MarkdownファイルをPandocでPDFに変換して配布用とする
* 公開先はGitHubとする

という運用に落ち着きました。以下、それぞれの説明です。

### 講義ノートをMarkdownで書く

理工系の講義ノートなので、図や式を含めたくなります。VS CodeはデフォルトでMarkdownのプレビューでKaTeXをサポートしており、そのまま数式がプレビューできます。

![preview](/images/github_lecture_note/katex.png)

図も普通に入れられます。

ただし、LaTeXのように数式に番号をつけて参照したり、図のサイズを指定したりはできません(できなくはありませんが面倒です)。

これについては、

* 図はベタで入れ、後で図1などと参照したりしない。
* 数式も参照は使わない

という割り切りで講義ノートを書くことにしました。そもそも遠くの図や式を参照しながら読むのは大変なので、必要があれば式や図を再度掲載することにして、基本的に直前直後の図や式しか参照しないような文章構成としました。

一種の縛りプレイですが、逆にその方が講義ノートとしては読みやすくなるのかな、とも思います。

### MarkdownファイルをPandocでHTMLに変換してウェブ閲覧用とする

GitHibにMarkdownファイルを公開すると、そのままGitHubでプレビューできます。以前は数式はサポートされていませんでしたが、最近ではデフォルトでKaTeXもサポートされました。しかし、箇条書き内に数式を入れると不具合が生じるなど、少しややこしいことをするとレンダリングに問題が起きます。

そこで、PandocでMarkdownをHTMLに変換し、GitHub Pagesで公開することにしました。

Pandocは`-D`オプションでデフォルトのテンプレートを表示できます。

```sh
pandoc -D 'html' > template.html
```

この`template.html`を自分で好きなように修正します。重要なのは数式対応とレスポンシブにすることです。

レスポンシブにするのは適当なCSSを使えば良く、また数式対応については`--mathjax`指定をすればOKです。

MarkdownからHTMLへの変換は、GNU makeによる手作業で行っています。GitHub Actionsを使って自動化しても良いのですが、とりあえずローカルでHTMLを確認してからpushしたいことが多かったので、HTMLもリポジトリで管理することにしました。

原則として一回の講義が１つのディレクトリにまとめられており、それぞれにREADME.mdファイルが置いてあり、それが講義ノートになっています。

例えば「ゼロから学ぶPython」の最初の三回分のディレクトリ構造は以下のようになっています。

```sh
$ tree -L 1 hello basic scope
hello
├── README.md
├── fig
├── index.html
└── logistic.md
basic
├── README.md
├── fig
└── index.html
scope
├── README.md
├── fig
└── index.html
```

`README.md`が講義ノート、`fig`が画像ファイルや講義スライド、`index.html`が`README.md`から作ったHTMLファイルです。

さて、GitHubでMarkdownを見ている時には、いわゆる「パンくずリスト」に対応するものがあるため、１つ上に戻ったりが簡単ですが、HTMLファイルにする場合はそれがありません。また、HTMLから直接GitHubリポジトリに飛べた方が便利です。

そこで、`README.md`から、まず`index.md`を作ります。その際、sedを使って「１つ上」へのリンクと、GitHubリポジトリへのリンクを貼り付けています。こんな感じです。

```makefile
%/index.md: %/README.md
        sed '2a [[Up]](../index.html)' $< > $@
        sed -i '3a [[Repository]](https://github.com/kaityo256/python_zero)\n' $@
```

こうして、サブディレクトリの`README.md`から`index.md`を作ったら、`index.md`から`index.html`を作ります。これはpandocで変換するだけです。

```makefile
PANDOC_HTMLOPT=--mathjax -t html --template=template
%/index.html: %/index.md
        pandoc -s $< -o $@ $(PANDOC_HTMLOPT) --shift-heading-level-by=-1
```

ここで、`--shift-heading-level-by=-1`を指定しています。これは、変換時に段落レベルを1つ引き上げるオプションです。例えば`H3`が`H2`に、`H2`が`H1`になります。このオプションの良いところは、もともと`H1`で指定されていたものがファイルのタイトルに指定されることです。例えばMarkdownファイルが

```markdown
# 条件分岐と繰り返し処理

## 本講で学ぶこと
```

となっている時、「条件分岐と繰り返し処理」も「本講で学ぶこと」も`H1`になり、かつ「条件分岐と繰り返し処理」がタイトル指定されます。PandocはMarkdownからHTMLに変換する時にタイトルを指定しないと怒ります。`--metadata pagetitle=`で指定する方法もありますが、`--shift-heading-level-by=-1`を使う方が便利だと思います。

変換したHTMLはこんな感じになります。

![html](/images/github_lecture_note/html.png)

Markdownにはなかった`[Up][Repository]`のリンクが貼られ、もともとレベルが違っていた「条件分岐と繰り返し処理」と「本講で学ぶこと」が同じレベルになり、さらに「条件分岐と繰り返し処理」がタイトルになっているのがわかると思います。

また、CSSによりレスポンシブになるようにしています。

![responsive](/images/github_lecture_note/responsive.png)

個人的に、**講義ノートがスマホで閲覧できる** というのはかなり重要だと考えています。 多くの学生がスマホでの情報閲覧に慣れており、スマホで講義ノートが見られると読んでくれるというのもありますし、自分でも時間がある時にスマホで見返すことでタイポを見つけたりもできます。
