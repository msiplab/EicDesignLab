# coding: UTF-8
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
	""" メイン関数 """
	# 接続ピン
	PIN_LD = 23
	# A/D変換チャネル数
	NUM_CH = 4
	
	# 赤色LED設定(PWM)
	red = PWMLED(PIN_LD)
	# フォトリフレクタ（複数）設定（A/D変換）
	photorefs = [ MCP3004(channel=idx) for idx in range(0,NUM_CH) ]
	
	# ループ処置
	while True:
		# 計測値平均の初期化
		ave = 0.0
		# 計測データの取得
		for idx in range(0,NUM_CH):
			pr = photorefs[idx]
			v = pr.value
			ave += v
			print('{}:{:4.2f} '.format(idx+1,v),end=' ')
		print()
		# 計測データの平均をLEDに出力
		red.value = ave/NUM_CH
		# 0.1秒待機
		sleep(0.1)

if __name__ == '__main__':
	main()
