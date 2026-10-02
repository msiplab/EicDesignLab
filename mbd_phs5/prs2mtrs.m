function mtrs = prs2mtrs(prs)
%PRS2MTRS フォトリフレクタの値からモータ制御信号への変換（制御則）
%
%   mtrs = prs2mtrs(prs)
%
%   入力　prs  : フォトリフレクタの値 [0,1]x4（左から順，白で1，黒で0）
%   出力　mtrs : モータ制御信号 [-1,1]x2（[左; 右]）
%
%   mbd_phs2 の mils_line_follower_ctrl.py，mbd_phs3 の lf_sim/controller.py
%   と同じ制御則です．シミュレーション（MATLAB，Simulink），ROS 2 の制御ノード，
%   Raspberry Pi へのコード生成で共通に使います．
%
%   このアルゴリズムは，細かい調整を除いて実機でも利用できるはずです．
%   各自で改善してください．
%
%   「電子情報通信設計製図」新潟大学工学部工学科電子情報通信プログラム
%
%   All rights reserved 2019-2026 (c) Shogo MURAMATSU

%#codegen
vecPrs = double(prs(:));

% 1行目が左モータ，2行目が右モータ．
% 例えば左側のセンサが黒（0）を検出すると，左モータが遅く
% 右モータが速くなり，車体は左（ラインの方向）に曲がる．
matA = [  1.0  0.2 -0.2 -1.0
         -1.0 -0.2  0.2  1.0 ];
vecMtrs = matA*vecPrs + 0.2;

mtrs = min(max(vecMtrs, -1), 1);  % 値の制限 [-1,1]
end
