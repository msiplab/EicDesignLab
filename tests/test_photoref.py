# coding: UTF-8
"""
	Mock テスト

	gpiozero と pigpio の導入が必要です。

	Raspberry Pi OS:
	
	$ sudo apt-get update
	$ sudo apt-get install python3-gpiozero python3-pigpio

	Windows:

	> py -m pip install gpiozero pigpio


	All rights revserved 2019-2022 (c) Shogo MURAMATSU
"""
import unittest
from gpiozero.pins.mock import MockFactory
from gpiozero import Device, Button, LED
from time import sleep

class TestPhotoRef(unittest.TestCase):
    """ フォトリフレクタテストクラス """
 
    def setUp(self):
        """ テスト前処理 """
        pass 
 
    def tearDown(self):
        """ テスト後処理 """
        pass
        
    def test_construction(self):
        """ 生成テスト """
        # 接続ピン
        PIN_LD = 23
        PIN_PR = 10

        # 周辺設定
        led = LED(PIN_LD)

        # 期待値
        valueLDExpctd = False # black

        # ターゲット生成
        photoref  = Button(PIN_PR,active_state=True,pull_up=None)

        # 接続
        led.source = photoref

        # 実際値
        valueLDActual = led.value

        # 評価
        try:
            self.assertEqual(valueLDActual,valueLDExpctd)
            sleep(0.1)
        finally:
            led.close()
            photoref.close()

    def test_drive(self):
        """ 駆動テスト """
        # 接続ピン
        PIN_LD = 23
        PIN_PR = 10

        # 周辺設定
        led = LED(PIN_LD)

        # 期待値
        highLDExpctd = True # white
        lowLDExpctd = False # black

        # ターゲット生成
        photoref  = Button(PIN_PR,active_state=True,pull_up=None)
        photoref_pin = Device.pin_factory.pin(PIN_PR)

        # 接続
        led.source = photoref

        # Highでフォトリフレクタを駆動（白）
        photoref_pin.drive_high()
        sleep(0.1)
        highLDActual = led.value

        # Lowでフォトリフレクタを駆動（黒）
        photoref_pin.drive_low()
        sleep(0.1)
        lowLDActual = led.value

        # 評価
        try:
            self.assertEqual(highLDActual,highLDExpctd)
            self.assertEqual(lowLDActual,lowLDExpctd)
            sleep(0.1)
        finally:
            led.close()
            photoref.close()

    def test_callback(self):
        """ コールバックテスト """
        # 接続ピン
        PIN_LD = 23
        PIN_PR = 10

        # 周辺設定
        led = LED(PIN_LD)

        # 期待値
        highLDExpctd = True # white
        lowLDExpctd = False # black

        # ターゲット生成
        photoref  = Button(PIN_PR,active_state=True,pull_up=None)
        photoref_pin = Device.pin_factory.pin(PIN_PR)

        # コールバック関数設定
        photoref.when_pressed = led.on
        photoref.when_released = led.off

        # Highでフォトリフレクタを駆動（白）
        photoref_pin.drive_high()
        sleep(0.1)
        highLDActual = led.value

        # Low でフォトリフレクタを駆動（黒）
        photoref_pin.drive_low()
        sleep(0.1)
        lowLDActual = led.value

        # 評価
        try:
            self.assertEqual(highLDActual,highLDExpctd)
            self.assertEqual(lowLDActual,lowLDExpctd)
            sleep(0.1)
        finally:
            led.close()
            photoref.close()

if __name__ == '__main__':
    # デフォルトのピンファクトリーをモックに設定
    Device.pin_factory = MockFactory()
    # ユニットテスト呼び出し
    unittest.main()
