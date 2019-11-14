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
import numpy as np
import pygame
import sys
import math

# 色の定義
WHITE = (255, 255, 255)
BLACK = (  0,   0,   0)
GREEN = (  0, 255,   0)    
BLUE  = (  0,   0, 255)

# コースデータ画像
COURSE_IMG = 'lfcourse.png'

# フォトリフレクタ数
NUM_PHOTOREFS = 4

# メイン関数
def main():
    # コースデータの読み込み
    course = LFCourse(COURSE_IMG)

    # 制御モデルのインスタンス生成
    controller = LFController()

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
    lf = LFPhysicalModel(course, controller, weight = 200, mntposprs = mpp)

    # MILSオブジェクトのインスタンス生成
    mils = LFModelInTheLoopSimulation(lf)

    # シミュレーションの実行
    mils.run()

def clamped(v):
    return max(-1,min(1,v))

class LFController:
    """ ライントレース制御クラス 
        
        ライントレース制御アルゴリズムを実装する。

        入力　フォトリフレクの値 [0,1]x4
        出力　モーター制御信号 [-1,1]x2
    """
    
    def __init__(self,prs = None):
        self._prs = prs

    def prs2mtrs(self):
        """ フォトリフレクタ→モータ制御 """

        # フォトリフレクタの値を読み出しとベクトル化
        vec_x = np.array([ self._prs[idx].value \
            for idx in range(NUM_PHOTOREFS) ])

        # モーター制御の強度値を計算（ここを工夫）
        mat_A = np.array([[0.4, 0.3, 0.2, 0.1],\
            [0.1, 0.2, 0.3, 0.4]])
        vec_y = np.dot(mat_A,vec_x)

        # 出力範囲を[-1,1]に直して出力
        left, right = vec_y[0], vec_y[1]

        return (clamped(left),clamped(right))

    @property
    def photorefs(self):
        return self._prs

    @photorefs.setter
    def photorefs(self,prs):
        self._prs = prs

class LFPhotoReflector:
    """ フォトリフレクタクラス """

    def __init__(self,value = 0.0):
        self._value = value
    
    @property
    def value(self):
        return self._value
    
    @value.setter
    def value(self,value):
        self._value = value

class LFPhysicalModel:
    """ ライントレーサー物理モデルクラス 
        
        ライントレーサーの物理モデルを実装する。

        入力　モーター制御信号 [-1,1]x2        
        出力　フォトリフレクタの値 [0,1]x4 
    """    
    
    SHAFT_LENGTH = 50 # mm
    TIRE_DIAMETER = 20 # mm

    def __init__(self, \
        course, \
        controller, \
        weight = 200, \
        mntposprs =  ((120,-40), (110,-20), (110,20), (120,40)) \
        ):

        self._course = course
        self._controller = controller
        self._weight = weight
        self._mntposprs = mntposprs
        self._x_mm = self.SHAFT_LENGTH + 10 # mm
        self._y_mm = self.SHAFT_LENGTH + 10 # mm
        self._angle = 0 # rad

        # 制御機へのフォトリフレクタ設定
        self._prs = [ LFPhotoReflector() \
            for idx in range(NUM_PHOTOREFS)]
        for idx in range(NUM_PHOTOREFS):
            self._prs[idx].value = 0.0
        self._controller.photorefs = self._prs

    @property
    def course(self):
        return self._course
    
    @property
    def angle(self):
        return self._angle

    def set_position_mm(self,x,y):
        self._x_mm = x # mm
        self._y_mm = y # mm

    def move_px(self,dx_px,dy_px):
        res = self._course.resolution # mm/pixel        
        self._x_mm = self._x_mm + dx_px*res # mm
        self._y_mm = self._y_mm + dy_px*res # mm   

    def rotate(self,angle):
        self._angle = angle # rad

    def set_interval(self,interval):
        self._interval = interval

    def draw_body(self,screen):
        #
        rect = np.asarray(self.get_rect_px())
        center = np.asarray(self.get_center_px())
        #
        apos00 = np.dot([[1,0,0,0],[0,1,0,0]],rect) - center
        apos10 = np.dot([[1,0,0,0],[0,1,0,1]],rect) - center
        apos01 = np.dot([[1,0,1,0],[0,1,0,0]],rect) - center
        apos11 = np.dot([[1,0,1,0],[0,1,0,1]],rect) - center
        #
        angle = self._angle
        rotate = np.asarray([
            [ np.cos(angle), -np.sin(angle) ],
            [ np.sin(angle),  np.cos(angle) ]
        ])
        apos00 = rotate.dot(apos00)
        apos10 = rotate.dot(apos10)
        apos01 = rotate.dot(apos01)
        apos11 = rotate.dot(apos11)
        #
        pos00 = (apos00 + center).tolist()
        pos10 = (apos10 + center).tolist()
        pos01 = (apos01 + center).tolist()
        pos11 = (apos11 + center).tolist()
        #
        pygame.draw.polygon(screen, BLUE, [pos00,pos10,pos01,pos11],0)

        # TODO: 車体，フォトリフレクタ描画

    def get_rect_px(self):
        res = self._course.resolution # mm/pixel
        pos_cx_mm = self._x_mm # pixel
        pos_cy_mm = self._y_mm # pixel
        car_width_mm = 120 # 車体幅 in mm
        car_length_mm = 160 # 車体長 in mm
        pos_topleft_x_px = int(pos_cx_mm/res-self.SHAFT_LENGTH)+10
        pos_topleft_y_px = int(pos_cy_mm/res-self.SHAFT_LENGTH)+10
        car_width_px = car_width_mm/res # 車体幅 in pixel  
        car_length_px = car_length_mm/res  # 車体長 in mm        
        rect = [pos_topleft_x_px,pos_topleft_y_px, car_length_px, car_width_px]
        return rect

    def get_center_px(self):
        res = self._course.resolution # mm/pixel        
        cx_mm = self._x_mm # pixel
        cy_mm = self._y_mm # pixel
        cx_px = cx_mm/res
        cy_px = cy_mm/res
        return [cx_px,cy_px]

    def drive(self):
        left, right = 0, 0
        self._x_mm = self._x
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

    # シミュレータ状態の定義
    STATES = ('sinit','slocate','srotate','swait','srun','squit')

    # シミュレータ遷移の定義
    #
    #               +=======================+
    #               ↓|                    　↑|
    # (sinit) → (slocate) ⇔ (srotate) → (srun)
    #               |           |           | 
    #               +-----------+-----+-----+
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
        {'trigger': 'rotated',     'source': 'srotate', 'dest': 'slocate', 'after': 'rflag_false' },
        {'trigger': 'start',       'source': 'slocate', 'dest': 'srun' },
        {'trigger': 'start',       'source': 'srotate', 'dest': 'srun' },                
        {'trigger': 'stop',        'source': 'srun',    'dest': 'slocate' },                
        {'trigger': 'quit',        'source': 'slocate', 'dest': 'squit', 'after': 'close'  },
        {'trigger': 'quit',        'source': 'srotate', 'dest': 'squit', 'after': 'close'  },
        {'trigger': 'quit',        'source': 'swait',   'dest': 'squit', 'after': 'close'  },
        {'trigger': 'quit',        'source': 'srun',    'dest': 'squit', 'after': 'close'  }
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
        font = pygame.font.Font(None, 40)

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit()

            # 背景描画
            self._screen.blit(self._course.image,[0, 0])

            # 位置設定
            mouseX, mouseY = pygame.mouse.get_pos()
            #txt1 = '{},{}'.format(mouseX, mouseY)
            mBtn1, mBtn2, mBtn3 = pygame.mouse.get_pressed()
            #txt2 = '{}:{}:{}'.format(mBtn1,mBtn2,mBtn3)

            key = pygame.key.get_pressed()
            if self.state == 'sinit': 
                # 初期化設定

                # スタート，ストップ，終了

                # 無条件で遷移
                self.initialized()

            msg = font.render('', True, GREEN) 
            if self.state == 'slocate': 
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
                elif self._flag_drag and mBtn1 == 0: # 設定終了判定
                    self.located()

            if self.state == 'srotate': 
                # 左クリックならば車体を回転
                if mBtn1 == 1:
                    if not self._flag_rot:
                        center_px = self._linefollower.get_center_px()
                        angle0 = self._linefollower.angle
                        self._flag_rot = True
                    dx_px = mouseX - center_px[0]
                    dy_px = mouseY - center_px[1]
                    angle = math.atan2(dy_px,dx_px)
                    self._linefollower.rotate(angle0+angle)
                elif self._flag_rot and mBtn1 == 0: # 設定終了判定
                    self.rotated()

            if self.state == 'srun':
                self._linefollower.drive()

            # キーボード入力
            if key[pygame.K_ESCAPE] == 1: # [ESP] ストップ
                self.stop()                                       
            if key[pygame.K_SPACE] == 1: # [SPACE] スタート
                self.start()                                                                
            if key[pygame.K_q] == 1: # [q] 終了
                self.quit()                                                                                                

            # 画面描画
            self._linefollower.draw_body(self._screen)
            sur = font.render(self.state, True, BLACK)
            self._screen.blit(sur,[int(self._width/2.0),int(self._height/2.0)])
            self._screen.blit(msg,[20,self._height-40])          
            pygame.display.update()

            # クロック
            self._clock.tick(self._fps)

    def lflag_false(self):
        self._flag_drag = False

    def rflag_false(self):
        self._flag_rot = False    

    def close(self):
        pygame.quit()
        sys.exit()

if __name__ == '__main__':
    main()