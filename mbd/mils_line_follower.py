#!/usr/bin/python3
# coding: UTF-8
"""
ライントレース Model In the Loop Simulation (MILS)

説明

　コースデータは画像(PNGやJPG)として準備してください。
　制御アルゴリズムの変更についてはLFController クラスを編集してください。
　物理モデルの変更についてはLFPhysicalModel クラスを編集してください。

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

準備

 $ sudo apt-get install python3-pygame
 $ sudo apt-get install python3-transitions

「電子情報通信設計製図」新潟大学工学部工学科電子情報通信プログラム
"""
from transitions import Machine
import pygame
import sys

# コースデータ画像
COURSE_IMG = 'lfcourse.png'

# メイン関数
def main():
    # コースデータの読み込み
    course = LFCourse(COURSE_IMG)

    # MILSオブジェクトのインスタンス生成
    mils = LFModelInTheLoopSimulation(course)

    # シミュレーションの実行
    mils.run()

class LFController:
    """ ライントレース制御クラス 
        
        ライントレース制御アルゴリズムを実装する。

        入力　フォトリフレクの値 [0,1]x4
        出力　モーター制御信号 [-1,1]x2
    """
    pass

class LFPhysicalModel:
    """ ライントレーサー物理モデルクラス 
        
        ライントレーサーの物理モデルを実装する。

        入力　モーター制御信号 [-1,1]x2        
        出力　フォトリフレクタの値 [0,1]x4 
    """    
    pass

class LFCourse:
    """ コースデータ 
    
        ライントレース用のコースデータを保持する。

    """
    def __init__(self,filename):
        self._width  = 800
        self._height = 600

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height        

class LFModelInTheLoopSimulation(object):
    """ ライントレースMILSクラス """

    # 色の定義
    WHITE = (255, 255, 255)
    BLACK = (  0,   0,   0)

    # シミュレータ状態の定義
    STATES = ('sinit','slocate','srotate','swait','srun','squit')

    # シミュレータ遷移の定義
    TRANSITIONS = (
        {'trigger': 'initialized', 'source': 'sinit',   'dest': 'slocate'},
        {'trigger': 'located',     'source': 'slocate', 'dest': 'srotate'},    
        {'trigger': 'rotated',     'source': 'srotate', 'dest': 'swait'  },        
        {'trigger': 'reset',       'source': 'srotate', 'dest': 'slocate'},            
        {'trigger': 'reset',       'source': 'swait',   'dest': 'slocate'},                
        {'trigger': 'start',       'source': 'swait',   'dest': 'srun'   },
        {'trigger': 'stop',        'source': 'srun',    'dest': 'swait'  },
        {'trigger': 'quit',        'source': 'slocate', 'dest': 'squit'  },
        {'trigger': 'quit',        'source': 'srotate', 'dest': 'squit'  },
        {'trigger': 'quit',        'source': 'swait',   'dest': 'squit'  },
        {'trigger': 'quit',        'source': 'srun',    'dest': 'squit'  }            
    )

    def __init__(self, course, fps = 10):

        self._clock = pygame.time.Clock()
        self._fps = fps

        # スクリーン設定
        self._width  = course.width
        self._height = course.height
        self._screen = pygame.display.set_mode((self._width,self._height))
    
        # 状態遷移機械(SFM)の設定
        self._sfm = Machine(\
            model=self, \
            states=self.STATES, \
            initial=self.STATES[0], \
            transitions=self.TRANSITIONS, \
            ignore_invalid_triggers=True
        )

    def run(self):

        pygame.init()
        pygame.display.set_caption('ライントレース・シミュレーター')
        font = pygame.font.Font(None, 40)

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            key = pygame.key.get_pressed()
            if key[pygame.K_i] == 1: # i 初期化終了
                self.initialized()
            if key[pygame.K_l] == 1: # l 位置設定終了
                self.located()
            if key[pygame.K_r] == 1: # r 回転設定終了
                self.rotated()                    
            if key[pygame.K_ESCAPE] == 1: # ESC 位置回転リセット
                self.reset()                                       
            if key[pygame.K_s] == 1: # s スタート
                self.start()                                                                
            if key[pygame.K_t] == 1: # t ストップ
                self.stop()                                                                                
            if key[pygame.K_q] == 1: # q 終了
                self.quit()                                                                                                

            self._screen.fill(self.WHITE)
            sur = font.render(self.state, True, self.BLACK)
            self._screen.blit(sur,[int(self._width/2.0),int(self._height/2.0)])

            pygame.display.update()
            self._clock.tick(self._fps)

if __name__ == '__main__':
    main()