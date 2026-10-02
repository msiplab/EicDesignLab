# coding: UTF-8
"""
Gazebo 版ライントレーサシミュレータの起動

  $ ros2 launch lf_gazebo lf_gazebo.launch.py
  $ ros2 launch lf_gazebo lf_gazebo.launch.py headless:=true   # Gazebo の画面を表示しない
  $ ros2 launch lf_gazebo lf_gazebo.launch.py controller:=false # 制御ノードを起動しない（MATLAB などの制御ノードを使う）

  制御ノードは mbd_phs3（lf_sim パッケージ）の lf_controller をそのまま使う．
"""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, OpaqueFunction, SetEnvironmentVariable
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def _gazebo(context):
    share = get_package_share_directory('lf_gazebo')
    world = os.path.join(share, 'worlds', 'lf_course.sdf')
    headless = LaunchConfiguration('headless').perform(context).lower() in ('true', '1')
    gz_args = '-r -s --headless-rendering ' + world if headless else '-r ' + world
    return [IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(
            get_package_share_directory('ros_gz_sim'), 'launch', 'gz_sim.launch.py')),
        launch_arguments={'gz_args': gz_args}.items())]


def generate_launch_description():
    share = get_package_share_directory('lf_gazebo')
    models = os.path.join(share, 'models')
    resource_path = models + os.pathsep + os.environ.get('GZ_SIM_RESOURCE_PATH', '')
    sim_time = {'use_sim_time': True}

    return LaunchDescription([
        DeclareLaunchArgument('headless', default_value='false',
                              description='Gazebo の画面を表示しない'),
        DeclareLaunchArgument('controller', default_value='true',
                              description='制御ノード lf_controller を起動する'),
        SetEnvironmentVariable('GZ_SIM_RESOURCE_PATH', resource_path),
        OpaqueFunction(function=_gazebo),
        Node(package='ros_gz_bridge', executable='parameter_bridge', name='lf_bridge', output='screen',
             parameters=[{'config_file': os.path.join(share, 'config', 'bridge.yaml')}, sim_time]),
        Node(package='lf_gazebo', executable='photorefs', name='lf_photorefs', output='screen',
             parameters=[sim_time]),
        Node(package='lf_gazebo', executable='motors', name='lf_motors', output='screen',
             parameters=[sim_time]),
        Node(package='lf_gazebo', executable='encoders', name='lf_encoders', output='screen',
             parameters=[sim_time]),
        Node(package='lf_sim', executable='controller', name='lf_controller', output='screen',
             parameters=[sim_time], condition=IfCondition(LaunchConfiguration('controller'))),
    ])
