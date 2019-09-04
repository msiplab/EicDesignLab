"""
LED の明るさ調整

「電子情報通信設計製図」新潟大学工学部工学科電子情報通信プログラム

参考サイト
	https://gpiozero.readthedocs.io/en/stable/index.html
"""
from gpiozero import PWMLED
from time import sleep

def main():
	red = PWMLED(23)
	
	while True:
		red.value = 0 # off
		sleep(1)
		red.value = 0.5 # 半分の明るさ
		sleep(1)
		red.value = 1 # 最大の明るさ
		sleep(1)

if __name__ == '__main__':
	main()
