# golfcart_navigation

Carter-style Nav2 wrapper for an Ackermann golf cart in Isaac Sim.

## Run
```bash
colcon build --packages-select golfcart_navigation
source install/setup.bash

ros2 launch golfcart_navigation golfcart_navigation.launch.py \
  slam:=False \
  use_sim_time:=True \
  map:=/home/isaacsim/map.yaml \
  zed_cloud:=/zed/zed_node/point_cloud/cloud_registered \
  ackermann_cmd:=/ackermann_cmd
```

## Contract (must be true)
- TF: `odom -> Mock_Robot` must exist.
- Either provide `map -> odom` (this launch publishes a static one by default) OR run localization.
- `/scan` should appear from `pointcloud_to_laserscan`.

