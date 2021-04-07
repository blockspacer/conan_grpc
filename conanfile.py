from conans import ConanFile, CMake, tools, RunEnvironment
from conans.errors import ConanInvalidConfiguration
import os, re, platform

class grpcConan(ConanFile):
    name = "grpc_conan"
    version = "v1.26.x"
    description = "Google's RPC library and framework."
    topics = ("conan", "grpc", "rpc")
    homepage = "https://github.com/grpc/grpc"
    repo_url = 'https://github.com/grpc/grpc.git'
    license = "Apache-2.0"
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake", "cmake_paths", "virtualenv", "cmake_find_package_multi"
    short_paths = True

    settings = "os_build", "os", "arch", "compiler", "build_type"
    options = {
        # "shared": [True, False],
        "fPIC": [True, False],
        "build_codegen": [True, False],
        "build_csharp_ext": [True, False],
        "withOpenSSL" : [True, False]
    }
    default_options = {
        "fPIC": True,
        "build_codegen": True,
        "build_csharp_ext": False,
        "withOpenSSL": True
    }

    #_source_subfolder = "source_subfolder"
    #_build_subfolder = "build_subfolder"

    @property
    def _source_dir(self):
        return "source_subfolder"
        #return self.source_folder

    @property
    def _build_dir(self):
        return "."
        #return self.build_folder

    #requires = (
    #    "zlib/1.2.11",
    #    #"openssl/1.1.1d",
    #    #"protobuf/3.9.1@bincrafters/stable",
    #    #"protoc_installer/3.9.1@bincrafters/stable",
    #    "c-ares/1.15.0"
    #)

    def requirements(self):
        if (self.options.withOpenSSL):
            self.requires("openssl/OpenSSL_1_1_1-stable@conan/stable")
        self.requires("zlib/v1.2.11@conan/stable")
        self.requires("c-ares/cares-1_15_0@conan/stable")
        self.requires("protobuf/v3.9.1@conan/stable")

    #def build_requirements(self):
        #if (self.options.withOpenSSL):
        #    self.build_requires("openssl/OpenSSL_1_1_1-stable@conan/stable")
        #self.build_requires("protobuf/v3.9.1@conan/stable")

    def build_cmake_prefix_path(self, cmake, *paths):
        cmake.definitions["CMAKE_PREFIX_PATH"] = ";".join(paths)
        cmake.definitions["CMAKE_MODULE_PATH"] = ";".join(paths)

    def configure(self):
        if self.settings.os == "Windows" and self.settings.compiler == "Visual Studio":
            del self.options.fPIC
            compiler_version = tools.Version(self.settings.compiler.version)
            if compiler_version < 14:
                raise ConanInvalidConfiguration("gRPC can only be built with Visual Studio 2015 or higher.")

    # see https://github.com/bincrafters/conan-llvm/blob/caa0f2da0086978b88631df6a545a13819588407/recipes/llvm-common/llvmcomponentpackage.py#L30
    @staticmethod
    def try_regex_replace_in_file(file, line_to_search, replace_with, conanfile_output = None):
        with open(file, 'r') as input_file:
            input = input_file.read()

        output = re.sub(line_to_search, replace_with, input, flags=re.MULTILINE|re.DOTALL)

        if input == output:
            return False

        if conanfile_output is not None:
            conanfile_output.info('Replacing \"{}\" in {} with \"{}\"'.format(line_to_search, file, replace_with))

        with open(file, 'w') as output_file:
            output_file.write(output)

        return True

    def source(self):
        cmake_path = os.path.join(self._source_dir, "CMakeLists.txt")
        inject_conan_basic_setup=r'''message(STATUS "Main {0} CMakeLists.txt (${{CMAKE_CURRENT_LIST_DIR}}) patched by conan")
project(\1)
message(STATUS "Loading conan scripts for {0} dependencies...")
list(APPEND CMAKE_MODULE_PATH ${{CMAKE_BINARY_DIR}})
list(APPEND CMAKE_MODULE_PATH ${{CMAKE_CURRENT_SOURCE_DIR}})
include("${{CMAKE_BINARY_DIR}}/conanbuildinfo.cmake")
include("${{CMAKE_BINARY_DIR}}/conan_paths.cmake" OPTIONAL)
message(STATUS "Doing conan basic setup")
conan_basic_setup()
#conan_basic_setup(
#    # prevent conan_basic_setup from resetting cmake variables
#    TARGETS
#    KEEP_RPATHS
#    # see https://github.com/conan-io/conan/issues/6012
#    NO_OUTPUT_DIRS)
list(APPEND CMAKE_PROGRAM_PATH ${{CONAN_BIN_DIRS}})
#list(APPEND CMAKE_PROGRAM_PATH bin)
# TODO: make better: link lib dirs
link_directories(${{CONAN_LIB_DIRS}})
#if (APPLE OR UNIX)
#    set(CMAKE_EXE_LINKER_FLAGS "${{CMAKE_EXE_LINKER_FLAGS}} -Wl,-rpath,${{CONAN_LIB_DIRS}}")
#    set(CMAKE_SHARED_LINKER_FLAGS "${{CMAKE_SHARED_LINKER_FLAGS}} -Wl,-rpath,${{CONAN_LIB_DIRS}}")
#endif ()
#
# see https://github.com/grpc/grpc/issues/21422
# set(CMAKE_CROSSCOMPILING 1)
set(PROTOBUF_PROTOC_LIBRARIES ${{CONAN_LIBS_PROTOBUF}})
set(PROTOBUF_INCLUDE_DIRS ${{CONAN_INCLUDE_DIRS_PROTOBUF}})
#
message(STATUS "Conan setup done.")
message(STATUS "PROTOBUF_PROTOC_LIBRARIES: ${{PROTOBUF_PROTOC_LIBRARIES}}")
message(STATUS "PROTOBUF_INCLUDE_DIRS: ${{PROTOBUF_INCLUDE_DIRS}}")
message(STATUS "CONAN_INCLUDE_DIRS_PROTOBUF: ${{CONAN_INCLUDE_DIRS_PROTOBUF}}")
message(STATUS "CONAN_LIBS_PROTOBUF: ${{CONAN_LIBS_PROTOBUF}}")
message(STATUS "CMAKE_LIBRARY_PATH: ${{CMAKE_LIBRARY_PATH}}")
message(STATUS "CMAKE_PROGRAM_PATH: ${{CMAKE_PROGRAM_PATH}}")
message(STATUS "CMAKE_EXE_LINKER_FLAGS: ${{CMAKE_EXE_LINKER_FLAGS}}")
message(STATUS "CMAKE_SHARED_LINKER_FLAGS: ${{CMAKE_SHARED_LINKER_FLAGS}}")
find_program(_gRPC_PROTOBUF_PROTOC_EXECUTABLE protoc)
message(STATUS "_gRPC_PROTOBUF_PROTOC_EXECUTABLE: ${{_gRPC_PROTOBUF_PROTOC_EXECUTABLE}}")
'''.format(self.name)
        replace_project_regex = r'project\((.+?)\)'

        #tools.get(**self.conan_data["sources"][self.version])
        #extracted_dir = self.name + "-" + self.version
        #os.rename(extracted_dir, self._source_dir)

        # NOTE: about `--recurse-submodules -j8` see https://stackoverflow.com/a/4438292
        #self.run("git clone --recurse-submodules -j8 -b 1.26.x https://github.com/grpc/grpc.git " + self._source_dir)
        self.run('git clone --progress --depth 1 --branch {} --recursive --recurse-submodules {} {}'.format(self.version, self.repo_url, self._source_dir))

        # This small hack might be useful to guarantee proper /MT /MD linkage in MSVC
        # if the packaged project doesn't have variables to set it properly
        # The most important line is list(APPEND CMAKE_PROGRAM_PATH ${{CONAN_BIN_DIRS}}) which adds the bin/ directories of the conan dependencies to the set of paths that CMake uses to search programs through find_program() calls.

        if not self.try_regex_replace_in_file(cmake_path, replace_project_regex, inject_conan_basic_setup, self.output):
            self.output.warn("Could not patch {} main CMakeLists.txt file to include conan config".format(self.name))

        tools.replace_in_file(os.path.join(self._source_dir, "cmake/ssl.cmake"), 'set(_gRPC_SSL_LIBRARIES OpenSSL::SSL OpenSSL::Crypto)',
                                                      'set(_gRPC_SSL_LIBRARIES OpenSSL::SSL OpenSSL::Crypto ${CONAN_LIBS_OPENSSL})' )

        tools.replace_in_file(os.path.join(self._source_dir, "cmake/ssl.cmake"), 'set(_gRPC_SSL_LIBRARIES ${OPENSSL_LIBRARIES})',
                                                      'set(_gRPC_SSL_LIBRARIES ${OPENSSL_LIBRARIES} ${CONAN_LIBS_OPENSSL})' )

        # See #5
        tools.replace_in_file(cmake_path, "_gRPC_PROTOBUF_LIBRARIES", "CONAN_LIBS_PROTOBUF")

        # See https://github.com/grpc/grpc/issues/21293 - OpenSSL 1.1.1+ doesn't work without
        tools.replace_in_file(
            cmake_path, "set(_gRPC_BASELIB_LIBRARIES wsock32 ws2_32)", "set(_gRPC_BASELIB_LIBRARIES wsock32 ws2_32 crypt32)")

        # cmake_find_package_multi is producing a c-ares::c-ares target, grpc is looking for c-ares::cares
        tools.replace_in_file(
            os.path.join(self._source_dir, "cmake", "cares.cmake"), "c-ares::cares", "c-ares::c-ares")

#        tools.replace_in_file(cmake_path, "install(FILES ${CMAKE_CURRENT_SOURCE_DIR}/etc/roots.pem", '''export(TARGETS %s NAMESPACE #gRPC:: FILE gRPCTargets.cmake)
#install(FILES ${CMAKE_CURRENT_SOURCE_DIR}/etc/roots.pem''' % ' '.join([
#    'address_sorting', 'gpr',
#    'grpc', 'grpc_cronet', 'grpc_unsecure',
#    'grpc++', 'grpc++_cronet', 'grpc++_error_details', 'grpc++_reflection', 'grpc++_unsecure', 'grpc_plugin_support',
#    'grpc_cpp_plugin',
#    'grpc_node_plugin', 'grpc_php_plugin', 'grpc_python_plugin', 'grpc_ruby_plugin',
#]))

        # Parts which should be options:
        # grpc_cronet
        # grpc++_cronet
        # grpc_unsecure (?)
        # grpc++_unsecure (?)
        # grpc++_reflection
        # gen_hpack_tables (?)
        # gen_legal_metadata_characters (?)
        # grpc_csharp_plugin
        # grpc_node_plugin
        # grpc_objective_c_plugin
        # grpc_php_plugin
        # grpc_python_plugin
        # grpc_ruby_plugin

    def _configure_cmake(self):
        #self.env_info.PATH.append(os.path.join(self.deps_cpp_info["protobuf"].rootpath, "bin"))
        #self.env_info.LD_LIBRARY_PATH.append(os.path.join(self.deps_cpp_info["protobuf"].rootpath, "lib"))

        #env_build = RunEnvironment(self)

        # NOTE: make sure `protoc` can be found using PATH environment variable
        bin_path = ""
        for p in self.deps_cpp_info.bin_paths:
            bin_path = "%s%s%s" % (p, os.pathsep, bin_path)

        lib_path = ""
        for p in self.deps_cpp_info.lib_paths:
            lib_path = "%s%s%s" % (p, os.pathsep, lib_path)

        # NOTE: make sure `grpc_cpp_plugin` can be found using PATH environment variable
        path_to_grpc_cpp_plugin = os.path.join(os.getcwd(), "bin")

        env = {
             "PATH": "%s%s%s%s%s" % (path_to_grpc_cpp_plugin, os.pathsep, bin_path, os.pathsep, os.environ['PATH']),
             "LD_LIBRARY_PATH": "%s%s%s" % (lib_path, os.pathsep, os.environ['LD_LIBRARY_PATH'])
        }
        self.output.info("=================linux environment for %s=================\n" % (self.name))
        self.output.info('PATH = %s' % (env['PATH']))
        self.output.info('LD_LIBRARY_PATH = %s' % (env['LD_LIBRARY_PATH']))
        self.output.info('')
        with tools.environment_append(env):
            cmake = CMake(self, set_cmake_flags=True)
            cmake.verbose = True

            if (self.options.withOpenSSL):
                cmake.definitions["gRPC_SSL_PROVIDER"]="package"
                cmake.definitions["OPENSSL_ROOT_DIR"] = self.deps_cpp_info["openssl"].rootpath

            # This doesn't work yet as one would expect, because the install target builds everything
            # and we need the install target because of the generated CMake files
            #
            #   enable_mobile=False # Enables iOS and Android support
            #   non_cpp_plugins=False # Enables plugins such as --java-out and --py-out (if False, only --cpp-out is possible)
            #
            # cmake.definitions['CONAN_ADDITIONAL_PLUGINS'] = "ON" if self.options.build_csharp_ext else "OFF"
            #
            # Doesn't work yet for the same reason as above
            #
            # cmake.definitions['CONAN_ENABLE_MOBILE'] = "ON" if self.options.build_csharp_ext else "OFF"

            cmake.definitions["gRPC_PROTOBUF_PACKAGE_TYPE"] = "CONFIG"
            cmake.definitions["gRPC_GFLAGS_PROVIDER"] = "package"
            #cmake.definitions["gRPC_GFLAGS_PROVIDER"] = "module"
            cmake.definitions["ZLIB_ROOT"] = self.deps_cpp_info["zlib"].rootpath

            # If CMAKE_CROSSCOMPILING -> find_program for `protoc` and `grpc_cpp_plugin`
            #cmake.definitions['CMAKE_CROSSCOMPILING'] = "1"

            cmake.definitions['gRPC_BUILD_CODEGEN'] = "ON" if self.options.build_codegen else "OFF"
            cmake.definitions['gRPC_BUILD_CSHARP_EXT'] = "ON" if self.options.build_csharp_ext else "OFF"
            cmake.definitions['gRPC_BUILD_TESTS'] = "OFF"

            # We need the generated cmake/ files (bc they depend on the list of targets, which is dynamic)
            cmake.definitions['gRPC_INSTALL'] = "ON"
            #cmake.definitions['CMAKE_INSTALL_PREFIX'] = self._build_dir
            #cmake.definitions['CMAKE_INSTALL_PREFIX'] = self.package_folder

            # tell grpc to use the find_package versions
            cmake.definitions['gRPC_CARES_PROVIDER'] = "package"
            cmake.definitions['gRPC_ZLIB_PROVIDER'] = "package"
            cmake.definitions['gRPC_SSL_PROVIDER'] = "package"
            cmake.definitions['gRPC_PROTOBUF_PROVIDER'] = "package"
            #cmake.definitions['gRPC_PROTOBUF_PROVIDER'] = "module"

            # Compilation on minGW GCC requires to set _WIN32_WINNTT to at least 0x600
            # https://github.com/grpc/grpc/blob/109c570727c3089fef655edcdd0dd02cc5958010/include/grpc/impl/codegen/port_platform.h#L44
            if self.settings.os == "Windows" and self.settings.compiler == "gcc":
                cmake.definitions["CMAKE_CXX_FLAGS"] = "-D_WIN32_WINNT=0x600"
                cmake.definitions["CMAKE_C_FLAGS"] = "-D_WIN32_WINNT=0x600"

            #self.build_cmake_prefix_path(cmake,
            #    self.deps_cpp_info["c-ares"].rootpath,
            #    self.deps_cpp_info["protobuf"].rootpath
            #    self._build_dir,
            #    self._source_dir
            #)

            #cmake.definitions["CMAKE_PROGRAM_PATH"] += ";" + "/home/avakimov_am/.conan/data/protobuf/v3.9.1/conan/stable/package/1a651c5b4129ad794b88522bece2281a7453aee4/bin"

            self.output.warn("c-ares rootpath = {}".format(self.deps_cpp_info["c-ares"].rootpath))
            cmake.definitions["CMAKE_PREFIX_PATH"] += ";" + self.deps_cpp_info["c-ares"].rootpath
            cmake.definitions["CMAKE_MODULE_PATH"] += ";" + self.deps_cpp_info["c-ares"].rootpath

            self.output.warn("protobuf rootpath = {}".format(self.deps_cpp_info["protobuf"].rootpath))
            cmake.definitions["CMAKE_PREFIX_PATH"] += ";" + self.deps_cpp_info["protobuf"].rootpath
            cmake.definitions["CMAKE_MODULE_PATH"] += ";" + self.deps_cpp_info["protobuf"].rootpath

            #self.output.warn("protobuf binpath = {}".format(self.deps_cpp_info["protobuf"].binpath))
            #cmake.definitions["CMAKE_PREFIX_PATH"] += ";" + self.deps_cpp_info["protobuf"].binpath
            #cmake.definitions["CMAKE_MODULE_PATH"] += ";" + self.deps_cpp_info["protobuf"].binpath
            #cmake.definitions["CMAKE_PROGRAM_PATH"] += ";" + self.deps_cpp_info["protobuf"].binpath

            self.output.warn("build_dir = {}".format(self._build_dir))
            cmake.definitions["CMAKE_PREFIX_PATH"] += ";" + self._build_dir
            cmake.definitions["CMAKE_MODULE_PATH"] += ";" + self._build_dir

            self.output.warn("source_dir = {}".format(self._source_dir))
            cmake.definitions["CMAKE_PREFIX_PATH"] += ";" + self._source_dir
            cmake.definitions["CMAKE_MODULE_PATH"] += ";" + self._source_dir

            self.output.warn("package_folder = {}".format(self.package_folder))
            cmake.definitions["CMAKE_PREFIX_PATH"] += ";" + self.package_folder
            cmake.definitions["CMAKE_MODULE_PATH"] += ";" + self.package_folder

            cmake.configure(source_folder=self._source_dir, build_folder=self._build_dir)
            return cmake

    def build(self):
        self.output.info('Building package \'{}\''.format(self.name))
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()

        #cmake_files = ["gRPCConfig.cmake", "gRPCConfigVersion.cmake", "gRPCTargets.cmake"]
        #for file in cmake_files:
        #    self.copy(file, dst='.', src=cmake_folder)

        self.copy(pattern="LICENSE", dst="licenses")
        self.copy('*', dst='include', src='{}/include'.format(self._source_dir))
        self.copy('*.cmake', dst='lib', src='{}/lib'.format(self._build_dir), keep_path=True)
        self.copy("*.lib", dst="lib", src="", keep_path=False)
        self.copy("*.a", dst="lib", src="", keep_path=False)
        self.copy("*", dst="bin", src="bin")
        self.copy("*.dll", dst="bin", keep_path=False)
        self.copy("*.so", dst="lib", keep_path=False)

        # Make sure we do not package .git
        tools.rmdir(os.path.join(self.package_folder, '.git'))
        tools.rmdir(os.path.join(self.build_folder, '.git'))
        tools.rmdir(os.path.join(self.package_folder, self._source_dir, '.git'))
        tools.rmdir(os.path.join(self.build_folder, self._source_dir, '.git'))

        # We may need to run tests during build,
        # but do not package tests ever
        tools.rmdir(os.path.join(self.package_folder, 'tests'))
        tools.rmdir(os.path.join(self.package_folder, 'lib', 'tests'))
        tools.rmdir(os.path.join(self.build_folder, 'tests'))
        tools.rmdir(os.path.join(self.build_folder, 'lib', 'tests'))

        #libupb.a

        #os.remove(os.path.join(self.package_folder, "lib", "sample.lib"))
        #os.remove(os.path.join(self.package_folder, "lib", "libsample.a"))
        #os.remove(os.path.join(self.package_folder, "lib", "03-simple.a"))
        #os.remove(os.path.join(self.package_folder, "lib", "04-simple.a"))
        #os.remove(os.path.join(self.package_folder, "lib", "06-diff.a"))

        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.includedirs = ['{}/include'.format(self.package_folder)]
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
        self.env_info.LD_LIBRARY_PATH.append(os.path.join(self.package_folder, "lib"))
        self.env_info.PATH.append(os.path.join(self.package_folder, "lib"))
        self.cpp_info.libdirs = ["lib"]
        self.cpp_info.bindirs = ["bin"]
        # collects libupb, make sure to remove 03-simple.a
        #self.cpp_info.libs = tools.collect_libs(self)

        self.cpp_info.libs += [
            "grpc++",
            "grpc",
            "grpc++_unsecure",
            "grpc++_reflection",
            "grpc++_error_details",
            "grpc_unsecure",
            "grpc_plugin_support",
            "grpc_cronet",
            "grpcpp_channelz",
            "gpr",
            "address_sorting",
            # see upb_msg_new
            "upb"
        ]
        if self.settings.compiler == "Visual Studio":
            self.cpp_info.system_libs += ["wsock32", "ws2_32"]
        for libpath in self.deps_cpp_info.lib_paths:
            self.env_info.LD_LIBRARY_PATH.append(libpath)

        grpc_cpp_plugin = "grpc_cpp_plugin.exe" if self.settings.os_build == "Windows" else "grpc_cpp_plugin"
        self.env_info.grpc_cpp_plugin_BIN = os.path.normpath(os.path.join(self.package_folder, "bin", grpc_cpp_plugin))
        self.user_info.grpc_cpp_plugin_BIN = self.env_info.grpc_cpp_plugin_BIN

    # see `conan install . -g deploy` in https://docs.conan.io/en/latest/devtools/running_packages.html
    #def deploy(self):
        # self.copy("*", dst="/usr/local/bin", src="bin", keep_path=False)
        #self.copy("*", dst="bin", src="bin", keep_path=False)
