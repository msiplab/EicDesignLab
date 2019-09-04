"""
LED の点灯と消灯

「電子情報通信設計製図」新潟大学工学部工学科電子情報通信プログラム

参考サイト
	https://gpiozero.readthedocs.io/en/stable/index.html
"""
from gpiozero import LED
from time import sleep

def main():
	red = LED(23)
	
	while True:
		red.on()
		sleep(1)
		red.off()
		sleep(1)

if __name__ == '__main__':
	main()
