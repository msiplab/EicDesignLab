# coding: UTF-8
"""
モータノード（モータ制御信号から車体の速度指令へ）

  購読  /cmd_motors  std_msgs/Float32MultiArray  モータ制御信号（左，右）[-1,1]
  配信  /cmd_vel     geometry_msgs/Twist         車体の速度と角速度（Gazebo の DiffDrive へ）

  各車輪の回転数はモータ制御信号に比例するものとし，制御信号が1のときの
  回転数をパラメータ max_wheel_rpm で与える．モータの応答の遅れは，
  Gazebo の DiffDrive の加速度の制限（model.sdf）で近似している．

「電子情報通信設計製図」新潟大学工学部工学科電子情報通信プログラム

All rights reserved 2026 (c) Shogo MURAMATSU
"""
import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_msgs.msg import Float32MultiArray

from .sensing import motors_to_twist

CMD_TIMEOUT_S = 0.5  # この時間モータ制御信号が来なければ停止


class LFMotorNode(Node):

    def __init__(self):
        super().__init__('lf_motors')
        self.declare_parameter('max_wheel_rpm', 160.0)
        self.declare_parameter('wheel_radius', 0.029)
        self.declare_parameter('wheel_separation', 0.10)
        self._pub = self.create_publisher(Twist, 'cmd_vel', 10)
        self.create_subscription(Float32MultiArray, 'cmd_motors', self._on_cmd, 10)
        self._last = self.get_clock().now()
        self.create_timer(0.1, self._watchdog)

    def _on_cmd(self, msg):
        if len(msg.data) < 2:
            return
        v, w = motors_to_twist(msg.data[0], msg.data[1],
                               self.get_parameter('max_wheel_rpm').value,
                               self.get_parameter('wheel_radius').value,
                               self.get_parameter('wheel_separation').value)
        twist = Twist()
        twist.linear.x = float(v)
        twist.angular.z = float(w)
        self._pub.publish(twist)
        self._last = self.get_clock().now()

    def _watchdog(self):
        if (self.get_clock().now() - self._last).nanoseconds*1e-9 > CMD_TIMEOUT_S:
            self._pub.publish(Twist())


def main(args=None):
    rclpy.init(args=args)
    node = LFMotorNode()
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
