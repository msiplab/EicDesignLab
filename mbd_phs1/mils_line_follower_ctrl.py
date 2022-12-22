#!/usr/bin/python3
# coding: UTF-8
"""
ライントレーサ制御クラス

説明

　制御アルゴリズムの変更についてはprs2mtrs() メソッドを編集してください。

参考資料

- 三平 満司：「非ホロノミック系のフィードバック制御」計測と制御
　1997 年 36 巻 6 号 p. 396-403
　
「電子情報通信設計製図」新潟大学工学部工学科電子情報通信プログラム

All rights revserved 2019-2022 (c) Shogo MURAMATSU
"""
import numpy as np

def clamped(v):
    """ 値の制限 [-1,1] """
    return max(-1,min(1,v))

class LFController:
    """ ライントレース制御クラス 
        
        ライントレース制御アルゴリズムを実装する。

        入力　フォトリフレクの値 [0,1]x4
        出力　モータ制御信号 [-1,1]x2
    """
    
    def __init__(self,prs = None):
        self._prs = prs

    def prs2mtrs(self):
        """ フォトリフレクタからモータ制御信号への変換メソッド
        
            4つフォトリフレクタの応答を2つのモーター制御信号に
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
        vec_prs = np.array([ self._prs[idx].value \
            for idx in range(len(self._prs)) ])

        # モーター制御の強度値を計算（ここを工夫）
        # Left <- 0 1 2 3 -> Right        
        mat_A = np.array([
            [-1.0,-0.2,0.2,1.0],
            [1.0,0.2,-0.2,-1.0]
            ])
        vec_mtrs = np.dot(mat_A,vec_prs)+0.2
        
        # 出力範囲を[-1,1]に直して出力
        mtr_left, mtr_right = vec_mtrs[0], vec_mtrs[1]
        return (clamped(mtr_left),clamped(mtr_right))

    @property
    def photorefs(self):
        return self._prs

    @photorefs.setter
    def photorefs(self,prs):
        self._prs = prs
