# golfcart_bringup

Bringup package with profile launchers for simulation and real vehicle runs.

## Run Profiles

Simulation profile:

```bash
ros2 launch golfcart_bringup sim.launch.py
```

Simulation profile with explicit map:

```bash
ros2 launch golfcart_bringup sim.launch.py map:=/home/isaacsim/golfcart_ws/src/golfcart_navigation/maps/racetrackmap.yaml
```

Real vehicle profile:

```bash
ros2 launch golfcart_bringup real.launch.py
```

Override Nav2 params in either profile:

```bash
ros2 launch golfcart_bringup sim.launch.py params_file:=/absolute/path/to/nav2_params.yaml
```

Notes:
- `sim.launch.py` forces `use_sim_time:=true`.
- `sim.launch.py` passes `map` to Nav2 localization so `map_server` gets `yaml_filename` for the existing map.
- `real.launch.py` forces `use_sim_time:=false`.
- `real.launch.py` includes TODO placeholders for networked ZED Box topics and the vehicle interface hardware backend node.

## RViz Localization Step (Required)

1. In RViz, set `Global Options -> Fixed Frame` to `map`.
2. Click `2D Pose Estimate` in the toolbar.
3. Click on the robot's location in the map, drag to indicate heading, and release.
4. Confirm `map -> odom` appears in TF and AMCL pose begins updating.
