"""
モーターのPWM制御

「電子情報通信設計製図」新潟大学工学部工学科電子情報通信プログラム

参考サイト
	https://gpiozero.readthedocs.io/en/stable/index.html
"""
from gpiozero import Robot
from time import sleep

def main():
	PIN_AIN1 = 6
	PIN_AIN2 = 5
	PIN_BIN1 = 26
	PIN_BIN2 = 27
	motors = Robot(left=(PIN_AIN1,PIN_AIN2),right=(PIN_BIN1,PIN_BIN2),pwm=True)

	while True:
		motors.forward(speed=0.5)
		sleep(0.2)
		motors.stop()
		sleep(0.2)
		motors.backward(speed=0.5)
		sleep(0.2)
		motors.stop()
		sleep(0.2)
		motors.forward(speed=1,curve_left=0.5)
		sleep(0.2)
		motors.reverse()
		sleep(0.2)
		motors.stop()
		sleep(0.2)
		motors.forward(speed=1,curve_right=0.5)
		sleep(0.2)
		motors.reverse()
		sleep(0.2)
		motors.stop()
		sleep(0.2)

if __name__ == '__main__':
	main()
