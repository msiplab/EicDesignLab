# coding: UTF-8
"""
フォトリフレクタのON/OFF入力（スレッド版）

「電子情報通信設計製図」新潟大学工学部工学科電子情報通信プログラム

参考サイト
				https://gpiozero.readthedocs.io/en/stable/index.html
"""
import gpiozero
from gpiozero import Button, LED
from gpiozero.tools import any_values
from signal import pause

def main():
	""" メイン関数 """
	# 接続ピン
	PIN_LD = 23
	PIN_PR = [ 10, 9, 11, 8 ]
	# フォトリフレクタラベル（フィールド追加）
	Button.label = 0
	
	# 赤色lED設定
	red = LED(PIN_LD)
	# フォトリフレクタ（複数）設定（ボタンとして）
	photorefs = [ Button(PIN_PR[idx], active_state=True, pull_up=None) \
	for idx in range(len(PIN_PR)) ]
	# フォトリフレクタラベル設定
	for idx in range(len(photorefs)):
		photorefs[idx].label = idx+1		     
	
	# フォトリフレクタ検出結果の論理和をLED入力に接続
	red.source = any_values(photorefs[0],photorefs[1], \
	photorefs[2],photorefs[3])
	
	# コールバック設定
	for pr in photorefs:
		# 白色検出時
		pr.when_pressed = white
		# 黒色検出時
		pr.when_released = black
	
	# 停止(Ctrl+c)まで待機
	pause()

def white(pr):
	""" 白色表示関数 """
	print('{}:White'.format(pr.label))

def black(pr):
	""" 黒色表示関数 """
	print('{}:Black'.format(pr.label))

if __name__ == '__main__':
	main()
