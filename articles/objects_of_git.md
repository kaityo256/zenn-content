---
title: "Gitのオブジェクトの中身"
emoji: "🤖"
type: "tech" # tech: 技術記事 / idea: アイデア
topics: ["Git"]
published: false
---

## はじめに

[Gitのインデックスの中身](https://zenn.dev/kaityo256/articles/inside_the_index)、[Gitのブランチの実装](https://zenn.dev/kaityo256/articles/inside_the_branch)に続く、Gitの中身を見てみようシリーズです。Gitが管理するオブジェクトの種類や中身について見てみます。基本的にはPro Gitの[10. Gitの内側](https://git-scm.com/book/ja/v2/Git%E3%81%AE%E5%86%85%E5%81%B4-%E9%85%8D%E7%AE%A1%EF%BC%88Plumbing%EF%BC%89%E3%81%A8%E7%A3%81%E5%99%A8%EF%BC%88Porcelain%EF%BC%89)をまとめなおしたものです。

## オブジェクトの種類

![objects](objects_of_git/objects.png)

Gitは、内部でファイルやコミットを「オブジェクト」として`.git/objects`以下に保存しています。オブジェクトには以下の4種類があります。

* blobオブジェクト： ファイルを圧縮したもの。ファイルシステムの「ファイル」に対応
* treeオブジェクト： Blobオブジェクトや別のTreeオブジェクトを管理する。ファイルシステムの「ディレクトリ」に対応
* コミットオブジェクト： Treeオブジェクトを包んだもの。コミットのスナップショットに対応するTreeオブジェクトに、親コミット、コミットメッセージなどを付加する
* タグオブジェクト： 他のGitオブジェクトを包んだもの。ほとんどの場合はコミットオブジェクトを包むが、TagのメッセージやTagをつけた人の情報などを付加する

## blobオブジェクト

blob[^blob]オブジェクトは、ファイルを保存するためのオブジェクトです。その実体は、ファイルに`blob ファイルサイズ`というヘッダ情報を付加し、zlibで圧縮したものです。

[^blob]: [Binary Large OBjectsの略](https://docs.github.com/en/rest/reference/git#blobs)らしい。

blobオブジェクトを作ってみましょう。適当なディレクトリで`git init`してから、適当なファイルを作ります。

```sh
mkdir blob
cd blob
git init
echo -n "Hello Git" > test.txt
```

改行が含まれないように、`echo`に`-n`オプションをつけています。これを`git add`すると対応するblobオブジェクトが作られます。

```sh
git add test.txt
```

blobオブジェクトのファイル名は、対象となるファイルの頭に`blob ファイルサイズ\0`をつけたもののSHA-1ハッシュ値です。

```sh
$ {echo -en 'blob 9\0';cat test.txt} | shasum
e51ca0d0b8c5b6e02473228bbf876ba000932e96  -
```

つまり、`e51ca0d...`というblobオブジェクトができているはずです。見てみましょう。

```sh
$ git cat-file -t e51ca0d0b8c5b6e02473228bbf876ba000932e96
blob

$ git cat-file -p e51ca0d0b8c5b6e02473228bbf876ba000932e96
Hello Git
```

`git cat-file`はGitのオブジェクトを調べるのに使います。`-t`でタイプを、`-p`で中身をいい感じに表示してくれます。

さて、`e51ca0d...`というオブジェクトができていることがわかりました。その実体は`.git/objects`以下に格納されています。見てみましょう。

```sh
$ ls -1 .git/objects/*/*
.git/objects/e5/1ca0d0b8c5b6e02473228bbf876ba000932e96
```

Gitはオブジェクトのファイル名の頭二文字をディレクトリにして、残りをその下のファイルとして保存します。なので、`e51ca0d...`というオブジェクトは、`.git/objects`以下の`e5`以下に、`1ca0d...`というファイル名で保存されます。

いまは、`git init`直後で、`git add`しただけなので、Gitが管理するオブジェクトはこのblobオブジェクト一つだけです。ここで、コミットをすると、treeオブジェクトやコミットオブジェクトが作られます。

```sh
$ git commit -m "initial commit"
[master (root-commit) ca70291] initial commit
 1 file changed, 1 insertion(+)
 create mode 100644 test.txt
```

コミットオブジェクト`ca70291...`が作られました。オブジェクトを見てみましょう。

```sh
$ ls -1 .git/objects/*/*
.git/objects/ca/70291031230dde40264d62b6e8d2424e2c9366
.git/objects/dd/1d7ee1e23a241a3597a0d0be5139a997fc29c8
.git/objects/e5/1ca0d0b8c5b6e02473228bbf876ba000932e96
```

blobオブジェクト`e51ca0d...`、`ca70291...`の他に、もう一つ、`dd1d7e...`ができています。これはコミットのスナップショットを表すtreeオブジェクトです。blobオブジェクトとtreeオブジェクトは、同じ操作をすれば同じファイル名になるはずです。一方、コミットオブジェクトのハッシュはぶつかっては困るので、毎回異なるものになります。

blobオブジェクトの中身を見てみましょう。これは、対象となるファイルに`blob ファイルサイズ\0`というヘッダを付与したものを`zlib`で圧縮したものです。Pro GitではRubyで再現していましたが、Pythonを使ってみましょうか。

```py
import zlib
content = "Hello Git" # ファイルの中身

# ヘッダ付与
store = f"blob {len(content)}\0{content}".encode("utf-8")

data = zlib.compress(store) # 圧縮
print(bytes.hex(data))      # 中身の表示
```

`Hello Git`というファイルに、`blob 9\0`というヘッダを付与して、`zlib.compress`で圧縮したバイト列を表示するスクリプトです。実行してみましょう。

```sh
$ python3 test.py
789c4bcac94f52b064f048cdc9c95770cf2c01002b750531
```

これがblobオブジェクトの中身のバイト列に一致しているはずです。見てみましょう。

```sh
$ od -tx1 .git/objects/e5/1ca0d0b8c5b6e02473228bbf876ba000932e96
0000000 78 01 4b ca c9 4f 52 b0 64 f0 48 cd c9 c9 57 70
0000020 cf 2c 01 00 2b 75 05 31
0000030
```

完全に一致していますね。

## タグオブジェクト

タグオブジェクトは、タグを付ける時にメッセージを含めた時に作成されるオブジェクトで、タグではありません。タグはあくまでブランチと同様に、主にコミットオブジェクトを指すリファレンスです。

タグには軽量タグ(lightweight tag)と、注釈付きタグ(annotated tag)がありますが、いずれもタグの実体は`.`git/refs/tags`の中に、タグと同名のファイルとして保存されています。

