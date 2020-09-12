#!/usr/bin/python3
# coding: UTF-8
"""
制御クラス

説明

　制御アルゴリズムの変更についてはprs2mtrs() メソッドを編集してください。
　
「電子情報通信設計製図」新潟大学工学部工学科電子情報通信プログラム

All rights revserved (c) Shogo MURAMATSU
"""
import numpy as np

def clamped(v):
    """ 値の制限 [-1,1] """
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
        """ フォトリフレクタからモータ制御信号への変換メソッド
        
            4つフォトリフレクタの応答を2つのモーター制御信号に
            変換する制御の最も重要な部分を実装しています。

            このメソッドに実装するアルゴリズムは、
            細かい調整を除いて実機でも利用できるはずです。

            実機での調整を減らすためには物理モデルの洗練化も必要です。
            工夫の余地が多く残されています。各自で改善してください。

            現代制御（カルマンフィルタ、パーティクルフィルタ）や
            強化学習（人工知能）など高度な技術を盛り込む部分にもなります。
        
        """

        # フォトリフレクタの値を読み出しとベクトル化(vec_x)
        # 白を検出すると 0，黒を検出すると 1
        vec_x = np.array([ self._prs[idx].value \
            for idx in range(len(self._prs)) ])

        # モーター制御の強度値を計算（ここを工夫）
        mat_A = np.array([
            [-0.4,0.0,0.2,0.4],
            [0.4,0.2,0.0,-0.4]
            ])
        vec_y = np.dot(mat_A,vec_x) + 0.1
        
        # 出力範囲を[-1,1]に直して出力
        left, right = vec_y[0], vec_y[1]
        return (clamped(left),clamped(right))

    @property
    def photorefs(self):
        return self._prs

    @photorefs.setter
    def photorefs(self,prs):
        self._prs = prs