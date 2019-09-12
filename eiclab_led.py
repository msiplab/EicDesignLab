# coding: UTF-8
"""
LED の点灯と消灯

「電子情報通信設計製図」新潟大学工学部工学科電子情報通信プログラム

参考サイト
	https://gpiozero.readthedocs.io/en/stable/index.html
"""
from gpiozero import LED
from time import sleep

def main():
	""" メイン関数 """
	# 赤色LED設定
	red = LED(23)
	
	# ループ処理
	while True:
		# 1秒間ON
		red.on()
		sleep(1)
		# 1秒間oFF
		red.off()
		sleep(1)

if __name__ == '__main__':
	main()
