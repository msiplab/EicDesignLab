#!/usr/bin/python3
# coding: UTF-8
"""
　物理モデル

説明

　物理モデルの変更については drive() メソッドを編集してください。

「電子情報通信設計製図」新潟大学工学部工学科電子情報通信プログラム

参考資料

- 三平 満司：「非ホロノミック系のフィードバック制御」計測と制御
　1997 年 36 巻 6 号 p. 396-403

All rights revserved (c) Shogo MURAMATSU
"""
from mils_line_follower_ctrl import LFController
from mils_line_follower_phrf import LFPhotoReflector
from scipy.integrate import odeint
import numpy as np
import pygame

# 色の定義
WHITE  = (255, 255, 255)
BLACK  = (  0,   0,   0)
GREEN  = (  0, 255,   0)    
BLUE   = (  0,   0, 255)
YELLOW = (  255, 128, 0)

# 車体のパラメータ
SHAFT_LENGTH = 50 # mm
TIRE_DIAMETER = 40 # mm

# フォトリフレクタ数
NUM_PHOTOREFS = 4

def rotate_pos(pos,center,angle):
    """ 座標位置の回転 """
    rotmtx = np.asarray([
        [ np.cos(angle), -np.sin(angle) ],
        [ np.sin(angle),  np.cos(angle) ]
    ])
    return rotmtx.dot(pos-center) + center

class LFPhysicalModel:
    """ ライントレーサー物理モデルクラス 
        
        ライントレーサーの物理モデルを実装しています。
        モーター制御信号が力に比例するという非常に単純なモデルです。
        
        左右の和を前後運動、左右の差を回転運動に換算しています。

        入力　モーター制御信号 [-1,1]x2        
        出力　フォトリフレクタの値 [0,1]x4 
    """    
    
    def __init__(self, \
        course, \
        weight = 200, \
        mntposprs = ((120,-40), (110,-20), (110,20), (120,40))
        ):

        self._course = course
        self._weight = weight
        self._mntposprs = mntposprs
        self._x_mm = SHAFT_LENGTH + 10 # mm
        self._y_mm = SHAFT_LENGTH + 10 # mm
        self._angle = 0.0 # rad
        self.reset()

        # 制御機とフォトリフレクタ設定
        self._controller = LFController()
        self._prs = [ LFPhotoReflector(self._course) \
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

    def reset(self):
        self._vx_mm = 0.0 # mm
        self._vy_mm = 0.0 # mm
        self._w = 0.0

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

        rect = np.asarray(self.get_rect_px())
        center = np.asarray(self.get_center_px())

        # 車体の描画
        apos00 = np.dot([[1,0,0,0],[0,1,0,0]],rect)
        apos10 = np.dot([[1,0,0,0],[0,1,0,1]],rect)
        apos01 = np.dot([[1,0,1,0],[0,1,0,0]],rect)
        apos11 = np.dot([[1,0,1,0],[0,1,0,1]],rect)
        # 
        angle = self._angle
        apos00 = rotate_pos(apos00,center,angle)
        apos10 = rotate_pos(apos10,center,angle)
        apos01 = rotate_pos(apos01,center,angle)
        apos11 = rotate_pos(apos11,center,angle)
        #
        pos00 = apos00.tolist()
        pos10 = apos10.tolist()
        pos01 = apos01.tolist()
        pos11 = apos11.tolist()
        #
        pygame.draw.polygon(screen, YELLOW, [pos00,pos01,pos11,pos10],0)

        # 解像度の読み込み
        res = self._course.resolution # mm/pixel

        # 左タイヤの描画
        pos_ltf = center + np.asarray([TIRE_DIAMETER/2,-SHAFT_LENGTH])/res
        pos_ltr = center + np.asarray([-TIRE_DIAMETER/2,-SHAFT_LENGTH])/res
        pos_ltf = (rotate_pos(pos_ltf,center,angle)+.5).astype(np.int32).tolist()
        pos_ltr = (rotate_pos(pos_ltr,center,angle)+.5).astype(np.int32).tolist()        
        pygame.draw.line(screen, BLACK, pos_ltf,pos_ltr,int(12/res))
        pygame.draw.circle(screen, BLACK, pos_ltf,int(6/res))
        pygame.draw.circle(screen, BLACK, pos_ltr,int(6/res))

        # 右タイヤ の描画     
        pos_rtf = center + np.asarray([TIRE_DIAMETER/2,SHAFT_LENGTH])/res
        pos_rtr = center + np.asarray([-TIRE_DIAMETER/2,SHAFT_LENGTH])/res
        pos_rtf = (rotate_pos(pos_rtf,center,angle)+.5).astype(np.int32).tolist()
        pos_rtr = (rotate_pos(pos_rtr,center,angle)+.5).astype(np.int32).tolist()        
        pygame.draw.line(screen, BLACK, pos_rtf,pos_rtr,int(12/res))   
        pygame.draw.circle(screen, BLACK, pos_rtf,int(6/res))
        pygame.draw.circle(screen, BLACK, pos_rtr,int(6/res))        

        # フォトリフレクタ描画
        for idx in range(NUM_PHOTOREFS):
            pos = center + np.asarray(self._mntposprs[idx])/res
            pos = (rotate_pos(pos,center,angle)+.5).astype(np.int32).tolist()
            if LFPhotoReflector.ACTIVE_WHITE:
                red = (int((1.0-self._prs[idx].value)*255.0), 0, 0)
            else:
                red = (int(self._prs[idx].value*255.0), 0, 0)
            pygame.draw.circle(screen, red, pos, 4)

    def get_rect_px(self):
        # 車体の四隅の座標
        res = self._course.resolution # mm/pixel
        pos_cx_mm = self._x_mm # pixel
        pos_cy_mm = self._y_mm # pixel
        car_width_mm = 2*SHAFT_LENGTH # 車体幅 in mm
        car_length_mm = car_width_mm+60 # 車体長 in mm
        pos_topleft_x_px = int((pos_cx_mm-0.7*SHAFT_LENGTH)/res+.5)
        pos_topleft_y_px = int((pos_cy_mm-0.7*SHAFT_LENGTH)/res+.5)
        car_width_px = (car_width_mm-0.6*SHAFT_LENGTH)/res # 車体幅 in pixel  
        car_length_px = (car_length_mm-0.6*SHAFT_LENGTH)/res # 車体長 in pixel    
        rect = [pos_topleft_x_px,pos_topleft_y_px, car_length_px, car_width_px]
        return rect

    def get_center_px(self):
        # 車体の回転の中心（シャフトの中心）
        res = self._course.resolution # mm/pixel        
        cx_mm = self._x_mm # pixel
        cy_mm = self._y_mm # pixel
        cx_px = cx_mm/res
        cy_px = cy_mm/res
        return [cx_px,cy_px]

    def drive(self,fps):
        """ 車体駆動メソッド"""

        # センサ値更新 
        self._sense()
        
        # モーター制御信号取得
        mtrs = np.asarray(self._controller.prs2mtrs())

        self.drive2019(mtrs,fps)        

    def drive2020(self,mtrs,fps):
        """ 車体駆動メソッド （2020）"""
    
    
    def drive2019(self,mtrs,fps):
        """ 車体駆動メソッド （2019）"""

        # モデルパラメータ
        sFwd = 1.0 # 前後運動の力への換算係数
        sRot = 3.0 # 回転運動の力への換算係数
        kFwd = 3.0 # 抵抗係数
        kRot = 1.0 # 抵抗係数
        weight_kg = 1e-3*self._weight

        # モーターから力の計算
        forceFwd = mtrs[0]+mtrs[1] # 前後運動
        forceRot = mtrs[0]-mtrs[1] # 回転運動

        # 加速度の計算
        angle = self._angle # 車体の方向
        direction  = np.asarray([ np.cos(angle), np.sin(angle)]) 
        accelFwd = sFwd*forceFwd*direction/weight_kg
        accelRot = sRot*forceRot/weight_kg

        # 運動方程式
        #
        # d^2p/dt^2 = -k/m dp/dt + a(t)
        #
        # d_ (  p ) =  ( 0     1  )( p ) + ( 0 )
        # dt (  p')    ( 0   -k/m )( p')   ( a )
        #
        # p = ( x )
        #     ( y )
        
        # 前後運動の計算        
        pos = [ 0.0 for idx in range(4) ]
        pos[0] = 1e-3*self._x_mm # m
        pos[1] = 1e-3*self._y_mm # m
        pos[2] = 1e-3*self._vx_mm # m
        pos[3] = 1e-3*self._vy_mm # m
        t = np.linspace(0,1/fps,2)
        # 前後運動の数値積分
        y = odeint(self._f,pos,t,args=(-kFwd/weight_kg,accelFwd))
        pos = y[-1]
        self._x_mm  = 1e3*pos[0]
        self._y_mm  = 1e3*pos[1]
        self._vx_mm = 1e3*pos[2]
        self._vy_mm = 1e3*pos[3]

        # 回転運動の計算
        ang = [0.0, 0.0]
        ang[0] = self._angle
        ang[1] = self._w
        # 回転運動の数値積分        
        z = odeint(self._g,ang,t,args=(-kRot/weight_kg,accelRot))
        ang = z[-1]
        self._angle = ang[0]
        self._w     = ang[1]        

    def _f(self,p,t,c,a):
        """ 前後運動の微分方程式 """
        return [ p[2], p[3], c*p[2]+a[0], c*p[3]+a[1] ]

    def _g(self,w,t,c,a):
        """ 回転運動の微分方程式 """        
        return [ w[1], c*w[1]+a ]

    def _sense(self):
        """ フォトリフレクタの位置情報の更新 """

        # 解像度
        res = self._course.resolution # mm/pixel                
        # 車体の位置と向き
        center_px = self.get_center_px()
        angle = self._angle

        # フォトリフレクタ位置を設定
        for idx in range(NUM_PHOTOREFS):
            pos = center_px + np.asarray(self._mntposprs[idx])/res
            self._prs[idx].pos_px = rotate_pos(pos,center_px,angle)
