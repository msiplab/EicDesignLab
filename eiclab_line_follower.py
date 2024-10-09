#!/usr/bin/python3
# coding: UTF-8
"""
ライントレーサー（スレッド版）

「電子情報通信設計製図」新潟大学工学部工学科電子情報通信プログラム

参考サイト
        https://gpiozero.readthedocs.io/en/stable/index.html
        https://gpiozero.readthedocs.io/en/stable/recipes_advanced.html#bluedot-robot
"""
import gpiozero
from gpiozero import MCP3004, Robot
from signal import pause

def prs2mtrs(photorefs):
        """ フォトリフレクタの値をモーター制御の強度値に変換 """
        # フォトリフレクタの値を読み出し
        pr0 = photorefs[0].value
        pr1 = photorefs[1].value
        pr2 = photorefs[2].value
        pr3 = photorefs[3].value

        # モーター制御の強度値を計算（ここを工夫）
        left = (pr0+pr1)/2.0
        right = (pr2+pr3)/2.0

        # 出力範囲を[-1,1]に直して出力
        return (clamped(left),clamped(right))

def clamped(v):
        return max(-1,min(1,v))
                  
def line_follow(photorefs):
        while True:
                yield prs2mtrs(photorefs)

def main():
        """ メイン関数 """
        # モータードライバ接続ピン
        PIN_AIN1 = 6
        PIN_AIN2 = 5
        PIN_BIN1 = 26
        PIN_BIN2 = 27

        # A/D変換チャネル数
        NUM_CH = 4

        # 左右モーター設定(PWM)
        motors = Robot(left=(PIN_AIN1,PIN_AIN2), \
                       right=(PIN_BIN1,PIN_BIN2) ) #, \
                       # pwm=True)
        # フォトリフレクタ（複数）設定（A/D変換）
        photorefs = [ MCP3004(channel=idx) for idx in range(NUM_CH) ]    

        # ライントレース処理
        motors.source = line_follow(photorefs)
        
        # 停止(Ctr+c)まで待機
        pause()

if __name__ == '__main__':
        main()
