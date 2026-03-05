# golfcart_bringup

Bringup package with profile launchers for simulation and real vehicle runs.

## Run Profiles

Simulation profile:

```bash
ros2 launch golfcart_bringup sim.launch.py
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
- `real.launch.py` forces `use_sim_time:=false`.
- `real.launch.py` includes TODO placeholders for networked ZED Box topics and the vehicle interface hardware backend node.
