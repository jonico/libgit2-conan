from conans import ConanFile, CMake
import os
from os import path
from shutil import copyfile

username = os.getenv("CONAN_USERNAME", "paulobrizolara")
channel = os.getenv("CONAN_CHANNEL", "testing")
library = "libgit2"
version = "0.24.2"

class PackageTest(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    requires = "%s/%s@%s/%s" % (library, version, username, channel)
    generators = "cmake"
    default_options = ""

    def build(self):
        #Make build dir
        build_dir = os.path.join(".", "build")
        self._try_make_dir(build_dir)

        #Copy
        build_info = "conanbuildinfo.cmake"
        copyfile(build_info, os.path.join(build_dir, build_info))

        #Change to build dir
        os.chdir(build_dir)

        cmake = CMake(self.settings)

        self.run('cmake "%s" %s' % (self.conanfile_directory, cmake.command_line))
        self.run('cmake --build . %s' % cmake.build_config)

    def test(self):
        self.run(path.join("bin", "example"))

    def _try_make_dir(self, dir):
        try:
            os.mkdir(dir)
        except OSError:
            #dir already exist
            pass
