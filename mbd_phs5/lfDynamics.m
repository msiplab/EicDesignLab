function dsdt = lfDynamics(s, u, p)
%LFDYNAMICS ライントレーサの物理モデルの状態方程式
%
%   dsdt = lfDynamics(s, u, p)
%
%   入力
%     s : 状態 [v; ω; x; y; θ]（速度 m/s，角速度 rad/s，位置 m，姿勢角 rad）
%     u : モータ制御信号 [左; 右]（-1〜1）
%     p : パラメータ（lfParams の出力）
%   出力
%     dsdt : 状態の時間微分
%
%   動力学（Dynamic）モデルは mbd_phs3（lf_sim/model.py の _odedydt()）と同じで，
%   車体の重心と車輪間の中心がずれた（距離 ℓc）モデルです．
%   運動学（Kinematic）モデルは
%
%      d/dt [x; y; θ] = [cosθ; sinθ; 0] v + [0; 0; 1] ω
%
%   「電子情報通信設計製図」新潟大学工学部工学科電子情報通信プログラム
%
%   All rights reserved 2019-2026 (c) Shogo MURAMATSU

%#codegen
v = s(1);
w = s(2);
theta = s(5);

uLin = (u(2) + u(1))/2;   % 直線運動
uRot = (u(2) - u(1))/2;   % 回転運動（右が速いと左回り）

% 動力学モデル
dv = (1/p.Tlin)*(-p.ellC*(p.Nlin/p.Dlin)*(-w*w) - v + p.Klin*uLin);
dw = (1/p.Trot)*(-p.ellC*(p.Nrot/p.Drot)*(v*w) - w + p.Krot*uRot);

% 運動学モデル
dsdt = [ dv; dw; cos(theta)*v; sin(theta)*v; w ];
end
