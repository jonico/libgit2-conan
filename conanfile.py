from conans import ConanFile, tools, CMake
import os
from os import path
import glob
from shutil import copyfile

class LibgitConan(ConanFile):
    """
    Conan package for libgit2 library https://github.com/libgit2/libgit2
    """
    name = "libgit2"
    version = "0.24.2"
    license="GPLv2+linkException"
    url = "https://github.com/paulobrizolara/libgit2-conan.git"

    generators = "cmake"

    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared" : [True, False],

        "use_openssl"   : [True, False],
        "use_ssh"       : [True, False],
    }
    default_options = "shared=True", "use_openssl=True", "use_ssh=True"

    scopes = {
        "build_examples" : [True, False],
        "build_tests" : [True, False]
    }
    default_scopes = "build_examples=False", "build_tests=False"

    ZIP_NAME = "v%s.tar.gz" % version
    UNZIPPED_FOLDER = "libgit2-%s" % version
    FILE_URL = "https://github.com/libgit2/libgit2/archive/%s" % ZIP_NAME
    FILE_SHA256 = '00f0a7403143fba69601accc80cacf49becc568b890ba232f300c1b2a37475e6'

    def requirements(self):
        if self.options.use_openssl:
            self.requires("OpenSSL/1.0.2h@lasote/stable")

        if self.options.use_ssh:
            pass #TODO: add dependency to libssh

    def source(self):
        tools.download(self.FILE_URL, self.ZIP_NAME)
        tools.check_sha256(self.ZIP_NAME, self.FILE_SHA256)
        tools.untargz(self.ZIP_NAME)
        os.unlink(self.ZIP_NAME)

    def cmake_args(self):
        """Generate arguments for cmake"""

        args = ["-DBUILD_SHARED_LIBS=%s" % ("ON" if self.options.shared else "OFF")]
        args += ['-DCMAKE_INSTALL_PREFIX="%s"' % self.package_folder]

        for opt_lib in ("openssl", "ssh"):
            use_arg = "use_" + opt_lib
            use = getattr(self.options, use_arg, False)

            args.append(self.cmake_bool_option(use_arg, use));

        args.append(self.cmake_bool_option("build_clar", self.scope.build_tests));
        args.append(self.cmake_bool_option("build_examples", self.scope.build_examples));

        return ' '.join(args)

    def cmake_bool_option(self, name, value):
        return "-D%s=%s" % (name.upper(), "ON" if value else "OFF");

    def build(self):
        #Make build dir
        build_dir = self.try_make_dir(os.path.join(".", "build"))

        #Change to build dir
        os.chdir(build_dir)

        cmake = CMake(self.settings)

        src_dir = path.join(self.conanfile_directory, self.UNZIPPED_FOLDER)

        self.run('cmake "%s" %s %s' % (src_dir, cmake.command_line, self.cmake_args()))
        self.run('cmake --build . --target install %s' % cmake.build_config)

    def package(self):
#        self.copy("*.hpp", "include", path.join(self.GIT_DIRNAME, "src"))
#        self.copy("*", "lib", path.join('build', 'bin'))
        pass

    def package_info(self):
        self.cpp_info.libs = ["git2"]

    def try_make_dir(self, dir):
        try:
            os.mkdir(dir)
            return dir
        except OSError:
            #dir already exist
            pass
