# 電子情報通信設計製図

[![Open in MATLAB Online](https://www.mathworks.com/images/responsive/global/open-in-matlab-online.svg)](https://matlab.mathworks.com/open/github/v1?repo=msiplab/EicDesignLab)

講義例題と演習課題例のソースコードを管理しています。

## ダウンロード

[ZIPファイル](https://github.com/msiplab/EicDesignLab/archive/refs/heads/master.zip)をダウンロードして展開するか、端末上で以下のコマンドを実行してください。

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

## Fritzing

製図アプリ Fritzing を WSL2上のUbuntuやRasperrypi OSにインストールする場合は以下のコマンドを実行してください。
      
    $ sudo apt-get update
    $ sudo apt-get upgrade -y
    $ sudo apt-get install fritzing fritzing-data fritzing-parts


## Wiki

マニュアルの訂正や補足事項など以下の Wiki サイトにまとめています。適宜参照してください。

- https://github.com/msiplab/EicDesignLab/wiki

## Pythonモジュール

Python の便利なモジュールとそのRaspbian 上でのインストール方法をまとめます。

- 準備 パッケージの更新方法は以下の通りです。時間を要するので余裕をもって実施してください。
    
      $ sudo apt-get update
      $ sudo apt-get upgrade -y
      $ sudo apt-get dist-upgrade
      $ sudo apt-get install python3-dev python3-setuptools python3-pip
      
      
- NumPy 高密度のデータ配列を効率的に格納し処理する ndarray オブジェクトを提供。

      $ sudo apt-get install python3-numpy

- SciPy 統計，最適化，線形代数，信号・画像処理，常微分方程式ソルバなどの機能を提供。

      $ sudo apt-get install python3-scipy
      
- Pygame 主にゲームを対象としたGUIアプリ制作に役立つモジュールを提供。

      $ sudo apt-get install python3-pygame
      
- pytransitions 軽量な有限状態機械オブジェクトを提供。

      $ sudo apt-get install python3-transitions

モデルベースシミュレーションに必要なものはここまで。

- Pandas ラベル付けされた列指向のデータを効率的に格納し処理するDataFrameオブジェクトを提供。

      $ sudo apt-get install python3-pandas


- matplotlib (+ seaborn) Pythonの柔軟なデータ可視化機能を提供。

      $ sudo apt-get install python3-matplotlib python3-seaborn

- scikit-learn 機械学習アルゴリズムの効率的なPython実装。

      $ sudo apt-get install python3-sklearn

- python-control フィードバック制御システムの分析と設計のための基本的な操作を提供。

      $ sudo apt-get install gfortran
      $ sudo apt-get install libblas-dev libatlas-base-dev liblapack-dev
      $ sudo pip3 install slycot
      $ sudo pip3 install control
      
Docker のインストールは以下の通りです。※TensorFlowのインストールに使います。
    
      $ sudo apt-get dist-upgrade
      $ curl -sSL https://get.docker.com | sh
      $ sudo usermod -aG docker pi
   
  ログオフ後，再度ログインしてください。
        
      
- TensorFlow 深層学習フレームワークを提供。

      $ docker pull tensorflow/tensorflow
      $ docker run -it -p 8888:8888 tensorflow/tensorflow

## Google Colaboratory

- https://colab.research.google.com/

## リンク

- [プログラミングBI/BII](https://github.com/msiplab/EicProgLab)
- [電子情報通信実験Ⅳ](https://github.com/msiplab/EicEngLabIV)

***
新潟大学工学部工学科　電子情報通信プログラム　
