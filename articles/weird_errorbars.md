---
title: "見たら「ん？」となるエラーバーのグラフ"
emoji: "🤖"
type: "tech" # tech: 技術記事 / idea: アイデア
topics: ["python","数値計算"]
published: false
---

## はじめに

実験や数値計算などでエラーバーがついているグラフをよく使いますが、見ていると「ん？」となるグラフをよく見かけます。いくつか例を挙げて見ましょう。

### ケース1

例えばこんなグラフがあったとします。

![weird_errorbars/exp1.png](weird_errorbars/exp1.png)

何かが時間に対して指数関数的に減衰していることを表しているようです。僕は発表でこういうグラフを見かけたら「ん？」と思います。

一方、こちらのグラフはまともです。

![weird_errorbars/exp2.png](weird_errorbars/exp2.png)

少なくともエラーバーの付き方はまともです。

### ケース2

