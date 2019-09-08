"""
モーターのON/OFF制御

「電子情報通信設計製図」新潟大学工学部工学科電子情報通信プログラム

参考サイト
	https://gpiozero.readthedocs.io/en/stable/index.html
"""
from gpiozero import Robot
from gpiozero.tools import sin_values, cos_values, post_delayed
from signal import pause

def main():
	PIN_AIN1 = 6
	PIN_AIN2 = 5
	PIN_BIN1 = 26
	PIN_BIN2 = 27
	motors = Robot(left=(PIN_AIN1,PIN_AIN2),right=(PIN_BIN1,PIN_BIN2),pwm=True)

	dirleft = post_delayed(scaled(alternating_values() ,-1,1),0.1)
	dirright = post_delayed(scaled(alternating_values() ,-1,1),0.1)
	
	motors.source = zip(dirleft,dirright)
	
	pause()

if __name__ == '__main__':
	main()
