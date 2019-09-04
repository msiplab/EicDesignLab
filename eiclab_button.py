"""
ボタンの押下検出

「電子情報通信設計製図」新潟大学工学部工学科電子情報通信プログラム

参考サイト
	https://gpiozero.readthedocs.io/en/stable/index.html
"""
from gpiozero import Button

def main():
	button = Button(25)

	while True:
		if button.is_pressed:
			print("Button is pressed")
		else:
			print("Button is not pressed")

if __name__ == '__main__':
	main()
