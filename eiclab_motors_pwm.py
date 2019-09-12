# coding: UTF-8
"""
モーターのPWM制御（スレッド版）

「電子情報通信設計製図」新潟大学工学部工学科電子情報通信プログラム

参考サイト
	https://gpiozero.readthedocs.io/en/stable/index.html
"""
from gpiozero import Robot
from gpiozero.tools import sin_values, cos_values, post_delayed
from signal import pause

def main():
	""" メイン関数 """
	# 接続ピン
	PIN_AIN1 = 6
	PIN_AIN2 = 5
	PIN_BIN1 = 26
	PIN_BIN2 = 27
	# 左右モーター設定(PWM)
	motors = Robot(left=(PIN_AIN1,PIN_AIN2),right=(PIN_BIN1,PIN_BIN2),pwm=True)
	
	# 0.1秒毎周期30（約3秒）のSIN値の信号源
	srcleft = post_delayed(sin_values(period=30),0.1)
	# 0.1秒毎周期30（約3秒）のCOS値の信号源
	srcright = post_delayed(cos_values(period=30),0.1)
	
	# 左右モータに信号源を接続
	motors.source = zip(srcleft,srcright)
	
	# 停止(Ctr+c)まで待機
	pause()

if __name__ == '__main__':
	main()
