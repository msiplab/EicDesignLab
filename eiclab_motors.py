"""
モーターのON/OFF制御

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
	motors = Robot(left=(PIN_AIN1,PIN_AIN2),right=(PIN_BIN1,PIN_BIN2),pwm=False)

	while True:
		motors.forward()
		sleep(0.2)
		motors.stop()
		sleep(0.2)
		motors.backward()
		sleep(0.2)
		motors.stop()
		sleep(0.2)
		motors.left()
		sleep(0.2)
		motors.stop()
		sleep(0.2)
		motors.right()
		sleep(0.2)
		motors.stop()
		sleep(0.2)

if __name__ == '__main__':
	main()
