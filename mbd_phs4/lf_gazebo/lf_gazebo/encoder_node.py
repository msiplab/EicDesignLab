# coding: UTF-8
"""
ロータリーエンコーダノード（車輪の関節の回転から回転数を求める）

  購読  /joint_states    sensor_msgs/JointState         車輪の関節の角速度（Gazebo）
  配信  /wheel_rpm       std_msgs/Float32MultiArray     ロータリーエンコーダで計測した左右の回転数 [rpm]（向きは区別しない）
        /wheel_rpm_true  std_msgs/Float32MultiArray     関節の角速度から求めた左右の回転数（真値，後退は負） [rpm]

  エンコーダの模擬には mbd_phs3（lf_sim パッケージ）の LFRotaryEncoder を使う．

「電子情報通信設計製図」新潟大学工学部工学科電子情報通信プログラム

All rights reserved 2026 (c) Shogo MURAMATSU
"""
import math

import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from sensor_msgs.msg import JointState
from std_msgs.msg import Float32MultiArray

from lf_sim.encoder import LFRotaryEncoder

JOINTS = ('left_wheel_joint', 'right_wheel_joint')


class LFEncoderNode(Node):

    def __init__(self):
        super().__init__('lf_encoders')
        self.declare_parameter('rate_hz', 20.0)
        self._encs = [LFRotaryEncoder(), LFRotaryEncoder()]
        self._omega = [0.0, 0.0]
        self._last_t = None
        self._pub = self.create_publisher(Float32MultiArray, 'wheel_rpm', 10)
        self._pub_true = self.create_publisher(Float32MultiArray, 'wheel_rpm_true', 10)
        self.create_subscription(JointState, 'joint_states', self._on_joint_states, 10)
        self.create_timer(1.0/self.get_parameter('rate_hz').value, self._on_timer)

    def _on_joint_states(self, msg):
        t = msg.header.stamp.sec + msg.header.stamp.nanosec*1e-9
        omega = list(self._omega)
        for k, name in enumerate(JOINTS):
            if name in msg.name and len(msg.velocity) == len(msg.name):
                omega[k] = msg.velocity[msg.name.index(name)]
        if self._last_t is not None and t > self._last_t:
            h = t - self._last_t
            for k in range(2):
                self._encs[k].update(omega[k], h)
        self._last_t = t
        self._omega = omega

    def _on_timer(self):
        rpm = [float(enc.read_rpm()) for enc in self._encs]
        rpm_true = [float(60*w/(2*math.pi)) for w in self._omega]
        self._pub.publish(Float32MultiArray(data=rpm))
        self._pub_true.publish(Float32MultiArray(data=rpm_true))


def main(args=None):
    rclpy.init(args=args)
    node = LFEncoderNode()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    except Exception:
        if rclpy.ok():  # 終了処理中（コンテキストが無効）の例外は無視する
            raise
    finally:
        try:
            node.destroy_node()
            rclpy.try_shutdown()
        except (KeyboardInterrupt, Exception):
            pass


if __name__ == '__main__':
    main()
