cmake_minimum_required(VERSION 3.20)
project(prima-engine VERSION 0.1.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(Python REQUIRED COMPONENTS Interpreter Development.Module)
find_package(nanobind CONFIG REQUIRED)

execute_process(
    COMMAND "${Python_EXECUTABLE}" -c
    "import numpy; print(numpy.get_include())"
    OUTPUT_VARIABLE _NUMPY_INCLUDE_DIR
    OUTPUT_STRIP_TRAILING_WHITESPACE
)

nanobind_add_module(_math_utils src/math_utils.cpp)
target_include_directories(_math_utils PRIVATE ${_NUMPY_INCLUDE_DIR})
install(TARGETS _math_utils LIBRARY DESTINATION prima/engine)

nanobind_add_module(_physics src/physics.cpp)
target_include_directories(_physics PRIVATE ${_NUMPY_INCLUDE_DIR})
install(TARGETS _physics LIBRARY DESTINATION prima/engine)
