import rclpy
from rclpy.node import Node
from sensor_msgs.msg import PointCloud2


class LidarProcessing(Node):

    def __init__(self):
        super().__init__('lidar_processing')

        self.subscription = self.create_subscription(
            PointCloud2,
            '/lidar/points',
            self.lidar_callback,
            10
        )

    def lidar_callback(self, msg):
        self.get_logger().info("Received LiDAR frame")


def main(args=None):
    rclpy.init(args=args)
    node = LidarProcessing()
    rclpy.spin(node)
    rclpy.shutdown()