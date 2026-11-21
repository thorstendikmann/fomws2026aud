add_executable(fivewords_snp fivewords.c)

# No optimization at all, so the benchmark measures the algorithms themselves.
target_compile_options(fivewords_snp PRIVATE -O0)
