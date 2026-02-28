import rclpy
from rclpy.node import Node
import carla
import random
import numpy as np
from sensor_msgs.msg import PointCloud2
from std_msgs.msg import Header
import sensor_msgs_py.point_cloud2 as pc2


class CarlaInterface(Node):

    def __init__(self):
        super().__init__('carla_interface')

        # Connect
        self.client = carla.Client('localhost', 2000)
        self.client.set_timeout(10.0)
        self.world = self.client.get_world()

        # Synchronous mode
        settings = self.world.get_settings()
        settings.synchronous_mode = True
        settings.fixed_delta_seconds = 0.05
        self.world.apply_settings(settings)

        blueprint_library = self.world.get_blueprint_library()

        # Spawn vehicle
        vehicle_bp = blueprint_library.find('vehicle.tesla.model3')
        spawn_point = random.choice(self.world.get_map().get_spawn_points())
        self.vehicle = self.world.spawn_actor(vehicle_bp, spawn_point)

        self.get_logger().info("Vehicle spawned")

        # Publisher
        self.lidar_pub = self.create_publisher(PointCloud2, '/lidar/points', 10)

        # Spawn LiDAR
        lidar_bp = blueprint_library.find('sensor.lidar.ray_cast')
        lidar_bp.set_attribute('range', '100')
        lidar_bp.set_attribute('channels', '32')

        lidar_transform = carla.Transform(carla.Location(x=0.0, z=2.5))
        self.lidar = self.world.spawn_actor(
            lidar_bp,
            lidar_transform,
            attach_to=self.vehicle
        )

        self.lidar.listen(self.lidar_callback)

        self.timer = self.create_timer(0.05, self.tick_world)

    def tick_world(self):
        self.world.tick()

    def lidar_callback(self, point_cloud):
        points = np.frombuffer(point_cloud.raw_data, dtype=np.float32)
        points = np.reshape(points, (-1, 4))

        header = Header()
        header.stamp = self.get_clock().now().to_msg()
        header.frame_id = "lidar"

        msg = pc2.create_cloud_xyz32(header, points[:, :3])
        self.lidar_pub.publish(msg)

    def destroy_node(self):
        self.lidar.stop()
        self.lidar.destroy()
        self.vehicle.destroy()
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = CarlaInterface()
    rclpy.spin(node)
    rclpy.shutdown()