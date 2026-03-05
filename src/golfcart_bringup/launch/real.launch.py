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

    params_file = LaunchConfiguration('params_file')

    nav_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory('golfcart_navigation'),
                'launch',
                'golfcart_navigation.launch.py',
            )
        ),
        launch_arguments={
            'use_sim_time': 'false',
            'params_file': params_file,
        }.items(),
    )

    # TODO(real): Add/enable networked ZED Box topic bridge/remaps.
    # TODO(real): Add vehicle_interface hardware backend node for drive-by-wire.

    return LaunchDescription([
        DeclareLaunchArgument(
            'params_file',
            default_value=default_params,
            description='Path to Nav2 params file',
        ),
        nav_launch,
    ])
