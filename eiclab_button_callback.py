# coding: UTF-8
"""
ボタンの押下検出（スレッド版）

「電子情報通信設計製図」新潟大学工学部工学科電子情報通信プログラム

参考サイト
	https://gpiozero.readthedocs.io/en/stable/index.html
"""
from gpiozero import Button
from signal import pause

def main():
	""" メイン関数 """
	# ボタン設定
	button = Button(25)
	
	# コールバック関数設定
	button.when_pressed = callback_pressed # 押下時
	button.when_released = callback_released # 解放時
	
	# 停止(Ctrl+c)まで待機
	pause()

def callback_pressed():
	""" 押下表示関数 """
	print("Button is pressed")

def callback_released():
	""" 解放表示関数 """
	print("Button is not pressed")

if __name__ == '__main__':
	main()
