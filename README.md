# Launch Guide

## Prerequisites
- CARLA 0.9.16 installed at `~/Desktop/Carla_Sim`
- Docker installed
- Python 3.10 venv set up at `~/Desktop/Carla_Sim/PythonAPI/examples/carla-env`

---

## 1 — Start CARLA Server (on host)

**Windowed** (if you want to see the simulation):
```bash
cd ~/Desktop/Carla_Sim
./CarlaUE4.sh -windowed -ResX=1280 -ResY=720
```

**Headless** (no display, faster):
```bash
cd ~/Desktop/Carla_Sim
./CarlaUE4.sh -RenderOffScreen
```

---

## 2 — Start Manual Control (on host, optional)

Open a new terminal:
```bash
cd ~/Desktop/Carla_Sim/PythonAPI/examples
source carla-env/bin/activate
python manual_control.py
```

> **Note:** Use WASD / arrow keys to drive. Close this window to stop the vehicle.
> Skip this step if you want the ROS2 node to control the vehicle instead.

---

## 3 — Build Docker Image

Only needed once, or after code changes:
```bash
cd ~/ros2_carla_ws
docker rmi -f carla_ros2   # remove old image if rebuilding
docker build -t carla_ros2 .
```

---

## 4 — Run Container

```bash
docker run -it --rm --network host carla_ros2 bash
```

> `--network host` lets the container reach the CARLA server on `localhost:2000`.

---

## 5 — Launch ROS2 Nodes (inside container)

```bash
source /opt/ros/humble/setup.bash
source /ros2_ws/install/setup.bash
ros2 launch carla_interface racing.launch.py
```

**If you made code changes and need to rebuild first:**
```bash
cd /ros2_ws
rm -rf build/ install/ log/
colcon build
source install/setup.bash
ros2 launch carla_interface racing.launch.py
```

---

## 6 — Visualize Point Cloud (optional, new terminal on host)

```bash
rviz2
```
Add a `PointCloud2` display and set the topic to `/lidar/points`.

---

## Full Terminal Layout

| Terminal | Location | Command |
|----------|----------|---------|
| 1 | Host | `./CarlaUE4.sh -windowed` |
| 2 | Host | `python manual_control.py` (optional) |
| 3 | Host | `docker run ... carla_ros2 bash` → launch nodes |
| 4 | Host | `rviz2` (optional) |