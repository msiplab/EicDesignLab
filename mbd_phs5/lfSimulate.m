function log = lfSimulate(p, course, tEnd, ctrl)
%LFSIMULATE ライントレーサの走行シミュレーション（MATLAB 版）
%
%   log = lfSimulate(p, course, tEnd)
%   log = lfSimulate(p, course, tEnd, ctrl)
%
%   入力
%     p      : パラメータ（lfParams の出力）
%     course : コース（lfLoadCourse の出力）
%     tEnd   : シミュレーションの時間 s（省略時は 30）
%     ctrl   : 制御則の関数ハンドル mtrs = ctrl(prs, t)（省略時は @(prs,t) prs2mtrs(prs)）
%   出力
%     log : 走行データの table（列は mbd_phs3 の CSV と同じ）
%       time_s, u_left, u_right, rpm_left, rpm_right, rpm_left_true, rpm_right_true,
%       v_m_s, w_rad_s, x_m, y_m, theta_rad, pr1, pr2, pr3, pr4
%
%   制御周期 p.Ts ごとにフォトリフレクタの値を読み，制御則でモータ制御信号を求め，
%   次の周期までその値を保持（ゼロ次ホールド）して物理モデルを ode45 で解きます．
%
%   「電子情報通信設計製図」新潟大学工学部工学科電子情報通信プログラム
%
%   All rights reserved 2026 (c) Shogo MURAMATSU
arguments
    p (1,1) struct
    course (1,1) struct
    tEnd (1,1) double {mustBePositive} = 30
    ctrl (1,1) function_handle = @(prs, t) prs2mtrs(prs)
end

Ts = p.Ts;
numSteps = round(tEnd/Ts);
s = [0; 0; p.pose0(:)];   % 状態 [v; ω; x; y; θ]
encL = LFRotaryEncoder('SampleTime', Ts);
encR = LFRotaryEncoder('SampleTime', Ts);
opts = odeset('RelTol', 1e-6, 'AbsTol', 1e-9);

data = zeros(numSteps+1, 16);
mtrs = [0; 0];
rpm = [0 0];
rpmTrue = [0 0];
for k = 0:numSteps
    t = k*Ts;
    prs = lfPhotorefs(s(3:5), course.white, course.res, p.mntPosPrf);
    data(k+1,:) = [t, mtrs.', rpm, rpmTrue, s(1), s(2), s(3:5).', prs.'];
    if k == numSteps
        break
    end

    % 制御則（次の周期までモータ制御信号を保持する）
    mtrs = ctrl(prs, t);
    mtrs = mtrs(:);

    % 物理モデル
    [~, sOut] = ode45(@(~, x) lfDynamics(x, mtrs, p), [0 Ts], s, opts);
    s = sOut(end,:).';

    % ロータリーエンコーダの計測（左右の車輪の角速度から）
    omegaL = (s(1) - (p.LC/2)*s(2))/p.rW;   % 左の車輪の角速度 rad/s
    omegaR = (s(1) + (p.LC/2)*s(2))/p.rW;   % 右の車輪の角速度 rad/s
    rpm = [encL(omegaL), encR(omegaR)];
    rpmTrue = 60*[omegaL, omegaR]/(2*pi);
end

log = array2table(data, 'VariableNames', {'time_s', 'u_left', 'u_right', ...
    'rpm_left', 'rpm_right', 'rpm_left_true', 'rpm_right_true', ...
    'v_m_s', 'w_rad_s', 'x_m', 'y_m', 'theta_rad', 'pr1', 'pr2', 'pr3', 'pr4'});
end
