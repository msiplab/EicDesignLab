#!/usr/bin/python3
# coding: UTF-8
"""
走行データのログ保存クラス

説明

　シミュレーションの走行データを CSV ファイルに保存します。
  ファイル名には走行開始の日時を含めます（例：lf_sim_20261007_103000.csv）。

  保存する項目
  - time_s                   : 走行開始からの経過時間 [s]
  - u_left, u_right          : 左右のモータ制御信号 [-1,1]
  - rpm_left, rpm_right      : ロータリーエンコーダで計測した左右の車輪の回転数 [rpm]
  - rpm_left_true, rpm_right_true : 物理モデルから求めた左右の車輪の回転数（真値） [rpm]
  - v_mm_s, w_rad_s          : 車体の速度 [mm/s] と角速度（左回りが正） [rad/s]
  - x_mm, y_mm, theta_rad    : 画面上の車体の位置 [mm] と角度 [rad]

「電子情報通信設計製図」新潟大学工学部工学科電子情報通信プログラム

All rights reserved 2026 (c) Shogo MURAMATSU
"""
import csv
from datetime import datetime

class LFDataLogger:
    """ 走行データのログ保存クラス """

    HEADER = [ 'time_s', 'u_left', 'u_right', 'rpm_left', 'rpm_right',
        'rpm_left_true', 'rpm_right_true', 'v_mm_s', 'w_rad_s',
        'x_mm', 'y_mm', 'theta_rad' ]

    def __init__(self, prefix='lf_sim'):
        self._prefix = prefix
        self._file = None
        self._writer = None
        self._filename = None

    def start(self):
        """ ログ保存の開始（新しいファイルを作成） """
        self.stop()
        stamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self._filename = '{}_{}.csv'.format(self._prefix, stamp)
        self._file = open(self._filename, 'w', newline='', encoding='utf-8')
        self._writer = csv.writer(self._file)
        self._writer.writerow(self.HEADER)

    def write(self, time_s, lf):
        """ 1行分のデータを書き込む（lf は LFPhysicalModel） """
        if self._writer is None:
            return
        u_l, u_r = lf.motor_signals
        rpm_l, rpm_r = lf.read_encoders_rpm()
        rpm_lt, rpm_rt = lf.wheels_rpm_true
        self._writer.writerow([ '{:.3f}'.format(time_s),
            '{:.3f}'.format(u_l), '{:.3f}'.format(u_r),
            '{:.1f}'.format(rpm_l), '{:.1f}'.format(rpm_r),
            '{:.1f}'.format(rpm_lt), '{:.1f}'.format(rpm_rt),
            '{:.1f}'.format(lf.velocity_mm_s), '{:.3f}'.format(lf.angular_velocity_rad_s),
            '{:.1f}'.format(lf.x_mm), '{:.1f}'.format(lf.y_mm), '{:.3f}'.format(lf.angle) ])

    def stop(self):
        """ ログ保存の終了（ファイルを閉じる） """
        if self._file is not None:
            self._file.close()
            print('走行データを {} に保存しました'.format(self._filename))
        self._file = None
        self._writer = None

    @property
    def filename(self):
        return self._filename
