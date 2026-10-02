function mdl = build_lf_mils_model(mdl)
%BUILD_LF_MILS_MODEL ライントレーサの Simulink モデル（MILS）を作成
%
%   build_lf_mils_model         % lf_mils.slx を作成
%   build_lf_mils_model(name)   % name.slx を作成
%
%   作成するモデルの構成
%
%     +------------+  mtrs（モータ制御信号）  +------+
%     | Controller | ---------------------> | Body | --> pose, rpm, ...
%     | （離散時間） | <--------------------- |（連続時間）|
%     +------------+  prs（フォトリフレクタ）  +------+
%
%   - Controller：制御則 prs2mtrs.m を呼び出す MATLAB Function ブロック
%                （制御周期 p.Ts の離散時間系．Raspberry Pi に実装する部分）
%   - Body：物理モデル lfDynamics.m と積分器，フォトリフレクタの模擬 lfPhotorefs.m，
%           ロータリーエンコーダの模擬 LFRotaryEncoder.m（MATLAB System ブロック）
%
%   パラメータ p（lfParams.m）とコース course（lfLoadCourse.m）は，
%   シミュレーションの開始時（モデルの InitFcn）にベースワークスペースに読み込まれます．
%
%   「電子情報通信設計製図」新潟大学工学部工学科電子情報通信プログラム
%
%   All rights reserved 2026 (c) Shogo MURAMATSU
arguments
    mdl {mustBeTextScalar} = 'lf_mils'
end
mdl = char(mdl);
here = fileparts(mfilename('fullpath'));

if bdIsLoaded(mdl)
    close_system(mdl, 0);
end
slx = fullfile(here, [mdl '.slx']);
if isfile(slx)
    delete(slx);  % 作り直す
end
new_system(mdl);
set_param(mdl, 'InitFcn', 'p = lfParams(); course = lfLoadCourse();', ...
    'Solver', 'ode45', 'StopTime', '30', 'MaxStep', 'p.Ts/5', ...
    'SaveOutput', 'off', 'SaveTime', 'off', 'SignalLogging', 'on');
evalin('base', 'p = lfParams(); course = lfLoadCourse();');

%% Controller（離散時間の制御器）
ctl = [mdl '/Controller'];
add_block('simulink/Ports & Subsystems/Subsystem', ctl, 'Position', [80 90 220 150]);
delete_line(ctl, 'In1/1', 'Out1/1');
set_param([ctl '/In1'], 'Name', 'prs', 'PortDimensions', '4', 'Position', [20 53 50 67]);
set_param([ctl '/Out1'], 'Name', 'mtrs', 'Position', [260 53 290 67]);
set_param(ctl, 'TreatAsAtomicUnit', 'on', 'SystemSampleTime', 'p.Ts');
addMatlabFunction([ctl '/prs2mtrs'], [100 35 200 85], ...
    { 'function mtrs = fcn(prs)'
      '% 制御則（prs2mtrs.m を編集してください）'
      'mtrs = prs2mtrs(prs);' });
add_line(ctl, 'prs/1', 'prs2mtrs/1');
add_line(ctl, 'prs2mtrs/1', 'mtrs/1');

%% Body（連続時間の物理モデル）
bdy = [mdl '/Body'];
add_block('simulink/Ports & Subsystems/Subsystem', bdy, 'Position', [340 60 500 220]);
delete_line(bdy, 'In1/1', 'Out1/1');
set_param([bdy '/In1'], 'Name', 'mtrs', 'Position', [20 63 50 77]);
set_param([bdy '/Out1'], 'Name', 'prs', 'Position', [700 63 730 77]);
add_block('simulink/Sinks/Out1', [bdy '/pose'], 'Position', [700 3 730 17]);
add_block('simulink/Sinks/Out1', [bdy '/rpm'], 'Position', [1000 183 1030 197]);
add_block('simulink/Sinks/Out1', [bdy '/rpm_true'], 'Position', [1000 273 1030 287]);

addMatlabFunction([bdy '/Dynamics'], [90 40 210 100], ...
    { 'function dsdt = fcn(u, s, p)'
      '% 物理モデルの状態方程式（lfDynamics.m を編集してください）'
      'dsdt = lfDynamics(s, u, p);' });
setParameterScope([bdy '/Dynamics'], {'p'});
add_block('simulink/Continuous/Integrator', [bdy '/Integrator'], ...
    'Position', [250 50 290 90], 'InitialCondition', '[0; 0; p.pose0(:)]');
add_block('simulink/Signal Routing/Selector', [bdy '/SelPose'], 'Position', [350 50 390 90], ...
    'InputPortWidth', '5', 'Indices', '[3 4 5]');
add_block('simulink/Signal Routing/Selector', [bdy '/SelVW'], 'Position', [350 170 390 210], ...
    'InputPortWidth', '5', 'Indices', '[1 2]');

% フォトリフレクタの模擬（制御周期でサンプリング）
add_block('simulink/Discrete/Zero-Order Hold', [bdy '/ZOH1'], 'Position', [440 55 470 85], 'SampleTime', 'p.Ts');
addMatlabFunction([bdy '/Photorefs'], [520 40 640 100], ...
    { 'function prs = fcn(pose, course, p)'
      '% フォトリフレクタの模擬（lfPhotorefs.m）'
      'prs = lfPhotorefs(pose, course.white, course.res, p.mntPosPrf);' });
setParameterScope([bdy '/Photorefs'], {'course', 'p'});

% 左右の車輪の角速度 [rad/s] と回転数 [rpm]
add_block('simulink/Discrete/Zero-Order Hold', [bdy '/ZOH2'], 'Position', [440 175 470 205], 'SampleTime', 'p.Ts');
add_block('simulink/Math Operations/Gain', [bdy '/Wheels'], 'Position', [520 170 600 210], ...
    'Gain', '[1 -p.LC/2; 1 p.LC/2]/p.rW', 'Multiplication', 'Matrix(K*u)');
add_block('simulink/Signal Routing/Demux', [bdy '/Demux'], 'Position', [660 160 665 220], 'Outputs', '2');
add_block('simulink/Math Operations/Gain', [bdy '/rad2rpm'], 'Position', [720 260 790 300], 'Gain', '60/(2*pi)');

% ロータリーエンコーダの模擬（MATLAB System ブロック）
add_block('simulink/User-Defined Functions/MATLAB System', [bdy '/EncoderL'], 'Position', [720 135 880 165]);
set_param([bdy '/EncoderL'], 'System', 'LFRotaryEncoder');
set_param([bdy '/EncoderL'], 'SampleTime', 'p.Ts');
add_block('simulink/User-Defined Functions/MATLAB System', [bdy '/EncoderR'], 'Position', [720 205 880 235]);
set_param([bdy '/EncoderR'], 'System', 'LFRotaryEncoder');
set_param([bdy '/EncoderR'], 'SampleTime', 'p.Ts');
add_block('simulink/Signal Routing/Mux', [bdy '/Mux'], 'Position', [930 160 935 220], 'Inputs', '2');

add_line(bdy, 'mtrs/1', 'Dynamics/1');
add_line(bdy, 'Dynamics/1', 'Integrator/1');
add_line(bdy, 'Integrator/1', 'Dynamics/2', 'autorouting', 'on');
add_line(bdy, 'Integrator/1', 'SelPose/1');
add_line(bdy, 'Integrator/1', 'SelVW/1', 'autorouting', 'on');
add_line(bdy, 'SelPose/1', 'pose/1', 'autorouting', 'on');
add_line(bdy, 'SelPose/1', 'ZOH1/1');
add_line(bdy, 'ZOH1/1', 'Photorefs/1');
add_line(bdy, 'Photorefs/1', 'prs/1');
add_line(bdy, 'SelVW/1', 'ZOH2/1');
add_line(bdy, 'ZOH2/1', 'Wheels/1');
add_line(bdy, 'Wheels/1', 'Demux/1');
add_line(bdy, 'Wheels/1', 'rad2rpm/1', 'autorouting', 'on');
add_line(bdy, 'Demux/1', 'EncoderL/1', 'autorouting', 'on');
add_line(bdy, 'Demux/2', 'EncoderR/1', 'autorouting', 'on');
add_line(bdy, 'EncoderL/1', 'Mux/1', 'autorouting', 'on');
add_line(bdy, 'EncoderR/1', 'Mux/2', 'autorouting', 'on');
add_line(bdy, 'Mux/1', 'rpm/1');
add_line(bdy, 'rad2rpm/1', 'rpm_true/1', 'autorouting', 'on');
movePort(bdy, 'prs', 1); movePort(bdy, 'pose', 2); movePort(bdy, 'rpm', 3); movePort(bdy, 'rpm_true', 4);

%% 結線と記録
add_line(mdl, 'Controller/1', 'Body/1', 'autorouting', 'on');
add_line(mdl, 'Body/1', 'Controller/1', 'autorouting', 'on');
add_block('simulink/Sinks/Scope', [mdl '/Scope'], 'Position', [640 20 680 100], 'NumInputPorts', '2');
add_line(mdl, 'Controller/1', 'Scope/1', 'autorouting', 'on');
add_line(mdl, 'Body/3', 'Scope/2', 'autorouting', 'on');
add_block('simulink/Sinks/Terminator', [mdl '/Term2'], 'Position', [560 110 580 130]);
add_line(mdl, 'Body/2', 'Term2/1', 'autorouting', 'on');
add_block('simulink/Sinks/Terminator', [mdl '/Term4'], 'Position', [560 190 580 210]);
add_line(mdl, 'Body/4', 'Term4/1', 'autorouting', 'on');
addLog(mdl, 'Controller', 1, 'mtrs');
addLog(mdl, 'Body', 1, 'prs');
addLog(mdl, 'Body', 2, 'pose');
addLog(mdl, 'Body', 3, 'rpm');
addLog(mdl, 'Body', 4, 'rpm_true');

save_system(mdl, slx);
fprintf('%s.slx を作成しました\n', mdl);
end

%% ローカル関数
function addMatlabFunction(blk, pos, code)
% MATLAB Function ブロックを追加してコードを設定する
add_block('simulink/User-Defined Functions/MATLAB Function', blk, 'Position', pos);
ch = find(slroot, '-isa', 'Stateflow.EMChart', 'Path', blk);
ch.Script = strjoin(code, newline);
end

function setParameterScope(blk, names)
% MATLAB Function ブロックの入力のうち names をパラメータ（ワークスペースの変数）にする
ch = find(slroot, '-isa', 'Stateflow.EMChart', 'Path', blk);
for k = 1:numel(names)
    d = find(ch, '-isa', 'Stateflow.Data', 'Name', names{k});
    d.Scope = 'Parameter';
    d.Tunable = false;
end
end

function movePort(sys, name, num)
set_param([sys '/' name], 'Port', num2str(num));
end

function addLog(mdl, blk, port, name)
% 信号に名前を付けて記録（logsout）する
ph = get_param([mdl '/' blk], 'PortHandles');
h = ph.Outport(port);
set_param(h, 'DataLogging', 'on', 'DataLoggingNameMode', 'Custom', 'DataLoggingName', name);
end
