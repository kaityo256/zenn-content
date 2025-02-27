---
title: "コードを書いてから論文が出版されるまで"
emoji: "🤖"
type: "tech" # tech: 技術記事 / idea: アイデア
topics: ["cpp","python","科学"]
published: false
---

## 概要

最近、我々の論文が出版されました。

これはスケールフリーネットワークにおいて、ノードの削除と追加を繰り返した場合、最終的にどのようなネットワーク構造になるかを調べたもので、SNSでユーザの退会と新規追加を模したシミュレーションになっています。

研究には、理論、実験に加え、数値計算と呼ばれる分野があります。数値計算は、研究者がプログラムを実行し、その結果を解析して研究を行うものです。研究に使われるプログラムは、業界でよく使われるもの(第一原理計算ならVASP、古典分子動力学シミュレーションならLAMMPSやGROMACS、NAMDなど)を使ったり、研究室に代々伝わるプログラム(ハウスコードと呼ばれます)を使ったりしますが、一部の分野では研究テーマごとにコードを書くことがあります。統計力学、特にモンテカルロ法では、モデル毎にコードを書き換えるため、論文ごとにコードを開発することが多いです。

今回の我々の論文も、特に業界標準のプログラムもなく、研究室で引き継がれたりしているものもないため、新たにこの研究のために開発しました。そのコードをこちらに公開しています。

[github.com/kaityo256/aging_network_cpp](https://github.com/kaityo256/aging_network_cpp)

もともと学生さんがPythonで開発していたものを、統計精度が必要になったためにC++で書き直して高速化したため、「_cpp」という名前がついています。

さらに、このコードを使って計算した結果のデータファイル、およびそのデータファイルから(必要に応じて解析コードを走らせて)gnuplotで論文用の図のPDFを作るところまでのデータとスクリプトも東京大学付属物性研究所のデータリポジトリで公開しています。

[isspns-gitlab.issp.u-tokyo.ac.jp/kaityo256/aging_network_data](https://isspns-gitlab.issp.u-tokyo.ac.jp/kaityo256/aging_network_data)

何度も使われることが想定されているコミュニティコードなどがOSSとして公開されることは多いですが、このような一度限りのコードが公開されることはあまりないように思います。以下では、テーマに対して一度だけ書かれ、以後は使われることが想定されていないコードがどのような思想で開発されたのかを説明してみようと思います。

## パラメータの与え方

数値計算の研究において、コードを一度実行して終わりということはほとんどなく、一般にはパラメータをいろいろ変えて何度も計算をすることになります。パラメータをコードに直接書くことをハードコーディングと呼びますが、それをやってしまうとバグの元になるだけでなく、後から「このデータを出力した時のパラメータはなんだったっけ？」とか「本当にこのパラメータで計算したんだっけ？」となり、再計算した時に異なるデータが出てきて困ったりします。なので、パラメータはインプットファイルにまとめ、形としては

```sh
./program inputfile
```

みたいにプログラムに渡して実行することになります。問題はインプットファイルをどのようなフォーマットとするかです。

このようなパラメータをまとめるファイルフォーマットとしては、JSONやYAMLなどが思いつきます。また、より簡単なTOMLというフォーマットもあります。どれを使っても良いのですが、以前、C++でこれらを読み書きするライブラリが重かった印象が強かったため、昔自作したインプットファイルライブラリを使うことにしました。

[github.com/kaityo256/param](https://github.com/kaityo256/param)

これは`*.hpp`ファイルが一つだけ、いわゆる「シングルヘッダーライブラリ」と呼ばれる形になっており、インクルードするだけで使えるようになります。

ファイルはこんなフォーマットです。

```txt
# Comment
bool=yes
int=12345
double=12.345
```

要するに、「名前 = 値」がずらずら並んでいるだけです。これを

```cpp
param::parameter param(filename);
```

として受け取ったら、

```cpp
bool b = param.get<bool>("bool");
int  i = param.get<int>("int");
double d = param.get<double>("double");
```

と、名前と型を指定して値を受け取ることになります。このパラメータクラスのインスタンスを受け取ってシミュレーションをすることになります。`argv[1]`でインプットファイル名を受け取るなら、こんな感じのコードになるでしょう。

```cpp
  std::string paramfile = argv[1];
  param::parameter param(paramfile);
```

後はこれをシミュレーションコードに渡してやればOKです。

## main関数の作り方

main関数がやることは、パラメータクラスのファイル名を受け取り、パラメータクラスのインスタンスを作ってシミュレーションコードに渡すだけです。しかし、乱数の扱いだけちょっと特殊です。

モンテカルロ法など、乱数を使うプログラムでは、必ず乱数のシードを指定するようにします。そうしないと実行毎に結果が変わってしまうため、デバッグしづらくなるからです。Pythonなどでは、最初に

```py
random.seed(0)
```

などとすればコード全体で共有されます(ただし、NumPy::randomは別扱いなので、そちらも別途シードを固定する必要があります)。

一方、C++で使われる乱数生成器のインスタンスはグローバル変数ではないため、設定したシードをコード全体で共有するためには、一度作った乱数生成器を使いまわす必要があります。

以上を考慮した`main.cpp`はこんな感じになります。

```cpp
#include "param/param.hpp"
#include "simulation.hpp"
#include <iostream>
#include <random>

int main(int argc, char **argv) {
  if (argc < 2) {
    printf("usage: ./aging_network parameterfile\n");
    return -1;
  }
  std::string paramfile = argv[1];
  param::parameter param(paramfile);
  if (!param) {
    std::cerr << "An error occurred while loading " << paramfile << std::endl;
    return -1;
  }
  int seed = param.get<int>("seed", 0);
  std::mt19937 rng(seed);
  simulate_sample(param, rng);
}
```

最初の引数チェックやエラー処理などの他に、パラメータクラスから乱数のシードを受け取り、乱数生成器(`std::mt19937`)のインスタンスを作り、それをシミュレーションの入口関数に渡しています。シミュレーションの入口関数`simulate_sample(param, rng)`は、パラメータと乱数生成器を受け取って適切にシミュレーションをすることになります。

## 自明並列

パラメータを与えて実行する系の計算では、パラメータの値によって振る舞いの種類が変わる場合があります。例えば古典イジングモデルにおいては、温度を変えると常磁性相から強磁性相に相転移します。複数のパラメータがある場合、どの領域でどんな振る舞いをするかの相図を書きたくなります。例えば二種類のパラメータがあり、それぞれのパラメータについて10種類ずつ計算することにすると、10x10の100本の計算を実行する必要があります。これらの計算は独立に実行できるため、クラスタやスパコンなどで一度に計算する仕組みが欲しくなります。一つのパラメータに対する計算をジョブと呼びますが、このようなパラメータ並列による複数のジョブを並列実行することを自明並列(trivial parallelization)、もしくは「馬鹿パラ」と呼びます(おそらく「馬鹿でもできるパラレルコンピューティング」の略)。

プログラムとしては

```sh
./program input.cfg
```

で実行できる形になっているため、

```sh
./program input00.cfg
./program input01.cfg
./program input02.cfg
./program input03.cfg
./program input04.cfg
...
```

のように複数のインプットファイルを与える計算が一度にまとめて実行できれば良いわけです。そのためにスパコンサイトによってはバルクジョブという仕組みが用意されていたりしますが、プロセス数とジョブ数が一致してないといけなかったり、プロセス数よりも多いジョブを並べることができなかったりと面倒です。そこで、このようなパラメータ並列を簡単に実行できるツール`cps`を作りました。

[github.com/kaityo256/cps](https://github.com/kaityo256/cps)

これは、

```sh:task.sh
./program input00.cfg
./program input01.cfg
./program input02.cfg
./program input03.cfg
./program input04.cfg
```

のように、一行毎に実行すべきコマンドが書いてあるタスクリスト(`task.sh`)を用意して、

```sh
mpirun -np 4 ./cps task.sh
```

のように実行すると、適当に並列実行してくれます。この例では4プロセスを立ち上げていますが、管理に1プロセス使うため、実際には3プロセスで実行されます。管理プロセスは`task.sh`に書かれたタスクを上から順番に空いているプロセスに割り当てていきます。プロセスは自分が実行しているタスクが終わったら、管理プロセスからまた新しいタスクをもらい、全てのタスクが終了したら終わります。

これにより、プロセス以上のタスクを実行することが可能です。例えば1時間かかるタスクが100個ある時に、100並列で実行する程でもないけれど、シングルプロセスで実行するのもしんどいので、たとえば12コアあるマシンで11並列で実行して10時間で終える、というのはちょうどいい感じだったりします。さらに、MPIを使っているのでノードをまたぐことができ、スパコンなどの計算資源さえあれば、1000並列とかも気軽にできます。

さて、今回の研究では、$\alpha$、$\beta$の二つのパラメータについての振る舞いを調べて相図を作るために、それぞれ10点ずつ、合計100点の計算をしました。そのためには100個のインプットファイルを作り、100行のタスクリストを作らなければなりません。当然手でやったらミスるので、スクリプトで生成することになります。そのために作ったのが[makeparam.py](https://github.com/kaityo256/aging_network_cpp/blob/main/makeparam.py)です。

必要なパラメータを受け取ってファイルを生成する関数はこんな感じになるでしょう。

```py
def save_param(N, alpha, beta, n_sample, data_dir, use_BA_model):
    param = f"""
system_size = {N}
alpha = {alpha}
beta = {beta}
n_sample = {n_sample}
data_dir = {data_dir}
percolation_sample = 100
use_BA_model = {use_BA_model}
"""
    ia = int(alpha * 10)
    ib = int(beta * 10)
    filename = f"N{N:05d}_a{ia}_b{ib}.cfg"
    print(filename)
    with open(filename, "w") as f:
        f.write(param)
    return filename
```

`date_dir`は、データ出力用のディレクトリ名です(後述)。

alphaとbetaがそれぞれ10点ずつ、合計100点の計算をするためのインプットファイルを生成する関数はこんな感じにかけます。

```py
def phase(N):
    n_sample = 1
    data_dir = "phase_diagram"
    use_BA_model = False
    params = []
    paramfiles = []
    for a in range(10):
        for b in range(10):
            alpha = -1.5 + a * 0.5
            beta = -1.5 + b * 0.5
            params.append((alpha, beta))
            print(f"{alpha} {beta}")
    for alpha, beta in params:
        filename = save_param(N, alpha, beta, n_sample, data_dir, use_BA_model)
        paramfiles.append(filename)
    with open("task.sh", "w") as f:
        for filename in paramfiles:
            f.write(f"./aging_simulation {filename}\n")
```

100個のインプットファイルと、後でcpsに渡すための自明並列用のタスクリストを作る関数です。この関数の引数にシステムサイズ`N`があるのは、まず小さい系で相図の概形を調べ、どのパラメータ領域を計算するべきかのあたりをつけてから、本命のサイズで計算するためです。

これを、`makeparam.py`の`main`関数から呼び出します。

```py
def main():
    # sampling(1.5, 3.0, 100)
    # finite_size()
    # BA_model()
    phase(10000)
    # distribution("data", False)
    # time_evolutions()

if __name__ == "__main__":
    main()
```

論文の図それぞれに必要な計算を行うためのインプットファイルを作る関数がずらずら並んでいます。そのどれを呼び出すかがハードコーディングされていますが、これくらいはいいかな、と手抜きをしています。必要に応じてコメントを外して呼び出す関数を切り替えるというよりは、自分がどんな関数を呼び出したかの記録を兼ねてコメントとして残している感じです。

## ディレクトリ管理

計算をしていくと、異なる目的のデータのまとまりができます。例えば相図を作るための計算結果、有限サイズ効果を調べるための計算結果などです。それぞれについて、計算結果の出力ディレクトリを分けたくなるでしょう。そこで、インプットファイルに出力ディレクトリを含めることにします。それが`data_dir`です。

これからも使うコードであれば、コードを管理するリポジトリと、データを管理するディレクトリは分けた方がよいと思いますが、このコードはこの論文を書くためだけに使われるものなので、出力結果も同じリポジトリに吐いてしまった方が管理は楽です。

ただし、コードを管理するリポジトリとデータを管理するリポジトリは分けた方が良いので、「コードを管理するリポジトリにデータは吐くけれど、そのデータはリポジトリでは管理せず、データは論文を書くためのリポジトリにコピーして、そこで管理する」という方針を取ります。

というわけで、ソースを管理するディレクトリに`data`とか`phase_diagram`とか`finite_size`とかのディレクトリを作り、それぞれの中に`.gitkeep`を置いて、`.gitignore`に`*.dat`と書くことでリポジトリでは管理せず、できた`*.dat`は論文執筆用リポジトリにコピーしてそちらで`git add;git commit`して管理する、という形にしました。

要するに`*.cpp`を管理するリポジトリに`*.dat`を吐くけれど、それは`*.tex`を管理するリポジトリにコピーし、`*.dat`はそちらで管理する、ということです。

## データから図の生成

数値計算をするのは、最終的には論文の図を作るためです。数値計算で`*.dat`を作りましたが、それらを最終的に`*.pdf`にしなければなりません。作図ソフトはPythonでもRubyなんでも良いのですが、僕はgnuplotを使うことが多いです。

作図において大事なのは「全く同じデータから全く同じ図が生成されること」です。エクセルなどを使って図を作ると、マウスでの作業が入るために、同じデータを使っても微妙に異なる図ができたりします。それではいろいろ困りますし、数日もすればどんな作業で図を作ったか忘れるため、そもそも同じ図を再現できない、ということが起きたりします。

そこで、データから図を作る作業はなるべく自動化します。理想的にはトップディレクトリで`make`と入力したら、データファイルから必要な解析を経由して図のPDFが生成され、さらにそれを取り込んでLaTeXが走って論文PDFが生成されるようにしたいところです。

実際に、以下のデータリポジトリにて、生データから論文に使う図のPDFがそのまま生成される仕組みを公開しています。

[isspns-gitlab.issp.u-tokyo.ac.jp/kaityo256/aging_network_data](https://isspns-gitlab.issp.u-tokyo.ac.jp/kaityo256/aging_network_data)

このリポジトリの`data`ディレクトリが、ほぼそのまま論文リポジトリの`fig`ディレクトリに対応しています。リポジトリのトップレベルには`Makefile`があり、`make`とすると論文に使われた図が生成されます。こんな感じです。

```sh
$ make
python3 data/ccdf.py data/alpha_dep/degree_distribution_N10000_a-10_b20.dat
data/alpha_dep/degree_distribution_N10000_a-10_b20.dat -> data/alpha_dep/degree_distribution_N10000_a-10_b20.ccdf
python3 data/ccdf.py data/alpha_dep/degree_distribution_N10000_a20_b20.dat
data/alpha_dep/degree_distribution_N10000_a20_b20.dat -> data/alpha_dep/degree_distribution_N10000_a20_b20.ccdf
python3 data/ccdf.py data/alpha_dep/degree_distribution_N10000_a00_b20.dat
data/alpha_dep/degree_distribution_N10000_a00_b20.dat -> data/alpha_dep/degree_distribution_N10000_a00_b20.ccdf
python3 data/ccdf.py data/alpha_dep/degree_distribution_N10000_a30_b20.dat
data/alpha_dep/degree_distribution_N10000_a30_b20.dat -> data/alpha_dep/degree_distribution_N10000_a30_b20.ccdf
python3 data/ccdf.py data/alpha_dep/degree_distribution_N10000_a10_b20.dat
data/alpha_dep/degree_distribution_N10000_a10_b20.dat -> data/alpha_dep/degree_distribution_N10000_a10_b20.ccdf
cd data/alpha_dep; gnuplot alpha_dep_loglog.plt
cp data/alpha_dep/alpha_dep_loglog.pdf fig05a.pdf
(snip)
cp data/finite_size/finite_size_a-15_b20.pdf figb1a.pdf
cd data/finite_size; gnuplot finite_size.plt
cp data/finite_size/finite_size_a30_b25.pdf figb1b.pdf
cd data/finite_size; gnuplot finite_size.plt
cp data/finite_size/finite_size_a-15_b-15.pdf figb1c.pdf
cd data/finite_size; gnuplot finite_size.plt
cp data/finite_size/finite_size_a20_b-10.pdf figb1d.pdf
```

最終的に`fig05a.pdf`から`figb1d.pdf`が生成されます。例えば`fig5a.pdf`に関係するところだけ抜き出すとこんな感じです。

```makefile
FIGS = fig05a.pdf fig05b.pdf fig06a.pdf fig06b.pdf fig07a.pdf fig07b.pdf fig08.pdf figa1.pdf figa2a.pdf figa2b.pdf figb1a.pdf figb1b.pdf figb1c.pdf figb1d.pdf

all: $(FIGS)

ALPHA_CCDF=data/alpha_dep/degree_distribution_N10000_a-10_b20.ccdf  data/alpha_dep/degree_distribution_N10000_a20_b20.ccdf data/alpha_dep/degree_distribution_N10000_a00_b20.ccdf data/alpha_dep/degree_distribution_N10000_a30_b20.ccdf data/alpha_dep/degree_distribution_N10000_a10_b20.ccdf

%.ccdf: %.dat
	python3 data/ccdf.py $<

data/alpha_dep/alpha_dep_loglog.pdf: $(ALPHA_CCDF)
	cd data/alpha_dep; gnuplot alpha_dep_loglog.plt

fig05a.pdf: data/alpha_dep/alpha_dep_loglog.pdf
	cp $< $@
```

生データ`*.dat`から、累積分布関数(Complementary Cumulative Distribution Function)データ`*.ccdf`をccdf.pyを使って作り、そのあとgnuplotで`alpha_dep_loglog.plt`を処理して`alpha_dep_loglog.pdf`を作り、それを`fig05a.pdf`としてコピーします。

## 終わりに

昨今、研究のデータを公開する流れになっていますが、Data availabilityのstatementには「Data available on reasonable request」という紋切り型の文章が並ぶことが多いです。また、研究者にとって、再利用しないコードを公開するメリットは基本的にありません。しかし、初めて研究のためにコードを開発し、データを解析し、論文を書く人にとって、「このやり方でいいんだろうか」と迷うことも多いでしょう。そんな中、既に掲載された論文を完全に再現できるコードとデータ、解析スクリプトが公開されていると、「どれくらいのコードを書いて、どのくらい実行すると査読論文として認められるデータや図を作ることができるのか」がわかります。いわゆるハウスコードだけに触れていると、研究室独自のルールややりかたを一般的な方法と思ったまま大学/大学院を卒業してしまうかもしれません。

こういうコードやデータ公開が、これから研究をしようとする学生さんのなんらかの助けになれば幸いです。
