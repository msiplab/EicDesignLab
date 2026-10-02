# coding: UTF-8
"""
ライントレーサシミュレータの起動

  $ ros2 launch lf_sim lf_sim.launch.py
  $ ros2 launch lf_sim lf_sim.launch.py log_csv:=true     # 走行データを CSV に保存
  $ ros2 launch lf_sim lf_sim.launch.py use_rviz:=false   # RViz2 を起動しない
  $ ros2 launch lf_sim lf_sim.launch.py controller:=false # 制御ノードを起動しない（MATLAB などの制御ノードを使う）
"""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    share = get_package_share_directory('lf_sim')
    log_csv = LaunchConfiguration('log_csv')
    use_rviz = LaunchConfiguration('use_rviz')
    controller = LaunchConfiguration('controller')

    return LaunchDescription([
        DeclareLaunchArgument('log_csv', default_value='false',
                              description='走行データを CSV ファイルに保存する'),
        DeclareLaunchArgument('use_rviz', default_value='true',
                              description='RViz2 を起動する'),
        DeclareLaunchArgument('controller', default_value='true',
                              description='制御ノード lf_controller を起動する'),
        Node(package='lf_sim', executable='body', name='lf_body', output='screen',
             parameters=[{'log_csv': log_csv}]),
        Node(package='lf_sim', executable='controller', name='lf_controller', output='screen',
             condition=IfCondition(controller)),
        Node(package='rviz2', executable='rviz2', name='rviz2',
             arguments=['-d', os.path.join(share, 'rviz', 'lf_sim.rviz')],
             condition=IfCondition(use_rviz)),
    ])
