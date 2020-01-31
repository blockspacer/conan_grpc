from conans import ConanFile, CMake, tools
import os


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_paths", "virtualenv", "cmake_find_package_multi"

    def build(self):
        cmake = CMake(self)
        cmake.definitions["protobuf_VERBOSE"] = True
        cmake.definitions["protobuf_MODULE_COMPATIBLE"] = True
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self.settings):
            self.run("protoc --version", run_environment=True)
        if not tools.cross_building(self.settings):
            bin_path = os.path.join(".", "bin", "greeter_client_server")
            self.run(bin_path, run_environment=True)

    def deploy(self):
        # self.copy("*", dst="/usr/local/bin", src="bin", keep_path=False)
        self.copy("*", dst="bin", src="bin", keep_path=False)
