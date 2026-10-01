# coding: UTF-8
"""
ライントレーサ車体（物理モデル）ノード

  購読  /cmd_motors      std_msgs/Float32MultiArray        モータ制御信号（左，右）[-1,1]
        /initialpose     geometry_msgs/PoseWithCovarianceStamped  車体の位置と向きの設定（RViz2 の 2D Pose Estimate）
  配信  /photorefs       std_msgs/Float32MultiArray        フォトリフレクタの値（左から順，白で1，黒で0）
        /wheel_rpm       std_msgs/Float32MultiArray        ロータリーエンコーダで計測した左右の車輪の回転数 [rpm]
        /wheel_rpm_true  std_msgs/Float32MultiArray        物理モデルから求めた左右の車輪の回転数（真値） [rpm]
        /odom            nav_msgs/Odometry                 車体の位置・姿勢と速度
        /map             nav_msgs/OccupancyGrid            コース（ラインを占有セルとして表示）
        /lf_markers      visualization_msgs/MarkerArray    車体の表示用マーカー
        TF  map → base_link
  サービス  ~/set_running  std_srvs/SetBool                走行の開始（true）と停止（false）

  パラメータ
        course_image          コース画像のファイル名
        course_resolution_mm  コース画像の解像度 [mm/pixel]
        rate_hz               シミュレーションの周期 [Hz]
        initial_pose          初期位置と向き [x (m), y (m), θ (rad)]
        log_csv               true なら走行データを CSV ファイル（lf_sim_日時.csv）に保存

「電子情報通信設計製図」新潟大学工学部工学科電子情報通信プログラム

All rights reserved 2026 (c) Shogo MURAMATSU
"""
import csv
import math
import os
from datetime import datetime

import numpy as np
import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from rclpy.qos import QoSProfile, DurabilityPolicy, ReliabilityPolicy
from ament_index_python.packages import get_package_share_directory
from std_msgs.msg import Float32MultiArray, ColorRGBA
from std_srvs.srv import SetBool
from geometry_msgs.msg import PoseWithCovarianceStamped, TransformStamped, Quaternion, Vector3
from nav_msgs.msg import Odometry, OccupancyGrid
from visualization_msgs.msg import Marker, MarkerArray
from tf2_ros import TransformBroadcaster

from .model import LFCourse, LFPhysicalModel, PARAMS_L_C, TIRE_DIAMETER

CMD_TIMEOUT_S = 0.5  # この時間モータ制御信号が来なければ停止


def yaw_to_quaternion(yaw):
    return Quaternion(x=0.0, y=0.0, z=math.sin(yaw/2), w=math.cos(yaw/2))


def quaternion_to_yaw(q):
    return math.atan2(2*(q.w*q.z + q.x*q.y), 1 - 2*(q.y*q.y + q.z*q.z))


class LFBodyNode(Node):

    def __init__(self):
        super().__init__('lf_body')

        # パラメータ
        share = get_package_share_directory('lf_sim')
        self.declare_parameter('course_image', os.path.join(share, 'images', 'course2025.png'))
        self.declare_parameter('course_resolution_mm', 2.5)
        self.declare_parameter('rate_hz', 20.0)
        self.declare_parameter('initial_pose', [0.75, 0.81, 0.0])
        self.declare_parameter('log_csv', False)
        course_image = self.get_parameter('course_image').value
        res_mm = self.get_parameter('course_resolution_mm').value
        self._rate_hz = self.get_parameter('rate_hz').value
        x0, y0, th0 = self.get_parameter('initial_pose').value

        # コースと物理モデル
        self._course = LFCourse(course_image, res_mm=res_mm)
        self._model = LFPhysicalModel(self._course)
        self._model.set_pose(x0, y0, th0)
        self._cmd = (0.0, 0.0)
        self._cmd_time = None
        self._running = True
        self._time_s = 0.0

        # 配信・購読・サービス
        self._pub_prs = self.create_publisher(Float32MultiArray, 'photorefs', 10)
        self._pub_rpm = self.create_publisher(Float32MultiArray, 'wheel_rpm', 10)
        self._pub_rpm_true = self.create_publisher(Float32MultiArray, 'wheel_rpm_true', 10)
        self._pub_odom = self.create_publisher(Odometry, 'odom', 10)
        self._pub_markers = self.create_publisher(MarkerArray, 'lf_markers', 10)
        map_qos = QoSProfile(depth=1, durability=DurabilityPolicy.TRANSIENT_LOCAL,
                             reliability=ReliabilityPolicy.RELIABLE)
        self._pub_map = self.create_publisher(OccupancyGrid, 'map', map_qos)
        self.create_subscription(Float32MultiArray, 'cmd_motors', self._on_cmd, 10)
        self.create_subscription(PoseWithCovarianceStamped, 'initialpose', self._on_initialpose, 10)
        self.create_service(SetBool, '~/set_running', self._on_set_running)
        self._tf = TransformBroadcaster(self)

        # 走行データのログ保存
        self._csv_file = None
        if self.get_parameter('log_csv').value:
            self._open_csv()

        self._publish_map()
        self.create_timer(1.0/self._rate_hz, self._on_timer)
        self.get_logger().info('course: {}'.format(course_image))

    # ------------------------------------------------------------------
    def _on_cmd(self, msg):
        if len(msg.data) >= 2:
            self._cmd = (float(msg.data[0]), float(msg.data[1]))
            self._cmd_time = self.get_clock().now()

    def _on_initialpose(self, msg):
        p = msg.pose.pose
        self._model.set_pose(p.position.x, p.position.y, quaternion_to_yaw(p.orientation))
        self.get_logger().info('pose set: x={:.3f} y={:.3f}'.format(p.position.x, p.position.y))

    def _on_set_running(self, request, response):
        self._running = request.data
        if not self._running:
            self._model.reset()
        response.success = True
        response.message = 'running' if self._running else 'stopped'
        return response

    def _on_timer(self):
        h = 1.0/self._rate_hz
        if self._running:
            cmd = self._cmd
            if self._cmd_time is None or \
                    (self.get_clock().now() - self._cmd_time).nanoseconds*1e-9 > CMD_TIMEOUT_S:
                cmd = (0.0, 0.0)
            self._model.step(cmd, h)
            self._time_s += h
            self._write_csv()
        self._publish_state()

    # ------------------------------------------------------------------
    def _publish_state(self):
        now = self.get_clock().now().to_msg()
        x, y, th = self._model.pose

        self._pub_prs.publish(Float32MultiArray(data=[float(v) for v in self._model.sense()]))
        self._pub_rpm.publish(Float32MultiArray(data=[float(v) for v in self._model.read_encoders_rpm()]))
        self._pub_rpm_true.publish(Float32MultiArray(data=[float(v) for v in self._model.wheels_rpm_true]))

        odom = Odometry()
        odom.header.stamp = now
        odom.header.frame_id = 'map'
        odom.child_frame_id = 'base_link'
        odom.pose.pose.position.x = float(x)
        odom.pose.pose.position.y = float(y)
        odom.pose.pose.orientation = yaw_to_quaternion(th)
        odom.twist.twist.linear.x = float(self._model.velocity)
        odom.twist.twist.angular.z = float(self._model.angular_velocity)
        self._pub_odom.publish(odom)

        tf = TransformStamped()
        tf.header.stamp = now
        tf.header.frame_id = 'map'
        tf.child_frame_id = 'base_link'
        tf.transform.translation.x = float(x)
        tf.transform.translation.y = float(y)
        tf.transform.rotation = yaw_to_quaternion(th)
        self._tf.sendTransform(tf)

        self._pub_markers.publish(self._make_markers(now))

    def _make_markers(self, stamp):
        markers = MarkerArray()

        def marker(mid, mtype, x, y, z, scale, color, yaw=0.0, roll=0.0):
            m = Marker()
            m.header.stamp = stamp
            m.header.frame_id = 'base_link'
            m.ns = 'lf'
            m.id = mid
            m.type = mtype
            m.action = Marker.ADD
            m.pose.position.x, m.pose.position.y, m.pose.position.z = x, y, z
            # roll（x 軸回り）と yaw（z 軸回り）だけを扱う
            cr, sr = math.cos(roll/2), math.sin(roll/2)
            cy, sy = math.cos(yaw/2), math.sin(yaw/2)
            m.pose.orientation = Quaternion(x=sr*cy, y=sr*sy, z=cr*sy, w=cr*cy)
            m.scale = Vector3(x=scale[0], y=scale[1], z=scale[2])
            m.color = ColorRGBA(r=color[0], g=color[1], b=color[2], a=color[3])
            return m

        # 車体（mbd_phs2 の描画と同じ大きさ：前後 -35〜95 mm，左右 ±35 mm）
        markers.markers.append(marker(0, Marker.CUBE, 0.030, 0.0, 0.010,
                                      (0.130, 0.070, 0.020), (1.0, 0.5, 0.0, 0.8)))
        # 左右の車輪
        for k, side in enumerate((1.0, -1.0)):
            markers.markers.append(marker(1+k, Marker.CYLINDER, 0.0, side*PARAMS_L_C/2, 0.010,
                                          (TIRE_DIAMETER, TIRE_DIAMETER, 0.012),
                                          (0.1, 0.1, 0.1, 1.0), roll=math.pi/2))
        # フォトリフレクタ（白を検出すると赤く表示）
        for k, ((dx, dy), value) in enumerate(zip(self._model.sensor_positions(), self._model.sense())):
            markers.markers.append(marker(3+k, Marker.SPHERE, dx, dy, 0.025,
                                          (0.012, 0.012, 0.012), (float(value), 0.0, 0.0, 1.0)))
        return markers

    def _publish_map(self):
        white = self._course.white[::-1, :]  # OccupancyGrid は下の行から並べる
        grid = OccupancyGrid()
        grid.header.stamp = self.get_clock().now().to_msg()
        grid.header.frame_id = 'map'
        grid.info.resolution = float(self._course.resolution)
        grid.info.width = self._course.width_px
        grid.info.height = self._course.height_px
        grid.info.origin.orientation.w = 1.0
        grid.data = np.where(white, 0, 100).astype(np.int8).flatten().tolist()
        self._pub_map.publish(grid)

    # ------------------------------------------------------------------
    def _open_csv(self):
        stamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self._csv_name = 'lf_sim_{}.csv'.format(stamp)
        # 1行ごとにファイルへ書き出す（途中で停止しても記録が残るように）
        self._csv_file = open(self._csv_name, 'w', newline='', encoding='utf-8', buffering=1)
        self._csv = csv.writer(self._csv_file)
        self._csv.writerow(['time_s', 'u_left', 'u_right', 'rpm_left', 'rpm_right',
                            'rpm_left_true', 'rpm_right_true', 'v_m_s', 'w_rad_s',
                            'x_m', 'y_m', 'theta_rad'])
        self.get_logger().info('logging to {}'.format(os.path.abspath(self._csv_name)))

    def _write_csv(self):
        if self._csv_file is None:
            return
        m = self._model
        x, y, th = m.pose
        u_l, u_r = m.motor_signals
        rpm_l, rpm_r = m.read_encoders_rpm()
        rpm_lt, rpm_rt = m.wheels_rpm_true
        self._csv.writerow(['{:.3f}'.format(self._time_s),
                            '{:.3f}'.format(u_l), '{:.3f}'.format(u_r),
                            '{:.1f}'.format(rpm_l), '{:.1f}'.format(rpm_r),
                            '{:.1f}'.format(rpm_lt), '{:.1f}'.format(rpm_rt),
                            '{:.4f}'.format(m.velocity), '{:.3f}'.format(m.angular_velocity),
                            '{:.4f}'.format(x), '{:.4f}'.format(y), '{:.3f}'.format(th)])

    def close_csv(self):
        if self._csv_file is not None:
            self._csv_file.close()
            self._csv_file = None
            print('saved {}'.format(os.path.abspath(self._csv_name)))


def main(args=None):
    rclpy.init(args=args)
    node = LFBodyNode()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        node.close_csv()
        try:
            node.destroy_node()
            rclpy.try_shutdown()
        except KeyboardInterrupt:  # 終了処理中に再度 Ctrl+C が押された場合
            pass


if __name__ == '__main__':
    main()
