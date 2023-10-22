cmake_minimum_required(VERSION 3.18) #FetchContent

find_package(opencv CONFIG QUIET) # Search for installed build

if (NOT opencv_FOUND)

	include(CPM)

	CPMAddPackage(
        NAME opencv
        GIT_REPOSITORY https://github.com/opencv/opencv.git
        GIT_TAG        4.4.0
	)
endif()