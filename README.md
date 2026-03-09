# Launch Guide

## Prerequisites
- CARLA 0.9.15 installed at `~/Desktop/CARLA_0.9.15`
- Docker image `carla_nodes` built from this repo

---

## Architecture Overview
```
Host                    Single Container (carla_nodes)
──────────────          ──────────────────────────────────────
CARLA server  ───────►  carla-ros-bridge  +  rclpy nodes + rviz2
(port 2000)             
```

---

## Step 1 — Start CARLA Server (host)
```bash
cd ~/Desktop/CARLA_0.9.15
./CarlaUE4.sh -RenderOffScreen -carla-rpc-port=2000
```

---

## Step 2 — Build image

```bash
cd ~/CARLA_AV
docker build --no-cache -t carla_nodes .
```

---

## Step 3 — Start container + bridge (Terminal 2)
```bash
docker run -it --rm --network host \
  -e DISPLAY=$DISPLAY \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  carla_nodes bash
```

Inside:
```bash
ros2 launch carla_ros_bridge carla_ros_bridge_with_example_ego_vehicle.launch.py \
  host:=localhost port:=2000 timeout:=10
```

> Add `synchronous_mode:=false` if using manual control to avoid input lag.

Wait for `All objects spawned.`

Another terminal for autopilot
```bash
docker exec -it $(docker ps | grep carla_nodes | awk '{print $1}') bash
ros2 topic pub /carla/hero/enable_autopilot std_msgs/Bool "data: true" --once
```
---

## Step 4 — Run your nodes + rviz2 (Terminal 3)
```bash
docker exec -it $(docker ps | grep carla_nodes | awk '{print $1}') bash
```

**Lidar node + rviz2:**
```bash
ros2 run perception lidar_node &
rviz2
```

In rviz2: Fixed Frame → `hero`, Add → PointCloud2 → `/carla/hero/lidar`

**Control node:**
```bash
ros2 run control control_node
```

With overrides:
```bash
ros2 run control control_node --ros-args -p target_speed_mps:=6.0 -p max_throttle:=0.5
```

---

## Rebuilding after code changes (inside container)
```bash
cd /ros2_ws
colcon build --packages-select perception control
source install/setup.bash
```

---

## Useful Debug Commands
```bash
# Check bridge is publishing
ros2 topic list | grep carla

# Confirm lidar data is flowing
ros2 topic hz /carla/hero/lidar

# Monitor vehicle speed
ros2 topic echo /carla/hero/speedometer

# Monitor control commands
ros2 topic echo /carla/hero/vehicle_control_cmd

# Check nodes are alive
ros2 node list
```

---

## Full Terminal Layout

| Terminal | Location | Command |
|----------|----------|---------|
| 1 | Host | CARLA server |
| 2 | Container | `ros2 launch carla_ros_bridge ...` |
| 3 | Container (`docker exec`) | nodes + rviz2 |
