function prs = lfPhotorefs(pose, white, res, mntPosPrf)
%LFPHOTOREFS フォトリフレクタの応答の模擬
%
%   prs = lfPhotorefs(pose, white, res, mntPosPrf)
%
%   入力
%     pose      : 車体の位置と姿勢 [x (m); y (m); θ (rad)]
%     white     : コースの白黒の配列（lfLoadCourse の course.white）
%     res       : コースの解像度 m/pixel（lfLoadCourse の course.res）
%     mntPosPrf : フォトリフレクタの取り付け位置（lfParams の mntPosPrf）
%   出力
%     prs : フォトリフレクタの値 [0,1]x4（左から順，白で1，黒で0）
%
%   各フォトリフレクタの位置の周辺 3x3 画素の白の割合を値とします
%   （コースの外は 0.5）．mbd_phs3（lf_sim/model.py）と同じ計算です．
%
%   「電子情報通信設計製図」新潟大学工学部工学科電子情報通信プログラム
%
%   All rights reserved 2026 (c) Shogo MURAMATSU

%#codegen
[heightPx, widthPx] = size(white);
c = cos(pose(3));
s = sin(pose(3));
num = size(mntPosPrf,1);
prs = zeros(num,1);
for k = 1:num
    dx = mntPosPrf(k,1);
    dy = mntPosPrf(k,2);
    % 車体の座標系 → コースの座標系
    px = pose(1) + c*dx - s*dy;
    py = pose(2) + s*dx + c*dy;
    % コースの座標系 → 画像の列と行（0 始まり）
    col = fix(px/res + 0.5);
    row = fix((heightPx*res - py)/res + 0.5);
    if row >= 1 && row < heightPx-1 && col >= 1 && col < widthPx-1
        block = white(row:row+2, col:col+2);  % 1 始まりの添字で row-1〜row+1 行
        prs(k) = sum(block(:))/9;
    else
        prs(k) = 0.5;
    end
end
end
