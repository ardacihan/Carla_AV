from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        # CARLA ROS Bridge
        Node(
            package='carla_ros_bridge',
            executable='carla_ros_bridge',
            name='carla_ros_bridge',
            output='screen'
        ),

        # Example perception node
        Node(
            package='your_nodes',
            executable='lidar_listener_node',
            name='lidar_listener',
            output='screen'
        ),
    ])