from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(
            package='carla_interface',
            executable='interface_node',
            output='screen'
        ),
        Node(
            package='racing_perception',
            executable='lidar_processing_node',
            output='screen'
        )
    ])