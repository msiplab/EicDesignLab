function lf_ros2_controller(duration)
%LF_ROS2_CONTROLLER MATLAB で動かす ROS 2 の制御ノード（ROS Toolbox）
%
%   lf_ros2_controller          % Ctrl+C で止めるまで動かす
%   lf_ros2_controller(60)      % 60 秒間動かす
%
%   mbd_phs3（lf_sim）や mbd_phs4（lf_gazebo）の制御ノード lf_controller の代わりに，
%   MATLAB の prs2mtrs.m を制御則とする ROS 2 のノード /lf_controller_matlab を動かします．
%
%     購読  /photorefs   std_msgs/Float32MultiArray  フォトリフレクタの値（左から順）
%     配信  /cmd_motors  std_msgs/Float32MultiArray  モータ制御信号（左，右）
%
%   WSL2 の Ubuntu で，制御ノードを起動せずにシミュレータを起動しておきます．
%
%     $ ros2 launch lf_sim lf_sim.launch.py controller:=false
%     $ ros2 launch lf_gazebo lf_gazebo.launch.py controller:=false
%
%   Windows の MATLAB と WSL2 の ROS 2 の間の通信の設定は README.md を参照してください．
%
%   「電子情報通信設計製図」新潟大学工学部工学科電子情報通信プログラム
%
%   All rights reserved 2026 (c) Shogo MURAMATSU
arguments
    duration (1,1) double {mustBePositive} = Inf
end

node = ros2node('/lf_controller_matlab');
pub = ros2publisher(node, '/cmd_motors', 'std_msgs/Float32MultiArray');
msgOut = ros2message(pub);
count = 0;
sub = ros2subscriber(node, '/photorefs', 'std_msgs/Float32MultiArray', @onPhotorefs); %#ok<NASGU>
cleanup = onCleanup(@() stopNode(node, pub));

fprintf('/photorefs を待っています（Ctrl+C で終了）\n');
tStart = tic;
while toc(tStart) < duration
    pause(1);
    fprintf('受信したメッセージ数: %d\n', count);
end

    function onPhotorefs(msg)
        % フォトリフレクタの値を受信するたびに，モータ制御信号を配信する
        mtrs = prs2mtrs(double(msg.data));
        msgOut.data = single(mtrs(:));
        send(pub, msgOut);
        count = count + 1;
    end
end

function stopNode(node, pub)
% 終了時にモータを止めてからノードを削除する
msg = ros2message(pub);
msg.data = single([0; 0]);
send(pub, msg);
delete(node);
fprintf('ノード /lf_controller_matlab を終了しました\n');
end
