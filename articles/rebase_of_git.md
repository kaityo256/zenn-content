---
title: "Gitのリベースの説明"
emoji: "🤖"
type: "tech" # tech: 技術記事 / idea: アイデア
topics: ["git"]
published: false
---

## はじめに

Gitのrebaseは、(特にSubversionから入ってきた人にとって)理解が難しいものです。rebaseの説明はネットに多数落ちており(例えば[Pro Git](https://git-scm.com/book/ja/v2/Git-%E3%81%AE%E3%83%96%E3%83%A9%E3%83%B3%E3%83%81%E6%A9%9F%E8%83%BD-%E3%83%AA%E3%83%99%E3%83%BC%E3%82%B9))、わかってから読み返すと「なるほど」と思うのですが、理解があやふやな時にrebaseでトラブルが起きるとどうして良いかわからなくなりがちです。

優れた解説が多い中、さらなる記事を書くのは屋上屋を架す感がありますが、「僕はこうやって教えてほしかった」的な覚書を残しておきます。

## コミットと差分

![commit.png](https://github.com/kaityo256/zenn-content/raw/main/articles/rebase_of_git/commit.png)

Gitのコミットは親コミットを覚えており、それをたどることで歴史を逆にさかのぼって行くことができます。Gitでは歴史を玉と線で表現することが多いです。玉はコミットを表し、コミットはその時点でのスナップショットを表しています。玉と玉の間の線は差分(パッチ)を表しており、一つ前のコミットにそのパッチを適用することで次のコミットが得られる、と解釈できます。

## マージとリベース

![beforemerge.png](https://github.com/kaityo256/zenn-content/raw/main/articles/rebase_of_git/beforemerge.png)

いま、歴史が分岐しているとしましょう。`master`と`branch`の二つのブランチがあり、共通のコミットからそれぞれ歴史が進んでいます。`branch`で加わった修正を`master`に取り込みたいとき、Gitは`merge`か`rebase`の二つの手段を選ぶことができます。

### マージの場合

マージする場合は両方の修正を一度に取り込んだコミットを作ります。`master`ブランチから`branch`にたいして`git merge`をかけた場合、こんな感じになります。

![aftermerge.png](https://github.com/kaityo256/zenn-content/raw/main/articles/rebase_of_git/aftermerge.png)

この時、二つの歴史が一つになります。したがって、現在`master`が指しているコミットの親は二つになります。親とつながる線は「その親から自分になるための修正パッチ」を意味しているため、それぞれ図示するとこんな感じになります。

![patch.png](https://github.com/kaityo256/zenn-content/raw/main/articles/rebase_of_git/patch.png)

### リベースの場合

`branch`ブランチの修正をマージで`master`に取り込みたいとき、`master`から`branch`に対して`git merge`をかけました。それに対して、リベースで取り込みたいときには、まず`branch`で`master`に対して`git rebase`をします。

するとGitは、`master`と`branch`の共通祖先から、`branch`の現在のコミットまでを切り出し、`master`の先につなげます。これにより`branch`の指すコミットの直接の祖先が`master`になるため、Fast Forwardマージが可能になります。

![rebase.png](https://github.com/kaityo256/zenn-content/raw/main/articles/rebase_of_git/rebase.png)

この図だけ見ると、`branch`にぶら下がっていたコミットを「移動」したように見えますが、実際には`branch`のコミット間から「パッチ」を取り出し、それを順番に適用することで新たにコミットを作っています。先ほどまでの図の例で見てみましょう。

![rebase2.png](https://github.com/kaityo256/zenn-content/raw/main/articles/rebase_of_git/rebase2.png)

この図を見ると、新しくできた`c1'`や`c2'`コミットは、リベース前の対応するコミット`c1`、`c2`とは異なるスナップショットを表していることがわかります。むしろ変わっていないのは、`c1`や`c1'`から親コミットに向かって伸びる線が表すパッチです。つまり、「リベースとは、玉(コミット)ではなく、線(パッチ)を移動する操作である」と理解できます。

## リベースのsquash

リベースが「共通祖先からリベース元にいたるまでのパッチを、リベース先に次々と適用することだ」と理解できると、`rebase -i`で出てくる`squash`の意味もわかります。

先ほどの状態で`branch`から`rebase -i master`を実行すると、どのコミットをどうするかを聞かれます。今回のケースでは二つコミットがあるので、それぞれについて対応を聞かれます。`rebase -i`で選べる対応は`pick`、`reword`、`edit`、`squash`、`fixup`、`x`がありますが、よく使うのは`pick`(コミットを使う)と、`squash`(コミットを使うが一つ前のコミットと融合してしまう)でしょう。

デフォルトは`pick`です。`-i`をつけずに`rebase`した場合は、リベース対象となっている玉の数だけ、リベース先にくっつくことになります。

![squash.png](https://github.com/kaityo256/zenn-content/raw/main/articles/rebase_of_git/squash.png)

`squash`は、コミットをまとめます。図を見ると「玉(コミット)をまとめる」というよりは「線(パッチ)をまとめる」といった方が実態に近い気がします。

## まとめ

Gitのリベースが何をやっているかを説明してみました。「Gitの歴史の表示においてコミットがスナップショット、コミット間の線がパッチを表す」ということ、「リベースは、共通祖先からリベース元へのパッチを、リベース先に次々適用することで一本の歴史を作る作業である」ということを理解するのに時間がかかりました。これがわかってしまうと、例えばマージならコンフリクトが一度しかおきないのに、リベースでは何度もコンフリクトが起きることがある理由がわかったり、[squashにより空のパッチができてしまってリベースに失敗して焦る](https://qiita.com/kaityo256/items/97706ee75e854bb55f73)ようなこともなくなるでしょう。

本稿が「リベースわからん」同志の助けになれば幸いです。

## 参考文献

* [「3.6 Git のブランチ機能 - リベース」 Pro Git](https://git-scm.com/book/ja/v2/Git-%E3%81%AE%E3%83%96%E3%83%A9%E3%83%B3%E3%83%81%E6%A9%9F%E8%83%BD-%E3%83%AA%E3%83%99%E3%83%BC%E3%82%B9)
* [「7. rebaseでマージする」 サル先生のGit入門](https://backlog.com/ja/git-tutorial/stepup/13/)