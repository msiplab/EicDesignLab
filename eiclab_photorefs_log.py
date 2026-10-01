# coding: UTF-8
"""
フォトリフレクタの検出状態のログ保存（ループ版）

「電子情報通信設計製図」新潟大学工学部工学科電子情報通信プログラム

フォトリフレクタの検出状態を一定周期で読み取り，経過時間とともに CSV ファイルに保存する．
プログラムの実行状況は logging モジュールでログファイルに記録する．

Mock ピンで試す場合:
	$ GPIOZERO_PIN_FACTORY=mock python3 eiclab_photorefs_log.py

参考サイト
	https://docs.python.org/ja/3/library/logging.html
	https://docs.python.org/ja/3/library/csv.html
"""
import csv
import logging
from datetime import datetime
from time import sleep, monotonic
from gpiozero import Button

def main():
	""" メイン関数 """
	# 接続ピン
	PIN_PR = [ 10, 9, 11, 8 ]
	# 記録周期 [s] と記録時間 [s]
	PERIOD_S = 0.1
	DURATION_S = 10.0

	# 保存するファイル名（実行開始の日時を含める）
	stamp = datetime.now().strftime('%Y%m%d_%H%M%S')
	csvname = 'photorefs_{}.csv'.format(stamp)
	logname = 'photorefs_{}.log'.format(stamp)

	# 実行ログの設定（日時，重要度，メッセージをファイルに記録）
	logging.basicConfig(filename=logname, level=logging.INFO, encoding='utf-8',
		format='%(asctime)s %(levelname)s %(message)s')
	logging.info('記録開始（周期 %.2f s，時間 %.1f s）', PERIOD_S, DURATION_S)

	# フォトリフレクタ（複数）設定（ボタンとして）
	photorefs = [ Button(pin, active_state=True, pull_up=None) for pin in PIN_PR ]

	try:
		with open(csvname, 'w', newline='', encoding='utf-8') as f:
			writer = csv.writer(f)
			# 見出し行（1: White，0: Black）
			writer.writerow([ 'time_s' ] + [ 'pr{}'.format(idx+1) for idx in range(len(PIN_PR)) ])
			lost = False
			t0 = monotonic()
			t = 0.0
			while t < DURATION_S:
				values = [ int(pr.value) for pr in photorefs ]
				writer.writerow([ '{:.3f}'.format(t) ] + values)
				# 全てのフォトリフレクタが黒を検出したら警告を記録
				if sum(values) == 0 and not lost:
					logging.warning('t=%.3f s: 全てのフォトリフレクタが黒を検出', t)
				lost = (sum(values) == 0)
				sleep(PERIOD_S)
				t = monotonic() - t0
	except KeyboardInterrupt:
		logging.info('Ctrl+C により中断')
	finally:
		for pr in photorefs:
			pr.close()
		logging.info('記録終了（%s）', csvname)
	print('{} と {} に保存しました'.format(csvname, logname))

if __name__ == '__main__':
	main()
