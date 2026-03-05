cmake_minimum_required(VERSION 3.8)
project(golfcart_navigation)

find_package(ament_cmake REQUIRED)

# Ensure this package is configured from its in-repo source tree.
foreach(required_dir IN ITEMS launch params rviz2 maps)
  if(NOT EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/${required_dir}")
    message(FATAL_ERROR
      "Missing '${required_dir}' under ${CMAKE_CURRENT_SOURCE_DIR}. "
      "Build golfcart_navigation from src/golfcart_navigation.")
  endif()
endforeach()

install(DIRECTORY launch params maps rviz2
  DESTINATION share/${PROJECT_NAME}
)

ament_package()
