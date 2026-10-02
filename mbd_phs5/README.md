# ライントレーサ MATLAB/Simulink シミュレータ（mbd_phs5）

`mbd_phs3`（ROS 2 版）と同じ物理モデル・制御則・ロータリーエンコーダの模擬を，
MATLAB と Simulink で動かすモデルベース開発の教材です。

1. MATLAB でシミュレーションする（`main_mils_line_follower.m`）
2. Simulink でシミュレーションする（`build_lf_mils_model.m`，`run_lf_mils.m`）
3. 走行データから物理モデルを同定する（`sysid_lf_model.m`）
4. MATLAB の制御ノードで ROS 2 のシミュレータ（`mbd_phs3`，`mbd_phs4`）を動かす（`lf_ros2_controller.m`）
5. Simulink のモデルから Raspberry Pi のプログラムを生成して実機を動かす（`build_lf_raspi_model.m`）

制御則 `prs2mtrs.m` は，1〜5 のすべてで共通です。

「電子情報通信設計製図」新潟大学工学部工学科電子情報通信プログラム

## 必要なもの

MATLAB R2026b で動作を確認しています（新潟大学の学生は大学のライセンスで利用できます）。

| 内容 | 必要な製品 |
|---|---|
| 1. MATLAB でのシミュレーション | MATLAB |
| 2. Simulink でのシミュレーション | Simulink |
| 3. 物理モデルの同定 | System Identification Toolbox |
| 4. ROS 2 との接続 | ROS Toolbox |
| 5. Raspberry Pi での実行 | Raspberry Pi Blockset，MATLAB Coder，Simulink Coder（Embedded Coder もあるとよい） |

1〜3 は MATLAB Online でも実行できます。

## ファイルの構成

| ファイル | 内容 |
|---|---|
| `lfParams.m` | 車体と物理モデルのパラメータ（`mbd_phs3` の `model.py` と同じ） |
| `lfDynamics.m` | 物理モデルの状態方程式（動力学モデルと運動学モデル） |
| `prs2mtrs.m` | 制御則（フォトリフレクタの値 → モータ制御信号） |
| `lfLoadCourse.m` | コース画像の読み込み（`../images/course2025.png`） |
| `lfPhotorefs.m` | フォトリフレクタの模擬 |
| `LFRotaryEncoder.m` | ロータリーエンコーダの模擬（System object．Simulink でも使える） |
| `lfSimulate.m` | 走行シミュレーション（MATLAB 版） |
| `lfPlotCourse.m` | コースの表示 |
| `lfLogsoutToTable.m` | Simulink で記録した信号を走行データの表にする |
| `main_mils_line_follower.m` | 1. MATLAB でのシミュレーション |
| `build_lf_mils_model.m`，`run_lf_mils.m` | 2. Simulink モデル `lf_mils.slx` の作成と実行 |
| `sysid_lf_model.m` | 3. 走行データからの物理モデルの同定 |
| `lf_ros2_controller.m` | 4. MATLAB で動かす ROS 2 の制御ノード |
| `build_lf_raspi_model.m` | 5. Raspberry Pi で動かす Simulink モデル `lf_raspi.slx` の作成 |
| `tests/test_lf_phs5.m` | テスト |

座標系は `mbd_phs3` と同じです（コースの座標系は x 軸が右・y 軸が上・原点は左下，
車体の座標系は x 軸が前・y 軸が左，角度と角速度は左回りが正，長さの単位は m）。

Simulink のモデル（`.slx`）はスクリプトで作成するので，リポジトリには含めていません。

## 準備

MATLAB の「現在のフォルダー」を `mbd_phs5` にしてから実行してください。

```
>> cd ~/EicDesignLab/mbd_phs5     % Windows の場合は clone したフォルダ
```

## 1. MATLAB でのシミュレーション

```
>> main_mils_line_follower
```

コース上を走る様子と，モータ制御信号，左右の車輪の回転数，速度と角速度のグラフが表示され，
走行データが `lf_sim_日時.csv` に保存されます（列は `mbd_phs3` の CSV と同じ）。

制御周期 `p.Ts`（0.05 s）ごとにフォトリフレクタの値を読み，制御則でモータ制御信号を求め，
次の周期までその値を保持して物理モデルを `ode45` で解きます。
`mbd_phs3` とは数値計算の方法が少し違うので，軌跡は 1 cm 程度ずれることがあります。

## 2. Simulink でのシミュレーション

```
>> build_lf_mils_model    % lf_mils.slx を作成
>> run_lf_mils            % 実行して結果を表示（モデルがなければ作成）
```

`lf_mils.slx` は，離散時間の制御器 `Controller` と連続時間の物理モデル `Body` からなります。

- `Controller`：`prs2mtrs.m` を呼び出す MATLAB Function ブロック（制御周期 `p.Ts`）
- `Body`：`lfDynamics.m` と積分器，フォトリフレクタの模擬 `lfPhotorefs.m`，
  ロータリーエンコーダの模擬 `LFRotaryEncoder.m`（MATLAB System ブロック）

シミュレーションの開始時に，パラメータ `p`（`lfParams.m`）とコース `course`（`lfLoadCourse.m`）が
ベースワークスペースに読み込まれます。結果は 1. の MATLAB 版と一致します。
Simulink の画面で実行する場合は，Scope でモータ制御信号とエンコーダの計測値を観測できます。

## 3. 走行データからの物理モデルの同定

```
>> sysid_lf_model
```

テキストの簡易物理モデル（直線運動 T_lin dv/dt + v = K_lin u_lin，回転運動 T_rot dω/dt + ω = K_rot u_rot）の
時定数とゲインを，走行データから `tfest` で推定します。
`csvFile` が空のときは，物理モデルにステップ状のモータ制御信号を与えて走行データを作ります。

```
            K_lin [m/s]  T_lin [s]   K_rot [rad/s]  T_rot [s]
エンコーダ      0.5350     0.5016       10.3352      0.5047
真値            0.4983     0.0357        9.8900      0.0402
パラメータ      0.4983     0.0357        9.9490      0.0406
```

真値（物理モデルの車輪の回転数）からはパラメータどおりの値が推定されますが，
エンコーダの計測値からは時定数が大きく推定されます。
エンコーダは数個のエッジの間隔から回転数を求めて平滑化するので，計測値が遅れるためです。
実機のデータから物理モデルを推定するときは，センサの特性にも注意しましょう。

`csvFile` に走行データの CSV ファイル（`time_s`，`u_left`，`u_right`，`rpm_left`，`rpm_right` の列が必要）を
指定すると，そのデータから推定します。実機の走行データを同じ形式で保存すれば，実機のモデルを推定できます。

## 4. ROS 2 のシミュレータとの接続

WSL2 の Ubuntu で，制御ノードを起動せずに `mbd_phs3` または `mbd_phs4` のシミュレータを起動し，
Windows の MATLAB で制御ノード `/lf_controller_matlab` を動かします。

```
$ ros2 launch lf_sim lf_sim.launch.py controller:=false          # mbd_phs3
$ ros2 launch lf_gazebo lf_gazebo.launch.py controller:=false    # mbd_phs4
```

```
>> lf_ros2_controller        % Ctrl+C で終了
>> lf_ros2_controller(60)    % 60 秒間
```

### Windows の MATLAB と WSL2 の ROS 2 の通信の設定

WSL2 の標準の設定（NAT）では，ROS 2 のノードが互いを自動で見つけられません。
以下のどちらかで設定してください。ROS Toolbox の ROS 2 は Jazzy 相当なので，ROS_STATIC_PEERS が使えます。

**A. 相手の IP アドレスを指定する（ROS_STATIC_PEERS）**

WSL2 の端末で，Windows の IP アドレスを指定してからシミュレータを起動します。

```
$ export ROS_STATIC_PEERS=$(ip route | awk '/default/ {print $3}')
$ hostname -I        # WSL2 の IP アドレス（MATLAB で使う）
```

MATLAB では，ROS 2 のノードを作る前に WSL2 の IP アドレスを指定します。

```
>> setenv('ROS_STATIC_PEERS', '172.29.16.103')   % hostname -I で表示されたアドレス
>> ros2 node list                                 % /lf_body などが表示されれば OK
```

WSL2 の IP アドレスは Windows を再起動すると変わることがあります。

**B. WSL2 のミラーモードを使う**

Windows のユーザーフォルダの `.wslconfig` に以下を書き，PowerShell で `wsl --shutdown` を実行してから
WSL2 を起動し直します。Windows と WSL2 が同じネットワークを共有するので，A の設定は不要です。

```
[wsl2]
networkingMode=mirrored
```

どちらの場合も，Windows ファイアウォールの許可を求められたら MATLAB の通信を許可してください。
ROS_DOMAIN_ID を設定している場合は，WSL2 と MATLAB（`setenv('ROS_DOMAIN_ID', ...)`）で同じ値にします。

## 5. Raspberry Pi での実行

```
>> build_lf_raspi_model                              % 32bit 版の Raspberry Pi OS
>> build_lf_raspi_model('lf_raspi', 'Raspberry Pi (64bit)')   % 64bit 版の場合
```

テキストの配線のライントレーサ（PiZeroW）を動かす Simulink モデル `lf_raspi.slx` を作成します。

```
MCP3004（SPI0 CE0，ch0〜3）→ Photorefs → Controller（prs2mtrs.m）→ Motors → PWM（BCM6, 5, 26, 27）
```

- フォトリフレクタ：A/D コンバーター MCP3004 のチャネル 0〜3（左から順）を SPI で読み，0〜1 の値にします
  （gpiozero の `MCP3004` と同じ値）。
- モータ：モータドライバの A 側（BCM6, 5）が左，B 側（BCM26, 27）が右です。
  モータ制御信号が正なら BCM6（26）に，負なら BCM5（27）に PWM 信号を出します
  （gpiozero の `Robot(left=(6, 5), right=(26, 27))` と同じ）。

実行の手順

1. MATLAB の「アドオン」→「ハードウェアの設定」で，Raspberry Pi Blockset のハードウェアセットアップを行う
   （PiZeroW に必要なライブラリがインストールされる）。SPI を有効にしておく。
2. `lf_raspi.slx` の「モデル設定」→「ハードウェア実装」で，デバイスのアドレス（`car01.local` など），
   ユーザー名とパスワードを設定する。
3. 「ハードウェア」タブの **Monitor & Tune** で実行すると，Scope でフォトリフレクタの値とモータ制御信号を観測できる。
   **ビルド、展開、起動** で実行すると，PiZeroW の上でプログラムが単独で動く。

注意

- 実行の前に車体を持ち上げるなどして，急に走り出しても安全なようにしておきましょう。
- 同じピンを Python のプログラム（`eiclab_*.py` やサービス）から使わないでください。
- 実機のフォトリフレクタの値が白で大きく黒で小さいことを確かめてください。
  逆の場合は `Photorefs` ブロックで `1 - 値` に直すか，制御則を調整します。

## テスト

```
>> runtests('tests')
```

## 参考

- `mbd_phs3`（ROS 2 版）：[README](../mbd_phs3/README.md)
- `mbd_phs4`（Gazebo 版）：[README](../mbd_phs4/README.md)
- Raspberry Pi Blockset：https://jp.mathworks.com/hardware-support/raspberry-pi-blockset.html
- Line Trace for Micromouse with Simulink：https://jp.mathworks.com/matlabcentral/fileexchange/182121-line-trace-for-micromouse-with-simulink
