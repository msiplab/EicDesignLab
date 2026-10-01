# coding: UTF-8
"""
ライントレーサー物理モデル（ROS に依存しない部分）

説明

　mbd_phs2 の物理モデル（車体の重心と車輪間の中心がずれたモデル）を，
  ROS の座標系の約束（REP 103）に合わせて書き直したものです。

  - 長さは m，角度は rad，時間は s で表す
  - コースの座標系（map）：x 軸が右，y 軸が上，原点はコース画像の左下
  - 車体の座標系（base_link）：x 軸が前，y 軸が左，原点は車輪間の中心
  - 角速度 ω と姿勢角 θ は左回り（反時計回り）が正

  物理モデルの変更については，以下のパラメータおよび _odedydt() メソッドを
  編集してください。

参考資料

- 三平 満司：「非ホロノミック系のフィードバック制御」計測と制御
  36 巻 6 号 p. 396-403, 1997 年
- Gregor Klancar, Andrej Zdesar, Saso Blazic and Igor Skrjanc: "Wheeled Mobile Robotics,"
  Elsevier, 2017

「電子情報通信設計製図」新潟大学工学部工学科電子情報通信プログラム

All rights reserved 2019-2026 (c) Shogo MURAMATSU
"""
import math
import numpy as np
from PIL import Image
from scipy.integrate import odeint

from .encoder import LFRotaryEncoder

# 車体のパラメータ
#
# 車輪間の中心(+)からのフォトリフレクタ(*)の相対座標 [m]（base_link 座標系）
#
#         y
#         ↑      * pr1 (x1,y1)
#       --|--   * pr2 (x2,y2)
#         + ------------→ x（前）
#       --|--   * pr3 (x3,y3)
#                * pr4 (x4,y4)
#
# 進行方向に向かって左から順に pr1, pr2, pr3, pr4
LF_MOUNT_POS_PRF = ((0.120, 0.060), (0.100, 0.020), (0.100, -0.020), (0.120, -0.060))  # m
LF_WEIGHT = 360      # 車体の重さ g（グラム）
SHAFT_LENGTH = 50e-3  # シャフト長 m（１本あたり）
TIRE_DIAMETER = 58e-3  # タイヤ直径 m

# 制御パラメータ（要調整）
COEF_K_P = 3.0  # 比例制御係数

# 物理モデルパラメータ（要調整）
PARAMS_MU_C = 1e-3  # kg/s 車体の直線運動の粘性摩擦係数（便宜上）
PARAMS_IOTA_C = 1e-4  # kg·m^2/s 車体の旋廻運動の粘性摩擦係数（便宜上）
PARAMS_ELL_C = 30e-3  # m 車体の重心から車輪間の中心までの距離
PARAMS_N = 58.2  # ギヤ比
PARAMS_L_C = 2*SHAFT_LENGTH  # m 車輪間の距離
PARAMS_R_W = (1/2)*TIRE_DIAMETER  # m 車輪の半径
PARAMS_K_T = 2e-3  # N·m/A モータのトルク係数（概算）
PARAMS_K_B = 2e-3  # V·s/rad モータの逆起電力定数（概算）
PARAMS_R_A = 2.0  # Ω 電機子抵抗（概算）
PARAMS_J_C = (1/3)*LF_WEIGHT*1e-3*((160e-3/2)**2+(60e-3/2)**2)  # kg·m^2 車体の重心周りの慣性モーメント（概算）
PARAMS_J_M = (1/2)*(5e-3)*((5e-3)**2)  # kg·m^2 電機子の慣性モーメント（概算）
PARAMS_J_G = 0  # kg·m^2 ギヤの慣性モーメント（ギヤ比 n>>1 より近似）
PARAMS_IOTA_M = 1e-6  # kg·m^2/s モータの粘性摩擦係数（概算）
PARAMS_IOTA_G = 0  # kg·m^2/s ギヤの粘性摩擦係数（ギヤ比 n>>1 より近似）

# フォトリフレクタ数
NUM_PHOTOREFS = 4


class LFCourse:
    """ コースデータ

        コース画像を白黒の配列として保持し，
        フォトリフレクタの応答（白で1，黒で0）を模擬する。
    """
    def __init__(self, filename, res_mm=2.5, size_px=(640, 360)):
        image = Image.open(filename).convert('L').resize(size_px, Image.NEAREST)
        self._white = np.asarray(image) > 0  # [行, 列]，0行目が画像の上端
        self._res = res_mm*1e-3  # m/pixel
        self._width_px, self._height_px = size_px

    @property
    def resolution(self):
        """ 解像度 [m/pixel] """
        return self._res

    @property
    def width_px(self):
        return self._width_px

    @property
    def height_px(self):
        return self._height_px

    @property
    def white(self):
        """ 白黒の配列（True が白） [行, 列]，0行目が画像の上端 """
        return self._white

    def to_pixel(self, x, y):
        """ コース座標 (x, y) [m] → 画像の (列, 行) """
        col = int(x/self._res + 0.5)
        row = int((self._height_px*self._res - y)/self._res + 0.5)
        return col, row

    def measure(self, x, y):
        """ 位置 (x, y) [m] 周辺 3x3 画素の白の割合（コース外は 0.5） """
        col, row = self.to_pixel(x, y)
        if 1 <= row < self._height_px-1 and 1 <= col < self._width_px-1:
            return float(self._white[row-1:row+2, col-1:col+2].mean())
        return 0.5


class LFPhysicalModel:
    """ ライントレーサ物理モデルクラス

        入力　モータ制御信号 [-1,1]x2（左，右）
        出力　フォトリフレクタの値 [0,1]x4（左から順，白で1，黒で0）
    """
    def __init__(self, course, weight=LF_WEIGHT, mntposprs=LF_MOUNT_POS_PRF):
        self._course = course
        self._weight = weight  # g
        self._mntposprs = mntposprs
        self._encs = [LFRotaryEncoder(), LFRotaryEncoder()]
        self.set_pose(0.0, 0.0, 0.0)

    # ------------------------------------------------------------------
    def set_pose(self, x, y, theta):
        """ 位置 [m] と姿勢角 [rad] を設定し，速度と計測を初期化 """
        self._x = x
        self._y = y
        self._theta = theta
        self.reset()

    def reset(self):
        """ 速度と計測の初期化 """
        self._v = 0.0  # m/s
        self._w = 0.0  # rad/s（左回りが正）
        self._mtrs = (0.0, 0.0)
        self._wheels_rpm_true = (0.0, 0.0)
        for enc in self._encs:
            enc.reset()

    # ------------------------------------------------------------------
    def sense(self):
        """ フォトリフレクタの値（左から順） """
        c, s = math.cos(self._theta), math.sin(self._theta)
        values = []
        for (dx, dy) in self._mntposprs:
            px = self._x + c*dx - s*dy
            py = self._y + s*dx + c*dy
            values.append(self._course.measure(px, py))
        return values

    def sensor_positions(self):
        """ フォトリフレクタの位置（base_link 座標系） """
        return self._mntposprs

    def step(self, mtrs, h):
        """ モータ制御信号 mtrs=(左, 右) を h [s] 間ゼロ次ホールドして状態を更新 """
        u_l, u_r = float(mtrs[0]), float(mtrs[1])
        u_lin = (u_r + u_l)/2.0  # 直線運動
        u_rot = (u_r - u_l)/2.0  # 回転運動（右が速いと左回り）

        # 速度・角速度（動力学モデル）
        t = np.linspace(0, h, 2)
        y1 = odeint(self._odedydt, [self._v, self._w], t, args=(u_lin, u_rot))
        v1, w1 = y1[-1]

        # 位置・姿勢（運動学モデル）
        p = odeint(self._odefun, [self._x, self._y, self._theta], t, args=(v1, w1))
        self._x, self._y, self._theta = p[-1]
        self._v, self._w = v1, w1
        self._mtrs = (u_l, u_r)

        # ロータリーエンコーダの計測（左右の車輪の角速度から）
        r_w = PARAMS_R_W
        half_L = PARAMS_L_C/2
        omega_l = (v1 - half_L*w1)/r_w  # 左の車輪の角速度 rad/s
        omega_r = (v1 + half_L*w1)/r_w  # 右の車輪の角速度 rad/s
        self._encs[0].update(omega_l, h)
        self._encs[1].update(omega_r, h)
        self._wheels_rpm_true = (60*omega_l/(2*math.pi), 60*omega_r/(2*math.pi))

    def _odedydt(self, y, t, u_lin, u_rot):
        """ 動力学(Dynamic)モデルの状態方程式（mbd_phs2 と同じ） """
        v, w = y

        mc_kg = 1e-3*self._weight  # g -> kg

        n = PARAMS_N
        r_w = PARAMS_R_W
        k_t = PARAMS_K_T
        k_b = PARAMS_K_B
        R_a = PARAMS_R_A
        J_m = PARAMS_J_M
        J_g = PARAMS_J_G
        iota_m = PARAMS_IOTA_M
        iota_g = PARAMS_IOTA_G
        iota_bar_m = iota_m + k_t*k_b/R_a
        iota_bar_g = iota_g + (n**2)*iota_bar_m
        J_bar_g = J_g + (n**2)*J_m
        zeta = n*k_t/R_a

        # 直線運動
        mu_c = PARAMS_MU_C
        D_lin = iota_bar_g + (1/2)*mu_c*(r_w**2)
        J_lin = J_bar_g + (1/2)*mc_kg*(r_w**2)
        T_lin = J_lin/D_lin  # 時定数
        K_lin = COEF_K_P*(zeta*r_w)/D_lin
        N_lin = (1/2)*mc_kg*(r_w**2)

        # 回転運動
        iota_c = PARAMS_IOTA_C
        l_c = PARAMS_ELL_C
        L_c = PARAMS_L_C
        J_c = PARAMS_J_C
        r_c = (2*r_w/L_c)
        D_rot = iota_bar_g + (1/2)*(mu_c*(l_c**2)+iota_c)*(r_c**2)
        J_rot = J_bar_g + (1/2)*(J_c + mc_kg*(l_c**2))*(r_c**2)
        T_rot = J_rot/D_rot  # 時定数
        K_rot = COEF_K_P*(zeta*r_c)/D_rot
        N_rot = (1/2)*mc_kg*(r_c**2)

        dydt0 = (1/T_lin)*(-l_c*(N_lin/D_lin)*(-w*w) - v + K_lin*u_lin)
        dydt1 = (1/T_rot)*(-l_c*(N_rot/D_rot)*(v*w) - w + K_rot*u_rot)
        return [dydt0, dydt1]

    def _odefun(self, pos, t, v, w):
        """ 運動(Kinematic)モデルの状態方程式

            d_ ( x ) = ( cosθ )v + ( 0 )ω
            dt ( y )   ( sinθ )    ( 0 )
               ( θ )   (  0   )    ( 1 )
        """
        theta = pos[2]
        return [math.cos(theta)*v, math.sin(theta)*v, w]

    # ------------------------------------------------------------------
    @property
    def pose(self):
        """ (x [m], y [m], θ [rad]) """
        return (self._x, self._y, self._theta)

    @property
    def velocity(self):
        """ 速度 [m/s] """
        return self._v

    @property
    def angular_velocity(self):
        """ 角速度（左回りが正） [rad/s] """
        return self._w

    @property
    def motor_signals(self):
        """ 直前の左右のモータ制御信号 """
        return self._mtrs

    @property
    def wheels_rpm_true(self):
        """ 物理モデルから求めた左右の車輪の回転数（真値，後退は負） [rpm] """
        return self._wheels_rpm_true

    def read_encoders_rpm(self):
        """ ロータリーエンコーダで計測した左右の車輪の回転数 [rpm] """
        return (self._encs[0].read_rpm(), self._encs[1].read_rpm())
