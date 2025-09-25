# coding: UTF-8

import time
from gpiozero import DigitalInputDevice

class RotaryEncoder:
    """
    フォトインタラプタ式ロータリーエンコーダ
    - フォトインタラプタ出力信号の両エッジを利用し、N個のエッジでdtを測定してRPMを算出
    - CPR: counts per revolution（スリット数×エッジ数）
    - edges_per_calc: 1回のrpmの計算に使うエッジ数
    - ema_alpha: 指数移動平均の平滑化係数. 0〜1（新しい値の重み）.
    - timeout_s: エッジが来なければ0rpmを返すまでの時間
    """
    def __init__(self, pin, cpr=32, edges_per_calc=4, ema_alpha=0.2, timeout_s=0.5):
        self.dev = DigitalInputDevice(pin)
        self.cpr = float(cpr)
        self.N = int(edges_per_calc)
        self.alpha = float(ema_alpha)
        self.timeout = float(timeout_s)

        self._rpm = 0.0
        self._t0 = None
        self._k = 0
        self._last_edge = None

        self.dev.when_activated   = self._on_edge
        self.dev.when_deactivated = self._on_edge

    
    def _on_edge(self):
        t = time.monotonic()
        self._last_edge = t
        if self._t0 is None:
            self._t0 = t; self._k = 0
            return
        self._k += 1
        if self._k >= self.N:
            dt = t - self._t0
            if dt > 0 and self.cpr > 0:
                rpm_inst = 60.0 * (self.N / dt) / self.cpr
                self._rpm = (1 - self.alpha) * self._rpm + self.alpha * rpm_inst if self.alpha > 0 else rpm_inst
            self._t0 = t; self._k = 0

    def read_rpm(self):
        if self._last_edge is not None and (time.monotonic() - self._last_edge) > self.timeout:
            return 0.0
        return self._rpm

    def close(self):
        #終了時に実行してコールバックを解除
        self.dev.when_activated   = None
        self.dev.when_deactivated = None
        self.dev.close()