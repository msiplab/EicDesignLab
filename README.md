# 電子情報通信設計製図

講義例題と演習課題例のソースコードを管理しています。

## ダウンロード

端末上で以下のコマンドを実行してください。

    $ cd ~
    $ git clone https://github.com/msiplab/EicDesignLab.git EicDesignLab

/home/pi/EicDesignLab の下にファイルが展開されます。

## ソースコードの更新

端末上で以下のコマンドを実行してください。

    $ cd ~/EicDesignLab
    $ git pull

/home/pi/EicProgLab 以下のソースコードが更新されます。

ソースコードを編集しており、更新がうまく行かない場合は以下のコマンドを実行してください。

    $ cd ~/EicDesignLab
    $ git stash
    $ git pull

編集内容を再度反映させる際は以下のコマンドを実行してください。

    $ git stash pop

## Wiki

Raspberry Pi Zero W のセットアップや機能については以下の Wiki サイトにまとめる予定です。適宜参照してください。

- https://github.com/msiplab/EicDesignLab/wiki

## Pythonモジュール

Python の便利なモジュールとそのRaspbian 上でのインストール方法をまとめます。

- 準備 パッケージの更新方法は以下の通りです。時間を要するので余裕をもって実施してください。
    
      $ sudo apt-get update
      $ sudo apt-get upgrade
      $ sudo apt-get dist-upgrade
      $ sudo apt-get install python3-dev python3-setuptools python3-pip
      
  Docker のインストールは以下の通りです。※TensorFlowのインストールに使います。
      
      $ curl -sSL https://get.docker.com | sh
      $ sudo usermod -aG docker pi
    
- Pandas ラベル付けされた列指向のデータを効率的に格納し処理するDataFrameオブジェクトを提供。

      $ sudo apt-get install python3-pandas

- NumPy 高密度のデータ配列を効率的に格納し処理する ndarray オブジェクトを提供。

      $ sudo apt-get install python3-numpy

- SciPy 統計，最適化，線形代数，信号・画像処理，常微分方程式ソルバなどの機能を提供。

      $ sudo apt-get install python3-scipy

- matplotlib (+ seaborn) Pythonの柔軟なデータ可視化機能を提供。

      $ sudo apt-get install python3-matplotlib python3-seaborn

- scikit-learn 機械学習アルゴリズムの効率的なPython実装。

      $ sudo apt-get install python3-sklearn

- pytransitions 軽量な有限状態機械オブジェクトを提供。

      $ sudo apt-get install python3-transitions

- python-control フィードバック制御システムの分析と設計のための基本的な操作を提供。

      $ sudo apt-get install gfortran
      $ sudo apt-get install libblas-dev libatlas-base-dev liblapack-dev
      $ sudo pip3 install slycot
      $ sudo pip3 install control
      
- TensorFlow 深層学習フレームワークを提供。

      $ docker pull tensorflow/tensorflow
      $ docker run -it -p 8888:8888 tensorflow/tensorflow

***
新潟大学工学部工学科　電子情報通信プログラム　新保一成，村松正吾，岡寿樹
