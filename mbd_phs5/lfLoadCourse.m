function course = lfLoadCourse(filename, resMm, sizePx)
%LFLOADCOURSE コース画像の読み込み
%
%   course = lfLoadCourse(filename, resMm, sizePx)
%
%   入力
%     filename : コース画像のファイル名（省略時は ../images/course2025.png）
%     resMm    : 解像度 mm/pixel（省略時は 2.5）
%     sizePx   : 画像の大きさ [幅 高さ] pixel（省略時は [640 360]）
%   出力
%     course.white : 白黒の配列（true が白）[行, 列]，1行目が画像の上端
%     course.res   : 解像度 m/pixel
%
%   mbd_phs3（lf_sim/model.py の LFCourse）と同じく，最近傍補間で縮小し，
%   輝度が 0 より大きい画素を白とします．
%
%   「電子情報通信設計製図」新潟大学工学部工学科電子情報通信プログラム
%
%   All rights reserved 2026 (c) Shogo MURAMATSU
arguments
    filename {mustBeTextScalar} = fullfile(fileparts(mfilename('fullpath')), '..', 'images', 'course2025.png')
    resMm (1,1) double {mustBePositive} = 2.5
    sizePx (1,2) double {mustBeInteger, mustBePositive} = [640 360]
end

img = imread(filename);
if size(img,3) == 4
    img = img(:,:,1:3);
end
if size(img,3) == 3
    % ITU-R 601-2 の輝度（Pillow の convert('L') と同じ）
    img = double(img);
    gray = floor((299*img(:,:,1) + 587*img(:,:,2) + 114*img(:,:,3))/1000);
else
    gray = double(img);
end

% 最近傍補間による縮小（Pillow の Image.NEAREST と同じ画素の選び方）
[h0, w0] = size(gray);
cols = min(floor(((0:sizePx(1)-1) + 0.5)*w0/sizePx(1)) + 1, w0);
rows = min(floor(((0:sizePx(2)-1) + 0.5)*h0/sizePx(2)) + 1, h0);

course.white = gray(rows, cols) > 0;
course.res = resMm*1e-3;
end
