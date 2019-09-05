"""
ボタンの押下検出（コールバック版）

「電子情報通信設計製図」新潟大学工学部工学科電子情報通信プログラム

参考サイト
	https://gpiozero.readthedocs.io/en/stable/index.html
"""
from gpiozero import Button
from signal import pause

def main():
        button = Button(25)

        button.when_pressed = callback_pressed
        button.when_released = callback_released

        pause()
	
def callback_pressed():
	print("Button is pressed")

def callback_released():
	print("Button is not pressed")

if __name__ == '__main__':
	main()
