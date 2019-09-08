"""
フォトリフレクタの強度入力（ループ版）

「電子情報通信設計製図」新潟大学工学部工学科電子情報通信プログラム

参考サイト
	https://gpiozero.readthedocs.io/en/stable/index.html
"""
import gpiozero
from gpiozero import MCP3004, PWMLED
from time import sleep

def main():
	PIN_LD = 23
	NUM_CH = 4

	red = PWMLED(PIN_LD)
	photorefs = [ MCP3004(channel=idx) for idx in range(0,NUM_CH) ]

	while True:
		ave = 0.0
		for idx in range(0,NUM_CH):
			pr = photorefs[idx]
			v = pr.value
			ave += v
			print('{}:{:4.2f} '.format(idx+1,v),end=' ')
		print()
		red.value = ave/NUM_CH
		sleep(0.1)

if __name__ == '__main__':
	main()
