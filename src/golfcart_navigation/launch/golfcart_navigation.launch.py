import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, TimerAction
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():
    use_sim_time = LaunchConfiguration('use_sim_time', default='True')
    autostart = LaunchConfiguration('autostart', default='true')
    scan_experiment = LaunchConfiguration('scan_experiment', default='false')

    default_map = os.path.join(
        get_package_share_directory("golfcart_navigation"), "maps", "racetrackmap.yaml"
    )
    map_dir = LaunchConfiguration("map")

    params_file = LaunchConfiguration(
        'params_file',
        default=os.path.join(get_package_share_directory('golfcart_navigation'), 'params', 'golfcart_nav2_params.yaml')
    )

    rviz_config = LaunchConfiguration(
        'rviz_config',
        default=os.path.join(get_package_share_directory('golfcart_navigation'), 'rviz2', 'golfcart_navigation.rviz')
    )
    

    # ZED depth->scan launcher expects camera_model (e.g., zedx, zedxm, zed2, zed2i, etc.)
    camera_model = LaunchConfiguration('camera_model', default='zedxm')

    # Keep these in case you still use them elsewhere
    zed_cloud = LaunchConfiguration('zed_cloud', default='/zed/zed_node/point_cloud/cloud_registered')
    ackermann_out = LaunchConfiguration('ackermann_cmd', default='/ackermann_cmd')

    nav2_launch_dir = os.path.join(get_package_share_directory('nav2_bringup'), 'launch')
    
    localization = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(nav2_launch_dir,
'localization_launch.py')),
        launch_arguments={
            'use_sim_time': use_sim_time,
            'map': map_dir,
            'params_file': params_file,
            'autostart': autostart,
        }.items(),
)

    #map_server = Node(
        #package='nav2_map_server',
        #executable='map_server',
        #name='map_server',
        #output='screen',
        #parameters=[{'use_sim_time': use_sim_time, 'yaml_filename': map_dir}],
    #)

    #map_lifecycle = Node(
        #package='nav2_lifecycle_manager',
        #executable='lifecycle_manager',
        #name='lifecycle_manager_map',
        #output='screen',
        #parameters=[{
        #    'use_sim_time': use_sim_time,
        #    'autostart': True,
        #    'node_names': ['map_server'],
        #}],
    #)

    #static_map_odom = Node(
        #package='tf2_ros',
        #executable='static_transform_publisher',
        #name='static_map_to_odom',
        #arguments=['0', '0', '0', '0', '0', '0', 'map', 'odom'],
        #output='screen'
   #)

    nav2 = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(nav2_launch_dir, 'navigation_launch.py')),
        launch_arguments={
            'use_sim_time': use_sim_time,
            'params_file': params_file,
            'slam': 'False',
            'use_docking': 'False',
            'autostart': autostart,
        }.items(),
    )

    # Include ZED depth->laserscan example launch
    # It will normally publish /zed/scan; we remap that to /scan so Nav2 stays unchanged.
    zed_depth_to_scan = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory('zed_depth_to_laserscan'),
                'launch',
                'zed_depth_to_laserscan.launch.py',
            )
        ),
        condition=IfCondition(scan_experiment),
        launch_arguments={
            'camera_model': camera_model,
            'rviz': 'false',
        }.items(),
    )


    rviz = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(nav2_launch_dir, 'rviz_launch.py')),
        launch_arguments={
            'namespace': '',
            'use_namespace': 'False',
            'rviz_config': rviz_config,
        }.items(),
    )

    # Delay RViz a bit so it discovers Nav2 servers cleanly
    rviz_delayed = TimerAction(period=3.0, actions=[rviz])

    cmdvel_to_ackermann = Node(
        package='cmdvel_to_ackermann',
        executable='cmdvel_to_ackermann.py',
        name='cmdvel_to_ackermann',
        output='screen',
        parameters=[{
            'wheelbase': 1.6764,
            'max_steering_angle': 0.523599,
            'min_speed': 0.0,
            'max_speed': 2.0,
        }]
    )

    return LaunchDescription([
        DeclareLaunchArgument('use_sim_time', default_value='True'),
        DeclareLaunchArgument('map', default_value=default_map),
        DeclareLaunchArgument('autostart', default_value='true'),
        DeclareLaunchArgument('scan_experiment', default_value='false'),
        DeclareLaunchArgument('params_file', default_value=params_file),
        DeclareLaunchArgument('rviz_config', default_value=rviz_config),
        DeclareLaunchArgument('camera_model', default_value=camera_model),
        DeclareLaunchArgument('zed_cloud', default_value=zed_cloud),
        DeclareLaunchArgument('ackermann_cmd', default_value=ackermann_out),

        #map_server,
        #map_lifecycle,
        #static_map_odom,

        zed_depth_to_scan,
        localization,
        nav2,
        rviz_delayed,
        cmdvel_to_ackermann,
    ])
