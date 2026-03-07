from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(
            package='carla_interface',
            executable='interface_node',
            name='carla_interface',
            output='screen',
            emulate_tty=True,
        ),
    ])