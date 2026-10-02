%% ライントレーサの走行シミュレーション（MATLAB 版）
%
% mbd_phs3（ROS 2 版）と同じ物理モデル・制御則・ロータリーエンコーダの模擬を
% MATLAB で実行し，走行の様子を表示して，走行データを CSV ファイルに保存します．
%
% - 物理モデル：lfParams.m（パラメータ），lfDynamics.m（状態方程式）
% - 制御則　　：prs2mtrs.m
% - フォトリフレクタの模擬：lfPhotorefs.m
% - ロータリーエンコーダの模擬：LFRotaryEncoder.m
%
% 「電子情報通信設計製図」新潟大学工学部工学科電子情報通信プログラム
%
% All rights reserved 2026 (c) Shogo MURAMATSU

%% パラメータとコース
p = lfParams();
course = lfLoadCourse();   % ../images/course2025.png
tEnd = 30;                 % シミュレーションの時間 s

%% シミュレーション
log = lfSimulate(p, course, tEnd);

%% 走行の様子（アニメーション）
figure(1)
clf
ax = lfPlotCourse(course);
hold(ax, 'on')
hTrace = plot(ax, NaN, NaN, 'r-', 'LineWidth', 1);
hBody = plot(ax, NaN, NaN, 'b-', 'LineWidth', 2);
hPrs = plot(ax, NaN, NaN, 'go', 'MarkerFaceColor', 'g', 'MarkerSize', 4);
hold(ax, 'off')
title(ax, 'ライントレーサの走行')
% 車体の外形（車体の座標系，m）
body = [ -0.04 0.13 0.13 -0.04 -0.04
         -0.07 -0.07 0.07 0.07 -0.07 ];
for k = 1:2:height(log)
    pose = [log.x_m(k); log.y_m(k); log.theta_rad(k)];
    R = [cos(pose(3)) -sin(pose(3)); sin(pose(3)) cos(pose(3))];
    b = R*body + pose(1:2);
    q = R*p.mntPosPrf.' + pose(1:2);
    set(hTrace, 'XData', log.x_m(1:k), 'YData', log.y_m(1:k));
    set(hBody, 'XData', b(1,:), 'YData', b(2,:));
    set(hPrs, 'XData', q(1,:), 'YData', q(2,:));
    drawnow limitrate
end

%% 走行データのグラフ
figure(2)
clf
tiledlayout(3,1)
nexttile
plot(log.time_s, [log.u_left log.u_right])
ylabel('モータ制御信号')
legend('左', '右')
grid on
nexttile
plot(log.time_s, [log.rpm_left log.rpm_right], log.time_s, [log.rpm_left_true log.rpm_right_true], '--')
ylabel('回転数 [rpm]')
legend('左（エンコーダ）', '右（エンコーダ）', '左（真値）', '右（真値）')
grid on
nexttile
plot(log.time_s, log.v_m_s, log.time_s, log.w_rad_s)
xlabel('時間 [s]')
legend('速度 [m/s]', '角速度 [rad/s]')
grid on

%% 走行データの保存（mbd_phs3 の CSV と同じ列）
filename = sprintf('lf_sim_%s.csv', string(datetime('now'), 'yyyyMMdd_HHmmss'));
writetable(log(:, 1:12), filename)
fprintf('走行データを %s に保存しました\n', filename)
