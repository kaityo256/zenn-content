---
title: "unicode-mathとlulalatexとboldsymbolの組み合わせの話"
emoji: "🤖"
type: "idea" # tech: 技術記事 / idea: アイデア
topics: ["数学","三角関数"]
published: false
---

## TL;DR

* `unicode-math`と`lualatex`と`boldsymbol`を組み合わせると、PDFで太字にならない
* Pandocから`lualatex`を使ってPDFを生成する時に`boldsymbol`が効かないのはこれが原因
* `lualatex`と`boldsymbol`の組み合わせなら大丈夫
* 簡単な対応策は、太字だが斜体にならない`\mathbf`を使うこと
* どうしても太字かつ斜体にしたければ、プリアンブルに以下を追加。

```tex
\setmainfont{XITS}
\setmathfont{XITS Math}
\setmathfont[version=bold,FakeBold=3.5]{XITS Math}
```

## 現象

### Markdown+Pandoc+LuaLatex

僕はMarkdownでノートを書き、PandocでPDF化しているのだが、数式を含むため、PDF化に`lualatex`を使っている。この時、`boldsymbol`が太字にならないことに困っていた。

例えば、

```md
# test

$$
\boldsymbol{r}=r
$$
```

みたいなMarkdownを書いて、

```sh
pandoc test.md -o test.pdf --pdf-engine=lualatex -V documentclass=ltjarticle
```

で変換すると、

![ng1](/images/unicode_math_lualatex/ng1.png)

のように、太字にならない。

特にエラーも警告も出ず、ただ出力されるPDFで`boldsymbol`が無視されるらしい。地道な二分探索の結果、以下のようなことがわかった。

## LuaLaTeX+boldsymbol

まず、LuaLaTeX+boldsymbolの組み合わせは問題ない。こんなTeXファイルを書いて

```tex
\documentclass{ltjarticle}
\usepackage{amsmath}
\begin{document}
$$
  \boldsymbol{r} = r
$$
\end{document}
```

```sh
lualatex test
```

としてPDFを作ると、ちゃんと太字になる。

![ok1](/images/unicode_math_lualatex/ok1.png)

## LuaLaTeX+unicode-math+boldsymbol

しかし、`unicode-math`パッケージを使うと、太字にならない。