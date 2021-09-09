---
title: "WSL2のUbuntuにpdftkをインストールするためのsnapのためにsystemdを起動する(必要はない)"
emoji: "🤖"
type: "tech" # tech: 技術記事 / idea: アイデア
topics: ["WSL","WSL2","Ubuntu"]
published: true
---

## TL;DR

WSL2のUbuntu (18.10以降)でPDFtkを使うためには、以下のようにすれば良い。

```sh
sudo apt install -y pdftk-java
```

## WSL2のUbuntuでPDFtkを使いたい

PDFを切り出したり、複数のPDFをくっつけたりしたいことが結構あります。そんな用途に便利なツールがPDFtkです。しかし、PDFtkはGCJ (GNU Compile for Java)に依存しており、GCC 7.1からGCJが消えてしまったため、aptで素直に入らなくなりました。

そのworkaroundとして、以下のやり方が有名です。

```sh
sudo apt-get update && sudo apt-get install -yqq daemonize dbus-user-session fontconfig
sudo daemonize /usr/bin/unshare --fork --pid --mount-proc /lib/systemd/systemd --system-unit=basic.target
exec sudo nsenter -t $(pidof systemd) -a su - $LOGNAME
sudo snap install pdftk
```

これは、

1. WSL2のUbuntuではデフォルトで起動していないsystemdをdaemonizeを使って簡易コンテナで起動し、
2. nsenterを使ってそのコンテナにログインすると、
3. snapdに接続できるようになるので
4. snapが使えてpdftkがインストールできる

という仕組みになっています。

Ubuntu 18.04まではPDFtkを使うには上記のようなことをするとかGCJをなんとかするとか面倒なことが必要だったのですが、18.10以降からはpdftk-javaというforkがあるので、それをインストールすれば`pdftk`が問題なく使えます。

で、上記の仕組みを散々調べた後に、Ubuntu 18.10 以降は`pdftk-java`を使えば解決、ということを[自分のツィート](https://twitter.com/kaityo256/status/1361307120981798918)で知ったので膝から崩れ落ちました。悲しいので、調べたことをまとめておきます。

## systemd on WSL2

pdftkを入れる方法として、Snappy経由で入れる、という方法があります。Snappyはパッケージ管理システムの一種で、ディストリビューションに依存せずにソフトウェアを管理、インストールできます。しかし、パッケージマネージャsnapを使うには、snapdというデーモンが動いている必要があります。

snapdはsystemd上で動きますが、WSL2のUbuntuでは、デフォルトでsystemdが動いていません。代わりにプロセスIDの1番として`init`が動いています。

```sh
$ ps -p 1 -o comm=
init
```

そこで、まずはなんとかしてsystemdを起動する必要があります。そのためのコマンドが以下です。

```sh
sudo daemonize /usr/bin/unshare --fork --pid --mount-proc /lib/systemd/systemd --system-unit=basic.target 
```

詳細は[こちらの記事](https://qiita.com/matarillo/items/f036a9561a4839275e5f)を読んでいただくことにして、これによりsystemdを別の名前空間で起動することができました。

```sh
$ pidof systemd
5229
```

systemdがプロセスIDの5229番として起動しています。これにより、snapdも起動します。

```sh
$ pidof snapd
5518

$ systemctl status snapd
● snapd.service - Snap Daemon
     Loaded: loaded (/lib/systemd/system/snapd.service; enabled; vendor preset: enabled)
     Active: active (running) since Thu 2021-09-09 21:17:30 JST; 1min 2s ago
TriggeredBy: ● snapd.socket
   Main PID: 279
      Tasks: 25 (limit: 7529)
     Memory: 90.8M
     CGroup: /system.slice/snapd.service
             └─279 /usr/lib/snapd/snapd
(snip)
```

しかし、systemdが別の名前空間で動いているので、snapdと通信はできません。

```sh
$ snap version
snap    2.49.2+20.04
snapd   unavailable
series  -
```

snapdがunavailableになっていますね。

そのために、nsenterコマンドで、先ほど作ったコンテナの中にログインします。

```sh
exec sudo nsenter --target $(pidof systemd) --all su - $LOGNAME
```

これにより、`systemd`がプロセスIDとして1番を持つ世界に入れます。

```sh
$ pidof systemd
584 1
```

systemdのPIDとして584番と1番が割り当てられています。

これでsnapdとやりとりできるようになりました。

```sh
$ snap version
snap    2.51.4
snapd   2.51.4
series  16
ubuntu  20.04
kernel  4.19.128-microsoft-standard
```

これによりsnap経由でpdftkがインストールできます。

```sh
sudo snap install pdftk
```

```sh
$ pdftk --version

pdftk 2.02 a Handy Tool for Manipulating PDF Documents
Copyright (c) 2003-13 Steward and Lee, LLC - Please Visit: www.pdftk.com
This is free software; see the source code for copying conditions. There is
NO warranty, not even for MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
```

無事に入りました。

## トラブルシューティング

一度WSL2を終了すると簡易コンテナからも抜けているので、snapが使えません。

```sh
$ snap version
snap    2.49.2+20.04
snapd   unavailable
series  -
```

それならまた簡易コンテナに入ろうと

```sh
exec sudo nsenter --target $(pidof systemd) --all su - $LOGNAME
```

を実行しようとするとターミナルが落ちます。その理由は、systemdが二つのPIDを持っているからです。先ほど、systemdのPIDは以下の二つでした。

```sh
$ pidof systemd
584 1
```

この状態でWSL2を閉じて、もう一度開くと、別のPIDになります。

```sh
$ pidof systemd
5991 5229
```

`pidof systemd`が値を二つ持っているので、`$(pidof systemd)`がおかしくなって、`nsenter`が正しく動作しません。

killで殺しても良いですが、なんか気持ち悪いので、PowerShellから

```sh
wsl --shutdown
```

で一度全プロセスをきれいにするのが良いと思います。

## まとめ

WSL2のUbuntuでpdftkを使うためにsnapを使うためにsystemdを起動したりなんだりしましたが、Ubuntu 18.10以降は`pdftk-java`を使えば一発です。Ubuntu 20.04は`sudo apt install pdftk`でも入りますが、多分`pdftk-java`と同じものです。

```sh
$ sudo apt install pdftk
$ pdftk --version
pdftk port to java 3.0.9 a Handy Tool for Manipulating PDF Documents
Copyright (c) 2017-2018 Marc Vinyals - https://gitlab.com/pdftk-java/pdftk
Copyright (c) 2003-2013 Steward and Lee, LLC.
pdftk includes a modified version of the iText library.
Copyright (c) 1999-2009 Bruno Lowagie, Paulo Soares, et al.
This is free software; see the source code for copying conditions. There is
NO warranty, not even for MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
```

もうWSL2のUbuntuでpdftkを使いたい人が面倒な思いをしないように本記事を埋葬しておきます。

## 参考文献

* [WSL2- Ubuntu 20.04 Snap store doesn't work due to systemd dependency](https://github.com/microsoft/WSL/issues/5126#issuecomment-653715201)
* [WSL2でSystemdを使うハック](https://qiita.com/matarillo/items/f036a9561a4839275e5f)