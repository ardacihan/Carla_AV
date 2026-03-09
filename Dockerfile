FROM carla-ros-bridge:humble-0.9.15

ENV DEBIAN_FRONTEND=noninteractive
ENV ROS_LOCALHOST_ONLY=0
SHELL ["/bin/bash", "-c"]

RUN apt-get update && apt-get install -y \
    ros-humble-rviz2 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /ros2_ws
COPY src/ src/

RUN source /opt/ros/humble/setup.bash && \
    source install/setup.bash && \
    colcon build --packages-select perception control

RUN echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc && \
    echo "source /ros2_ws/install/setup.bash" >> ~/.bashrc

CMD ["bash"]