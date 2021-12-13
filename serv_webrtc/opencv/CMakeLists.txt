# https://docs.opencv.org/4.x/db/df5/tutorial_linux_gcc_cmake.html

# Version
cmake_minimum_required(VERSION 3.18)

# Project Name
project(findfaces)

# OpenCV Pkg
find_package(OpenCV REQUIRED)
include_directories(${OpenCV_INCLUDE_DIRS})

# Allow pybind to find Python
set(PYBIND11_FINDPYTHON ON)

# Pybind11
add_subdirectory(pybind11)

# Exec
# add_executable (findfaces main.cpp)
pybind11_add_module(findfaces main.cpp)

# Shared libs
target_link_libraries (findfaces PRIVATE ${OpenCV_LIBS})
