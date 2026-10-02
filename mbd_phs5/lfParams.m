function p = lfParams()
%LFPARAMS ライントレーサの車体と物理モデルのパラメータ
%
%   p = lfParams() は，mbd_phs3（lf_sim/model.py）と同じパラメータを
%   構造体 p で返します．
%
%   - 長さは m，角度は rad，時間は s で表す
%   - コースの座標系：x 軸が右，y 軸が上，原点はコース画像の左下
%   - 車体の座標系：x 軸が前，y 軸が左，原点は車輪間の中心
%   - 角速度 ω と姿勢角 θ は左回り（反時計回り）が正
%
%   物理モデルの変更については，このファイルのパラメータと
%   lfDynamics.m を編集してください．
%
%   「電子情報通信設計製図」新潟大学工学部工学科電子情報通信プログラム
%
%   All rights reserved 2019-2026 (c) Shogo MURAMATSU

% 車輪間の中心(+)からのフォトリフレクタ(*)の相対座標 [m]（車体の座標系）
%
%         y
%         ↑      * pr1 (x1,y1)
%       --|--   * pr2 (x2,y2)
%         + ------------→ x（前）
%       --|--   * pr3 (x3,y3)
%                * pr4 (x4,y4)
%
% 進行方向に向かって左から順に pr1, pr2, pr3, pr4（1行に1個）
p.mntPosPrf = [ 0.120  0.060
                0.100  0.020
                0.100 -0.020
                0.120 -0.060 ]; % m
p.numPhotorefs = size(p.mntPosPrf,1);

p.weight = 360;           % 車体の重さ g（グラム）
shaftLength = 50e-3;      % シャフト長 m（１本あたり）
tireDiameter = 58e-3;     % タイヤ直径 m

% 物理モデルパラメータ（要調整）
p.coefKp = 3.0;           % モータ制御信号から電圧への係数（mbd_phs2 の COEF_K_P）
p.muC = 1e-3;             % kg/s 車体の直線運動の粘性摩擦係数（便宜上）
p.iotaC = 1e-4;           % kg·m^2/s 車体の旋廻運動の粘性摩擦係数（便宜上）
p.ellC = 30e-3;           % m 車体の重心から車輪間の中心までの距離
p.n = 58.2;               % ギヤ比
p.LC = 2*shaftLength;     % m 車輪間の距離
p.rW = tireDiameter/2;    % m 車輪の半径
p.kT = 2e-3;              % N·m/A モータのトルク係数（概算）
p.kB = 2e-3;              % V·s/rad モータの逆起電力定数（概算）
p.Ra = 2.0;               % Ω 電機子抵抗（概算）
p.JC = (1/3)*p.weight*1e-3*((160e-3/2)^2+(60e-3/2)^2); % kg·m^2 車体の重心周りの慣性モーメント（概算）
p.JM = (1/2)*(5e-3)*((5e-3)^2); % kg·m^2 電機子の慣性モーメント（概算）
p.JG = 0;                 % kg·m^2 ギヤの慣性モーメント（ギヤ比 n>>1 より近似）
p.iotaM = 1e-6;           % kg·m^2/s モータの粘性摩擦係数（概算）
p.iotaG = 0;              % kg·m^2/s ギヤの粘性摩擦係数（ギヤ比 n>>1 より近似）

% 直線運動と回転運動の1次遅れ系の係数（lfDynamics.m で使用）
mC = 1e-3*p.weight;                      % kg
iotaBarM = p.iotaM + p.kT*p.kB/p.Ra;
iotaBarG = p.iotaG + (p.n^2)*iotaBarM;
JBarG = p.JG + (p.n^2)*p.JM;
zeta = p.n*p.kT/p.Ra;

% 直線運動
p.Dlin = iotaBarG + (1/2)*p.muC*(p.rW^2);
Jlin = JBarG + (1/2)*mC*(p.rW^2);
p.Tlin = Jlin/p.Dlin;                    % 時定数 s
p.Klin = p.coefKp*(zeta*p.rW)/p.Dlin;    % ゲイン m/s
p.Nlin = (1/2)*mC*(p.rW^2);

% 回転運動
rC = 2*p.rW/p.LC;
p.Drot = iotaBarG + (1/2)*(p.muC*(p.ellC^2)+p.iotaC)*(rC^2);
Jrot = JBarG + (1/2)*(p.JC + mC*(p.ellC^2))*(rC^2);
p.Trot = Jrot/p.Drot;                    % 時定数 s
p.Krot = p.coefKp*(zeta*rC)/p.Drot;      % ゲイン rad/s
p.Nrot = (1/2)*mC*(rC^2);

% シミュレーションの設定
p.Ts = 0.05;                             % 制御周期 s（mbd_phs3 の rate_hz = 20）
p.pose0 = [0.75; 0.81; 0];               % 初期位置 [x (m); y (m); θ (rad)]
end
