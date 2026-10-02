# coding: UTF-8
"""
フォトリフレクタの画素の対応とモータの換算のテスト（ROS なしで実行できる）

  $ python3 -m pytest test/test_sensing.py
"""
import math
import os
import sys

import numpy as np

try:
    from lf_gazebo.sensing import sensor_pixels, photoref_values, motors_to_twist
except ImportError:
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
    from lf_gazebo.sensing import sensor_pixels, photoref_values, motors_to_twist

W, H = 64, 8


def test_sensor_pixels_left_to_right():
    """ 左のフォトリフレクタほど画像の左（列が小さい），前のものほど上（行が小さい） """
    px = sensor_pixels(W, H)
    cols = [c for c, _ in px]
    rows = [r for _, r in px]
    assert cols == sorted(cols)
    assert cols[0] + cols[3] == W - 1 or abs((cols[0] + cols[3]) - (W - 1)) <= 1  # 左右対称
    assert rows[0] < rows[1] and rows[3] < rows[2]   # pr1, pr4 は pr2, pr3 より前


def test_photoref_values_black_line_in_center():
    """ 画像の中央に黒い線があるとき，内側の2つだけが黒（0）に近い """
    gray = np.full((H, W), 255.0)
    gray[:, 28:36] = 0.0
    px = sensor_pixels(W, H)
    values = photoref_values(gray, px)
    assert values[0] == 1.0 and values[3] == 1.0
    gray2 = np.full((H, W), 255.0)
    c = px[1][0]
    gray2[:, c - 2:c + 3] = 0.0
    assert photoref_values(gray2, px)[1] == 0.0


def test_motors_to_twist():
    v, w = motors_to_twist(1.0, 1.0, 60.0, 0.029, 0.10)
    assert math.isclose(v, 2*math.pi*0.029) and w == 0.0
    v, w = motors_to_twist(0.0, 1.0, 60.0, 0.029, 0.10)   # 右が速い → 左回り
    assert w > 0.0
    v, w = motors_to_twist(2.0, -2.0, 60.0, 0.029, 0.10)  # 範囲外は [-1,1] に制限
    assert v == 0.0 and math.isclose(w, -2*2*math.pi*0.029/0.10)
