import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


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

    params_file = LaunchConfiguration('params_file')
    map_yaml = LaunchConfiguration('map')
    zed_cloud = LaunchConfiguration('zed_cloud')

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

    # Convert incoming ZED pointcloud to LaserScan for AMCL/Nav2.
    pointcloud_to_scan = Node(
        package='pointcloud_to_laserscan',
        executable='pointcloud_to_laserscan_node',
        name='pointcloud_to_laserscan',
        output='screen',
        remappings=[
            ('cloud_in', zed_cloud),
            ('scan', '/zed/scan'),
        ],
        parameters=[{
            'range_min': 0.5,
            'range_max': 20.0,
            'scan_time': 0.1,
            'use_inf': True,
        }],
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
            'zed_cloud',
            default_value='/zed/zed_node/point_cloud/cloud_registered',
            description='Input PointCloud2 topic used to generate /zed/scan',
        ),
        pointcloud_to_scan,
        nav_launch,
    ])
