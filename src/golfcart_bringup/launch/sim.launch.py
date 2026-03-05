import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    default_params = os.path.join(
        get_package_share_directory('golfcart_navigation'),
        'params',
        'golfcart_nav2_params.yaml',
    )
    default_map = os.path.join(
        get_package_share_directory('golfcart_navigation'),
        'maps',
        'racetrackmap.yaml',
    )
    default_zed_cvt_config = os.path.join(
        get_package_share_directory('golfcart_bringup'),
        'config',
        'zed_depth_to_laserscan_nav2.yaml',
    )

    params_file = LaunchConfiguration('params_file')
    map_yaml = LaunchConfiguration('map')
    zed_camera_name = LaunchConfiguration('zed_camera_name')
    zed_node_name = LaunchConfiguration('zed_node_name')
    zed_camera_model = LaunchConfiguration('zed_camera_model')
    zed_cvt_config = LaunchConfiguration('zed_cvt_config')

    nav_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory('golfcart_navigation'),
                'launch',
                'golfcart_navigation.launch.py',
            )
        ),
        launch_arguments={
            'use_sim_time': 'true',
            'params_file': params_file,
            'localization_map': map_yaml,
            'autostart': 'true',
        }.items(),
    )

    # Stereolabs converter package. With camera_name=zed and zed_node_name=zed_node,
    # input depth is /zed/zed_node/depth/depth_registered and output scan is /zed/scan.
    zed_depth_to_scan = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory('zed_depth_to_laserscan'),
                'launch',
                'zed_depth_to_laserscan.launch.py',
            )
        ),
        launch_arguments={
            'camera_name': zed_camera_name,
            'zed_node_name': zed_node_name,
            'camera_model': zed_camera_model,
            'config_path_cvt': zed_cvt_config,
            'rviz': 'false',
            'publish_urdf': 'false',
        }.items(),
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'params_file',
            default_value=default_params,
            description='Path to Nav2 params file',
        ),
        DeclareLaunchArgument(
            'map',
            default_value=default_map,
            description='Path to existing map yaml used by nav2_map_server',
        ),
        DeclareLaunchArgument(
            'zed_camera_name',
            default_value='zed',
            description='ZED namespace; determines /<camera_name>/scan output topic',
        ),
        DeclareLaunchArgument(
            'zed_node_name',
            default_value='zed_node',
            description='ZED node name; determines depth input topic path',
        ),
        DeclareLaunchArgument(
            'zed_camera_model',
            default_value='zed2i',
            description='ZED camera model for zed_depth_to_laserscan launch',
        ),
        DeclareLaunchArgument(
            'zed_cvt_config',
            default_value=default_zed_cvt_config,
            description='Depth-to-laserscan parameter file path',
        ),
        zed_depth_to_scan,
        nav_launch,
    ])
