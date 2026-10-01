#!/usr/bin/python3
# coding: UTF-8
"""
ロータリーエンコーダクラス

説明

　車輪の回転をロータリーエンコーダで計測する様子を模擬しています。
  実機用の rotary_encoder.py の RotaryEncoder クラスと同じ方法で
  回転数 [rpm] を算出するので，実機の計測結果と比較できます。

  - フォトインタラプタ出力信号の両エッジを利用し，
    edges_per_calc 個のエッジの間隔 dt から回転数を算出
  - 指数移動平均で平滑化
  - timeout_s の間エッジが来なければ 0 rpm を返す
  - 回転の向きは区別しない（実機と同じ）

「電子情報通信設計製図」新潟大学工学部工学科電子情報通信プログラム

All rights reserved 2026 (c) Shogo MURAMATSU
"""
import math

class LFRotaryEncoder:
    """ ロータリーエンコーダクラス

        - cpr: 1回転あたりのカウント数（スリット数×エッジ数）
        - edges_per_calc: 1回の回転数の計算に使うエッジ数
        - ema_alpha: 指数移動平均の平滑化係数（0〜1，新しい値の重み）
        - timeout_s: エッジが来なければ 0 rpm を返すまでの時間 [s]
    """
    def __init__(self, cpr=32, edges_per_calc=4, ema_alpha=0.2, timeout_s=0.5):
        self.cpr = float(cpr)
        self.N = int(edges_per_calc)
        self.alpha = float(ema_alpha)
        self.timeout = float(timeout_s)
        self.reset()

    def reset(self):
        """ 計測状態の初期化 """
        self._time_s = 0.0      # 時刻 [s]
        self._angle_rad = 0.0   # 車輪の累積回転角（向きは区別しない） [rad]
        self._rpm = 0.0
        self._t0 = None
        self._k = 0
        self._last_edge = None

    def update(self, omega_w, h):
        """ 車輪の角速度 omega_w [rad/s] で h [s] 経過したときの計測を更新 """
        speed = abs(omega_w)
        angle0 = self._angle_rad
        angle1 = angle0 + speed*h
        # この間に通過したエッジの時刻を求めて，実機と同じ処理を行う
        step = 2.0*math.pi/self.cpr
        edge = math.floor(angle0/step) + 1
        while edge*step <= angle1:
            t_edge = self._time_s + (edge*step - angle0)/speed
            self._on_edge(t_edge)
            edge += 1
        self._angle_rad = angle1
        self._time_s += h

    def _on_edge(self, t):
        """ エッジ検出時の処理（rotary_encoder.py の _on_edge() と同じ） """
        self._last_edge = t
        if self._t0 is None:
            self._t0 = t
            self._k = 0
            return
        self._k += 1
        if self._k >= self.N:
            dt = t - self._t0
            if dt > 0 and self.cpr > 0:
                rpm_inst = 60.0*(self.N/dt)/self.cpr
                self._rpm = (1 - self.alpha)*self._rpm + self.alpha*rpm_inst if self.alpha > 0 else rpm_inst
            self._t0 = t
            self._k = 0

    def read_rpm(self):
        """ 回転数 [rpm] の読み出し """
        if self._last_edge is None or (self._time_s - self._last_edge) > self.timeout:
            return 0.0
        return self._rpm
