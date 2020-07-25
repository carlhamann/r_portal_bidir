cmake_minimum_required(VERSION 3.10)
project(r_portal_bidir)

option(LM_BUILD_TESTS "" ON)
option(LM_BUILD_EXAMPLES "" ON)
add_subdirectory(lightmetrica-v3)

list(APPEND CMAKE_MODULE_PATH "${CMAKE_CURRENT_LIST_DIR}/lightmetrica-v3/cmake")
include(LmAddPlugin)

lm_add_plugin(
    NAME r_portal_bidir
    SOURCES
        "renderer_portal_bdpt.cpp"
        "portal.h"
        "debug.h"
)
