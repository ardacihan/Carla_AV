import rclpy
from rclpy.node import Node
from sensor_msgs.msg import PointCloud2
from rclpy.qos import QoSProfile, ReliabilityPolicy, DurabilityPolicy

BEST_EFFORT_QOS = QoSProfile(
    reliability=ReliabilityPolicy.BEST_EFFORT,
    durability=DurabilityPolicy.VOLATILE,
    depth=10,
)


class LidarProcessing(Node):

    def __init__(self):
        super().__init__('lidar_processing')

        self.subscription = self.create_subscription(
            PointCloud2,
            '/carla/hero/lidar',
            self.lidar_callback,
            BEST_EFFORT_QOS
        )
        self.get_logger().info('LidarProcessing node started, waiting for data...')

    def lidar_callback(self, msg):
        self.get_logger().info(
            f'LiDAR frame: width={msg.width} height={msg.height} point_step={msg.point_step}'
        )


def main(args=None):
    rclpy.init(args=args)
    node = LidarProcessing()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()