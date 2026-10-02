# ライントレーサ ROS 2 シミュレータ（mbd_phs3）

`mbd_phs2` の物理モデル（車体の重心と車輪間の中心がずれたモデル）とロータリーエンコーダの模擬を，
ROS 2 のノードとして動かすシミュレータです。
Windows 11 の WSL2 上の Ubuntu 24.04 と **ROS 2 Jazzy Jalisco** で動かすことを想定しています。
Raspberry Pi 4/5 で動かす場合は，Ubuntu 24.04（64bit）を導入してください（Raspberry Pi OS では `ros2setup.bash` は動きません）。

「電子情報通信設計製図」新潟大学工学部工学科電子情報通信プログラム

同じ制御ノード（`lf_controller`）を Gazebo の3次元の物理シミュレーションで動かす版は [`mbd_phs4`](../mbd_phs4/README.md) にあります。

## 構成

```
               /photorefs（フォトリフレクタの値，左から順）
   +---------+ ------------------------------------> +---------------+
   | lf_body |                                       | lf_controller |
   | 物理モデル | <------------------------------------ | 制御則         |
   +---------+   /cmd_motors（モータ制御信号，左・右）   +---------------+
        |
        +--> /wheel_rpm, /wheel_rpm_true（左右の車輪の回転数：エンコーダの計測値と真値）
        +--> /odom, TF（map → base_link）
        +--> /map（コース），/lf_markers（車体の表示）  --> RViz2
```

| ファイル | 内容 |
|---|---|
| `lf_sim/lf_sim/model.py` | コースと物理モデル（ROS に依存しない） |
| `lf_sim/lf_sim/encoder.py` | ロータリーエンコーダの模擬（`mbd_phs2` と同じ） |
| `lf_sim/lf_sim/controller.py` | 制御則 `prs2mtrs()`（ROS に依存しない） |
| `lf_sim/lf_sim/body_node.py` | 車体ノード `lf_body` |
| `lf_sim/lf_sim/controller_node.py` | 制御ノード `lf_controller` |
| `lf_sim/launch/lf_sim.launch.py` | 2つのノードと RViz2 の起動 |
| `lf_sim/test/test_model.py` | 物理モデルと制御則のテスト（ROS なしでも実行可） |

座標系は ROS の約束（REP 103）に従います。コースの座標系 `map` は x 軸が右・y 軸が上，
車体の座標系 `base_link` は x 軸が前・y 軸が左で，角度と角速度は左回りが正です。

## 準備

### 1. WSL2 と Ubuntu 24.04（Windows の PowerShell）

```
> wsl --install -d Ubuntu-24.04
```

Windows 11 の WSL2 では，RViz2 などの GUI アプリをそのまま表示できます（WSLg）。

### 2. ROS 2 Jazzy（Ubuntu の端末）

このリポジトリを WSL の Ubuntu のホームディレクトリにクローンし，セットアップスクリプトを実行します。
Windows 側のフォルダ（`/mnt/c/...`）ではビルドが遅くなるので，Ubuntu 側に置いてください。

```
$ mkdir -p ~/ros2_ws/src
$ cd ~/ros2_ws/src
$ git clone https://github.com/msiplab/EicDesignLab.git
$ bash EicDesignLab/mbd_phs3/ros2setup.bash
$ source ~/.bashrc
```

### 3. ビルド

```
$ cd ~/ros2_ws
$ colcon build --symlink-install --packages-select lf_sim
$ source install/setup.bash
```

## 実行

```
$ ros2 launch lf_sim lf_sim.launch.py
```

- RViz2 にコースと車体が表示され，車体がラインに沿って走り始めます。
- RViz2 の「2D Pose Estimate」でコース上をドラッグすると，車体の位置と向きを変えられます。
- 走行の停止と再開
  ```
  $ ros2 service call /lf_body/set_running std_srvs/srv/SetBool "{data: false}"
  $ ros2 service call /lf_body/set_running std_srvs/srv/SetBool "{data: true}"
  ```

## 観測と記録

別の端末で以下を実行します（各端末で `source ~/ros2_ws/install/setup.bash` が必要です）。

```
$ ros2 topic list                       # トピックの一覧
$ ros2 topic echo /wheel_rpm            # エンコーダで計測した左右の回転数 [rpm]
$ ros2 run rqt_plot rqt_plot /wheel_rpm/data[0] /wheel_rpm/data[1]   # グラフ表示
$ rqt_graph                             # ノードとトピックのつながり
```

走行データは `ros2 bag` で記録・再生できます。

```
$ ros2 bag record /cmd_motors /photorefs /wheel_rpm /wheel_rpm_true /odom
$ ros2 bag play （記録したフォルダ名）
```

走行データを CSV ファイル（`lf_sim_日時.csv`）に保存することもできます。
列の構成は `mbd_phs2` とほぼ同じですが，長さの単位は m で，座標系は ROS の約束（y 軸が上向き，角度は左回りが正）です。
`ros2 launch` を1回起動するごとに1つのファイルが，起動したディレクトリに作られます。
`rpm_left`，`rpm_right`（エンコーダの計測値）は回転の向きを区別しません。

```
$ ros2 launch lf_sim lf_sim.launch.py log_csv:=true
```

## 制御則と物理モデルの変更

- 制御則：`lf_sim/lf_sim/controller.py` の `prs2mtrs()`
- 物理モデル：`lf_sim/lf_sim/model.py` のパラメータと `_odedydt()`

`--symlink-install` でビルドしていれば，ファイルを編集した後にビルドし直す必要はありません。
ノードを起動し直すと変更が反映されます。

## テスト

```
$ cd ~/ros2_ws/src/EicDesignLab/mbd_phs3/lf_sim
$ python3 -m pytest test/test_model.py
```

ROS 2 のワークスペースでは `colcon test --packages-select lf_sim` でも実行できます。

## うまく動かないとき

- RViz2 の画面が真っ黒，または起動しない：`export LIBGL_ALWAYS_SOFTWARE=1` を実行してから起動してください。
- `ros2: command not found`：`source /opt/ros/jazzy/setup.bash` を実行してください。
- パッケージが見つからない：`source ~/ros2_ws/install/setup.bash` を実行してください。
