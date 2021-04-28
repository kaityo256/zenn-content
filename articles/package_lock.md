---
title: "Zenn-CLIを使っててpackage-lock.jsonがコンフリクトした時の対処"
emoji: "🤖"
type: "tech" # tech: 技術記事 / idea: アイデア
topics: [npm,zenn]
published: true
---

## TL;DR

Zenn-CLIを使って、かつGitHubリポジトリで連携している時、マージしようとして`package-lock.json`がコンフリクトした場合は、

```sh
npm install zenn-cli@latest
git add package-lock.json
git commit -m "updates package-lock.json"
```

とすれば良い。

## はじめに

Zenn-CLIを使い、かつGitHubリポジトリ連携でZennのコンテンツを管理している人は多いと思う。で、ある場所でコンテンツをアップデートしてpushした後、別の場所でfetch;mergeしたら、package-lock.jsonがコンフリクトしたよ、と言われ、npmに詳しくない人(例えば俺)は「え？何それ」と焦ることになる。この記事はそういう人のために、何が起きたか、どうすれば良いかをまとめたもの。

## 何が起きたか

Zenn-CLIはNode Package Manager(npm)のパッケージとして管理されている。npmでプロジェクトを作ると、`package-lock.json`ができる。ここには、現在インストールされているパッケージのバージョンが記録されている。さて、Zenn-CLIは、新しいバージョンがあると更新通知を出すので、そこで以下のコマンドを実行する。

```sh
npm install zenn-cli@latest
```

この時、このコマンドによりZenn-CLIや依存パッケージのバージョンが上がり、それが`package-lock.json`に記録される。`package-lock.json`もGit管理下にあるので、そのままadd, commit, pushにより更新される。この状態で、まだZenn-CLIが古いままの別のマシンでgit fetch;mergeすると、`package-lock.json`がコンフリクトすることになる。

## どうすれば良いか

`package-lock.json`は、現在のプロジェクトのパッケージのバージョンを記載しているだけなので、使っているパッケージを最新版にアップデートすれば良い。今回の場合なら、`zenn-cli`を最新版にすれば良いので、コンフリクトした状態のまま以下のコマンドを実行する。

```sh
npm install zenn-cli@latest
```

すると、(必要があれば)パッケージのバージョンが上がり、かつ`package-lock.json`が作り直されて上書きされるので、あとはaddしてcommitすれば良い。

通常、`package-lock.json`を使うことはないが、リポジトリ間でパッケージのバージョンが違ったりすると地味に嫌なことが置きそうなので、`.gitignore`に入れたりはしないほうが良いと思う。また、`npm ci`を使ったりする場合には必要となる。

## まとめ

* `package-lock.json`は、現在のプロジェクトのパッケージのバージョンを記録している
* `package-lock.json`がコンフリクトしたら、`npm install`で必要なパッケージを更新し、`package-lock.json`を上書きしてadd, commitすれば良い。

## 参考文献

* [package-lock.jsonについて知りたくても聞けなかったこと](https://qiita.com/fj_yohei/items/7ca887a45e0855917279)
* [npm ciを使おう あるいはより速く](https://qiita.com/mstssk/items/8759c71f328cab802670)