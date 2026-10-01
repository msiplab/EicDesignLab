# coding: UTF-8
"""
物理モデルと制御則のテスト（ROS なしで実行できる）

  $ python3 -m pytest test/test_model.py      # パッケージのディレクトリで実行
  $ colcon test --packages-select lf_sim       # ROS 2 のワークスペースで実行
"""
import math
import os
import sys

import numpy as np
import pytest

try:
    from lf_sim.model import LFCourse, LFPhysicalModel
    from lf_sim.controller import prs2mtrs
except ImportError:
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
    from lf_sim.model import LFCourse, LFPhysicalModel
    from lf_sim.controller import prs2mtrs

INITIAL_POSE = (0.75, 0.81, 0.0)  # body_node.py の initial_pose の既定値
FPS = 20.0


def course_path():
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                     '..', '..', '..', 'images', 'course2025.png')
    if os.path.exists(p):
        return p
    from ament_index_python.packages import get_package_share_directory
    return os.path.join(get_package_share_directory('lf_sim'), 'images', 'course2025.png')


@pytest.fixture(scope='module')
def course():
    return LFCourse(course_path())


def black_distance(course, x, y):
    """ 位置 (x, y) から最も近い黒の画素までの距離 [m] """
    rows, cols = np.nonzero(~course.white)
    col, row = course.to_pixel(x, y)
    return math.sqrt(((cols - col)**2 + (rows - row)**2).min())*course.resolution


def test_turn_direction(course):
    """ 右モータだけを回すと左回り（θ が増加） """
    lf = LFPhysicalModel(course)
    lf.set_pose(0.8, 0.45, 0.0)
    for _ in range(10):
        lf.step((0.0, 1.0), 1/FPS)
    assert lf.pose[2] > 0.0
    assert lf.angular_velocity > 0.0


def test_initial_pose_on_line(course):
    assert black_distance(course, INITIAL_POSE[0], INITIAL_POSE[1]) < 0.010


@pytest.mark.parametrize('theta', [0.0, math.pi])
def test_line_following(course, theta):
    """ 制御則で60秒間走行し，ライン付近を走り続けること
        （ROS のトピック経由と同じく，制御は1ステップ遅れて反映） """
    lf = LFPhysicalModel(course)
    lf.set_pose(INITIAL_POSE[0], INITIAL_POSE[1], theta)
    cmd = (0.0, 0.0)
    on_line = 0
    steps = int(60*FPS)
    for _ in range(steps):
        lf.step(cmd, 1/FPS)
        cmd = prs2mtrs(lf.sense())
        x, y, _ = lf.pose
        if black_distance(course, x, y) < 0.030:
            on_line += 1
    assert on_line/steps > 0.8


def test_encoder_tracks_true_rpm(course):
    lf = LFPhysicalModel(course)
    lf.set_pose(*INITIAL_POSE)
    meas, true = [], []
    for k in range(int(20*FPS)):
        lf.step((0.5, 0.5), 1/FPS)
        if k > FPS:  # 立ち上がりの1秒を除く
            meas.append(np.mean(lf.read_encoders_rpm()))
            true.append(np.mean(lf.wheels_rpm_true))
    assert abs(np.mean(meas) - np.mean(true)) < 0.05*np.mean(true)
