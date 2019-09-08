"""
フォトリフレクタのON/OFF入力

「電子情報通信設計製図」新潟大学工学部工学科電子情報通信プログラム

参考サイト
				https://gpiozero.readthedocs.io/en/stable/index.html
"""
import gpiozero
from gpiozero import Button, LED
from gpiozero.tools import any_values
from signal import pause

def main():
	PIN_LD = 23
	PIN_PR = [ 10, 9, 11, 8 ]
	Button.label = 0
	
	red = LED(PIN_LD)
	photorefs = [ Button(PIN_PR[idx], active_state=True, pull_up=None) \
	for idx in range(0,len(PIN_PR)) ]
	for idx in range(0,len(photorefs)):
		photorefs[idx].label = idx+1		     
	
	red.source = any_values(photorefs[0],photorefs[1], \
	photorefs[2],photorefs[3])
	
	for pr in photorefs:
		pr.when_pressed = white
		pr.when_released = black
		
	pause()

def white(pr):
	print('{}:White'.format(pr.label))

def black(pr):
	print('{}:Black'.format(pr.label))

if __name__ == '__main__':
	main()
