function log = lfLogsoutToTable(logsout, p)
%LFLOGSOUTTOTABLE Simulink で記録した信号を制御周期ごとの表にする
%
%   log = lfLogsoutToTable(out.logsout, p)
%
%   lf_mils.slx で記録した信号（mtrs, pose, rpm, rpm_true）を，制御周期 p.Ts ごとの
%   走行データの table にします．列は mbd_phs3 の CSV と同じです．
%
%   「電子情報通信設計製図」新潟大学工学部工学科電子情報通信プログラム
%
%   All rights reserved 2026 (c) Shogo MURAMATSU
arguments
    logsout (1,1) Simulink.SimulationData.Dataset
    p (1,1) struct
end
rpm = logsout.getElement('rpm').Values;
t = rpm.Time;                       % 制御周期ごとの時刻
at = @(name) samples(logsout.getElement(name).Values, t);

mtrs = at('mtrs');
% 各時刻までの1周期に使ったモータ制御信号にする（mbd_phs3 の CSV と同じ）
mtrs = [zeros(1, size(mtrs,2)); mtrs(1:end-1,:)];
rpmEnc = at('rpm');
rpmTrue = at('rpm_true');
pose = at('pose');

% 車輪の回転数（真値）から速度と角速度を求める
omega = rpmTrue*2*pi/60;            % 左右の車輪の角速度 rad/s
v = p.rW*(omega(:,1) + omega(:,2))/2;
w = p.rW*(omega(:,2) - omega(:,1))/p.LC;

log = table(t, mtrs(:,1), mtrs(:,2), rpmEnc(:,1), rpmEnc(:,2), rpmTrue(:,1), rpmTrue(:,2), ...
    v, w, pose(:,1), pose(:,2), pose(:,3), 'VariableNames', {'time_s', 'u_left', 'u_right', ...
    'rpm_left', 'rpm_right', 'rpm_left_true', 'rpm_right_true', 'v_m_s', 'w_rad_s', ...
    'x_m', 'y_m', 'theta_rad'});
end

function y = samples(ts, t)
% 時系列 ts の時刻 t における値（各時刻で最後に記録された値）
data = squeeze(ts.Data);
if size(data,1) ~= numel(ts.Time)
    data = data.';
end
[~, idx] = unique(ts.Time, 'last');
y = interp1(ts.Time(idx), data(idx,:), t, 'previous', 'extrap');
end
