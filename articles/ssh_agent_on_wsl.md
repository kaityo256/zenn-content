---
title: "WSL2のUbuntuでkeychain経由でssh-agentを使う"
emoji: "🤖"
type: "tech" # tech: 技術記事 / idea: アイデア
topics: ["WSL","WSL2","Ubuntu","SSH","keychain"]
published: true
---

## TL;DR

WSL2のUbuntuで`ssh-agent`を使うには、`keychain`を使って、`.zshrc`に

```sh
/usr/bin/keychain -q --nogui $HOME/.ssh/id_rsa
source $HOME/.keychain/$HOST-sh
```

と書けば良い。cshやfishは、`$HOST-sh`の`-sh`を`-csh`や`-fish`にする。

## はじめに

WSL2のUbuntuで`ssh-agent`を使うために`eval`してる人、いると思います。

```sh
eval `ssh-agent`
```

このあと`ssh-add`するとパスフレーズが記憶されます。しかし、一度ターミナルを抜けてもう一度開くと、`ssh-agent`プロセスは生きているのに、`ssh-add`ができません。

```sh
$ pidof ssh-agent
95
$ ssh-add
Could not open a connection to your authentication agent.
```

だもんで面倒だから`.zshrc`に

```sh
eval `ssh-agent`
```

って書いてて、毎回`ssh-agent`を起動してたんだけど、そうすると

* 毎回`ssh-agent`が起動する
* ターミナルを開くたびに`ssh-add`する必要がある

という問題が生じます。とりあえず、手元のターミナルではこんなことになりました。

```sh
$ pidof ssh-agent                                                                                                   
32173 31548 31344 31137 29020 28832 27947 27740 27248 27156 22731 22181 21753 21580 20882 19950 19721 18981 18612 18466 17212 16870 16678 16613 16482 15297 14260 13290 12988 12923 12591 12089 12084 11110 10915 10581 10386 10155 10036 9839 9505 9131 8890 7440 6796 6345 5675 5404 5147 4812 4709 3981 3679 3416 3378 3200 2907 2455 2065 1870 1433 952 279 95
```

これはさすがにひどいのでなんとかしましょう、という話です。

## keychainの導入

上記は、`keychain`を導入することで解決できます。まずは不要なプロセスを全部殺しておきます。PowerShellから以下を実行すると楽です。

```sh
wsl --shutdown
```

次にWSL2のUbuntuで、`keychain`を入れます。

```sh
sudo apt-get install keychain
```

`keychain`を起動します。

```sh
/usr/bin/keychain -q --nogui $HOME/.ssh/id_rsa
```

初回起動時はパスフレーズを聞かれるので入力します。すると、`$HOME/.keychain`にいくつかシェルスクリプトが出来るので、それを実行します。

```sh
source $HOME/.keychain/$HOST-sh
```

これにより、`keychain`が`ssh-agent`を探し、もし無ければ起動してくれ、既存の`ssh-agent`プロセスがあれば接続してくれるようになります。一度パスフレーズを入力したら、WSLをシャットダウンしない限りパスフレーズを覚えておいてくれます。これでパスフレーズを何度も入力したり、`ssh-agent`が複数起動することもなくなりました。めでたしめでたし。

## 参考文献

以下の記事を参考にしました

* [Using SSH-Agent the right way in Windows 10 WSL2](https://esc.sh/blog/ssh-agent-windows10-wsl2/)