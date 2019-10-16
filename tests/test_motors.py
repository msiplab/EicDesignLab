# coding: UTF-8
import unittest
from gpiozero.pins.mock import MockFactory
from gpiozero import Device, Motor, LED
from time import sleep

class TestMotor(unittest.TestCase):
	""" モーターテストクラス """

	def test_construction(self):
		""" 生成テスト """
		# 接続ピン
		PIN_AIN1 = 6
		PIN_AIN2 = 5

		# 期待値
		valueAIN1Expctd = 0 # low
		valueAIN2Expctd = 0 # low

		# ターゲット生成
		motor = Motor(PIN_AIN1, PIN_AIN2, pwm=False)
		ain1_pin = Device.pin_factory.pin(PIN_AIN1)
		ain2_pin = Device.pin_factory.pin(PIN_AIN2)

		# 実際値
		valueAIN1Actual = ain1_pin.state
		valueAIN2Actual = ain2_pin.state

		# 評価
		try:
			self.assertEqual(valueAIN1Actual,valueAIN1Expctd)
			self.assertEqual(valueAIN2Actual,valueAIN2Expctd)
			sleep(0.1)
		finally:
			motor.close()

	def test_forward(self):
		""" 前進テスト """
		# 接続ピン
		PIN_AIN1 = 6
		PIN_AIN2 = 5

		# 期待値
		valueAIN1FwExpctd = 1 # high
		valueAIN2FwExpctd = 0 # low
		valueAIN1NuExpctd = 0 # low
		valueAIN2NuExpctd = 0 # low

		# ターゲット生成
		motor = Motor(PIN_AIN1, PIN_AIN2, pwm=False)
		ain1_pin = Device.pin_factory.pin(PIN_AIN1)
		ain2_pin = Device.pin_factory.pin(PIN_AIN2)

		# 実際値
		motor.forward()
		sleep(0.1)                
		valueAIN1Actual = ain1_pin.state
		valueAIN2Actual = ain2_pin.state

		# 評価
		self.assertEqual(valueAIN1Actual,valueAIN1FwExpctd)
		self.assertEqual(valueAIN2Actual,valueAIN2FwExpctd)

		# 実際値
		motor.stop()
		sleep(0.1)                
		valueAIN1Actual = ain1_pin.state
		valueAIN2Actual = ain2_pin.state

		# 評価
		try:
			self.assertEqual(valueAIN1Actual,valueAIN1NuExpctd)
			self.assertEqual(valueAIN2Actual,valueAIN2NuExpctd)
			sleep(0.1)
		finally:
			motor.close()

	def test_backward(self):
		""" 後退テスト """
		# 接続ピン
		PIN_AIN1 = 6
		PIN_AIN2 = 5

		# 期待値
		valueAIN1BwExpctd = 0 # low
		valueAIN2BwExpctd = 1 # high
		valueAIN1NuExpctd = 0 # low
		valueAIN2NuExpctd = 0 # low

		# ターゲット生成
		motor = Motor(PIN_AIN1, PIN_AIN2, pwm=False)
		ain1_pin = Device.pin_factory.pin(PIN_AIN1)
		ain2_pin = Device.pin_factory.pin(PIN_AIN2)

		# 実際値
		motor.backward()
		sleep(0.1)                
		valueAIN1Actual = ain1_pin.state
		valueAIN2Actual = ain2_pin.state

		try:
			# 評価
			self.assertEqual(valueAIN1Actual,valueAIN1BwExpctd)
			self.assertEqual(valueAIN2Actual,valueAIN2BwExpctd)

			# 実際値
			motor.stop()
			sleep(0.1)
			valueAIN1Actual = ain1_pin.state
			valueAIN2Actual = ain2_pin.state

			# 評価
			self.assertEqual(valueAIN1Actual,valueAIN1NuExpctd)
			self.assertEqual(valueAIN2Actual,valueAIN2NuExpctd)
			sleep(0.1)
		finally:
			# 終了
			motor.close()

if __name__ == '__main__':
	# デフォルトのピンファクトリーをモックに設定
	Device.pin_factory = MockFactory()
	# ユニットテスト呼び出し
	unittest.main()
