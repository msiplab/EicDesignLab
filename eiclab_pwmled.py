# coding: UTF-8
"""
LED の明るさ調整

「電子情報通信設計製図」新潟大学工学部工学科電子情報通信プログラム

参考サイト
	https://gpiozero.readthedocs.io/en/stable/index.html
"""
from gpiozero import PWMLED
from time import sleep

def main():
	""" メイン関数 """
	# LED設定(PWM)
	red = PWMLED(23)
	
	# ループ処理
	while True:
		# 1秒間 off
		red.value = 0
		sleep(1)
		# 1秒間明るさ50%
		red.value = 0.5
		sleep(1)
		# 1秒間明るさ100%
		red.value = 1 
		sleep(1)

if __name__ == '__main__':
	main()
