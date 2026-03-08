# CARLA + ROS2 Simulation Setup

This guide launches a CARLA simulation on the host and publishes sensor data through ROS2 nodes running inside Docker.

You can then subscribe to those topics from the host using ROS2 tools like `ros2 topic` or RViz.

---

# Requirements

Host system:

Ubuntu 22.04
ROS2 Humble installed
Docker installed
CARLA 0.9.16 downloaded
---

# Step 1 — Start the CARLA simulator

Open a terminal on the host:

cd ~/Carla_Sim

./CarlaUE4.sh -RenderOffScreen

---

# Step 2 — Build the ROS2 Docker image

Open a new terminal.

cd ~/ros2_carla_ws

docker build -t carla_ros2 .

---

# Step 3 — Start the ROS container

Run the container using host networking so ROS DDS can communicate with the host.

docker run -it --rm --network host -e ROS_DOMAIN_ID=0 -e RMW_IMPLEMENTATION=rmw_fastrtps_cpp -e ROS_LOCALHOST_ONLY=0 carla_ros2

---

# Step 4 — Launch ROS nodes

Inside the container:

ros2 launch carla_interface racing.launch.py

You should see messages like:

Vehicle spawned ...
CarlaInterface ready — all sensors spawned

---

# Step 5 — Verify topics from host

Open a new host terminal.

source /opt/ros/humble/setup.bash

List topics:

ros2 topic list

Expected output:

/lidar/points
/camera/image_raw
/gnss/fix
/imu/data

---

# Step 6 — Subscribe to sensor data

Example:

ros2 topic echo /imu/data --qos-reliability best_effort

---

# Step 7 — Visualize LiDAR (optional)

Run RViz on the host:

rviz2

Add a display:

PointCloud2

Set topic:

/lidar/points

---

# Recommended terminal layout

Terminal 1 (host)

cd ~/Desktop/Carla_Sim
./CarlaUE4.sh -windowed

Terminal 2 (host)

cd ~/ros2_carla_ws
docker run --network host carla_ros2

Terminal 3 (container)

ros2 launch carla_interface racing.launch.py

Terminal 4 (host)

ros2 topic echo /imu/data

Terminal 5 (host optional)

rviz2
