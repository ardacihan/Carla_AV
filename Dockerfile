# ----------------------------
# Dockerfile for ROS2 Humble + CARLA 0.9.16
# ----------------------------

FROM ros:humble-ros-base

ENV DEBIAN_FRONTEND=noninteractive
SHELL ["/bin/bash", "-c"]

# ----------------------------
# System + ROS dependencies
# ----------------------------
RUN apt-get update && apt-get install -y \
    python3-pip \
    python3-colcon-common-extensions \
    python3-opencv \
    python3-numpy \
    build-essential \
    git \
    tree \
    ros-humble-rclpy \
    ros-humble-std-msgs \
    ros-humble-sensor-msgs \
    ros-humble-geometry-msgs \
    ros-humble-cv-bridge \
    ros-humble-rviz2 \
    && rm -rf /var/lib/apt/lists/*

# ----------------------------
# Upgrade pip
# ----------------------------
RUN python3 -m pip install --upgrade pip setuptools "setuptools==65.7.0" wheel

# ----------------------------
# Install CARLA Python API
# ----------------------------
COPY carla-0.9.16-cp310-cp310-manylinux_2_31_x86_64.whl /tmp/
RUN python3 -m pip install /tmp/carla-0.9.16-cp310-cp310-manylinux_2_31_x86_64.whl

# ----------------------------
# Create workspace
# ----------------------------
WORKDIR /ros2_ws

# Copy only src (build/install/log must NOT exist inside src)
COPY src/ src/

# ----------------------------
# Build workspace
# ----------------------------
RUN source /opt/ros/humble/setup.bash && \
    colcon build

# ----------------------------
# Auto-source workspace
# ----------------------------
RUN echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc && \
    echo "source /ros2_ws/install/setup.bash" >> ~/.bashrc

# ----------------------------
# Default command
# ----------------------------
CMD ["bash"]