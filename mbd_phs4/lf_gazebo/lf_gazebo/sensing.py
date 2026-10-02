# coding: UTF-8
"""
カメラ画像からフォトリフレクタの値を求める計算（ROS に依存しない部分）

  床を真下に見るカメラの画像のうち，4つのフォトリフレクタの位置に
  当たる画素の周辺 3x3 画素の白の割合を，フォトリフレクタの値とする
  （白で1，黒で0．mbd_phs2/phs3 のフォトリフレクタの模擬と同じ）．

  車体の座標系（base_link）：x 軸が前，y 軸が左
  画像：上が車体の前，左が車体の左

「電子情報通信設計製図」新潟大学工学部工学科電子情報通信プログラム

All rights reserved 2026 (c) Shogo MURAMATSU
"""
import math
import numpy as np

# フォトリフレクタの位置（base_link 座標系，左から順） [m]（mbd_phs3 と同じ）
LF_MOUNT_POS_PRF = ((0.120, 0.060), (0.100, 0.020), (0.100, -0.020), (0.120, -0.060))

# カメラ（model.sdf と同じ値）
CAMERA_X = 0.11        # カメラの x 座標 [m]
CAMERA_HEIGHT = 0.15   # カメラの高さ [m]（車輪の中心からではなく床から）
CAMERA_HFOV = 1.0808   # 水平画角 [rad]


def sensor_pixels(width, height, mntpos=LF_MOUNT_POS_PRF,
                  cam_x=CAMERA_X, cam_h=CAMERA_HEIGHT, hfov=CAMERA_HFOV):
    """ フォトリフレクタの位置に当たる画素の（列, 行）のリスト """
    half_w = cam_h*math.tan(hfov/2)      # 画像の左右の端の y [m]
    half_v = half_w*height/width          # 画像の上下の端の x - cam_x [m]
    pixels = []
    for (x, y) in mntpos:
        col = (half_w - y)/(2*half_w)*width
        row = (cam_x + half_v - x)/(2*half_v)*height
        col = min(max(int(col), 0), width - 1)
        row = min(max(int(row), 0), height - 1)
        pixels.append((col, row))
    return pixels


def photoref_values(gray, pixels, threshold=128):
    """ 濃淡画像 gray[行, 列] から，各画素の周辺 3x3 の白の割合を求める """
    h, w = gray.shape
    values = []
    for (col, row) in pixels:
        r0, r1 = max(row - 1, 0), min(row + 2, h)
        c0, c1 = max(col - 1, 0), min(col + 2, w)
        values.append(float((gray[r0:r1, c0:c1] >= threshold).mean()))
    return values


def rgb_to_gray(data, width, height, step):
    """ R8G8B8 の画像データを濃淡画像に変換 """
    a = np.frombuffer(bytes(data), dtype=np.uint8).reshape(height, step)[:, :width*3]
    a = a.reshape(height, width, 3).astype(np.float32)
    return 0.299*a[:, :, 0] + 0.587*a[:, :, 1] + 0.114*a[:, :, 2]


def motors_to_twist(u_left, u_right, max_wheel_rpm, wheel_radius, wheel_separation):
    """ モータ制御信号 [-1,1] から車体の速度 v [m/s] と角速度 ω [rad/s]（左回りが正）

        各車輪の回転数はモータ制御信号に比例し，制御信号が1のとき max_wheel_rpm とする
    """
    u_l = max(-1.0, min(1.0, u_left))
    u_r = max(-1.0, min(1.0, u_right))
    w_max = 2*math.pi*max_wheel_rpm/60   # rad/s
    omega_l, omega_r = u_l*w_max, u_r*w_max
    v = wheel_radius*(omega_r + omega_l)/2
    w = wheel_radius*(omega_r - omega_l)/wheel_separation
    return v, w
