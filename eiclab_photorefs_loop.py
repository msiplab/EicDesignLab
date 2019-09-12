# coding: UTF-8
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
	""" メイン関数 """
	# 接続ピン
	PIN_LD = 23
	PIN_PR = [ 10, 9, 11, 8 ]
	# フォトリフレクタ検出状態
	PR_STATE = [ 'Black', 'White' ]
	
	# 赤色LED設定
	red = LED(PIN_LD)
	# フォトリフレクタ（複数）設定（ボタンとして）
	photorefs = [ Button(PIN_PR[idx],active_state=True,pull_up=None) \
	for idx in range(0,len(PIN_PR)) ]
	
	# ループ処理
	while True:
		# 検出結果の初期化
		redflag = False
		# 検出結果の取得
		for idx in range(0,len(PIN_PR)):
			pr = photorefs[idx]
			bw = PR_STATE[pr.is_pressed]
			redflag = redflag or pr.is_pressed
			print('{}:{} '.format(idx+1,bw),end=' ')
		print()
		# 検出結果の論理和をLEDに出力 
		red.value = redflag
		# 0.1秒待機
		sleep(0.1)

if __name__ == '__main__':
	main()
