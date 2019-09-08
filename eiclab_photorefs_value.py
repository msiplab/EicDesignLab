"""
フォトリフレクタの強度入力

「電子情報通信設計製図」新潟大学工学部工学科電子情報通信プログラム

参考サイト
				https://gpiozero.readthedocs.io/en/stable/index.html
"""
import gpiozero
from gpiozero import MCP3004, PWMLED
from gpiozero.tools import averaged
from signal import pause

def main():
	PIN_LD = 23
	NUM_CH = 4

	red = PWMLED(PIN_LD)
	photorefs = [ MCP3004(channel=idx) for idx in range(0,NUM_CH) ]

	red.source = averaged(photorefs[0],photorefs[1], photorefs[2],photorefs[3])

	pause()

if __name__ == '__main__':
	main()
