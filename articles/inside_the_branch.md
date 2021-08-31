---
title: "Gitのブランチの実装"
emoji: "🤖"
type: "tech" # tech: 技術記事 / idea: アイデア
topics: ["git"]
published: false
---

## はじめに

Gitのブランチがどう実装されているか見てみましょう、という記事です。実装は今後変更される可能性があります。とりあえずWSL2の

## ブランチの実体

通常、GitではHEADがブランチを、ブランチがコミットを指しています。例えばカレントブランチが`master`である場合を考えましょう。`HEAD`の実体は`.git/HEAD`というファイルで、`master`の実体は`.git/refs/heads/master`になっています。それを見ていきましょう。

### `git init`直後

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

`HEAD -> master`と、`HEAD`が`master`を指しているｋとおが明示されています。

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

先ほどと異なり、`HEAD`と`master`の間の矢印が消えました。