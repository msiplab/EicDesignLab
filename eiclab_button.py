# coding: UTF-8
"""
ボタンの押下検出

「電子情報通信設計製図」新潟大学工学部工学科電子情報通信プログラム

参考サイト
	https://gpiozero.readthedocs.io/en/stable/index.html
"""
from gpiozero import Button

def main():
	""" メイン関数 """
	# ボタン設定
	button = Button(25)
	
	# ループ処理
	while True:
		if button.is_pressed: # ボタン押下時
			print("Button is pressed")
		else: # ボタン解放時
			print("Button is not pressed")

if __name__ == '__main__':
	main()
