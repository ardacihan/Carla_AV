import rclpy
from rclpy.node import Node
import carla
import random
import numpy as np
from sensor_msgs.msg import PointCloud2, Image, NavSatFix, Imu
from std_msgs.msg import Header
from geometry_msgs.msg import Vector3
import sensor_msgs_py.point_cloud2 as pc2
from cv_bridge import CvBridge


class CarlaInterface(Node):

    def __init__(self):
        super().__init__('carla_interface')

        # ── Connect to CARLA ──────────────────────────────────────────
        self.client = carla.Client('localhost', 2000)
        self.client.set_timeout(10.0)
        self.world = self.client.get_world()
        self.bridge = CvBridge()
        self.actors = []  # track all spawned actors for cleanup

        # ── Synchronous mode ──────────────────────────────────────────
        settings = self.world.get_settings()
        settings.synchronous_mode = True
        settings.fixed_delta_seconds = 0.05  # 20 Hz
        self.world.apply_settings(settings)

        bp_lib = self.world.get_blueprint_library()

        # ── Spawn ego vehicle ─────────────────────────────────────────
        vehicle_bp = bp_lib.find('vehicle.tesla.model3')
        spawn_point = random.choice(self.world.get_map().get_spawn_points())
        self.vehicle = self.world.spawn_actor(vehicle_bp, spawn_point)
        self.actors.append(self.vehicle)
        self.get_logger().info(f"Vehicle spawned at {spawn_point.location}")

        # ── Publishers ────────────────────────────────────────────────
        self.lidar_pub  = self.create_publisher(PointCloud2, '/lidar/points', 10)
        self.camera_pub = self.create_publisher(Image,       '/camera/image_raw', 10)
        self.gnss_pub   = self.create_publisher(NavSatFix,   '/gnss/fix', 10)
        self.imu_pub    = self.create_publisher(Imu,         '/imu/data', 10)

        # ── LiDAR ─────────────────────────────────────────────────────
        lidar_bp = bp_lib.find('sensor.lidar.ray_cast')
        lidar_bp.set_attribute('range',              '100')
        lidar_bp.set_attribute('channels',           '32')
        lidar_bp.set_attribute('points_per_second',  '100000')
        lidar_bp.set_attribute('rotation_frequency', '20')
        lidar_bp.set_attribute('upper_fov',          '10')
        lidar_bp.set_attribute('lower_fov',          '-30')
        lidar_tf = carla.Transform(carla.Location(x=0.0, z=2.5))
        lidar = self.world.spawn_actor(lidar_bp, lidar_tf, attach_to=self.vehicle)
        lidar.listen(self.lidar_callback)
        self.actors.append(lidar)

        # ── RGB Camera ────────────────────────────────────────────────
        cam_bp = bp_lib.find('sensor.camera.rgb')
        cam_bp.set_attribute('image_size_x', '800')
        cam_bp.set_attribute('image_size_y', '600')
        cam_bp.set_attribute('fov',          '90')
        cam_tf = carla.Transform(carla.Location(x=1.5, z=2.2))
        camera = self.world.spawn_actor(cam_bp, cam_tf, attach_to=self.vehicle)
        camera.listen(self.camera_callback)
        self.actors.append(camera)

        # ── GNSS ──────────────────────────────────────────────────────
        gnss_bp = bp_lib.find('sensor.other.gnss')
        gnss_bp.set_attribute('sensor_tick', '0.1')
        gnss_tf = carla.Transform(carla.Location(x=0.0, z=2.0))
        gnss = self.world.spawn_actor(gnss_bp, gnss_tf, attach_to=self.vehicle)
        gnss.listen(self.gnss_callback)
        self.actors.append(gnss)

        # ── IMU ───────────────────────────────────────────────────────
        imu_bp = bp_lib.find('sensor.other.imu')
        imu_bp.set_attribute('sensor_tick', '0.05')
        imu_tf = carla.Transform(carla.Location(x=0.0, z=1.0))
        imu = self.world.spawn_actor(imu_bp, imu_tf, attach_to=self.vehicle)
        imu.listen(self.imu_callback)
        self.actors.append(imu)

        # ── World tick timer ──────────────────────────────────────────
        self.timer = self.create_timer(0.05, self.tick_world)
        self.get_logger().info("CarlaInterface ready — all sensors spawned")

    # ── Tick ──────────────────────────────────────────────────────────
    def tick_world(self):
        self.world.tick()

    # ── Sensor callbacks ──────────────────────────────────────────────
    def lidar_callback(self, point_cloud):
        points = np.frombuffer(point_cloud.raw_data, dtype=np.float32).reshape(-1, 4)
        header = self._make_header("lidar")
        msg = pc2.create_cloud_xyz32(header, points[:, :3])
        self.lidar_pub.publish(msg)

    def camera_callback(self, image):
        # CARLA gives BGRA; convert to BGR for cv_bridge
        array = np.frombuffer(image.raw_data, dtype=np.uint8)
        array = array.reshape((image.height, image.width, 4))
        bgr = array[:, :, :3]
        msg = self.bridge.cv2_to_imgmsg(bgr, encoding='bgr8')
        msg.header = self._make_header("camera")
        self.camera_pub.publish(msg)

    def gnss_callback(self, gnss):
        msg = NavSatFix()
        msg.header   = self._make_header("gnss")
        msg.latitude  = gnss.latitude
        msg.longitude = gnss.longitude
        msg.altitude  = gnss.altitude
        self.gnss_pub.publish(msg)

    def imu_callback(self, imu):
        msg = Imu()
        msg.header = self._make_header("imu")
        msg.linear_acceleration.x = imu.accelerometer.x
        msg.linear_acceleration.y = imu.accelerometer.y
        msg.linear_acceleration.z = imu.accelerometer.z
        msg.angular_velocity.x = imu.gyroscope.x
        msg.angular_velocity.y = imu.gyroscope.y
        msg.angular_velocity.z = imu.gyroscope.z
        self.imu_pub.publish(msg)

    # ── Helpers ───────────────────────────────────────────────────────
    def _make_header(self, frame_id: str) -> Header:
        h = Header()
        h.stamp    = self.get_clock().now().to_msg()
        h.frame_id = frame_id
        return h

    def destroy_node(self):
        self.get_logger().info("Destroying actors...")
        # Restore async mode before exit
        settings = self.world.get_settings()
        settings.synchronous_mode = False
        self.world.apply_settings(settings)
        for actor in reversed(self.actors):
            if actor.is_alive:
                actor.destroy()
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = CarlaInterface()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()