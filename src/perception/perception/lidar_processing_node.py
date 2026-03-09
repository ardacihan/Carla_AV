import rclpy
from rclpy.node import Node
from sensor_msgs.msg import PointCloud2


class LidarProcessing(Node):

    def __init__(self):
        super().__init__('lidar_processing')

        self.subscription = self.create_subscription(
            PointCloud2,
            '/carla/hero/lidar',
            self.lidar_callback,
            10
        )

    def lidar_callback(self, msg):
        self.get_logger().info("Received LiDAR frame")
        self.get_logger().info(f"PointCloud2 data: width={msg.width}, height={msg.height}, point_step={msg.point_step}")


def main(args=None):
    rclpy.init(args=args)
    node = LidarProcessing()
    rclpy.spin(node)
    rclpy.shutdown()