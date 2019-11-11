#!/usr/bin/python3
# coding: UTF-8
"""
ライントレース Model In the Loop Simulation (MILS)

プロパティ

- コースデータ（白黒画像）
- サンプリングレート（秒）
- ライントレーサー
  - 制御：　フォトリフレクタ入力　-> [制御モジュール] -> モーター制御信号
  - 構成：　センサ位置（固定）、モータ特性（固定）
  - 状態：　座標、方向、速度、加速度
  - 振舞：　センシング、移動

機能

- コース表示
- ライントレーサー表示
- フォトリフレクタへの白黒情報を提供
- ライントレーサー位置情報の取得

「電子情報通信設計製図」新潟大学工学部工学科電子情報通信プログラム
"""
import pygame
import sys
import transitions

WHITE = (255, 255, 255)
BLACK = (  0,   0,   0)

class LFControler:
    """ ライントレース制御クラス 
        
        ライントレース制御アルゴリズムを実装する。

        入力　フォトリフレクの値 [0,1]x4
        出力　モーター制御信号 [-1,1]x2
    """
    pass

class LFPhisicalModel:
    """ ライントレーサー物理モデルクラス 
        
        ライントレーサーの物理モデを構築する。

        入力　モーター制御信号 [-1,1]x2        
        出力　フォトリフレクタの値 [0,1]x4 
    """    
    pass

class LFMils:
    """ ライントレースMILSクラス """

    def __init__(self,freq):
        self._clock = pygame.time.Clock()
        self._freq = freq

    def run(self):

        pygame.init()
        pygame.display.set_caption('ライントレース・シミュレーター')
        screen = pygame.display.set_mode((800,600))
        screen.fill(WHITE)

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            pygame.display.update()
            self._clock.tick(self._freq)

def main():
    mils = LFMils(freq = 10)
    mils.run()

if __name__ == '__main__':
    main()