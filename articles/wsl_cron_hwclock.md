---
title: "WSL上のcronで時刻を定期的に修正する"
emoji: "🤖"
type: "tech" # tech: 技術記事 / idea: アイデア
topics: ["WSL","Ubuntu"]
published: true
---

## はじめに

WSLはなぜか時計(システムクロック)がよく狂います。修正するためには、

```sh
sudo hwclock -s
```

を実行する必要があります。`-s`は`--hctosys`の短縮オプションで、システムクロックをハードウェアクロックに合わせるものです。で、これを毎回気が付いた時にやるのは面倒なので、cronで定期実行したいですね。でも、WSLはデフォルトでcronが動いていません。これをなんとかしましょう、という話です。

## `sudo hwclock`をパスワードなしに

まず、`hwclock`によるハードウェアクロックへのアクセスにはroot権限が必要なので、`sudo hwclock`する必要があります。すると、パスワードが要求されてしまいます。これではcronに載せられないので、パスワードなしに実行できるようにしましょう。事前に`hwclock`のパスを調べておきます。

```sh
$ which hwclock
/sbin/hwclock
```

場合によって`/usr/sbin/`だったりするようです(18から20に上げたりすると場所が違う？)。

次に`/etc/sudoers`を編集します。編集に失敗すると`sudo`コマンドが使えなくなって面倒なので、`visudo`を使って修正すると良いでしょう。ファイルフォーマットが不正だと警告してくれるようになります。ただ、Ubuntuのデフォルトエディタはnanoなので、Vimを使いたい人は、あらかじめ`sudo apt purge nano`とかしておくと幸せかもしれません(`crontab -e`なんかも同様)。

```sh
sudo visudo
```

そして、`/etc/sudoers`の最後あたりに以下の行を追加します。

```txt
username ALL=NOPASSWD: /sbin/hwclock
```

`username`は自分のアカウント名を入れてください。

```sh
sudo hwclock
```

を実行し、パスワードを聞かれなければ成功です。

## cronの実行と設定

crondが起動しているか調べます。デフォルトでは動いていないと思います。

```sh
$ service cron status
 * cron is not running
```

cronを起動しましょう。

```sh
$ sudo service cron start
 * Starting periodic command scheduler cron
```

cronが起動したはずです。

```sh
$ service cron status
 * cron is running
```

あとは適当な頻度、例えば10分おきぐらいに`sudo hwclock -s`を実行してやればOKです。`crontab -e`でcronを編集しましょう。

```txt
*/10 * * * * /sbin/hwclock -s
```

## crondの起動

さて、WSLのcronは自動起動してくれないので、Windowsを再起動したらcronはまた止まってしまいます。バッチファイルに起動スクリプトを書いてスタートアップに入れてWindows起動時に自動実行させる方法もありますが、実行にroot権限が必要なものを勝手に起動させるのもちょっと気が引けます。そこで、ターミナル起動時にチェックして、起動してなければ実行する形式にしてみましょう。以下を`.zshrc`に入れておきます。

```sh
if [[ -n `service cron status | grep not` ]];then
    echo "cron is not running. Type password to run it."
    sudo service cron start
fi
```

これで、ターミナルを起動時にcronが起動していなければパスワードが要求され、cronが起動します。

## まとめ

WSLでcronを起動し、`sudo hwclock -s`を定期実行させる環境を作ってみました。やったことは以下の通りです。

* `/etc/sudoers`を編集して、`sudo hwclock`の実行にパスワードを不要にした
* cronにコマンドを登録して`sudo hwclock -s`を定期実行させるようにした
* `.zshrc`でサービスをチェックし、cronが実行していなければ`sudo service cron start`させるようにした

僕はターミナル起動時に一度だけパスワード入力するのは良いかな、と思いましたが、Windows起動時にcronを自動実行したい場合は以下の記事を参考にすると良いでしょう。

* [WSL上cronをwindows起動時に自動実行する](https://qiita.com/yuinyan/items/4e23d9bd90f93988a88c)
* [WSL で cron を利用する方法・Windows 起動時に自動実行する方法](https://loumo.jp/archives/24595)
