add_executable(fivewords fivewords.c)
install(TARGETS fivewords DESTINATION bin/u02)

# No optimization at all, so the benchmark measures the algorithms themselves.
target_compile_options(fivewords PRIVATE -O0)
