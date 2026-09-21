set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin/snippets/u01)

add_executable(rechteck_snippet rechteck.c)
add_executable(datum_snippet datum.c)

add_executable(eingabe_snippet eingabe.c)
if (NOT WIN32)
    target_link_libraries(eingabe_snippet m) # math
endif()

add_executable(algorithmen_snippet algorithmen.c)
if (NOT WIN32)
    target_link_libraries(algorithmen_snippet m) # math
endif()
