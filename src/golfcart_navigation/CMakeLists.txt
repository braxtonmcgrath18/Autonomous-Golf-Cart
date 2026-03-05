cmake_minimum_required(VERSION 3.8)
project(golfcart_navigation)

find_package(ament_cmake REQUIRED)

install(DIRECTORY launch params rviz2 maps
  DESTINATION share/${PROJECT_NAME}
)

ament_package()
