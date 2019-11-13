#!/usr/bin/python3
# coding: UTF-8
"""
ライントレース Model In the Loop Simulation (MILS)

説明

　コースデータは画像(PNGやJPG)として準備してください。
　制御アルゴリズムの変更についてはLFController クラスを編集してください。
　物理モデルの変更についてはLFPhysicalModel クラスを編集してください。

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

準備

 $ sudo apt-get install python3-pygame
 $ sudo apt-get install python3-transitions

「電子情報通信設計製図」新潟大学工学部工学科電子情報通信プログラム
"""
from transitions import Machine
import pygame
import sys
import math

# コースデータ画像
COURSE_IMG = 'lfcourse.png'

# メイン関数
def main():
    # コースデータの読み込み
    course = LFCourse(COURSE_IMG)

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
    mpp = ((120,-40), (110,-20), (110,20), (120,40))
    lf = LFPhysicalModel(course, weight = 200, mntposprs = mpp)

    # MILSオブジェクトのインスタンス生成
    mils = LFModelInTheLoopSimulation(lf)

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
    
    SHAFT_LENGTH = 50 # mm
    TIRE_DIAMETER = 20 # mm

    BLUE = (  0,  0, 255)

    def __init__(self, \
        course, \
        weight = 200, \
        mntposprs =  ((120,-40), (110,-20), (110,20), (120,40)) \
        ):
        self._weight = weight
        self._mntposprs = mntposprs
        self._course = course
        self._x = self.SHAFT_LENGTH + 10 # mm
        self._y = self.SHAFT_LENGTH + 10 # mm

    @property
    def course(self):
        return self._course        

    def set_position_mm(self,x,y):
        self._x = x # mm
        self._y = y # mm

    def move_px(self,dx_px,dy_px):
        res = self._course.resolution # mm/pixel        
        self._x = self._x + dx_px*res # mm
        self._y = self._y + dy_px*res # mm        

    def set_angle(self,angle):
        self._angle = angle # rad
    
    def set_interval(self,interval):
        self._interval = interval

    def draw_body(self,screen):
        #pos = [int(self._x/res) , int(self._y/res)] # pixels
        #rad = int(self.SHAFT_LENGTH/res)
        #pygame.draw.circle(screen, self.BLUE, pos, rad)
        rect = self.get_rect_px()
        pygame.draw.rect(screen, self.BLUE, rect) 

    def get_rect_px(self):
        res = self._course.resolution # mm/pixel
        pos_cx_mm = self._x # pixel
        pos_cy_mm = self._y # pixel
        car_width_mm = 120 # 車体幅 in mm
        car_length_mm = 160 # 車体長 in mm
        pos_topleft_x_px = int(pos_cx_mm/res-self.SHAFT_LENGTH)+10
        pos_topleft_y_px = int(pos_cy_mm/res-self.SHAFT_LENGTH)+10
        car_width_px = car_width_mm/res # 車体幅 in pixel  
        car_length_px = car_length_mm/res  # 車体長 in mm        
        rect = [pos_topleft_x_px,pos_topleft_y_px, car_length_px, car_width_px]
        return rect

    def drive(self, left, right):
        pass

    def sense(self):
        return []

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
    """ ライントレースMILSクラス """

    # 色の定義
    WHITE = (255, 255, 255)
    BLACK = (  0,   0,   0)
    GREEN = (  0, 255,   0)    

    # シミュレータ状態の定義
    STATES = ('sinit','slocate','srotate','swait','srun','squit')

    # シミュレータ遷移の定義
    #
    #               +-----------------------+
    #               ↓                       |
    # (sinit) → (slocate) ⇔ (srotate) → (swait) ⇔ (srun)
    #               |            |          |          |                                    
    #               +------------+----+-----+----------+
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

    def run(self):

        pygame.init()
        pygame.display.set_caption('ライントレース・シミュレーター')
        font = pygame.font.Font(None, 40)

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            # 背景描画
            self._screen.blit(self._course.image,[0, 0])

            key = pygame.key.get_pressed()
            if self.state == 'sinit': 
                # 初期化設定
                flag_drag = False

                # 無条件で遷移
                self.initialized()

            if self.state == 'slocate': 
                # 位置設定
                mouseX, mouseY = pygame.mouse.get_pos()
                txt1 = '{},{}'.format(mouseX, mouseY)
                mBtn1, mBtn2, mBtn3 = pygame.mouse.get_pressed()
                txt2 = '{}:{}:{}'.format(mBtn1,mBtn2,mBtn3)
                # マウスポインタが車体上かつ左クリックならば
                # 車体をドラッグ
                rect = self._linefollower.get_rect_px()
                isMouseIn = rect[0] < mouseX and mouseX < rect[0]+rect[2] and \
                    rect[1] < mouseY and mouseY < rect[1]+rect[3]
                if (isMouseIn or flag_drag) and mBtn1 == 1:
                    if not flag_drag:
                        preX, preY = mouseX, mouseY
                        flag_drag = True
                    dx_px, dy_px = mouseX - preX, mouseY - preY
                    self._linefollower.move_px(dx_px,dy_px)                    
                    preX, preY = mouseX, mouseY
                else:
                    flag_drag = False
                    msg = font.render('Out of car', True, self.GREEN)

                msg = font.render(txt1 +' '+ txt2, True, self.GREEN)

                # 設定終了判定
                if key[pygame.K_l] == 1: # l 位置設定終了
                    # 条件付き遷移
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

            #self._screen.fill(self.WHITE)
            self._linefollower.draw_body(self._screen)
            sur = font.render(self.state, True, self.BLACK)
            self._screen.blit(sur,[int(self._width/2.0),int(self._height/2.0)])
            self._screen.blit(msg,[20,self._height-40])          

            pygame.display.update()
            self._clock.tick(self._fps)

if __name__ == '__main__':
    main()