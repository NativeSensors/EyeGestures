cmake_minimum_required(VERSION 3.20)

# Organise CMake scripts into a folder
list(APPEND CMAKE_MODULE_PATH 
    "${CMAKE_CURRENT_LIST_DIR}/CMake/")

# Embed versioning from Git-Tag
find_package(Version.cmake)

# Enumerate supported languages for target
# @see `CmakeDetermine*` in https://github.com/Kitware/CMake/tree/master/Modules
include(CheckLanguage)

enable_language( C CXX )

project(eyeGestures)

OPTION(DEBUG "For enabling debug output" OFF) # Enabled by default
IF(DEBUG)
    ADD_DEFINITIONS(-DDEBUG)
ENDIF(DEBUG)

find_package(opencv REQUIRED)

add_executable(eyeGestures
    main.cpp)

target_link_libraries(eyeGestures PRIVATE
    opencv
)