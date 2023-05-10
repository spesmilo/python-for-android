
from pythonforandroid.recipe import CythonRecipe, Recipe
from pythonforandroid.toolchain import shprint, current_directory, info
from os.path import join, exists
import sh


class HidapiRecipe(CythonRecipe):
    # version = '0.14.0.post2'
    version = 'bb52ce495fc9c9fcdc0909cb9902666138f9e3cd'
    # url = 'https://github.com/trezor/cython-hidapi/archive/{version}.tar.gz'
    url = 'git+https://github.com/trezor/cython-hidapi.git'
    sha256sum = '72c51470f529f6e2f1b14a11c0220ed426af36efcd04dd1e58b97f3fb5702d74'
    name = 'hidapi'
    depends = ['python3', 'libusb', 'libhidapi']

    patches = ['no-explicit-cythonize.patch']

    # cythonize = False

    # call_hostpython_via_targetpython = False

    # def get_recipe_env(self, arch):
    #     env = super().get_recipe_env(arch)
    #     # libusb= self.get_recipe('libusb', self.ctx)
    #     # env['WITH_LIBUSB'] = join(libusb.get_build_dir(arch.arch), 'libusb')
    #     return env

    # def build_arch(self, arch):
    #     source_dir = self.get_build_dir(arch.arch)
    # #     install_target = join(source_dir, 'install_target')
    # #
    #     with current_directory(source_dir):
            # env = self.get_recipe_env(arch)
    #         shprint(sh.cmake, source_dir,
    #                 '-DANDROID_ABI={}'.format(arch.arch),
    #                 '-DANDROID_NATIVE_API_LEVEL={}'.format(self.ctx.ndk_api),
    #                 '-DCMAKE_TOOLCHAIN_FILE={}'.format(
    #                     join(self.ctx.ndk_dir, 'build', 'cmake',
    #                          'android.toolchain.cmake')),
    #                 '-DCMAKE_INSTALL_PREFIX={}'.format(install_target),
    #                 '-DCMAKE_BUILD_TYPE=Release',
    #                 '-DBUILD_SHARED_LIBS=1',
    #                 _env=env)
    #         shprint(sh.make, _env=env)
    #
    #         shprint(sh.make, 'install', _env=env)

    def get_recipe_env(self, arch=None, with_flags_in_cc=True):
        env = super().get_recipe_env(arch, with_flags_in_cc)

        libhidapi = self.get_recipe('libhidapi', self.ctx)
        libhidapi_dir = libhidapi.get_build_dir(arch.arch)
        # env['PYTHON_ROOT'] = self.ctx.get_python_install_dir(arch.arch)
        env['HIDAPI_CFLAGS'] = '-I' + join(libhidapi_dir, 'install_target', 'include', 'hidapi')
        env['HIDAPI_LIBS'] = '-L' + join(libhidapi_dir, 'install_target', 'lib')
        env['HIDAPI_WITH_LIBUSB'] = '1'
        env['HIDAPI_SYSTEM_HIDAPI'] = '1'

        libusb = self.get_recipe('libusb', self.ctx)
        libusb_dir = libusb.get_build_dir(arch.arch)
        env['LIBUSB_CFLAGS'] = '-I' + join(libusb_dir, 'libusb')
        env['LIBUSB_LIBS'] = '-L' + join(libusb_dir, 'libusb', '.libs')

        env['HIDAPI_LIB'] = join(libhidapi_dir, 'install_target', 'lib', 'libhidapi-libusb.a')
        env['LIBUSB_LIB'] = join(libusb_dir, 'libusb', '.libs', 'libusb-1.0.a')

        # env['ANDROID_ABI'] = str(arch.arch)
        # env['ANDROID_NATIVE_API_LEVEL'] = str(self.ctx.ndk_api)
        # env['CMAKE_TOOLCHAIN_FILE'] = join(self.ctx.ndk_dir, 'build', 'cmake', 'android.toolchain.cmake')
        # env['LIBS'] = env.get('LIBS', '') + ' -landroid -lzbar'
        return env

    def build_cython_components(self, arch):

        # libhidapi_recipe = Recipe.get_recipe('libhidapi', self.ctx)
        # libhidapi_prefix = join(libhidapi_recipe.get_build_dir(arch.arch), "install")
        # self.setup_extra_args = ["--with-system-hidapi={}".format(libzmq_prefix)]
        # self.build_cmd = "configure"

        env = self.get_recipe_env(arch)

        return super().build_cython_components(arch)

        # with current_directory(self.get_build_dir(arch.arch)):
        #     hostpython = sh.Command(self.hostpython_location)
        #     shprint(hostpython, 'setup.py', 'configure', '-v', _env=env)
        #     shprint(hostpython, 'setup.py', 'build_ext', '-v', _env=env)
        #     build_dir = glob.glob('build/lib.*')[0]
        #     shprint(sh.find, build_dir, '-name', '"*.o"', '-exec',
        #             env['STRIP'], '{}', ';', _env=env)

recipe = HidapiRecipe()
