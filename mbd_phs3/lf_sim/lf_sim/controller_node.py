# coding: UTF-8
"""
ライントレーサ制御ノード

  購読  /photorefs   std_msgs/Float32MultiArray  フォトリフレクタの値（左から順）
  配信  /cmd_motors  std_msgs/Float32MultiArray  モータ制御信号（左，右）

「電子情報通信設計製図」新潟大学工学部工学科電子情報通信プログラム

All rights reserved 2026 (c) Shogo MURAMATSU
"""
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32MultiArray

from .controller import prs2mtrs


class LFControllerNode(Node):

    def __init__(self):
        super().__init__('lf_controller')
        self._pub = self.create_publisher(Float32MultiArray, 'cmd_motors', 10)
        self.create_subscription(Float32MultiArray, 'photorefs', self._on_photorefs, 10)

    def _on_photorefs(self, msg):
        mtr_left, mtr_right = prs2mtrs(msg.data)
        self._pub.publish(Float32MultiArray(data=[float(mtr_left), float(mtr_right)]))


def main(args=None):
    rclpy.init(args=args)
    node = LFControllerNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
