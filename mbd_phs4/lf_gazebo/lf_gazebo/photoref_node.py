# coding: UTF-8
"""
フォトリフレクタノード（Gazebo のカメラ画像から /photorefs を求める）

  購読  /photoref_camera/image  sensor_msgs/Image
  配信  /photorefs              std_msgs/Float32MultiArray  フォトリフレクタの値（左から順，白で1，黒で0）

「電子情報通信設計製図」新潟大学工学部工学科電子情報通信プログラム

All rights reserved 2026 (c) Shogo MURAMATSU
"""
import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import Image
from std_msgs.msg import Float32MultiArray

from .sensing import sensor_pixels, photoref_values, rgb_to_gray


class LFPhotorefNode(Node):

    def __init__(self):
        super().__init__('lf_photorefs')
        self.declare_parameter('threshold', 128)
        self._threshold = self.get_parameter('threshold').value
        self._pixels = None
        self._pub = self.create_publisher(Float32MultiArray, 'photorefs', 10)
        self.create_subscription(Image, 'photoref_camera/image', self._on_image, qos_profile_sensor_data)

    def _on_image(self, msg):
        if msg.encoding not in ('rgb8', 'bgr8'):
            self.get_logger().warn('unsupported encoding: {}'.format(msg.encoding), once=True)
            return
        if self._pixels is None:
            self._pixels = sensor_pixels(msg.width, msg.height)
            self.get_logger().info('sensor pixels (col, row): {}'.format(self._pixels))
        gray = rgb_to_gray(msg.data, msg.width, msg.height, msg.step)
        values = photoref_values(gray, self._pixels, self._threshold)
        self._pub.publish(Float32MultiArray(data=values))


def main(args=None):
    rclpy.init(args=args)
    node = LFPhotorefNode()
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
