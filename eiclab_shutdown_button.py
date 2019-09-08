#!/usr/bin/python3
# coding:utf-8
"""
シャットダウンボタン

「電子情報通信設計製図」新潟大学工学部工学科電子情報通信プログラム

参考サイト
	https://gpiozero.readthedocs.io/en/stable/index.html
"""
from gpiozero import Button
from subprocess import check_call
from signal import pause

def main():
    PIN_BT = 3

    shutdown_btn = Button(PIN_BT, hold_time=2)
    shutdown_btn.when_held = shutdown

    pause()

def shutdown():
    check_call(['sudo', 'wall', 'poweroff'])
    check_call(['sudo', 'poweroff'])

if __name__ == '__main__':
    main()
