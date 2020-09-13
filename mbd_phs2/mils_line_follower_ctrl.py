#!/usr/bin/python3
# coding: UTF-8
"""
ライントレーサー制御クラス（Twist型出力）

説明

  ROS制御（シミュレーション）ができるよう制御信号にTwist型（直線速度，角速度）を利用。
　制御アルゴリズムの変更についてはprs2twist() メソッドを編集してください。
　Raspberry Pi の制御には，速度制御信号をモータ制御信号に変えるtwist2mtrs()メソッドも必要です。

参考資料

- 三平 満司：「非ホロノミック系のフィードバック制御」計測と制御
　1997 年 36 巻 6 号 p. 396-403
- トランジスタ技術2019年7月号
　
「電子情報通信設計製図」新潟大学工学部工学科電子情報通信プログラム

All rights revserved 2019-2020 (c) Shogo MURAMATSU
"""
import numpy as np

def clamped(v):
    """ 値の制限 [-1,1] """
    return max(-1,min(1,v))

class LFController:
    """ ライントレース制御クラス 
        
        ライントレース制御アルゴリズムを実装する。

        入力　フォトリフレクの値 [0,1]x4
        出力　速度制御信号Twist型 （ROS対応準備）
             { "linear":{"x":0.,"y":0.,"z":0.}, "angular":{"x":0.,"y":0.,"z":0.}, "angular":{} }
    """
    
    def __init__(self,prs = None):
        self._prs = prs

    def prs2mtrs(self):
        """ フォトリフレクタ応答からモーター制御信号への変換メソッド
            （参考）

            4つのフォトリフレクタの応答を2つのモーター制御信号に
            変換するメソッド。
        """
        return self.twist2mtrs(self.prs2twist())

    def prs2twist(self):
        """ フォトリフレクタから速度制御信号への変換メソッド
            （ROS対応Twist型出力，シミュレーションで利用）

            4つフォトリフレクタの応答を2つの速度制御信号に
            変換する制御の最も重要な部分を実装しています。

            このメソッドに実装するアルゴリズムは、
            細かい調整を除いて実機でも利用できるはずです。

            実機での調整を減らすためには物理モデルの洗練化も必要です。
            工夫の余地が多く残されています。各自で改善してください。

            作成するライントレーサーは2輪車両であり非線形なシステムです。
            PID制御のような通常のフィードバック制御で安定して制御することは難しく，
            安定な制御のためには状態方程式から考察される時変の状態フィードバックや
            不連続フィードバックなどが必要です。
            現代制御（カルマンフィルタ，パーティクルフィルタ）や
            強化学習（人工知能）など高度な技術などこの部分に実装することになります。
        """
        # フォトリフレクタの値を読み出しとベクトル化(vec_x)
        # 白を検出すると 0，黒を検出すると 1
        vec_x = np.array([ self._prs[idx].value \
            for idx in range(len(self._prs)) ])

        # 速度制御の強度値を計算（ここを工夫）
        mat_A = np.array([
            [ -0.4, 0.5, 0.5, -0.4 ],
            [ -80.0,-30.0, 30.0, 80.0 ]
            ])
        vec_b = np.array( [ 0.1, 0.0 ] )
        vec_y = np.dot(mat_A,vec_x) + vec_b
        
        # 直線速度vを linear.x, 角速度wを angular.z に格納して出力
        v = vec_y[0]
        w = vec_y[1]
        twist = { "linear":{"x":v,"y":0.,"z":0.}, "angular":{"x":0.,"y":0.,"z":w} }
        return twist

    def twist2mtrs(self,twist):
        """ 速度制御信号からモーター制御信号への変換メソッド 
            （参考）
        """

        # 制御情報の抽出
        v = twist["linear"]["x"] # 目標直線速度
        w = twist["angular"]["z"] # 目標旋廻角速度

        # モータ制御信号への換算
        vleft, vright = self.spd2vlt(v,w)
        
        # 出力範囲を[-1,1]に直して出力
        return (clamped(vleft),clamped(vright))

    def spd2vlt(self, v, w):
        """
        速度電圧換算（概算）

        ツインモーターギヤボックス性能
        - 重量 80 g（推定）
        - 全長 75mm
        - 取り付け幅 50mm
        - 全高23mm
        - 出力シャフト長 100mm
        | ギヤ比 n:1    | 58.2:1      | 203.7:1     |
        ---------------------------------------------
        | トルク(g・cm) | 419         | 1404        | τw=nτm
        | トルク(Nm)    | 0.041090073 | 0.137686068 |
        ---------------------------------------------        
        | 回転数(rpm)   | 227         | 65          | θw=θm/n
        | 角速度(rad/s) | 23.77138441 | 6.806784083 |        

        DCモータ性能
        - 重量 18 g (プーリー付き測定値，公称値 17 g)
        - モータトルク τm ~ 6.9 - 7.2 gcm
        - モータ回転数 θm ~ 13211 - 13241 rpm
        （参考FA-130-RA-18100仕様）https://product.mabuchi-motor.co.jp/detail.html?id=10
        電圧               | 無負荷        | 最高効率時                         | 停止時        
        操作範囲   | 公称値 | 回転数 | 電流 | 回転数 | 電流 | トルク       | 出力 | トルク      | 電流
        V         | V      | r/min | A    | r/min | A    | mN·m | g·cm |  W   | mN·m | g·cm | A       
        1.5 - 3.0 | 3      | 12300 | 0.15 | 9710  | 0.56 | 0.74 | 7.6  | 0.76 | 3.53 | 36   | 2.10
        ※ N rpm = Nπ/30 rad/s

        （上記の仕様より，トラ技2019年7月号P.62参照）※要同定
        - トルク定数 kt ~ 3.53e-3 N·m/2.10A ~ 0.00168 N·m/A
        - 抵抗         ( Rm ) ~ ( 0.15 12300π/30 )^-1 ( 3.0 ) ~ ( 1.4305 ) Ω
        - 逆起電力定数  ( kb )   ( 0.56 9710π/30  )   ( 3.0 )    ( 0.0022 ) V·s/rad
          import numpy as np
          A = np.matrix( [[ 0.15, 12300*np.pi/30], [ 0.56, 9710*np.pi/30 ]])
          b = np.matrix( [[3.0],[3.0]])
          x = np.linalg.solve(A,b)

        ナロータイヤ１個分
        - 58mm径（内径約40mm) 
        - 15mm幅
        - 重量 21 g
        - モータ軸まわりの慣性モーメント（推定）
        　J = (3/4*a^2+c^2)*M ~ 1.018e-5 kgm^2
           (中心半径a=25e-3m,管半径c=4e-3m,M=21e-3kgの円環で近似)
        
        ボールキャスター
        - 重量 10 g （推定）

        ユニバーサルプレート
        - 重量 23 g
        - 160 mm x 60 mm x 3 mm 

        充電池
        - 重量 26.2 g/本
        - 電池ケース 3本用 10 g
        - 電池ケース 2本用  7 g

        Raspberry Pi Zero WH
        - 重量 12 g
        - 65 mm x 30 mm

        車体の構造モデル
        - 車体の総重量 Mp (推定)
        　ギヤボックス　タイヤ　ボールキャスタ　プレート　電池（ボックス）　RasPiZeroW　回路基板など
          Mp = 80g  + 21g x 2 + 23g + 10g + 26.2g x 5 + 17g + 12g + α ~ 360g 
        - 車体の重心z軸まわりの慣性モーメント Ip（立方体で推定）
          Ip ~
        - 車体の重心xy座標と回転中心xy座標の距離 rpd
          rpd ~ 
        - 車体の回転中心z軸まわりの慣性モーメント Id（推定）
        　Id = Ip + Mp*rpd^2

        """

        # ギヤボックス・ナロータイやの仕様より無負荷最大速度を推定
        # maxspeed = rω = 29mm x 23.77 rad/s ~ 689.33e-1 m/s 
        Rw = 29e-3
        vleft, vright = (v + Rw*w)/2, (v - Rw*w)/2
        return vleft, vright

    @property
    def photorefs(self):
        return self._prs

    @photorefs.setter
    def photorefs(self,prs):
        self._prs = prs
