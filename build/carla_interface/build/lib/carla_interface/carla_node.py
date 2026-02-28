import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
import carla
import numpy as np
import cv2
from cv_bridge import CvBridge

class CarlaNode(Node):
    def __init__(self):
        super().__init__('carla_node')
        self.bridge = CvBridge()
        self.image_pub = self.create_publisher(Image, 'carla_camera/image_raw', 10)
        
        # Connect to CARLA
        self.client = carla.Client('localhost', 2000)
        self.client.set_timeout(10.0)
        self.world = self.client.get_world()
        blueprint_library = self.world.get_blueprint_library()
        
        vehicle_bp = blueprint_library.filter('vehicle.*')[0]
        spawn_point = self.world.get_map().get_spawn_points()[0]
        self.vehicle = self.world.spawn_actor(vehicle_bp, spawn_point)
        
        camera_bp = blueprint_library.find('sensor.camera.rgb')
        camera_bp.set_attribute('image_size_x', '640')
        camera_bp.set_attribute('image_size_y', '480')
        camera_bp.set_attribute('fov', '110')
        camera_transform = carla.Transform(carla.Location(x=1.5, z=2.4))
        self.camera = self.world.spawn_actor(camera_bp, camera_transform, attach_to=self.vehicle)
        self.camera.listen(self.camera_callback)
    
    def camera_callback(self, image):
        array = np.frombuffer(image.raw_data, dtype=np.uint8).reshape((image.height, image.width, 4))
        array = array[:, :, :3]  # drop alpha
        msg = self.bridge.cv2_to_imgmsg(array, encoding="rgb8")
        self.image_pub.publish(msg)
        self.get_logger().info('Published camera frame')

def main(args=None):
    rclpy.init(args=args)
    node = CarlaNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.camera.stop()
        node.vehicle.destroy()
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()