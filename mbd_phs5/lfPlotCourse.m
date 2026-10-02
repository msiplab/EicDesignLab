function ax = lfPlotCourse(course, ax)
%LFPLOTCOURSE コースの表示
%
%   ax = lfPlotCourse(course)
%   ax = lfPlotCourse(course, ax)
%
%   コースの座標系（x 軸が右，y 軸が上，原点は左下，単位 m）でコースを表示します．
%
%   「電子情報通信設計製図」新潟大学工学部工学科電子情報通信プログラム
%
%   All rights reserved 2026 (c) Shogo MURAMATSU
arguments
    course (1,1) struct
    ax = gca
end
[h, w] = size(course.white);
res = course.res;
% 画素の中心の座標（lfPhotorefs.m と同じ対応．1行目が画像の上端なので，y は上から下へ減る）
image(ax, [0 (w-1)*res], [h*res res], repmat(uint8(course.white)*255, 1, 1, 3));
set(ax, 'YDir', 'normal');
axis(ax, 'equal');
axis(ax, [0 w*res 0 h*res]);
xlabel(ax, 'x [m]');
ylabel(ax, 'y [m]');
end
