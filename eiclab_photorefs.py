"""
フォトリフレクタの応答

「電子情報通信設計製図」新潟大学工学部工学科電子情報通信プログラム

参考サイト
	https://gpiozero.readthedocs.io/en/stable/index.html
"""
import gpiozero
from gpiozero import Button
from signal import pause

def main():
  PIN_PR = 10
  photoref = Button(PIN_PR,active_state=True,pull_up=None)

  photoref.when_pressed = callback_pressed
  photoref.when_released = callback_released

  pause()

def callback_pressed():
  print("White")

def callback_released():
  print("Black")

if __name__ == '__main__':
  main()

