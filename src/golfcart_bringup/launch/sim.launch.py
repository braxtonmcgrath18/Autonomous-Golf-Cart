import os
import subprocess

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    GroupAction,
    IncludeLaunchDescription,
    LogInfo,
    OpaqueFunction,
)
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node, SetRemap


def _topic_set():
    try:
        result = subprocess.run(
            ['ros2', 'topic', 'list'],
            check=False,
            capture_output=True,
            text=True,
            timeout=3,
        )
    except Exception:
        return set()
    if result.returncode != 0:
        return set()
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def _scan_pipeline_actions(context):
    pipeline = LaunchConfiguration('scan_pipeline').perform(context).strip()
    scan_topic = LaunchConfiguration('scan_topic').perform(context).strip()
    depth_topic = LaunchConfiguration('depth_topic').perform(context).strip()
    depth_info_topic = LaunchConfiguration('depth_info_topic').perform(context).strip()
    pointcloud_topic = LaunchConfiguration('pointcloud_topic').perform(context).strip()
    zed_camera_name = LaunchConfiguration('zed_camera_name').perform(context).strip()
    zed_node_name = LaunchConfiguration('zed_node_name').perform(context).strip()
    zed_camera_model = LaunchConfiguration('zed_camera_model').perform(context).strip()
    zed_cvt_config = LaunchConfiguration('zed_cvt_config').perform(context).strip()

    if pipeline == 'none':
        return [LogInfo(msg='[sim.launch] scan_pipeline=none: leaving /zed/scan external.')]

    if pipeline == 'zed_depth':
        topics = _topic_set()
        required_topics = [depth_topic, depth_info_topic]
        missing = [topic for topic in required_topics if topic not in topics]
        if missing:
            return [
                LogInfo(
                    msg=(
                        '[WARN] [sim.launch] scan_pipeline=zed_depth requested but required topics '
                        f'not found: {missing}. Skipping zed_depth_to_laserscan.'
                    )
                )
            ]

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

        return [
            GroupAction(
                actions=[
                    SetRemap(src='/zed/scan', dst=scan_topic),
                    SetRemap(src='/zed/zed_node/depth/depth_registered', dst=depth_topic),
                    SetRemap(src='/zed/zed_node/depth/camera_info', dst=depth_info_topic),
                    zed_depth_to_scan,
                ]
            )
        ]

    if pipeline == 'pointcloud':
        return [
            Node(
                package='pointcloud_to_laserscan',
                executable='pointcloud_to_laserscan_node',
                name='pointcloud_to_laserscan',
                output='screen',
                remappings=[
                    ('cloud_in', pointcloud_topic),
                    ('scan', scan_topic),
                ],
                parameters=[{
                    'range_min': 0.5,
                    'range_max': 20.0,
                    'scan_time': 0.1,
                    'use_inf': True,
                }],
            )
        ]

    return [
        LogInfo(
            msg=(
                f"[WARN] [sim.launch] Unknown scan_pipeline='{pipeline}'. "
                "Valid values: none, zed_depth, pointcloud."
            )
        )
    ]


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
            'map': map_yaml,
            'autostart': 'true',
            'scan_experiment': 'false',
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
            'scan_pipeline',
            default_value='none',
            choices=['none', 'zed_depth', 'pointcloud'],
            description='none|zed_depth|pointcloud scan conversion pipeline',
        ),
        DeclareLaunchArgument(
            'scan_topic',
            default_value='/zed/scan',
            description='Output LaserScan topic for AMCL/Nav2',
        ),
        DeclareLaunchArgument(
            'depth_topic',
            default_value='/zed/zed_node/depth/depth_registered',
            description='Depth image input topic for zed_depth pipeline',
        ),
        DeclareLaunchArgument(
            'depth_info_topic',
            default_value='/zed/zed_node/depth/camera_info',
            description='Depth camera info topic for zed_depth pipeline',
        ),
        DeclareLaunchArgument(
            'pointcloud_topic',
            default_value='/zed/zed_node/point_cloud/cloud_registered',
            description='PointCloud2 input topic for pointcloud pipeline',
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
        OpaqueFunction(function=_scan_pipeline_actions),
        nav_launch,
    ])
