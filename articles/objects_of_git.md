---
title: "Gitのオブジェクトの中身"
emoji: "🤖"
type: "tech" # tech: 技術記事 / idea: アイデア
topics: ["Git"]
published: true
---

## はじめに

[Gitのインデックスの中身](https://zenn.dev/kaityo256/articles/inside_the_index)、[Gitのブランチの実装](https://zenn.dev/kaityo256/articles/inside_the_branch)に続く、Gitの中身を見てみようシリーズです。Gitが管理するオブジェクトの種類や中身について見てみます。基本的にはPro Gitの[10. Gitの内側](https://git-scm.com/book/ja/v2/Git%E3%81%AE%E5%86%85%E5%81%B4-%E9%85%8D%E7%AE%A1%EF%BC%88Plumbing%EF%BC%89%E3%81%A8%E7%A3%81%E5%99%A8%EF%BC%88Porcelain%EF%BC%89)をまとめなおしたものです。

## オブジェクトの種類

![objects](https://github.com/kaityo256/zenn-content/raw/main/articles/objects_of_git/objects.png)

Gitは、内部でファイルやコミットを「オブジェクト」として`.git/objects`以下に保存しています。オブジェクトには以下の4種類があります。

* blobオブジェクト： ファイルを圧縮したもの。ファイルシステムの「ファイル」に対応
* treeオブジェクト： Blobオブジェクトや別のTreeオブジェクトを管理する。ファイルシステムの「ディレクトリ」に対応
* コミットオブジェクト： Treeオブジェクトを包んだもの。コミットのスナップショットに対応するTreeオブジェクトに、親コミット、コミットメッセージなどを付加する
* タグオブジェクト： 他のGitオブジェクトを包んだもの。ほとんどの場合はコミットオブジェクトを包むが、TagのメッセージやTagをつけた人の情報などを付加する

## blobオブジェクト

![blob](https://github.com/kaityo256/zenn-content/raw/main/articles/objects_of_git/blob.png)

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

## コミットオブジェクト

コミットオブジェクトは、コミット、すなわちスナップショットを保存するためのものです。スナップショットは、次の説明するtreeオブジェクトが保存しています。また、親コミットの情報も持っています。以上をまとめると、コミットオブジェクトは

* スナップショットを保存するtreeオブジェクト
* 親コミットのコミットハッシュ
  * root-commitなら親コミット情報なし
  * merge commitなら親コミット情報二つ
* コミットの作成者情報
* コミットメッセージ

をまとめたものです。さっき作ったコミットオブジェクト`ca70291`を見てみましょう。

```sh
$ git cat-file -p ca70291
tree dd1d7ee1e23a241a3597a0d0be5139a997fc29c8
author Robota <kaityo256@example.com> 1630735083 +0900
committer Robota <kaityo256@example.com> 1630735083 +0900

initial commit
```

treeコミット、作成者、コミットメッセージを含んでいることがわかります。なお、これはroot commitなので、親コミットの情報は持っていません。適当に修正してコミットしてみましょう。

```sh
$ echo "Hello commit object" >> test.txt
$ git commit -am "update"
[master 1f620eb] update
 1 file changed, 1 insertion(+), 1 deletion(-)
```

![commit.png](https://github.com/kaityo256/zenn-content/raw/main/articles/objects_of_git/commit.png)

新しく`1f620eb`というコミットができました。中身を見てみましょう。

```sh
$ git cat-file -p 1f620eb
tree 55e11d02569af14b5d29fe56fd44c1cc32c55e72
parent ca70291031230dde40264d62b6e8d2424e2c9366
author Robota <kaityo256@example.com> 1630738892 +0900
committer Robota <kaityo256@example.com> 1630738892 +0900

update
```

スナップショットを表すtreeオブジェクトが`dd1d7ee`から`55e11d0`に更新され、新たに親コミットとして、先ほどの`ca70291`が保存されています。

マージにより作られたマージコミットの場合は、二つの親コミットの情報を含んでいます。いま、こんな歴史を持つリポジトリを考えましょう。

```sh
$ git log --graph --pretty=oneline
*   f4baa057ce89467a2faced36229da02799c9e394 (HEAD -> master) Merge branch 'branch'
|\
| * 6aecd68aa423651edda9d22e20925314ff3e8386 (branch) update
* | 953cb6056e5f0437f0d4e102f232d8eb705f6428 adds test2.txt
|/
* 6db4350c6ebd75338ac4bc2eb2a2924895a0c73b initial commit
```

root commitである`6db4350`から`6aecd68`と`953cb60`が分岐し、マージされて`f4baa05`になっています。

![merge](https://github.com/kaityo256/zenn-content/raw/main/articles/objects_of_git/merge.png)

この最後のマージコミット`f4baa05`の中身を見てみましょう。

```sh
$ git cat-file -p f4baa05
tree 706a1741c1d94977ba496449d80ab848ca945e14
parent 953cb6056e5f0437f0d4e102f232d8eb705f6428
parent 6aecd68aa423651edda9d22e20925314ff3e8386
author Robota <kaityo256@example.com> 1630743012 +0900
committer Robota <kaityo256@example.com> 1630743012 +0900

Merge branch 'branch'
```

スナップショットを保存するtreeオブジェクト`706a174`の他に、二つの親コミット`953cb60`と`6aecd68`が保存されていることがわかります。

## treeオブジェクト

treeオブジェクトは、ディレクトリに対応するオブジェクトです。先ほどのblobオブジェクトの作り方を見てわかるように、blobオブジェクトはファイル名を保存していません。blobオブジェクトとファイル名を対応させるのもtreeオブジェクトの役目です。また、コミットオブジェクトが格納するのは、スナップショット全体を表現するtreeオブジェクトです。

treeオブジェクトがディレクトリに対応することを見るため、適当にディレクトリを含むリポジトリを作ってみましょう。

```sh
mkdir tree
cd tree
git init
mkdir dir1 dir2
echo "file1" > dir1/file1.txt
echo "file2" > dir2/file2.txt
echo "README" > README.md
git add README.md dir1 dir2
```

コミットしてみます。

```sh
$ git commit -m "initial commit"
[master (root-commit) 662458a] initial commit
 3 files changed, 3 insertions(+)
 create mode 100644 README.md
 create mode 100644 dir1/file1.txt
 create mode 100644 dir2/file2.txt
```

これで、コミットオブジェクト(662458a)が作られました。中身を見てみましょう。

```sh
$ git cat-file -p 662458a
tree 193fea0500b331a7ccb536aa691d8eb7df8afd13
author Robota <kaityo256@example.com> 1630737694 +0900
committer Robota <kaityo256@example.com> 1630737694 +0900

initial commit
```

treeオブジェクトとコミットメッセージ等の情報を含んでいます。root commitなので、親コミットの情報はありません。同じ手順を踏めば、コミットハッシュは異なっても、同じtreeオブジェクトができているはずです。treeオブジェクト`193fea0`は、このコミットのスナップショットを保存しています。見てみましょう。

```sh
$ git cat-file -p 193fea0
100644 blob e845566c06f9bf557d35e8292c37cf05d97a9769    README.md
040000 tree 0b9f291245f6c596fd30bee925fe94fe0cbadd60    dir1
040000 tree 345699cffb47ac20257e0ce4cebcbfc4b2a7f9e3    dir2
```

ファイル`README.md`に対応する`blob`オブジェクトと、ディレクトリ`dir1`、`dir2`に対応するtreeオブジェクトが含まれています。二つのtreeオブジェクトも見てみましょう。

```sh
$ git cat-file -p 0b9f291
100644 blob e2129701f1a4d54dc44f03c93bca0a2aec7c5449    file1.txt
$ git cat-file -p 345699c
100644 blob 6c493ff740f9380390d5c9ddef4af18697ac9375    file2.txt
```

ファイル構造とオブジェクトの構造を図示するとこんな感じです。

![tree.png](https://github.com/kaityo256/zenn-content/raw/main/articles/objects_of_git/tree.png)

さて、blobオブジェクトやtreeオブジェクトにはファイル名、ディレクトリ名は含まれておらず、treeオブジェクトは、自分が管理するオブジェクトと名前の対応を管理しています[^ext4]。

[^ext4]: ファイルシステム(例えばext4)のinodeと同じノリです。

また、blobオブジェクトのハッシュは、ファイルサイズと中身だけで決まり、ファイル名は関係ありません。したがって、Gitは「同じ中身だけど、異なるファイル名」を、同じblobオブジェクトで管理します。見てみましょう。

```s
mkdir synonym
cd synonym
git init
echo "Hello" > file1.txt
cp file1.txt file2.txt
git add file1.txt file2.txt
```

これで、中身が同じファイル`file1.txt`、`file2.txt`がステージングされました。コミットしてみましょう。

```sh
$ git commit -m "initial commit"
[master (root-commit) 75470e6] initial commit
 2 files changed, 2 insertions(+)
 create mode 100644 file1.txt
 create mode 100644 file2.txt
```

コミットオブジェクト`75470e6`ができたので、中身を見てみます。

```sh
$ git cat-file -p 75470e6
tree e79a5d99a8e5cd5da0260866b85df60052fd045e
author Robota <kaityo256@example.com> 1630745015 +0900
committer Robota <kaityo256@example.com> 1630745015 +0900

initial commit
```

treeオブジェクト`e79a5d9`ができました。中身を見てみましょう。

```sh
$ git cat-file -p e79a5d9
100644 blob e965047ad7c57865823c7d992b1d046ea66edf78    file1.txt
100644 blob e965047ad7c57865823c7d992b1d046ea66edf78    file2.txt
```

全く同じblobオブジェクトに別名を与えていることがわかります。

## タグオブジェクト

タグオブジェクトは、注釈付きタグをつける時に作成されるオブジェクトで、タグではありません。タグはあくまでブランチと同様に、主にコミットオブジェクトを指すリファレンスです。

タグには軽量タグ(lightweight tag)と、注釈付きタグ(annotated tag)がありますが、いずれもタグの実体は`.git/refs/tags`の中に、タグと同名のファイルとして保存されています。

適当なリポジトリを作り、root commitを作りましょう。

```sh
$ mkdir tag
$ cd tag
$ git init
$ echo "Hello Tag" > test.txt
$ git add test.txt
$ git commit -m "initial commit"
[master (root-commit) ca686d2] initial commit
 1 file changed, 1 insertion(+)
 create mode 100644 test.txt
```

これでroot commitとしてコミットオブジェクト`ca686d2`ができました。これに軽量タグと注釈付きタグを付けてみましょう。`git tag`で、タグ名だけを指定すると軽量タグになります。

```sh
git tag lightweight_tag
```

こうして出来たタグは、直接コミットオブジェクトを指しています。タグの実体は`.git/refs/tags`にあります。見てみましょう。

```sh
$ cat .git/refs/tags/lightweight_tag
ca686d23b06faada3e1955ad022bfa11be5cc2a2
```

先ほど作られたコミットオブジェクトを指しています。つまり、軽量タグはブランチと全く同じ実装になっています。

タグを作る際に`-m`などでメッセージを付けると、注釈付きタグが作られます。

```sh
git tag annotated_tag -m "tag with annotation"
```

注釈付きタグも、オブジェクトを指すのは同じですが、指しているのはコミットオブジェクトではありません。

```sh
$ cat .git/refs/tags/annotated_tag
a6e23bf19c7c64775942f9971aed984c8af4e304
```

新たにタグオブジェクト`a6e23bf`が作られ、そこを指していました。中身を見てみましょう。

```sh
$ git cat-file -p a6e23bf
object ca686d23b06faada3e1955ad022bfa11be5cc2a2
type commit
tag annotated_tag
tagger Robota <kaityo256@example.com> 1630745563 +0900

tag wit annotation
```

コミットオブジェクト`ca686d2`を指しており、そこにタグを付けた人の情報やタグをつけた時のメッセージが含まれていることがわかります。

![tag.png](https://github.com/kaityo256/zenn-content/raw/main/articles/objects_of_git/tag.png)

つまり、タグとしては`lightweight_tag`も`annotated_tag`も同じコミットを指していますが、軽量タグ`lightweight_tag`が直接コミットオブジェクトを指しているのに対して、注釈付きタグ`annotated_tag`は、コミットオブジェクトを「包んだ」タグオブジェクトを指しています。これにより、コミットメッセージとは別に、タグをつけた時にメッセージを保存できるようになっています。

なお、タグオブジェクトはコミットオブジェクトだけでなく、どんなオブジェクトに対しても作ることができます。

```sh
$ git cat-file -p ca686d2
tree 65e9e7f6be25f8882af44cdf8485dc36556bfd8c
author Robota <kaityo256@example.com> 1630745294 +0900
committer Robota <kaityo256@example.com> 1630745294 +0900

initial commit
```

スナップショットを保存しているtreeオブジェクト`65e9e7f`にタグをつけてみましょう。

```sh
git tag tag_on_tree_light 65e9e7f
```

treeオブジェクトを指す軽量タグが作成されました。中身はtreeオブジェクトのハッシュを指しています。

```sh
$ cat .git/refs/tags/tag_on_tree_light
65e9e7f6be25f8882af44cdf8485dc36556bfd8c
```

タグオブジェクトを作ることもできます。

```sh
$ git tag tag_on_tree_annotated 65e9e7f -m "tag on tree"
$ cat .git/refs/tags/tag_on_tree_annotated
1806f1c1a58944fcc9fff52da4201ac9410b5923
$ git cat-file -p 1806f1c
object 65e9e7f6be25f8882af44cdf8485dc36556bfd8c
type tree
tag tag_on_tree_annotated
tagger Robota <kaityo256@example.com> 1630746476 +0900

tag on tree
```

「treeオブジェクトについたタグだよ(`type tree`)」という情報とともに、treeオブジェクトを包んだタグオブジェクトができました。

コミットオブジェクトを指しているタグならば、そこからブランチを作ることができます。

```sh
$ git switch -c branch_from_tag annotated_tag
Switched to a new branch 'branch_from_tag'
```

しかし、コミットオブジェクト以外を指しているタグからブランチを作ることはできません。

```sh
$ git switch -c branch_from_tree tag_on_tree_annotated
fatal: Cannot switch branch to a non-commit 'tag_on_tree_annotated'
```

## まとめ

Gitのオブジェクトについてまとめてました。blobオブジェクトがヘッダをつけてzlibで圧縮しているだけであったり、treeオブジェクトがディレクトリと対応していたりと、非常に素直な実装になっていることがわかります。また、Gitが管理するのはあくまでもblobオブジェクトであるため、空ディレクトリは管理対象外になる理由もわかります。タグとタグオブジェクトは違うもので、タグが指しているのはあくまでもオブジェクトであり、それが直接コミットを指すか(軽量タグ)、タグオブジェクトを指すか(注釈付きタグ)の違いがあります。

これくらいわかると、`.git`の中身がほぼ理解できると思います。中身が理解できたからといって特にGitの利用に役に立つわけではありませんが、「なるほどなぁ」と思っていただければ幸いです。

## 参考文献

* [Gitのインデックスの中身](https://zenn.dev/kaityo256/articles/inside_the_index)
* [Gitのブランチの実装](https://zenn.dev/kaityo256/articles/inside_the_branch)
* [Pro Git - 10. Gitの内側](https://git-scm.com/book/ja/v2/Git%E3%81%AE%E5%86%85%E5%81%B4-%E9%85%8D%E7%AE%A1%EF%BC%88Plumbing%EF%BC%89%E3%81%A8%E7%A3%81%E5%99%A8%EF%BC%88Porcelain%EF%BC%89)
