import unittest
from gpiozero.pins.mock import MockFactory
from gpiozero import Device, Button, LED
from time import sleep

class TestPhotoRef(unittest.TestCase):

        def test_construction(self):
                # Pin assignemnt
                PIN_LD = 23
                PIN_PR = 10

                # Construction of peripherals
                led = LED(PIN_LD)

                # Expected values
                valueLDExpctd = False # black

                # Construction of target
                photoref  = Button(PIN_PR,active_state=True,pull_up=None)

                # Connect
                led.source = photoref

                # Actual values
                valueLDActual = led.value

                # Evaluation
                self.assertEqual(valueLDActual,valueLDExpctd)

                # Destruction
                sleep(0.1)
                led.__del__()
                photoref.__del__()

        def test_drive(self):
                # Pin assignemnt
                PIN_LD = 23
                PIN_PR = 10

                # Construction of peripherals
                led = LED(PIN_LD)

                # Expected values
                highLDExpctd = True # white
                lowLDExpctd = False # black

                # Construction of targert
                photoref  = Button(PIN_PR,active_state=True,pull_up=None)
                photoref_pin = Device.pin_factory.pin(PIN_PR)

                # Connect devices
                led.source = photoref

                # Drive photoref to high (white)
                photoref_pin.drive_high()
                sleep(0.1)
                highLDActual = led.value

                # Drive photoref to low (black)
                photoref_pin.drive_low()
                sleep(0.1)
                lowLDActual = led.value

                # Evaluation
                self.assertEqual(highLDActual,highLDExpctd)
                self.assertEqual(lowLDActual,lowLDExpctd)

                # Destraction
                sleep(0.1)
                led.__del__()
                photoref.__del__()

        def test_callback(self):
                # Pin assignemnt
                PIN_LD = 23
                PIN_PR = 10

                # Construction of peripherals
                led = LED(PIN_LD)

                # Expected values
                highLDExpctd = True # white
                lowLDExpctd = False # black

                # Construction of targert
                photoref  = Button(PIN_PR,active_state=True,pull_up=None)
                photoref_pin = Device.pin_factory.pin(PIN_PR)

                # Set callback function
                photoref.when_pressed = led.on
                photoref.when_released = led.off

                # Drive photoref to high (white)
                photoref_pin.drive_high()
                sleep(0.1)
                highLDActual = led.value

                # Drive photoref to low (black)
                photoref_pin.drive_low()
                sleep(0.1)
                lowLDActual = led.value

                # Evaluation
                self.assertEqual(highLDActual,highLDExpctd)
                self.assertEqual(lowLDActual,lowLDExpctd)

                # Destraction
                sleep(0.1)
                led.__del__()
                photoref.__del__()

if __name__ == '__main__':
        # Set the default pin factory to a mock factory
        Device.pin_factory = MockFactory()
        unittest.main()
