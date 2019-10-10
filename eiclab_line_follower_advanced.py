#!/usr/bin/python3
# coding: UTF-8
"""
ライントレーサー（スレッド版クラス実装）

「電子情報通信設計製図」新潟大学工学部工学科電子情報通信プログラム

参考サイト
        https://gpiozero.readthedocs.io/en/stable/index.html
        https://gpiozero.readthedocs.io/en/stable/recipes_advanced.html#bluedot-robot
"""
import numpy as np
import gpiozero
from gpiozero import MCP3004, Robot
from signal import pause

class LineFollower:

        def __init__(self,photorefs):
                self.prs = photorefs                
                
        def prs2mtrs(self):
                """ フォトリフレクタの値をモーター制御の強度値に変換 """
	        # フォトリフレクタの値を読み出しとベクトル化
                vec_x = np.array([ self.prs[idx].value \
                                 for idx in range(len(self.prs)) ])
                
                # モーター制御の強度値を計算（ここを工夫）
                mat_A = np.array([[0.4, 0.3, 0.2, 0.1],\
                                  [0.1, 0.2, 0.3, 0.4]])
                vec_y = np.dot(mat_A,vec_x)

                # 出力範囲を[-1,1]に直して出力
                left, right = vec_y[0], vec_y[1]
                return (clamped(left),clamped(right))
                  
        def line_follow(self):
                while True:
                        yield self.prs2mtrs()

def clamped(v):
        return max(-1,min(1,v))

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
                       right=(PIN_BIN1,PIN_BIN2), \
                       pwm=True)
        # フォトリフレクタ（複数）設定（A/D変換）
        photorefs = [ MCP3004(channel=idx) for idx in range(NUM_CH) ]    

        # ライントレース処理
        lf = LineFollower(photorefs)
        motors.source = lf.line_follow()
        
        # 停止(Ctr+c)まで待機
        pause()

if __name__ == '__main__':
        main()
