# Default to an optimised build when the user did not pick a configuration.
if(NOT CMAKE_BUILD_TYPE AND NOT CMAKE_CONFIGURATION_TYPES)
  set(CMAKE_BUILD_TYPE Release CACHE STRING "Build type" FORCE)
endif()

find_package(OpenCV REQUIRED)

message("-- Check for Google Flags")
# gflags 2.1 and later ship a CMake config package; fall back to a manual
# search for older or hand-built installs.
find_package(gflags CONFIG QUIET)
if(NOT gflags_FOUND)
  find_path(GFLAGS_INCLUDE_DIR NAMES gflags/gflags.h)
  find_library(GFLAGS_LIB NAMES gflags gflags_static)
  if(NOT GFLAGS_INCLUDE_DIR OR NOT GFLAGS_LIB)
    message(FATAL_ERROR
      "Google Flags not found. Install libgflags-dev, or point CMAKE_PREFIX_PATH at it.")
  endif()
  add_library(gflags UNKNOWN IMPORTED)
  set_target_properties(gflags PROPERTIES
    IMPORTED_LOCATION "${GFLAGS_LIB}"
    INTERFACE_INCLUDE_DIRECTORIES "${GFLAGS_INCLUDE_DIR}")
endif()

add_executable(linedetection linedetection.cpp linedetector.cpp)

target_include_directories(linedetection PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR} ${OpenCV_INCLUDE_DIRS})
target_link_libraries(linedetection PRIVATE ${OpenCV_LIBS} gflags)

set_target_properties(linedetection PROPERTIES
  CXX_STANDARD 11
  CXX_STANDARD_REQUIRED ON
  RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR})

if(MSVC)
  target_compile_definitions(linedetection PRIVATE _CRT_SECURE_NO_WARNINGS NOMINMAX)
endif()
