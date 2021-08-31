---
title: "Gitのブランチの実装"
emoji: "🤖"
type: "tech" # tech: 技術記事 / idea: アイデア
topics: ["git"]
published: false
---

## はじめに

Gitのブランチがどう実装されているか見てみましょう、という記事です。実装は今後変更される可能性があります。とりあえずWSL2の

## HEADとブランチの実体

通常、GitではHEADがブランチを、ブランチがコミットを指しています。例えばカレントブランチが`master`である場合を考えましょう。`HEAD`の実体は`.git/HEAD`というファイルで、`master`の実体は`.git/refs/heads/master`になっています。それを見ていきましょう。

適当なディレクトリ`test`を作って、その中で`git init`しましょう。

```sh
mkdir test
cd test
git init
```

この時点で`.git`が作られ、その中に`HEAD`が作られます。見てみましょう。

```sh
$ cat .git/HEAD
ref: refs/heads/master
```

`HEAD`は`refs/heads/master`を指しているよ、とあります。しかし、`git init`直後はまだこのファイルはありません。

```sh
$ cat .git/refs/heads/master
cat: .git/refs/heads/master: そのようなファイルやディレクトリはありません
```

この状態で`git log`しても「歴史が無いよ」と言われます。

```sh
$ git log
fatal: your current branch 'master' does not have any commits yet
```

さて、適当なファイルを作って、`git add`、`git commit`しましょう。

```sh
$ echo "Hello" > hello.txt
$ git add hello.txt
$ git commit -m "initial commit"
[master (root-commit) c950332] initial commit
 1 file changed, 1 insertion(+)
 create mode 100644 hello.txt
```

初めて`git commit`した時点で、`master`ブランチの実体が作られます。

```sh
$ cat .git/refs/heads/master
c9503326279796b24be86bdf9beb01c1af2d2b95
```

先ほど作られたコミットオブジェクト`c950332`を指していますね。このように、通常は`HEAD`はブランチのファイルの場所を指し、ブランチのファイルはコミットオブジェクトのハッシュを保存しています。`git log`で見てみましょう。

```sh
$ git log --oneline
c950332 (HEAD -> master) initial commit
```

`HEAD -> master`と、`HEAD`が`master`を指していることが明示されています。

## Detached HEAD状態

さて、直接コミットハッシュを指定して`git checkout`してみましょう。

```sh
$ git checkout c950332
Note: switching to 'c950332'.

You are in 'detached HEAD' state. You can look around, make experimental
changes and commit them, and you can discard any commits you make in this
state without impacting any branches by switching back to a branch.

If you want to create a new branch to retain commits you create, you may
do so (now or later) by using -c with the switch command. Example:

  git switch -c <new-branch-name>

Or undo this operation with:

  git switch -

Turn off this advice by setting config variable advice.detachedHead to false

HEAD is now at c950332 initial commit
```

これで、`HEAD`がブランチを介してではなく、直接コミットを指している状態、いわゆる「detached HEAD」になりました。この状態で`git log`を見てみます。

```sh
$ git log --oneline
c950332 (HEAD, master) initial commit
```

先ほどと異なり、`HEAD`と`master`の間の矢印が消えました。`HEAD`の中身を見てみましょう。

```sh
$ cat .git/HEAD
c9503326279796b24be86bdf9beb01c1af2d2b95
```

`HEAD`が直接コミットを指していることがわかります。`master`に戻りましょう。

```sh
$ git switch master
$ cat .git/HEAD
ref: refs/heads/master
```

`.git/HEAD`の中身がブランチへの参照に戻ります。

## ブランチの作成と削除

`master`ブランチから、もう一つブランチを生やして見ましょう。

```sh
git switch -c branch
```

これで、`branch`ブランチが作られ、`master`の指すコミットと同じコミットを指しているはずです。まずは`git log`で見てみましょう。

```sh
$ git log --oneline
c950332 (HEAD -> branch, master) initial commit
```

`HEAD`は`branch`を指し、`branch`も`master`も`c950332`を指している状態です。ファイルの中身も確認しましょう。

```sh
$ cat .git/HEAD
ref: refs/heads/branch

$ cat .git/refs/heads/master
c9503326279796b24be86bdf9beb01c1af2d2b95

$ cat .git/refs/heads/branch
c9503326279796b24be86bdf9beb01c1af2d2b95
```

`.git/refs/heads/master`と同じ内容の`.git/refs/heads/branch`が作成されています。

では、人為的に`.git/refs/heads/`にもう一つファイルを作ったらどうなるでしょうか？

```sh
$ cp .git/refs/heads/master .git/refs/heads/branch2
$ ls .git/refs/heads
branch  branch2  master
```

`.git/refs/heads`内に、`branch2`というファイルが作成されました。`git log`を見てみましょう。

```sh
$ git log --oneline
c950332 (HEAD -> branch, master, branch2) initial commit
```

`branch2`が増え、`master`や`branch`と同じコミットを指していることが表示されました。すなわち、`git`は`git log`が叩かれた時、全てのブランチがどのコミットを指しているか調べています。また、ブランチの作成が、単にファイルのコピーで実装されていることがわかります。

作った`branch2`をgitを使って消しましょう。

```sh
$ git branch -d branch2
Deleted branch branch2 (was c950332).

$ ls .git/refs/heads
branch  master
```

問題なく消せます。`.git/refs/heads`にあったブランチの実体も消えました。つまり、ブランチの削除は単にファイルの削除です。


