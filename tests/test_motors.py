import unittest
from gpiozero.pins.mock import MockFactory
from gpiozero import Device, Motor, LED
from time import sleep

class TestMotor(unittest.TestCase):

	def test_construction(self):
		# Pin assignemnt
		PIN_AIN1 = 6
		PIN_AIN2 = 5

		# Expected values
		valueAIN1Expctd = 0 # low
		valueAIN2Expctd = 0 # low

		# Construction of target
		motor = Motor(PIN_AIN1, PIN_AIN2, pwm=False)
		ain1_pin = Device.pin_factory.pin(PIN_AIN1)
		ain2_pin = Device.pin_factory.pin(PIN_AIN2)

		# Actual values
		valueAIN1Actual = ain1_pin.state
		valueAIN2Actual = ain2_pin.state

		# Evaluation
		self.assertEqual(valueAIN1Actual,valueAIN1Expctd)
		self.assertEqual(valueAIN2Actual,valueAIN2Expctd)

		# Destruction
		sleep(0.1)
		motor.__del__()

	def test_forward(self):
		# Pin assignemnt
		PIN_AIN1 = 6
		PIN_AIN2 = 5

		# Expected values
		valueAIN1FwExpctd = 1 # high
		valueAIN2FwExpctd = 0 # low
		valueAIN1NuExpctd = 0 # low
		valueAIN2NuExpctd = 0 # low

		# Construction of target
		motor = Motor(PIN_AIN1, PIN_AIN2, pwm=False)
		ain1_pin = Device.pin_factory.pin(PIN_AIN1)
		ain2_pin = Device.pin_factory.pin(PIN_AIN2)

		# Actual values
		motor.forward()
		sleep(0.1)                
		valueAIN1Actual = ain1_pin.state
		valueAIN2Actual = ain2_pin.state

		# Evaluation
		self.assertEqual(valueAIN1Actual,valueAIN1FwExpctd)
		self.assertEqual(valueAIN2Actual,valueAIN2FwExpctd)

		# Actual values
		motor.stop()
		sleep(0.1)                
		valueAIN1Actual = ain1_pin.state
		valueAIN2Actual = ain2_pin.state

		# Evaluation
		self.assertEqual(valueAIN1Actual,valueAIN1NuExpctd)
		self.assertEqual(valueAIN2Actual,valueAIN2NuExpctd)

		# Destruction
		sleep(0.1)
		motor.__del__()

	def test_backward(self):
		# Pin assignemnt
		PIN_AIN1 = 6
		PIN_AIN2 = 5

		# Expected values
		valueAIN1BwExpctd = 0 # low
		valueAIN2BwExpctd = 1 # high
		valueAIN1NuExpctd = 0 # low
		valueAIN2NuExpctd = 0 # low

		# Construction of target
		motor = Motor(PIN_AIN1, PIN_AIN2, pwm=False)
		ain1_pin = Device.pin_factory.pin(PIN_AIN1)
		ain2_pin = Device.pin_factory.pin(PIN_AIN2)

		# Actual values
		motor.backward()
		sleep(0.1)                
		valueAIN1Actual = ain1_pin.state
		valueAIN2Actual = ain2_pin.state

		# Evaluation
		self.assertEqual(valueAIN1Actual,valueAIN1BwExpctd)
		self.assertEqual(valueAIN2Actual,valueAIN2BwExpctd)

		# Actual values
		motor.stop()
		sleep(0.1)
		valueAIN1Actual = ain1_pin.state
		valueAIN2Actual = ain2_pin.state

		# Evaluation
		self.assertEqual(valueAIN1Actual,valueAIN1NuExpctd)
		self.assertEqual(valueAIN2Actual,valueAIN2NuExpctd)

		# Destruction
		sleep(0.1)
		motor.__del__()

if __name__ == '__main__':
	# Set the default pin factory to a mock factory
	Device.pin_factory = MockFactory()
	unittest.main()
