"""
Vehicle control node.

Subscribes to:
  /carla/ego_vehicle/speedometer    (std_msgs/Float32)
  /carla/ego_vehicle/odometry       (nav_msgs/Odometry)

Publishes:
  /carla/ego_vehicle/vehicle_control_cmd  (carla_msgs/CarlaEgoVehicleControl)
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32
from nav_msgs.msg import Odometry
from carla_msgs.msg import CarlaEgoVehicleControl
from rclpy.qos import QoSProfile, ReliabilityPolicy, DurabilityPolicy

BEST_EFFORT_QOS = QoSProfile(
    reliability=ReliabilityPolicy.BEST_EFFORT,
    durability=DurabilityPolicy.VOLATILE,
    depth=10,
)

class ControlNode(Node):

    def __init__(self):
        super().__init__('control_node')

        # ── Parameters ──────────────────────────────────────────────────
        self.declare_parameter('target_speed_mps', 5.0)
        self.declare_parameter('max_throttle', 0.6)
        self.declare_parameter('max_brake', 1.0)

        self.target_speed = self.get_parameter('target_speed_mps').value
        self.max_throttle = self.get_parameter('max_throttle').value
        self.max_brake    = self.get_parameter('max_brake').value

        self.current_speed: float = 0.0

        # ── Subscribers ─────────────────────────────────────────────────
        self.create_subscription(
            Float32,
            '/carla/hero/speedometer',
            self._speed_callback,
            BEST_EFFORT_QOS,
        )
        self.create_subscription(
            Odometry,
            '/carla/hero/odometry',
            self._odom_callback,
            BEST_EFFORT_QOS,
        )

        # ── Publisher ───────────────────────────────────────────────────
        self.control_pub = self.create_publisher(
            CarlaEgoVehicleControl,
            '/carla/hero/vehicle_control_cmd',
            BEST_EFFORT_QOS,
        )

        # ── Control loop at 20 Hz ────────────────────────────────────────
        self.create_timer(0.05, self._control_loop)

        self.get_logger().info(
            f'ControlNode ready — target speed {self.target_speed} m/s'
        )

    # ── Callbacks ────────────────────────────────────────────────────────
    def _speed_callback(self, msg: Float32):
        self.current_speed = msg.data

    def _odom_callback(self, msg: Odometry):
        # available when you need pose / heading
        pass

    # ── Control loop ─────────────────────────────────────────────────────
    def _control_loop(self):
        cmd = self._compute_control()
        self.control_pub.publish(cmd)

    def _compute_control(self) -> CarlaEgoVehicleControl:
        """
        Simple proportional speed controller.
        Replace this method with your own algorithm.
        steer range : -1.0 (full left) → +1.0 (full right)
        throttle    :  0.0 → 1.0
        brake       :  0.0 → 1.0
        """
        cmd = CarlaEgoVehicleControl()
        cmd.hand_brake = False
        cmd.reverse    = False
        cmd.manual_gear_shift = False
        cmd.steer = 0.0  # ← your steering logic goes here

        error = self.target_speed - self.current_speed

        if error > 0:
            cmd.throttle = float(min(0.2 * error, self.max_throttle))
            cmd.brake    = 0.0
        else:
            cmd.throttle = 0.0
            cmd.brake    = float(min(0.5 * abs(error), self.max_brake))

        self.get_logger().debug(
            f'speed={self.current_speed:.2f}  target={self.target_speed:.2f}  '
            f'throttle={cmd.throttle:.2f}  brake={cmd.brake:.2f}'
        )
        return cmd


def main(args=None):
    rclpy.init(args=args)
    node = ControlNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()