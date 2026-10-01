# coding: UTF-8
"""
ライントレーサ制御則（ROS に依存しない部分）

説明

　制御アルゴリズムの変更については prs2mtrs() 関数を編集してください。
  mbd_phs2 の mils_line_follower_ctrl.py と同じ制御則です。

「電子情報通信設計製図」新潟大学工学部工学科電子情報通信プログラム

All rights reserved 2019-2026 (c) Shogo MURAMATSU
"""
import numpy as np


def clamped(v):
    """ 値の制限 [-1,1] """
    return max(-1.0, min(1.0, v))


def prs2mtrs(prs):
    """ フォトリフレクタの値からモータ制御信号への変換

        入力　フォトリフレクタの値 [0,1]x4（左から順，白で1，黒で0）
        出力　モータ制御信号 [-1,1]x2（左，右）

        このアルゴリズムは，細かい調整を除いて実機でも利用できるはずです。
        各自で改善してください。
    """
    vec_prs = np.asarray(prs, dtype=float)

    # 1行目が左モータ，2行目が右モータ．
    # 例えば左側のセンサが黒（0）を検出すると，左モータが遅く
    # 右モータが速くなり，車体は左（ラインの方向）に曲がる．
    mat_A = np.array([
        [1.0, 0.2, -0.2, -1.0],
        [-1.0, -0.2, 0.2, 1.0]
        ])
    vec_mtrs = np.dot(mat_A, vec_prs) + 0.2

    return (clamped(vec_mtrs[0]), clamped(vec_mtrs[1]))
