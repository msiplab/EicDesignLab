# coding: UTF-8
"""
ロータリーエンコーダサンプルプログラム
「電子情報通信設計製図」新潟大学工学部工学科電子情報通信プログラム
"""

from gpiozero import Robot
from time import sleep
from rotary_encoder import RotaryEncoder


def main():
    # モーター接続ピン
    PIN_AIN1 = 6
    PIN_AIN2 = 5
    PIN_BIN1 = 26
    PIN_BIN2 = 27

    # エンコーダ設定
    ENC_LEFT_PIN = 17    # 左エンコーダ接続ピン
    ENC_RIGHT_PIN = 22   # 右エンコーダ接続ピン
    CPR = 32             # 16スリット両エッジ=32（片エッジなら16）
    EDGES_PER_CALC = 4   # 何回のエッジごとにrpmを計算するか     
    EMA_ALPHA = 0.2  # 指数移動平均の平滑化係数 (0 ~ 1.0)
                     # 小さいと過去データの寄与が大きく、長い時定数で滑らか（応答遅め）
                     # 大きいと最新データを強く反映し、短い時定数で敏感（応答速い）　
    TIMEOUT_S = 0.5      # タイムアウトでrpm = 0を返す時間（秒）

    #モーター出力値設定
    MOT_VAL = float(input("モータの出力値を -1.0 ～ 1.0 で入力してください（終了はCtrl+C）： "))
    
    # 入力範囲をクリップ
    if MOT_VAL < -1.0: MOT_VAL = -1.0
    if MOT_VAL > 1.0: MOT_VAL = 1.0
    print(f"PWM={MOT_VAL:.2f} で回転中。Ctrl+Cで停止")

    #モーター設定
    motors = Robot(left=(PIN_AIN1, PIN_AIN2), right=(PIN_BIN1, PIN_BIN2))

    #エンコーダ設定
    enc_left = RotaryEncoder(ENC_LEFT_PIN, CPR, EDGES_PER_CALC, EMA_ALPHA, TIMEOUT_S)
    enc_right = RotaryEncoder(ENC_RIGHT_PIN, CPR, EDGES_PER_CALC, EMA_ALPHA, TIMEOUT_S)

    try:
        while True:
            # 左右のモーターに同じ値を与える
            motors.value = (MOT_VAL, MOT_VAL)
            
            #ロータリーエンコーダ計測値取得
            rpm_left = enc_left.read_rpm()
            rpm_right = enc_right.read_rpm()
            print("enc_left:{:7.2f}, enc_right:{:7.2f}".format(rpm_left,rpm_right))
            sleep(0.1)

    finally:
        motors.stop()
        sleep(0.1)
        enc_left.close()   # コールバック解除
        sleep(0.1)
        enc_right.close()  # コールバック解除


if __name__ == '__main__':
    main()
