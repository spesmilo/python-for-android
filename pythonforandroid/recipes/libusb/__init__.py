
from pythonforandroid.recipe import CythonRecipe, Recipe
from pythonforandroid.toolchain import shprint, current_directory, info
from os.path import join, exists
import sh


class LibUsbRecipe(Recipe):
    version = '1.0.29'
    url = 'https://github.com/libusb/libusb/archive/v{version}.tar.gz'
    sha256sum = '7c2dd39c0b2589236e48c93247c986ae272e27570942b4163cb00a060fcf1b74'
    name = 'libusb'
    depends = ['python3']
    built_libraries = {'libusb-1.0.a': 'libusb/.libs'}

    patches = ['android-logging.patch']

    def get_recipe_env(self, arch):
        env = super().get_recipe_env(arch)
        env['NOCONFIGURE'] = '1'  # don't let autogen.sh call configure without params
        env['ENABLE_LOGGING'] = '1'
        # env['ENABLE_DEBUG_LOGGING'] = '1'
        env['USE_SYSTEM_LOGGING_FACILITY'] = '1'
        return env

    def build_arch(self, arch):
        env = self.get_recipe_env(arch)
        with current_directory(self.get_build_dir(arch.arch)):
            if not exists('configure'):
                shprint(sh.Command('./autogen.sh'), _env=env)
            shprint(
                sh.Command('./configure'),
                '--host=' + arch.command_prefix,
                '--prefix=' + self.ctx.get_python_install_dir(arch.arch),
                # '--enable-shared',
                '--disable-udev',
                _env=env)
            shprint(sh.make, _env=env)

            shprint(sh.make, 'install', _env=env)

recipe = LibUsbRecipe()
