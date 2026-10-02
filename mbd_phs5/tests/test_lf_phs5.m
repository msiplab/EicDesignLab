function tests = test_lf_phs5
%TEST_LF_PHS5 mbd_phs5 の物理モデル・制御則・模擬のテスト
%
%   >> cd mbd_phs5
%   >> runtests('tests')
%
%   「電子情報通信設計製図」新潟大学工学部工学科電子情報通信プログラム
%
%   All rights reserved 2026 (c) Shogo MURAMATSU
tests = functiontests(localfunctions);
end

function setupOnce(tc)
tc.applyFixture(matlab.unittest.fixtures.PathFixture(fullfile(fileparts(mfilename('fullpath')), '..')));
tc.TestData.p = lfParams();
tc.TestData.course = lfLoadCourse();
end

function testPrs2mtrs(tc)
% 全て白なら直進，左側が黒なら左に曲がる（左が遅く右が速い），値は [-1,1]
tc.verifyEqual(prs2mtrs([1 1 1 1]), [0.2; 0.2], 'AbsTol', 1e-12);
m = prs2mtrs([0 1 1 1]);
tc.verifyLessThan(m(1), m(2));
m = prs2mtrs([1 1 1 0]);
tc.verifyGreaterThan(m(1), m(2));
m = prs2mtrs([5 0 0 -5]);
tc.verifyLessThanOrEqual(abs(m), 1);
end

function testCourse(tc)
c = tc.TestData.course;
tc.verifySize(c.white, [360 640]);
tc.verifyEqual(c.res, 2.5e-3);
end

function testPhotorefs(tc)
% mbd_phs3（lf_sim/model.py）で求めた値と比べる
p = tc.TestData.p;
c = tc.TestData.course;
poses = [0.75 0.81 0; 0.3 0.2 1.0; 1.2 0.5 -2.0; 0.1001 0.1234 0.3];
expected = [1 1 1/3 1; 1 1 1 1; 1 1 0 1; 1 2/3 0 1];
for k = 1:size(poses,1)
    prs = lfPhotorefs(poses(k,:).', c.white, c.res, p.mntPosPrf);
    tc.verifyEqual(prs.', expected(k,:), 'AbsTol', 1e-12);
end
% コースの外は 0.5
tc.verifyEqual(lfPhotorefs([-1; -1; 0], c.white, c.res, p.mntPosPrf), 0.5*ones(4,1));
end

function testDynamicsSteadyState(tc)
% 直進の定常状態は v = K_lin u，その場の回転の定常状態は ω = K_rot u
p = tc.TestData.p;
u = 0.5;
[~, s] = ode45(@(~, x) lfDynamics(x, [u; u], p), [0 1], zeros(5,1));
tc.verifyEqual(s(end,1), p.Klin*u, 'RelTol', 1e-4);
tc.verifyEqual(s(end,2), 0, 'AbsTol', 1e-9);
[~, s] = ode45(@(~, x) lfDynamics(x, [-u; u], p), [0 1], zeros(5,1));
% 重心のずれ（ℓc）の影響で回転中にわずかに速度 v が生じ，ω は K_rot u より少し小さくなる
tc.verifyEqual(s(end,2), p.Krot*u, 'RelTol', 1e-2);
tc.verifyLessThan(s(end,2), p.Krot*u);
end

function testEncoder(tc)
% 一定の回転数のとき，エンコーダの計測値は真値に近づき，止まると 0 になる
Ts = 0.01;
enc = LFRotaryEncoder('SampleTime', Ts);
rpmTrue = 100;
omega = rpmTrue*2*pi/60;
for k = 1:300
    rpm = enc(omega);
end
tc.verifyEqual(rpm, rpmTrue, 'RelTol', 1e-3);
tc.verifyEqual(enc(-omega), rpm, 'RelTol', 1e-3);  % 回転の向きは区別しない
for k = 1:60
    rpm = enc(0);
end
tc.verifyEqual(rpm, 0);
end

function testSimulateFollowsLine(tc)
% 30 秒間の走行で，ラインに沿って 2.5 m 以上進む
log = lfSimulate(tc.TestData.p, tc.TestData.course, 30);
dist = sum(hypot(diff(log.x_m), diff(log.y_m)));
tc.verifyGreaterThan(dist, 2.5);
prs = log{:, {'pr1', 'pr2', 'pr3', 'pr4'}};
tc.verifyGreaterThan(mean(any(prs < 1, 2)), 0.5);  % 半分以上の時間でラインを検出
end
