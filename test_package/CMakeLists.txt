project(MyHello)
cmake_minimum_required(VERSION 2.8)

message(STATUS "Loading conan scripts for {0} dependencies...")
list(APPEND CMAKE_MODULE_PATH ${CMAKE_BINARY_DIR})
list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_SOURCE_DIR})
include("${CMAKE_BINARY_DIR}/conanbuildinfo.cmake")
include("${CMAKE_BINARY_DIR}/conan_paths.cmake" OPTIONAL)
message(STATUS "Doing conan basic setup")
conan_basic_setup()
#conan_basic_setup(
#    # prevent conan_basic_setup from resetting cmake variables
#    TARGETS
#    KEEP_RPATHS
#    # see https://github.com/conan-io/conan/issues/6012
#    NO_OUTPUT_DIRS)
list(APPEND CMAKE_PROGRAM_PATH ${CONAN_BIN_DIRS})
# TODO: make better: link lib dirs
link_directories(${CONAN_LIB_DIRS})
#if (APPLE OR UNIX)
#    set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} -Wl,-rpath,${CONAN_LIB_DIRS}")
#    set(CMAKE_SHARED_LINKER_FLAGS "${CMAKE_SHARED_LINKER_FLAGS} -Wl,-rpath,${CONAN_LIB_DIRS}")
#endif ()
#
# see https://github.com/grpc/grpc/issues/21422
#set(CMAKE_CROSSCOMPILING 1)
#set(PROTOBUF_PROTOC_LIBRARIES ${CONAN_LIBS_PROTOBUF})
#set(PROTOBUF_INCLUDE_DIRS ${CONAN_INCLUDE_DIRS_PROTOBUF})
#
message(STATUS "Test Conan setup done.")
#message(STATUS "PROTOBUF_PROTOC_LIBRARIES: ${PROTOBUF_PROTOC_LIBRARIES}")
#message(STATUS "PROTOBUF_INCLUDE_DIRS: ${PROTOBUF_INCLUDE_DIRS}")
message(STATUS "CONAN_INCLUDE_DIRS_PROTOBUF: ${CONAN_INCLUDE_DIRS_PROTOBUF}")
message(STATUS "CONAN_LIBS: ${CONAN_LIBS}")
message(STATUS "_gRPC_PROTOBUF_LIBRARIES: ${_gRPC_PROTOBUF_LIBRARIES}")
message(STATUS "CONAN_LIBS_GRPC_CONAN: ${CONAN_LIBS_GRPC_CONAN}")
message(STATUS "CONAN_LIBS_PROTOBUF: ${CONAN_LIBS_PROTOBUF}")
message(STATUS "CMAKE_LIBRARY_PATH: ${CMAKE_LIBRARY_PATH}")
message(STATUS "CMAKE_PROGRAM_PATH: ${CMAKE_PROGRAM_PATH}")
message(STATUS "CMAKE_EXE_LINKER_FLAGS: ${CMAKE_EXE_LINKER_FLAGS}")
message(STATUS "CMAKE_SHARED_LINKER_FLAGS: ${CMAKE_SHARED_LINKER_FLAGS}")
find_program(_gRPC_PROTOBUF_PROTOC_EXECUTABLE protoc NO_SYSTEM_ENVIRONMENT_PATH NO_CMAKE_SYSTEM_PATH)
message(STATUS "_gRPC_PROTOBUF_PROTOC_EXECUTABLE: ${_gRPC_PROTOBUF_PROTOC_EXECUTABLE}")

#include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
#conan_basic_setup()

if (MSVC)
  add_definitions(/MP)
endif (MSVC)

find_package(gRPC REQUIRED)
find_package(protobuf REQUIRED)
#find_package(Protobuf REQUIRED)
#find_package(GRPC REQUIRED)
find_package( Threads REQUIRED )

find_program(GRPC_GRPC_CPP_PLUGIN grpc_cpp_plugin PATHS ${CONAN_BIN_DIRS_GRPC} NO_SYSTEM_ENVIRONMENT_PATH NO_CMAKE_SYSTEM_PATH )
function(GRPC_GENERATE_CPP SRCS HDRS)
  if(NOT ARGN)
    message(SEND_ERROR "Error: GRPC_GENERATE_CPP() called without any proto files")
    return()
  endif()

  if(PROTOBUF_GENERATE_CPP_APPEND_PATH)
    # Create an include path for each file specified
    foreach(FIL ${ARGN})
      get_filename_component(ABS_FIL ${FIL} ABSOLUTE)
      get_filename_component(ABS_PATH ${ABS_FIL} PATH)
      list(FIND _protobuf_include_path ${ABS_PATH} _contains_already)
      if(${_contains_already} EQUAL -1)
          list(APPEND _protobuf_include_path -I ${ABS_PATH})
      endif()
    endforeach()
  else()
    set(_protobuf_include_path -I ${CMAKE_CURRENT_SOURCE_DIR})
  endif()

  if(DEFINED Protobuf_IMPORT_DIRS)
    foreach(DIR ${Protobuf_IMPORT_DIRS})
      get_filename_component(ABS_PATH ${DIR} ABSOLUTE)
      list(FIND _protobuf_include_path ${ABS_PATH} _contains_already)
      if(${_contains_already} EQUAL -1)
          list(APPEND _protobuf_include_path -I ${ABS_PATH})
      endif()
    endforeach()
  endif()

  set(${SRCS})
  set(${HDRS})
  foreach(FIL ${ARGN})
    get_filename_component(ABS_FIL ${FIL} ABSOLUTE)
    get_filename_component(FIL_WE ${FIL} NAME_WE)

    list(APPEND ${SRCS} "${CMAKE_CURRENT_BINARY_DIR}/${FIL_WE}.grpc.pb.cc")
    list(APPEND ${HDRS} "${CMAKE_CURRENT_BINARY_DIR}/${FIL_WE}.grpc.pb.h")

    add_custom_command(
      OUTPUT "${CMAKE_CURRENT_BINARY_DIR}/${FIL_WE}.grpc.pb.cc"
             "${CMAKE_CURRENT_BINARY_DIR}/${FIL_WE}.grpc.pb.h"
      COMMAND  ${Protobuf_PROTOC_EXECUTABLE}
          --plugin=protoc-gen-grpc=${GRPC_GRPC_CPP_PLUGIN}
          --grpc_out=${CMAKE_CURRENT_BINARY_DIR}
          ${_protobuf_include_path}
          ${ABS_FIL}
      DEPENDS ${ABS_FIL} ${Protobuf_PROTOC_EXECUTABLE} ${GRPC_GRPC_CPP_PLUGIN}
      COMMENT "Running C++ protocol buffer compiler with the GRPC plugin on ${FIL}"
      VERBATIM )
  endforeach()

  set_source_files_properties(${${SRCS}} ${${HDRS}} PROPERTIES GENERATED TRUE)
  set(${SRCS} ${${SRCS}} PARENT_SCOPE)
  set(${HDRS} ${${HDRS}} PARENT_SCOPE)
endfunction()

PROTOBUF_GENERATE_CPP(SRC_FILE HEADER_FILE helloworld.proto)
GRPC_GENERATE_CPP(GRPC_SRC_FILE GRPC_HEADER_FILE helloworld.proto)
#protobuf_generate_cpp(SRC_FILE HEADER_FILE helloworld.proto)
#protobuf_generate_grpc_cpp(GRPC_SRC_FILE GRPC_HEADER_FILE helloworld.proto)

if(MSVC)
    add_definitions(-D_WIN32_WINNT=0x600) # This is a GRPC requirement!!
endif()

include_directories(${Protobuf_INCLUDE_DIRS} ${CMAKE_CURRENT_BINARY_DIR}) # CMAKE_CURRENT_BINARY_DIR is where our generated files are (.pb.hpp)
add_executable(greeter_client_server greeter_client_server.cc ${SRC_FILE} ${HEADER_FILE} ${GRPC_SRC_FILE} ${GRPC_HEADER_FILE})
if(NOT TARGET protobuf::libprotobuf)
    message(FATAL_ERROR "WE DIDN'T FIND LIBPROTOBUFS IMPORT TARGET (Protobuf_LIBRARIES = ${Protobuf_LIBRARIES})")
endif()
target_link_libraries(greeter_client_server
  ${CONAN_LIBS}
  #${CONAN_LIBS_PROTOBUF}
  #${CONAN_LIBS_GRPC_CONAN}
  #${CONAN_LIBS_ZLIB}
  #${CONAN_LIBS_C-ARES}
) # This is still faulty: protobuf::libprotobuf gRPC::grpc++ gRPC::grpc does not work (neither with gRPC::gpr OpenSSL::SSL added)