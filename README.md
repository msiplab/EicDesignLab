# 電子情報通信設計製図

[![Open in MATLAB Online](https://www.mathworks.com/images/responsive/global/open-in-matlab-online.svg)](https://matlab.mathworks.com/open/github/v1?repo=msiplab/EicDesignLab)

「電子情報通信設計製図」（新潟大学工学部工学科電子情報通信プログラム）の講義例題と演習課題例のソースコードを管理しています。
ライントレーサの実機（Raspberry Pi Zero 2 W）で動かす演習のプログラムと，モデルベース開発のためのシミュレータ（Python，ROS 2，Gazebo，MATLAB/Simulink）があります。

上の「Open in MATLAB Online」のボタンを押すと，このリポジトリを MATLAB Online で開けます（`mbd_phs5` のシミュレーションと物理モデルの同定などを，ブラウザで実行できます）。

## ダウンロード

端末で以下のコマンドを実行してください（Raspberry Pi OS や Ubuntu の場合）。ZIP ファイルをダウンロードして展開し，ホームディレクトリの `~/EicDesignLab` に置きます。

    $ cd ~
    $ curl -L -o EicDesignLab.zip https://github.com/msiplab/EicDesignLab/archive/refs/heads/master.zip
    $ unzip EicDesignLab.zip
    $ mv EicDesignLab-master EicDesignLab
    $ rm EicDesignLab.zip

`unzip` がない場合は `sudo apt-get install unzip` で導入してください。
ブラウザで [ZIP ファイル](https://github.com/msiplab/EicDesignLab/archive/refs/heads/master.zip)をダウンロードして展開しても同じです（展開したフォルダ `EicDesignLab-master` を `EicDesignLab` に名前を変えて使います）。

git に慣れている場合は，`git clone` でも取得できます。

    $ cd ~
    $ git clone https://github.com/msiplab/EicDesignLab.git

公開リポジトリなので，どちらの方法でも GitHub のアカウントは不要です（アカウントが必要になるのは，自分の変更を GitHub に push するときだけです）。

## ソースコードの更新

ZIP でダウンロードした場合は，もう一度ダウンロードして展開し，古いフォルダと置き換えてください。自分で編集したファイルは，先に別の場所へコピーしておきます。

    $ cd ~
    $ mv EicDesignLab EicDesignLab_old
    $ curl -L -o EicDesignLab.zip https://github.com/msiplab/EicDesignLab/archive/refs/heads/master.zip
    $ unzip EicDesignLab.zip && mv EicDesignLab-master EicDesignLab && rm EicDesignLab.zip

`git clone` で取得した場合は，以下のコマンドで更新できます。

    $ cd ~/EicDesignLab
    $ git pull

ソースコードを編集していて更新がうまく行かない場合は，以下のコマンドを実行してください（編集内容を一時的に退避します）。

    $ cd ~/EicDesignLab
    $ git stash
    $ git pull

退避した編集内容を元に戻すときは，以下のコマンドを実行してください。

    $ git stash pop

## フォルダの構成

| フォルダ・ファイル | 内容 |
|---|---|
| `eiclab_*.py`, `rotary_encoder*.py` | 演習例題のプログラム（PiZeroW で実行） |
| `tests/` | Mock テストのプログラム（`gpiozero` があれば PC でも実行可） |
| `services/` | プログラムの自動起動に使うサービスファイル |
| `fritzing/` | Fritzing のパーツデータ（フォトリフレクタ LBR-127HLD） |
| `images/` | 各年度のコースの画像，シミュレータの画面 |
| `mbd_phs1/` | 簡易シミュレータ（簡略パラメータモデル，pygame，[README](mbd_phs1/README.md)） |
| `mbd_phs2/` | 簡易シミュレータ（詳細パラメータモデル，ロータリーエンコーダの模擬と走行データの CSV 保存，[README](mbd_phs2/README.md)） |
| `mbd_phs3/` | ROS 2 版シミュレータ（WSL2 + ROS 2 Jazzy，[README](mbd_phs3/README.md)） |
| `mbd_phs4/` | Gazebo 版シミュレータ（WSL2 + ROS 2 Jazzy + Gazebo Harmonic，[README](mbd_phs4/README.md)） |
| `mbd_phs5/` | MATLAB/Simulink 版シミュレータ（物理モデルの同定，ROS 2 との接続，Raspberry Pi へのコード生成，[README](mbd_phs5/README.md)） |
| `matlab/` | グループ分けの抽選（MATLAB Live Script） |

本書（テキスト）の配線の約束：モータドライバの A 側（BCM6, 5）が左のモータ，B 側（BCM26, 27）が右のモータ，
フォトリフレクタは進行方向に向かって左から順に BCM10, 9, 11, 8（A/D コンバーターを使う場合はチャネル 0〜3）です。

## シミュレータの実行

`mbd_phs1`・`mbd_phs2` は，PC や Raspberry Pi 4/5 で以下のように実行します（Raspberry Pi OS や Ubuntu の場合）。

    $ sudo apt-get install python3-pygame python3-transitions python3-numpy python3-scipy
    $ cd ~/EicDesignLab/mbd_phs1
    $ python3 main_mils_line_follower.py

Windows で python.org の Python を使う場合は `py -m pip install pygame transitions numpy scipy` でモジュールを導入し，`py main_mils_line_follower.py` で実行します。
操作の方法や変更してよい場所など，各シミュレータの使い方はそれぞれの README を参照してください。

## Fritzing

製図アプリ Fritzing を WSL2 上の Ubuntu や Raspberry Pi OS にインストールする場合は，以下のコマンドを実行してください。

    $ sudo apt-get update
    $ sudo apt-get upgrade -y
    $ sudo apt-get install fritzing fritzing-data fritzing-parts

## Wiki

過去の版のマニュアルの訂正や補足事項（Fritzing による製図の方法，よくある質問など）を，以下の Wiki サイトにまとめています。最新の内容はテキストを参照してください。

- https://github.com/msiplab/EicDesignLab/wiki

## Python モジュール

Python の便利なモジュールとその Raspberry Pi OS 上でのインストール方法をまとめます。

- 準備：パッケージの更新方法は以下の通りです。時間がかかるので，余裕をもって実施してください。

      $ sudo apt-get update
      $ sudo apt-get upgrade -y
      $ sudo apt-get dist-upgrade
      $ sudo apt-get install python3-dev python3-setuptools python3-pip

- NumPy：多次元のデータ配列を効率的に格納し処理する ndarray オブジェクトを提供。

      $ sudo apt-get install python3-numpy

- SciPy：統計，最適化，線形代数，信号・画像処理，常微分方程式ソルバなどの機能を提供。

      $ sudo apt-get install python3-scipy

- Pygame：主にゲームを対象とした GUI アプリの制作に役立つモジュールを提供。

      $ sudo apt-get install python3-pygame

- pytransitions：軽量な有限状態機械オブジェクトを提供。

      $ sudo apt-get install python3-transitions

モデルベースシミュレーション（`mbd_phs1`，`mbd_phs2`）に必要なものはここまでです。

- Pandas：ラベル付けされた列指向のデータを効率的に格納し処理する DataFrame オブジェクトを提供。走行データの CSV ファイルの分析に便利です。

      $ sudo apt-get install python3-pandas

- matplotlib（+ seaborn）：Python の柔軟なデータ可視化機能を提供。

      $ sudo apt-get install python3-matplotlib python3-seaborn

- scikit-learn：機械学習アルゴリズムの効率的な Python 実装。

      $ sudo apt-get install python3-sklearn

- python-control：フィードバック制御システムの分析と設計のための基本的な操作を提供。
  Raspberry Pi OS（Bookworm 以降）では `pip` によるシステム全体へのインストールはできないので，仮想環境（venv）にインストールします。

      $ sudo apt-get install python3-numpy python3-scipy python3-matplotlib
      $ python3 -m venv --system-site-packages ~/venv
      $ source ~/venv/bin/activate
      (venv) $ pip install control

- 深層学習フレームワーク（PyTorch，TensorFlow）：ニューラルネットワークの学習と推論の機能を提供。
  どちらも 64bit 環境（64bit 版の Raspberry Pi OS や PC など）向けです。32bit 版の Raspberry Pi OS では利用できません。
  学習には計算量とメモリが必要なので，PC（WSL2 を含む）や Raspberry Pi 4/5 で実施しましょう。

  [PyTorch](https://pytorch.org/get-started/locally/) は，仮想環境（venv）に pip でインストールします。

      $ python3 -m venv --system-site-packages ~/venv
      $ source ~/venv/bin/activate
      (venv) $ pip install torch torchvision

  [TensorFlow](https://www.tensorflow.org/install/docker) は，Docker のコンテナで利用できます。Docker のインストールは以下の通りです。

      $ curl -sSL https://get.docker.com | sh
      $ sudo usermod -aG docker $USER

  ログオフ後，再度ログインしてから以下を実行します。

      $ docker pull tensorflow/tensorflow
      $ docker run -it -p 8888:8888 tensorflow/tensorflow

  メモリの少ない PiZeroW では，PC などで学習したモデルを [LiteRT](https://ai.google.dev/edge/litert)（旧 TensorFlow Lite）の形式に変換して，推論のみを実行するとよいでしょう。
  PyTorch のモデルも LiteRT の形式に変換できます。

## Google Colaboratory

- https://colab.research.google.com/

## リンク

- [プログラミングBI/BII](https://github.com/msiplab/EicProgLab)
- [電子情報通信実験Ⅳ](https://github.com/msiplab/EicEngLabIV)

***
新潟大学工学部工学科 電子情報通信プログラム
