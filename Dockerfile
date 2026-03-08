FROM ros:jazzy-ros-base

ENV ROS_DOMAIN_ID=0
ENV RMW_IMPLEMENTATION=rmw_fastrtps_cpp
ENV ROS_LOCALHOST_ONLY=0

SHELL ["/bin/bash","-c"]

# ----------------------------
# System dependencies
# ----------------------------
RUN apt-get update && apt-get install -y \
    python3-colcon-common-extensions \
    python3-pip \
    python3-opencv \
    python3-numpy \
    git \
    cmake \
    build-essential \
    libpcl-dev \
    ros-jazzy-pcl-conversions \
    ros-jazzy-cv-bridge \
    ros-jazzy-tf2-ros \
    ros-jazzy-rviz2 \
    && rm -rf /var/lib/apt/lists/*

# ----------------------------
# Workspace
# ----------------------------
WORKDIR /ros2_ws
COPY src src

# ----------------------------
# Build workspace
# ----------------------------
RUN . /opt/ros/jazzy/setup.bash && colcon build --symlink-install

# ----------------------------
# Auto-source workspace
# ----------------------------
RUN echo "source /opt/ros/jazzy/setup.bash" >> ~/.bashrc && \
    echo "source /ros2_ws/install/setup.bash" >> ~/.bashrc

CMD ["bash"]