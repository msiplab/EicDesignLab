%% ライントレーサの走行シミュレーション（Simulink 版）
%
% build_lf_mils_model.m で作成した Simulink モデル lf_mils.slx を実行し，
% 走行の軌跡と左右の車輪の回転数を表示して，走行データを CSV ファイルに保存します．
% モデルがなければ作成します．
%
% 「電子情報通信設計製図」新潟大学工学部工学科電子情報通信プログラム
%
% All rights reserved 2026 (c) Shogo MURAMATSU

%% モデルの作成と実行
mdl = 'lf_mils';
if ~isfile(fullfile(fileparts(mfilename('fullpath')), [mdl '.slx']))
    build_lf_mils_model(mdl);
end
out = sim(mdl);   % p（lfParams）と course（lfLoadCourse）はモデルの InitFcn で読み込まれる

%% 記録した信号を制御周期ごとの表にする
log = lfLogsoutToTable(out.logsout, p);

%% 走行の軌跡
figure(1)
clf
ax = lfPlotCourse(course);
hold(ax, 'on')
plot(ax, log.x_m, log.y_m, 'r-', 'LineWidth', 1)
hold(ax, 'off')
title(ax, 'ライントレーサの走行（Simulink）')

%% 左右の車輪の回転数
figure(2)
clf
plot(log.time_s, [log.rpm_left log.rpm_right], log.time_s, [log.rpm_left_true log.rpm_right_true], '--')
xlabel('時間 [s]')
ylabel('回転数 [rpm]')
legend('左（エンコーダ）', '右（エンコーダ）', '左（真値）', '右（真値）')
grid on

%% 走行データの保存（mbd_phs3 の CSV と同じ列）
filename = sprintf('lf_sim_%s.csv', string(datetime('now'), 'yyyyMMdd_HHmmss'));
writetable(log, filename)
fprintf('走行データを %s に保存しました\n', filename)
