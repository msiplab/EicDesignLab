# coding: UTF-8
"""
モーターのON/OFF制御（スレッド版）

「電子情報通信設計製図」新潟大学工学部工学科電子情報通信プログラム

参考サイト
	https://gpiozero.readthedocs.io/en/stable/index.html
"""
from gpiozero import Robot
from gpiozero.tools import scaled, alternating_values, post_delayed
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
	
	# 1秒毎の正負パルス値の信号源
	dirleft = post_delayed(scaled(alternating_values(True) ,-1,1),1)
	dirright = post_delayed(scaled(alternating_values(False) ,-1,1),1)
	
	# 左右モーターに信号源を接続
	motors.source = zip(dirleft,dirright)
	
	# 停止(Ctrl+c)まで待機
	pause()

if __name__ == '__main__':
	main()
