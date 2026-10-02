# ライントレース簡易シミュレータ（mbd_phs1）

簡略パラメータモデル（テキストの「簡易物理モデル」）に従うライントレーサを，
pygame の画面上でコースに沿って走らせるシミュレータです。
制御則を考えたり，物理モデルのパラメータの影響を調べたりするのに使います。

「電子情報通信設計製図」新潟大学工学部工学科電子情報通信プログラム

ロータリーエンコーダの模擬と走行データの CSV 保存が付いた詳細パラメータモデルの版は
[`mbd_phs2`](../mbd_phs2/README.md) にあります。

## 準備

PC（Windows，WSL2 の Ubuntu）や Raspberry Pi 4/5 で実行します。

Raspberry Pi OS や Ubuntu の場合

```
$ sudo apt-get install python3-pygame python3-transitions python3-numpy python3-scipy
```

Windows で python.org の Python を使う場合

```
> py -m pip install pygame transitions numpy scipy
```

## 実行

```
$ cd ~/EicDesignLab/mbd_phs1
$ python3 main_mils_line_follower.py
```

Windows の場合は `py main_mils_line_follower.py` で実行します。

## 操作

画面の下に，次の操作の案内が表示されます。

1. 車体をマウスでドラッグして，置く位置を決める
2. マウスをクリックしたままドラッグして，車体の向きを決める
3. クリックすると走り始める（[SPACE] キーでも開始）
4. クリックすると止まり，1. に戻る（[ESC] キーでも停止）

[q] キーで終了します。

## ファイルの構成

| ファイル | 内容 |
|---|---|
| `main_mils_line_follower.py` | シミュレータの本体（コースの読み込み，画面の描画，操作の状態遷移） |
| `mils_line_follower_body.py` | 車体の物理モデル（簡略パラメータモデル） |
| `mils_line_follower_ctrl.py` | 制御則 |
| `mils_line_follower_phrf.py` | フォトリフレクタの模擬 |

## 変更してみよう

- 制御則：`mils_line_follower_ctrl.py` の `prs2mtrs()`
  （入力はフォトリフレクタの値 [0,1]×4（左から順，白で1，黒で0），出力はモータ制御信号 [-1,1]×2（左，右））
- フォトリフレクタの配置：`mils_line_follower_body.py` の `LF_MOUNT_POS_PRF`
- 車体の重さや大きさ，摩擦係数：`mils_line_follower_body.py` の `LF_WEIGHT`，`SHAFT_LENGTH`，`TIRE_DIAMETER`，`PARAMS_*`
- コース：`main_mils_line_follower.py` の `COURSE_IMG`（`../images` の画像），`COURSE_RES`（解像度 mm/pixel）

## 参考

- `mbd_phs2`（詳細パラメータモデル，ロータリーエンコーダの模擬と CSV 保存）：[README](../mbd_phs2/README.md)
- `mbd_phs3`（ROS 2 版）：[README](../mbd_phs3/README.md)
- `mbd_phs4`（Gazebo 版）：[README](../mbd_phs4/README.md)
- `mbd_phs5`（MATLAB/Simulink 版）：[README](../mbd_phs5/README.md)
