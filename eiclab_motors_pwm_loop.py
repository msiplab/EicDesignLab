# coding: UTF-8
"""
モーターのPWM制御（ループ版）

「電子情報通信設計製図」新潟大学工学部工学科電子情報通信プログラム

参考サイト
	https://gpiozero.readthedocs.io/en/stable/index.html
"""
from gpiozero import Robot
from time import sleep

def main():
	""" メイン関数 """
	# 接続ピン
	PIN_AIN1 = 6
	PIN_AIN2 = 5
	PIN_BIN1 = 26
	PIN_BIN2 = 27
	# 左右モーター設定(PWM)
	motors = Robot(left=(PIN_AIN1,PIN_AIN2),right=(PIN_BIN1,PIN_BIN2)) #,pwm=True)
	
	# ループ処理
	while True:
		# 0.2秒前進(50%)
		motors.forward(speed=0.5)
		sleep(0.2)
		# 0.2秒停止
		motors.stop()
		sleep(0.2)
		# 0.2秒後退(50%)
		motors.backward(speed=0.5)
		sleep(0.2)
		# 0.2秒停止
		motors.stop()
		sleep(0.2)
		# 0.2秒左カーブ(50%)前進(100%)
		motors.forward(speed=1,curve_left=0.5)
		sleep(0.2)
		# 0.2秒逆転
		motors.reverse()
		sleep(0.2)
		# 0.2秒停止
		motors.stop()
		sleep(0.2)
		# 0.2秒右カーブ(50%)前進(100%)
		motors.forward(speed=1,curve_right=0.5)
		sleep(0.2)
		# 0.2秒逆転
		motors.reverse()
		sleep(0.2)
		# 0.2秒停止
		motors.stop()
		sleep(0.2)

if __name__ == '__main__':
	main()
