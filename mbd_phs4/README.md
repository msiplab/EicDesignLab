# ライントレーサ Gazebo シミュレータ（mbd_phs4）

ライントレーサを Gazebo（Harmonic）の3次元の物理シミュレーションで走らせるシミュレータです。
Windows 11 の WSL2 上の Ubuntu 24.04 と **ROS 2 Jazzy Jalisco** で動かすことを想定しています。
制御ノードは `mbd_phs3` の `lf_controller`（`lf_sim` パッケージ）をそのまま使うので，
同じ制御則が，簡易な物理モデル（phs3）でも物理エンジン（phs4）でも動くことを確かめられます。

「電子情報通信設計製図」新潟大学工学部工学科電子情報通信プログラム

## 構成

```
  Gazebo（lf_course.sdf：コースの床と車体）
    │ カメラ画像                         ↑ /cmd_vel（車体の速度と角速度）
    ↓ /photoref_camera/image            │
  lf_photorefs ── /photorefs ──→ lf_controller ── /cmd_motors ──→ lf_motors
  （画像の4点の明るさ）              （mbd_phs3 の制御則）           （制御信号 → 速度）

  Gazebo ── /joint_states ──→ lf_encoders ──→ /wheel_rpm, /wheel_rpm_true
  Gazebo ── /odom（車体の位置と姿勢，コースの座標系 map）
```

| ファイル | 内容 |
|---|---|
| `lf_gazebo/worlds/lf_course.sdf` | ワールド（コースの床と車体） |
| `lf_gazebo/models/lf_course/` | コース（2025年度のコース画像を 1.6 m × 0.9 m の床に貼る） |
| `lf_gazebo/models/line_follower/` | 車体（差動2輪，ボールキャスター，フォトリフレクタの代わりのカメラ） |
| `lf_gazebo/lf_gazebo/sensing.py` | 画像からフォトリフレクタの値を求める計算，モータの換算（ROS に依存しない） |
| `lf_gazebo/lf_gazebo/photoref_node.py` | フォトリフレクタノード `lf_photorefs` |
| `lf_gazebo/lf_gazebo/motor_node.py` | モータノード `lf_motors` |
| `lf_gazebo/lf_gazebo/encoder_node.py` | ロータリーエンコーダノード `lf_encoders` |
| `lf_gazebo/config/bridge.yaml` | ROS 2 と Gazebo の間のトピックの橋渡し |
| `lf_gazebo/launch/lf_gazebo.launch.py` | Gazebo と各ノードの起動 |

座標系は `mbd_phs3` と同じ（コースの座標系は x 軸が右・y 軸が上・原点は左下，
車体の座標系は x 軸が前・y 軸が左，角度と角速度は左回りが正）です。

フォトリフレクタは，前方の床を真下に見る小さなカメラ（64 × 8 画素）で模擬しています。
画像のうち，4つのフォトリフレクタの位置に当たる画素の周辺 3 × 3 画素の白の割合を，
フォトリフレクタの値（白で1，黒で0）とします。
各車輪の回転数はモータ制御信号に比例するものとし（制御信号が1のとき `max_wheel_rpm`），
モータの応答の遅れは Gazebo の DiffDrive の加速度の制限で近似しています。

## 準備

`mbd_phs3` の README に従って ROS 2 Jazzy をインストールし，`lf_sim` をビルドしておきます。
そのうえで，Gazebo と ROS 2 をつなぐパッケージをインストールします。

```
$ sudo apt install -y ros-jazzy-ros-gz
```

`lf_sim` と `lf_gazebo` をビルドします。

```
$ cd ~/ros2_ws
$ colcon build --symlink-install --packages-select lf_sim lf_gazebo
$ source install/setup.bash
```

## 実行

```
$ ros2 launch lf_gazebo lf_gazebo.launch.py
```

Gazebo の画面にコースと車体が表示され，車体がラインに沿って走ります。
画面を表示しない場合は `headless:=true` を付けます。

観測と記録の方法は `mbd_phs3` と同じです（`ros2 topic echo /wheel_rpm`，`ros2 bag record` など）。

## 変更してみよう

- 制御則：`mbd_phs3/lf_sim/lf_sim/controller.py` の `prs2mtrs()`（phs3 と共通）
- フォトリフレクタの配置：`lf_gazebo/lf_gazebo/sensing.py` の `LF_MOUNT_POS_PRF`
  （カメラに写る範囲は x = 0.10〜0.12 m，y = −0.08〜0.08 m）
- モータの最大回転数：`ros2 launch` の後に `ros2 param set /lf_motors max_wheel_rpm 120` など
- 車体の大きさや重さ，摩擦：`lf_gazebo/models/line_follower/model.sdf`

## テスト

```
$ cd ~/ros2_ws/src/EicDesignLab/mbd_phs4/lf_gazebo
$ python3 -m pytest test/test_sensing.py
```

## うまく動かないとき

- `libEGL warning: failed to open /dev/dri/renderD128: Permission denied` と表示される：
  GPU を使えずソフトウェアで描画しています（動作はします）。
  `sudo usermod -aG render $USER` を実行して WSL を再起動すると，GPU を使える場合があります。
- Gazebo の画面が表示されない：`headless:=true` で起動して，トピックが流れているか確認してください。
