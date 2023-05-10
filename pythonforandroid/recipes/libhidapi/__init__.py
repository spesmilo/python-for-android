
from pythonforandroid.recipe import Recipe
from pythonforandroid.util import ensure_dir
from pythonforandroid.toolchain import shprint, current_directory, info
from os.path import join, exists
import sh


class LibHidapiRecipe(Recipe):
    version = '0.14.0'
    url = 'https://github.com/libusb/hidapi/archive/hidapi-{version}.tar.gz'
    sha256sum = 'a5714234abe6e1f53647dd8cba7d69f65f71c558b7896ed218864ffcf405bcbd'
    name = 'libhidapi'
    depends = ['python3', 'libusb']
    built_libraries = {'libhidapi-libusb.a': 'install_target/lib'}
    patches = ['libusb-locate.patch', 'android-init.patch']

    def get_recipe_env(self, arch):
        env = super().get_recipe_env(arch)
        libusb = self.get_recipe('libusb', self.ctx)
        env['WITH_LIBUSB'] = join(libusb.get_build_dir(arch.arch), 'libusb')
        return env

    def build_arch(self, arch):
        source_dir = self.get_build_dir(arch.arch)
        install_target = join(source_dir, 'install_target')

        with current_directory(source_dir):
            env = self.get_recipe_env(arch)
            shprint(sh.cmake, source_dir,
                    '-DANDROID_ABI={}'.format(arch.arch),
                    '-DANDROID_NATIVE_API_LEVEL={}'.format(self.ctx.ndk_api),
                    '-DCMAKE_TOOLCHAIN_FILE={}'.format(
                        join(self.ctx.ndk_dir, 'build', 'cmake',
                             'android.toolchain.cmake')),
                    '-DCMAKE_INSTALL_PREFIX={}'.format(install_target),
                    '-DCMAKE_BUILD_TYPE=Release',
                    '-DBUILD_SHARED_LIBS=0',
                    _env=env)
            shprint(sh.make, _env=env)

            shprint(sh.make, 'install', _env=env)


recipe = LibHidapiRecipe()
