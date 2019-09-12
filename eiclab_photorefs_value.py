# coding: UTF-8
"""
フォトリフレクタの強度入力（スレッド版）

「電子情報通信設計製図」新潟大学工学部工学科電子情報通信プログラム

参考サイト
				https://gpiozero.readthedocs.io/en/stable/index.html
"""
import gpiozero
from gpiozero import MCP3004, PWMLED
from gpiozero.tools import averaged
from signal import pause

def main():
	""" メイン関数 """
	# 接続ピン
	PIN_LD = 23
	# A/D変換チャネル数
	NUM_CH = 4
	
	# 赤色LED設定(PWM)
	red = PWMLED(PIN_LD)
	# フォトリフレクタ（複数）設定（A/D変換）
	photorefs = [ MCP3004(channel=idx) for idx in range(NUM_CH) ]    
	
	# 計測データ平均をLED入力に接続
	red.source = averaged(photorefs[0],photorefs[1], photorefs[2],photorefs[3])
	
	# 停止(Ctrl+c)まで待機
	pause()

if __name__ == '__main__':
	main()
