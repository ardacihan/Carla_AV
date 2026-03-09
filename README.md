# Launch Guide

## Prerequisites
- CARLA 0.9.15 installed at `~/Desktop/CARLA_0.9.15`
- Docker installed
- Python 3.10 venv at `~/Desktop/CARLA_0.9.15/PythonAPI/examples/carla-env`

---

## Architecture Overview
```
Terminal 1            Terminal 2                  Terminal 3
──────────────        ──────────────────────────  ──────────────────────────
CARLA server    ───►  carla-ros-bridge container  Your nodes container
(host)                (spawns ego vehicle,        (perception, control)
                       publishes sensor topics)
```

---

## Step 1 — Start CARLA Server (host)
```bash
cd ~/Desktop/CARLA_0.9.15
./CarlaUE4.sh -RenderOffScreen -carla-rpc-port=2000
```

> Leave this terminal running. CARLA is ready when you see `Waiting for connection`.

---

## Step 2 — Start carla-ros-bridge (host, new terminal)
```bash
docker run -it --rm --network host your_bridge_image \
  ros2 launch carla_ros_bridge carla_ros_bridge_with_example_ego_vehicle.launch.py \
    host:=localhost port:=2000
```

> The bridge spawns the ego vehicle and starts publishing sensor topics.
> Verify it's working: `ros2 topic list | grep carla`

---

## Step 3 — Build your nodes image

Only needed once, or after code changes:
```bash
cd ~/ros2_carla_ws
docker build -t carla_nodes .
```

To force a clean rebuild:
```bash
docker rmi -f carla_nodes
docker build -t carla_nodes .
```

---

## Step 4 — Run the container (host, new terminal)
```bash
docker run -it --rm --network host carla_nodes bash
```

Then inside the container, source the workspace:
```bash
source /opt/ros/humble/setup.bash
source /ros2_ws/install/setup.bash
```

---

## Step 5 — Running nodes

### All nodes together (recommended)
```bash
ros2 launch bringup racing.launch.py
```

With overrides:
```bash
ros2 launch bringup racing.launch.py target_speed_mps:=8.0 max_throttle:=0.8
```

Perception only — no control commands sent to vehicle:
```bash
ros2 launch bringup racing.launch.py enable_control:=false
```

---

### Nodes individually

Each of these needs its own terminal with the workspace sourced.

**Lidar node only:**
```bash
ros2 run perception lidar_node
```
Subscribes to: `/carla/ego_vehicle/lidar/lidar1/point_cloud`
Publishes to:  `/perception/lidar/points`

With parameter overrides:
```bash
ros2 run perception lidar_node --ros-args -p min_range:=1.0 -p max_range:=30.0
```

---

**Camera node only:**
```bash
ros2 run perception camera_node
```
Subscribes to: `/carla/ego_vehicle/rgb_front/image`
Publishes to:  `/perception/camera/annotated`

---

**Control node only:**
```bash
ros2 run control control_node
```
Subscribes to: `/carla/ego_vehicle/speedometer`, `/carla/ego_vehicle/odometry`
Publishes to:  `/carla/ego_vehicle/vehicle_control_cmd`

With parameter overrides:
```bash
ros2 run control control_node --ros-args -p target_speed_mps:=6.0 -p max_throttle:=0.5
```

---

## Step 6 — Rebuilding after code changes (inside container)

**Rebuild everything:**
```bash
cd /ros2_ws
rm -rf build/ install/ log/
colcon build
source install/setup.bash
```

**Rebuild one package only (faster):**
```bash
cd /ros2_ws
colcon build --packages-select perception
source install/setup.bash
```

---

## Step 7 — Visualize (optional, new terminal on host)
```bash
rviz2
```

| What | Display type | Topic |
|------|-------------|-------|
| Filtered lidar | `PointCloud2` | `/perception/lidar/points` |
| Raw lidar | `PointCloud2` | `/carla/ego_vehicle/lidar/lidar1/point_cloud` |
| Annotated camera | `Image` | `/perception/camera/annotated` |

---

## Useful Debug Commands

Check what the bridge is publishing:
```bash
ros2 topic list | grep carla
```

Monitor vehicle speed:
```bash
ros2 topic echo /carla/ego_vehicle/speedometer
```

Monitor control commands being sent:
```bash
ros2 topic echo /carla/ego_vehicle/vehicle_control_cmd
```

Check a node is alive:
```bash
ros2 node list
```

Check topic frequency:
```bash
ros2 topic hz /perception/lidar/points
```

---

## Full Terminal Layout

| Terminal | Location | Command |
|----------|----------|---------|
| 1 | Host | CARLA server |
| 2 | Host | carla-ros-bridge container |
| 3 | Container | your nodes (`ros2 launch bringup racing.launch.py`) |
| 4 | Host | `rviz2` (optional) |

---

## Manual Control (optional, instead of control node)

If you want to drive the vehicle yourself rather than use the control node:
```bash
cd ~/Desktop/CARLA_0.9.15/PythonAPI/examples
source carla-env/bin/activate
python manual_control.py
```

> WASD / arrow keys to drive. If running this, launch with `enable_control:=false`
> so the control node doesn't fight your inputs:
> `ros2 launch bringup racing.launch.py enable_control:=false`