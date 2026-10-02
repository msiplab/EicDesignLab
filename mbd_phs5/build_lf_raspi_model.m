function mdl = build_lf_raspi_model(mdl, board)
%BUILD_LF_RASPI_MODEL Raspberry Pi で動かすライントレーサの Simulink モデルを作成
%
%   build_lf_raspi_model                        % lf_raspi.slx を作成（Pi Zero 2 W，32bit OS）
%   build_lf_raspi_model(name, 'Raspberry Pi (64bit)')   % 64bit 版の Raspberry Pi OS の場合
%
%   Raspberry Pi Blockset のブロックで，実機（テキストの配線）の
%   フォトリフレクタとモータを読み書きし，制御則 prs2mtrs.m で走らせるモデルを作成します．
%   制御則は lf_mils.slx（シミュレーション）の Controller と同じ prs2mtrs.m です．
%
%     MCP3004（SPI0 CE0，チャネル 0〜3）→ Photorefs → Controller → Motors → PWM
%
%   - フォトリフレクタ：A/D コンバーター MCP3004 のチャネル 0〜3（左から順）を
%     SPI Controller Transfer ブロックで読み，0〜1 の値にする（gpiozero の MCP3004 と同じ）
%   - モータ：モータドライバの A 側（BCM6, 5）が左，B 側（BCM26, 27）が右．
%     モータ制御信号が正なら BCM6（26）に，負なら BCM5（27）に PWM 信号を出す
%     （gpiozero の Robot(left=(6, 5), right=(26, 27)) と同じ）
%
%   「モデル設定」→「ハードウェア実装」で Raspberry Pi の IP アドレス（またはホスト名
%   car01.local），ユーザ名とパスワードを設定してから，「ハードウェア」タブの
%   「ビルド、展開、起動」または「Monitor & Tune」で実行します．
%
%   「電子情報通信設計製図」新潟大学工学部工学科電子情報通信プログラム
%
%   All rights reserved 2026 (c) Shogo MURAMATSU
arguments
    mdl {mustBeTextScalar} = 'lf_raspi'
    board {mustBeMember(board, {'Raspberry Pi', 'Raspberry Pi (64bit)'})} = 'Raspberry Pi'
end
mdl = char(mdl);
here = fileparts(mfilename('fullpath'));
piModel = 'Pi Zero 2 W';      % ボードの種類
pinsPwm = [6 5 26 27];        % 左の正転，左の逆転，右の正転，右の逆転
Ts = 0.05;                    % 制御周期 s

if bdIsLoaded(mdl)
    close_system(mdl, 0);
end
slx = fullfile(here, [mdl '.slx']);
if isfile(slx)
    delete(slx);  % 作り直す
end
new_system(mdl);
set_param(mdl, 'HardwareBoard', board);
set_param(mdl, 'SolverType', 'Fixed-step', 'Solver', 'FixedStepDiscrete', ...
    'FixedStep', num2str(Ts), 'StopTime', 'Inf');

%% フォトリフレクタ（MCP3004 を SPI で読む）
for ch = 0:3
    y = 40 + 70*ch;
    cst = sprintf('%s/Cmd%d', mdl, ch);
    spi = sprintf('%s/SPI%d', mdl, ch);
    % 開始ビット，シングルエンド入力とチャネル番号，ダミー
    add_block('simulink/Sources/Constant', cst, 'Position', [40 y 140 y+30], ...
        'Value', sprintf('uint8([1; %d; 0])', 128 + 16*ch), 'SampleTime', num2str(Ts));
    add_block('raspberrypiCommlib/SPI Controller Transfer', spi, 'Position', [190 y-5 330 y+35]);
    set_param(spi, 'BoardProperty', piModel, 'SSPin', 'SPI0_CE0', 'OutputDataType', 'uint8', ...
        'OutputDataLength', '3');
    add_line(mdl, sprintf('Cmd%d/1', ch), sprintf('SPI%d/1', ch));
end
add_block('simulink/Signal Routing/Mux', [mdl '/MuxSPI'], 'Position', [380 30 385 300], 'Inputs', '4');
for ch = 0:3
    add_line(mdl, sprintf('SPI%d/1', ch), sprintf('MuxSPI/%d', ch+1), 'autorouting', 'on');
end
addMatlabFunction([mdl '/Photorefs'], [430 140 550 190], ...
    { 'function prs = fcn(rx)'
      '% MCP3004 の応答（チャネルごとに3バイト）から 0〜1 の値を求める'
      'rx = reshape(double(rx), 3, 4);'
      'raw = mod(rx(2,:), 4)*256 + rx(3,:);   % 10 ビットの値（0〜1023）'
      'prs = (raw/1023).'';' });
add_line(mdl, 'MuxSPI/1', 'Photorefs/1');

%% 制御則（lf_mils.slx の Controller と同じ）
addMatlabFunction([mdl '/Controller'], [600 140 720 190], ...
    { 'function mtrs = fcn(prs)'
      '% 制御則（prs2mtrs.m を編集してください）'
      'mtrs = prs2mtrs(prs);' });
add_line(mdl, 'Photorefs/1', 'Controller/1');

%% モータ（PWM）
addMatlabFunction([mdl '/Motors'], [770 140 890 190], ...
    { 'function duty = fcn(mtrs)'
      '% モータ制御信号 [-1,1]（左，右）から各ピンの PWM のデューティ比 [0,1] を求める'
      '% [左の正転; 左の逆転; 右の正転; 右の逆転]'
      'm = min(max(double(mtrs(:)), -1), 1);'
      'duty = [max(m(1),0); max(-m(1),0); max(m(2),0); max(-m(2),0)];' });
add_line(mdl, 'Controller/1', 'Motors/1');
add_block('simulink/Signal Routing/Demux', [mdl '/DemuxPWM'], 'Position', [940 40 945 300], 'Outputs', '4');
add_line(mdl, 'Motors/1', 'DemuxPWM/1');
for k = 1:4
    y = 40 + 70*(k-1);
    blk = sprintf('%s/PWM%d', mdl, pinsPwm(k));
    add_block('raspberrypiBasiclib/PWM', blk, 'Position', [1000 y 1100 y+40]);
    set_param(blk, 'board', piModel, 'Pin_', num2str(pinsPwm(k)));
    add_line(mdl, sprintf('DemuxPWM/%d', k), sprintf('PWM%d/1', pinsPwm(k)), 'autorouting', 'on');
end

%% Monitor & Tune で観測する信号
add_block('simulink/Sinks/Scope', [mdl '/Scope'], 'Position', [800 330 840 390], 'NumInputPorts', '2');
add_line(mdl, 'Photorefs/1', 'Scope/1', 'autorouting', 'on');
add_line(mdl, 'Controller/1', 'Scope/2', 'autorouting', 'on');

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
