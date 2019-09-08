"""
フォトリフレクタのON/OFF入力（ループ版）

「電子情報通信設計製図」新潟大学工学部工学科電子情報通信プログラム

参考サイト
	https://gpiozero.readthedocs.io/en/stable/index.html
"""
import gpiozero
from gpiozero import Button, LED
from time import sleep

def main():
	PIN_LD = 23
	PIN_PR = [ 10, 9, 11, 8 ]
	PR_STATE = [ 'Black', 'White' ]

	red = LED(PIN_LD)
	photorefs = [ Button(PIN_PR[idx],active_state=True,pull_up=None) \
	for idx in range(0,len(PIN_PR)) ]

	while True:
		redflag = False
		for idx in range(0,len(PIN_PR)):
			pr = photorefs[idx]
			bw = PR_STATE[pr.is_pressed]
			redflag = redflag or pr.is_pressed
			print('{}:{} '.format(idx+1,bw),end=' ')
		print()
		red.value = redflag
                sleep(0.1)

if __name__ == '__main__':
	main()
