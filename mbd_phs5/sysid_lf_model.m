%% 走行データからの物理モデルの同定（System Identification Toolbox）
%
% モータ制御信号と車輪の回転数の走行データから，簡易物理モデル（テキストの式）
%
%   直線運動：T_lin dv/dt + v = K_lin u_lin，  u_lin = (u_R + u_L)/2
%   回転運動：T_rot dω/dt + ω = K_rot u_rot，  u_rot = (u_R - u_L)/2
%
% の時定数 T とゲイン K を，1次遅れ系の伝達関数 K/(Ts+1) として推定します（tfest）．
%
% - csvFile が空のとき：物理モデル（lfSimulate）でステップ状のモータ制御信号を
%   与えて走行データを作り，物理モデルのパラメータ（lfParams）から求めた値と比べます．
% - csvFile を指定したとき：その走行データ（列は mbd_phs3 の CSV と同じ．
%   time_s, u_left, u_right, rpm_left, rpm_right が必要）から推定します．
%   実機の走行データを同じ形式で保存すれば，実機のモデルを推定できます．
%
% ロータリーエンコーダは回転の向きを区別しないので，車輪の回転の向きは
% モータ制御信号の符号と同じとみなします．
%
% 「電子情報通信設計製図」新潟大学工学部工学科電子情報通信プログラム
%
% All rights reserved 2026 (c) Shogo MURAMATSU

%% 設定
csvFile = '';      % 走行データの CSV ファイル（空なら物理モデルで作成）
p = lfParams();
p.Ts = 0.01;       % 記録の周期 s（同定には制御周期より細かく記録するとよい）

%% 走行データ
if isempty(csvFile)
    course = lfLoadCourse();
    rng(0)
    % 直線運動（左右同じ）と回転運動（左右逆）のステップ状の信号を 1 s ごとに切り替える
    levels = 0.2 + 0.8*rand(20,1);
    stepLin = @(t) levels(min(floor(t)+1, 10));
    stepRot = @(t) levels(min(floor(t-10)+11, 20));
    ctrl = @(prs, t) (t < 10)*[stepLin(t); stepLin(t)] + (t >= 10)*[-stepRot(t); stepRot(t)];
    log = lfSimulate(p, course, 20, ctrl);
    % lfSimulate の u_left, u_right は各時刻までの1周期に使った値
else
    log = readtable(csvFile);
end
Ts = median(diff(log.time_s));

% 回転の向き付きの車輪の角速度 [rad/s]（エンコーダの計測値と真値）
toOmega = @(rpm, u) sign(u).*rpm*2*pi/60;
omegaL = toOmega(log.rpm_left, log.u_left);
omegaR = toOmega(log.rpm_right, log.u_right);
uLin = (log.u_right + log.u_left)/2;
uRot = (log.u_right - log.u_left)/2;
vEnc = p.rW*(omegaR + omegaL)/2;
wEnc = p.rW*(omegaR - omegaL)/p.LC;

%% 1次遅れ系の推定（1つの極，零点なし）
% 走行データの u(k) は時刻 k までの1周期に使った値なので，1サンプル進めて
% 「時刻 k から次の時刻まで u が一定」（ゼロ次ホールド）の形に揃える
mkdata = @(y, u) iddata(y(1:end-1), u(2:end), Ts);
if isempty(csvFile)
    isLin = log.time_s < 10;
    isRot = log.time_s >= 10;
else
    isLin = true(height(log),1);
    isRot = true(height(log),1);
end
sysLinEnc = tfest(mkdata(vEnc(isLin), uLin(isLin)), 1, 0);
sysRotEnc = tfest(mkdata(wEnc(isRot), uRot(isRot)), 1, 0);
[KlinEnc, TlinEnc] = firstOrder(sysLinEnc);
[KrotEnc, TrotEnc] = firstOrder(sysRotEnc);

fprintf('            K_lin [m/s]  T_lin [s]   K_rot [rad/s]  T_rot [s]\n');
fprintf('エンコーダ  %10.4f  %9.4f  %12.4f  %10.4f\n', KlinEnc, TlinEnc, KrotEnc, TrotEnc);

if isempty(csvFile)
    % 真値（物理モデルの車輪の回転数）からの推定と，パラメータから求めた値
    omegaLt = log.rpm_left_true*2*pi/60;
    omegaRt = log.rpm_right_true*2*pi/60;
    vTrue = p.rW*(omegaRt + omegaLt)/2;
    wTrue = p.rW*(omegaRt - omegaLt)/p.LC;
    sysLinTrue = tfest(mkdata(vTrue(isLin), uLin(isLin)), 1, 0);
    sysRotTrue = tfest(mkdata(wTrue(isRot), uRot(isRot)), 1, 0);
    [KlinTrue, TlinTrue] = firstOrder(sysLinTrue);
    [KrotTrue, TrotTrue] = firstOrder(sysRotTrue);
    fprintf('真値        %10.4f  %9.4f  %12.4f  %10.4f\n', KlinTrue, TlinTrue, KrotTrue, TrotTrue);
    fprintf('パラメータ  %10.4f  %9.4f  %12.4f  %10.4f\n', p.Klin, p.Tlin, p.Krot, p.Trot);
end

%% 推定したモデルの応答と走行データの比較
figure(1)
clf
tiledlayout(2,1)
nexttile
compare(mkdata(vEnc(isLin), uLin(isLin)), sysLinEnc)
title('直線運動（速度 v）')
nexttile
compare(mkdata(wEnc(isRot), uRot(isRot)), sysRotEnc)
title('回転運動（角速度 \omega）')

%% ローカル関数
function [K, T] = firstOrder(sys)
% 1次遅れ系 b/(s+a) のゲイン K = b/a と時定数 T = 1/a
a = sys.Denominator(end);
b = sys.Numerator(end);
K = b/a;
T = 1/a;
end
