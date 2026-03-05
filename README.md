# Golf Cart Sim-to-Real ROS 2 Workspace

This repository is a ROS 2 colcon workspace scaffold for autonomous golf cart sim-to-real integration.

## Workspace Layout

- `src/golfcart_bringup/`
  - `launch/`
  - `config/`
- `src/golfcart_navigation/`
  - `config/`
  - `launch/`
- `src/golfcart_vehicle_interface/`
  - `src/`
  - `launch/`
  - `config/`
- `src/golfcart_interfaces/`
  - `msg/`
  - `srv/`

## Topic and TF Contracts

### TF Frames

- `map -> odom` is provided by localization (AMCL) or SLAM.
- `odom -> base_link` is provided by simulation or hardware odometry.
- Sensor frames must be attached under `base_link`.

### Command Path

- Nav2 outputs `/cmd_vel`.
- A converter node maps `/cmd_vel` to `/cmd_ackermann` (or `/ackermann_cmd`).
- `golfcart_vehicle_interface` is the only node allowed to command actuators.
