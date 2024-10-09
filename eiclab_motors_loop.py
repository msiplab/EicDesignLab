# coding: UTF-8
"""
モーターのON/OFF制御（ループ版）

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
	# 左右モーター設定(ON/OFF)
	motors = Robot(left=(PIN_AIN1,PIN_AIN2),right=(PIN_BIN1,PIN_BIN2)) #,pwm=False)
	
	# ループ処理
	while True:
		# 0.2秒前進
		motors.forward()
		sleep(0.2)
		# 0.2秒停止
		motors.stop()
		sleep(0.2)
		# 0.2秒後退
		motors.backward()
		sleep(0.2)
		# 0.2秒停止
		motors.stop()
		sleep(0.2)
		# 0.2秒左旋回
		motors.left()
		sleep(0.2)
		# 0.2秒停止
		motors.stop()
		sleep(0.2)
		# 0.2秒右旋回
		motors.right()
		sleep(0.2)
		# 0.2秒停止
		motors.stop()
		sleep(0.2)

if __name__ == '__main__':
	main()
