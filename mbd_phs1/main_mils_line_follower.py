#!/usr/bin/python3
# coding: UTF-8
"""
ライントレース Model In the Loop Simulation (MILS)
（β版）

説明

　コースデータは画像(PNGやJPG)として準備してください。
  プログラムと同じフォルダに置くかフォルダを指定してください。

　制御アルゴリズムの変更についてはLFController クラスの
　prs2mtrs() メソッドを編集してください。
　
　物理モデルの変更についてはLFPhysicalModel クラスの
  drive() メソッドを編集してください。

プロパティ

- コースデータ（モノクロ画像）
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

準備 (Raspbian の場合)

 $ sudo apt-get install python3-numpy
 $ sudo apt-get install python3-scipy
 $ sudo apt-get install python3-pygame
 $ sudo apt-get install python3-transitions

「電子情報通信設計製図」新潟大学工学部工学科電子情報通信プログラム

All rights revserved (c) Shogo MURAMATSU
"""
from mils_line_follower_body import LFPhysicalModel
from transitions import Machine
import pygame
import sys
import math

# 色の定義
WHITE  = (255, 255, 255)
BLACK  = (  0,   0,   0)
GREEN  = (  0, 255,   0)    
BLUE   = (  0,   0, 255)
YELLOW = (  255, 128, 0)

# コースデータ画像
#COURSE_IMG = 'lfcourse.png'
#COURSE_RES = 1.25
COURSE_IMG = 'finalcourse.png'
COURSE_RES = 2.5

# メイン関数
def main():
    """ メイン関数
        
        フォトリフレクタの配置や車体の重さなどを設定して、
        シミュレータを走らせています。

        車体の大きさについては、LFPhysicalModelクラスで定数として
        設定しています。重心は明示的に考慮していません。
        比例係数の値を変える形で実装しています。
        より現実に近い物理モデルは各自で検討してください。

    """

    # コースデータの読み込み
    course = LFCourse(COURSE_IMG,res=COURSE_RES)

    # シャフト中心(+)からのフォトリフレクタ(*)の
    # 相対座標[mm]
    #  
    #       --|--          * pr1 (dx1,dy1)
    #         |           * pr2 (dx2,dy2)       
    #  (0,0)  + -------------            → x
    #   ↓     |           * pr3 (dx3,dy3)       
    #   y   --|--          * pr4 (dx4,dy4)
    #
    # ((dx1,dy1), (dx2,dy2), (dx3,dy3), (dx4,dy4)) 
    lf_mount_pos_prf = ((120,-60), (100,-20), (100,20), (120,60)) # mm
    
    # 車体の重さ
    lf_weight = 100 # g（グラム）

    # 車体のインスタンス生成
    lf = LFPhysicalModel(course, \
        weight = lf_weight, \
        mntposprs = lf_mount_pos_prf)

    # MILSオブジェクトのインスタンス生成
    mils = LFModelInTheLoopSimulation(lf)

    # シミュレーションの実行
    mils.run()

class LFCourse:
    """ コースデータ 
    
        ライントレース用のコースデータを保持する。

        res [mm/pixel]

    """
    def __init__(self,filename,res=1.25):
        self._filename = filename
        self._width  = 640
        self._height = 360
        self._res = res
        image = pygame.image.load(self._filename)
        self._image = pygame.transform.scale(image,(640,360))

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height

    @property
    def resolution(self):
        return self._res

    @property
    def realwidth(self):
        return self._width*self._res

    @property
    def realheight(self):
        return self._height*self._res

    @property
    def image(self):
        return self._image

class LFModelInTheLoopSimulation(object):
    """ ライントレースMILSクラス 
    
        シミュレーションの状態遷移を管理
    
    """

    # シミュレータ状態の定義
    STATES = ('sinit','slocate','srotate','swait','srun','squit')

    # シミュレータ遷移の定義
    #
    #               +-------------------------------+
    #               ↓                           　  ↑
    # (sinit) → (slocate) → (srotate) → (swait) → (srun)
    #               |           |          |        |
    #               +-----------+-----+----+--------+
    #                                 ↓
    #                              (squit) 
    #
    # sinit:   初期設定*
    # slocate: ライントレーサー位置設定
    # srotate: ライントレーサー角度設定
    # swait:   走行準備
    # srun:    走行
    # squit:   終了
    #
    TRANSITIONS = (
        {'trigger': 'initialized', 'source': 'sinit',   'dest': 'slocate' },
        {'trigger': 'located',     'source': 'slocate', 'dest': 'srotate', 'after': 'lflag_false' },        
        {'trigger': 'rotated',     'source': 'srotate', 'dest': 'swait',   'after': 'rflag_false' },
        {'trigger': 'start',       'source': 'swait',   'dest': 'srun' },
        {'trigger': 'stop',        'source': 'srun',    'dest': 'slocate', 'after': 'reset' },                
        {'trigger': 'quit',        'source': 'slocate', 'dest': 'squit',   'after': 'close'  },
        {'trigger': 'quit',        'source': 'srotate', 'dest': 'squit',   'after': 'close'  },
        {'trigger': 'quit',        'source': 'swait',   'dest': 'squit',   'after': 'close'  },
        {'trigger': 'quit',        'source': 'srun',    'dest': 'squit',   'after': 'close'  }
    )

    def __init__(self, linefollower, fps = 10):

        self._clock = pygame.time.Clock()
        self._fps = fps

        # スクリーン設定
        self._linefollower = linefollower
        self._course = self._linefollower.course
        self._width  = self._course.width
        self._height = self._course.height
        self._screen = pygame.display.set_mode((self._width,self._height))

        # 状態遷移機械(SFM)の設定
        self._sfm = Machine(\
            model=self, \
            states=self.STATES, \
            initial=self.STATES[0], \
            transitions=self.TRANSITIONS, \
            ignore_invalid_triggers=True
        )
        self._flag_drag = False
        self._flag_rot  = False

    def run(self):

        pygame.init()
        pygame.display.set_caption('ライントレース・シミュレーター')
        font40 = pygame.font.Font(None, 40)
        font20 = pygame.font.Font(None, 20)        

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit()

            # 背景描画
            self._screen.blit(self._course.image,[0, 0])

            # 位置設定
            mouseX, mouseY = pygame.mouse.get_pos()
            mBtn1, mBtn2, mBtn3 = pygame.mouse.get_pressed()
            #txt1 = '{},{}'.format(mouseX, mouseY)
            #txt2 = '{}:{}:{}'.format(mBtn1,mBtn2,mBtn3)

            key = pygame.key.get_pressed()
            if self.state == 'sinit': 
                msg = 'Initializing　...'
                # 初期化設定
                self._linefollower.set_position_mm(60,60) # mm
                self.initialized()

            msg = font20.render('', True, BLUE) 
            if self.state == 'slocate': 
                msg = 'Please locate the car with mouse.'
                # マウスポインタが車体上かつ左クリックならば
                # 車体をドラッグ
                rect = self._linefollower.get_rect_px()
                isMouseIn = rect[0] < mouseX and mouseX < rect[0]+rect[2] and \
                    rect[1] < mouseY and mouseY < rect[1]+rect[3]
                if (self._flag_drag or isMouseIn) and mBtn1 == 1:
                    if not self._flag_drag:
                        preX, preY = mouseX, mouseY
                        self._flag_drag = True
                    dx_px, dy_px = mouseX - preX, mouseY - preY
                    self._linefollower.move_px(dx_px,dy_px)                    
                    preX, preY = mouseX, mouseY
                elif self._flag_drag: # 設定終了判定
                    self.located()

            if self.state == 'srotate': 
                msg = 'Please rotate the car with mouse.'                
                # 左クリックならば車体を回転
                if mBtn1 == 1:
                    if not self._flag_rot:
                        center_px = self._linefollower.get_center_px()
                        self._flag_rot = True
                    dx_px = mouseX - center_px[0]
                    dy_px = mouseY - center_px[1]
                    angle = math.atan2(dy_px,dx_px)
                    self._linefollower.rotate(angle)
                elif self._flag_rot and mBtn1 == 0: # 設定終了判定
                    self.rotated()

            if self.state == 'swait':
                msg = 'Please click to run the car.'                                
                if mBtn1 == 1:
                    if not self._flag_drag:
                        self._flag_drag = True
                elif self._flag_drag:
                    self._flag_drag = False
                    self.start()

            if self.state == 'srun':
                msg = 'Please click to stop the car.'                                                
                if mBtn1 == 1:
                    self.stop()
                else:
                    self._linefollower.drive(self._fps)

            # キーボード入力
            if key[pygame.K_ESCAPE] == 1: # [ESP] ストップ
                self.stop()
            if key[pygame.K_SPACE] == 1: # [SPACE] スタート
                self.start()                                                                
            if key[pygame.K_q] == 1: # [q] 終了
                self.quit()                                                                                                

            # 画面描画
            self._linefollower.draw_body(self._screen)
            sur = font20.render(msg, True, BLUE)            
            self._screen.blit(sur,[10,self._height-20])          
            pygame.display.update()

            # クロック
            self._clock.tick(self._fps)

    def lflag_false(self):
        self._flag_drag = False

    def rflag_false(self):
        self._flag_rot = False    

    def reset(self):
        self._linefollower.reset()

    def close(self):
        pygame.quit()
        sys.exit()

if __name__ == '__main__':
    main()