# Moonlight Tizen — Samsung TV build notes

This is a fork of the `Moonlight Chrome` project adapted to run on Samsung Tizen TVs.
Changes made:

- WebAssembly is used instead of Native Client
- Main adaptation layer is in a wasm/ directory instead of the root project directory

## Used Tizen specific features

- [Tizen WASM Player](https://developer.samsung.com/smarttv/develop/extension-libraries/webassembly/tizen-wasm-player/overview.html)
- [Tizen Sockets Extension](https://developer.samsung.com/smarttv/develop/extension-libraries/webassembly/api-reference/tizen-sockets-extension.html)

## Dependencies

This independent repository currently has no active Git submodules. The required dependency source trees are committed directly in the repository, so a normal clone is sufficient and no `git submodule update` step is needed.

## Building

### Required software
- [Samsung Emscripten fork](https://developer.samsung.com/smarttv/develop/extension-libraries/webassembly/getting-started/downloading-and-installing.html)
- cmake (at least 3.10 - tested using CMake 3.10 and CMake 3.18)
- ninja (at least 1.8.2- recommended for Windows)

### Build procedure

```bash
mkdir build
cd build/
cmake -DCMAKE_TOOLCHAIN_FILE=<YOUR EMSCRIPTEN INSTALLATION_DIR>/cmake/Modules/Platform/Emscripten.cmake -G Ninja ..
ninja

# CMake 3.10 (and above):
cmake -DCMAKE_INSTALL_PREFIX=. -P cmake_install.cmake

# CMake 3.15 (and above):
cmake --install . --prefix .
```

*Note:* On Linux and macOS you can also use `Makefile` cmake generators.

After that you can pack widget as described in [Sample cURL application built using CLI tools](https://developer.samsung.com/smarttv/develop/extension-libraries/webassembly/tizen-sockets-extension/sample-curl-application-built-using-cli-tools.html) tutorial.
