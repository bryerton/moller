cmake_minimum_required(VERSION 3.10)

project(moller_ctrl)

add_executable(moller_ctrl main.c )

target_link_libraries(moller_ctrl zmq pthread)
