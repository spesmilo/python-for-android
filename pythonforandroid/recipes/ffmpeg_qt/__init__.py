from multiprocessing import cpu_count
from os.path import join

import sh

from pythonforandroid.logger import shprint
from pythonforandroid.recipe import Recipe
from pythonforandroid.util import current_directory


class FFmpegQtRecipe(Recipe):
    """FFmpeg libraries for Qt 6's Android Camera2 capture backend.

    This build supports camera preview and frame conversion. Playback and
    recording codecs are deliberately omitted; the general-purpose ffmpeg
    recipe remains available for applications that need them.
    """

    version = '7.1.5'
    url = 'https://ffmpeg.org/releases/ffmpeg-{version}.tar.xz'
    depends = []
    conflicts = ['ffmpeg']
    built_libraries = {
        'libavcodec.so': 'install/lib',
        'libavformat.so': 'install/lib',
        'libavutil.so': 'install/lib',
        'libswresample.so': 'install/lib',
        'libswscale.so': 'install/lib',
    }

    def get_install_dir(self, arch):
        return join(self.get_build_dir(arch), 'install')

    def build_arch(self, arch):
        # Keep the target flags in CC too: FFmpeg uses CC for linking without
        # CFLAGS, which would otherwise make the NDK clang target the host.
        env = self.get_recipe_env(arch)
        ffmpeg_arch = {
            'armeabi-v7a': 'arm',
            'arm64-v8a': 'aarch64',
            'x86': 'x86',
            'x86_64': 'x86_64',
        }[arch.arch]
        flags = [
            '--prefix=' + self.get_install_dir(arch.arch),
            # Android installs unversioned .so files and uses matching SONAMEs.
            '--target-os=android',
            '--enable-cross-compile',
            '--arch=' + ffmpeg_arch,
            '--sysroot=' + self.ctx.ndk.sysroot,
            # FFmpeg does not use CC/AR/etc. from the environment.
            '--cc=' + env['CC'],
            '--cxx=' + env['CXX'],
            '--ar=' + env['AR'],
            '--ranlib=' + env['RANLIB'],
            '--strip=' + self.ctx.ndk.llvm_strip,
            '--nm=' + self.ctx.ndk.llvm_binutils_prefix + 'nm',
            '--disable-autodetect',
            '--pkg-config=false',
            '--disable-iconv',
            '--disable-everything',
            '--disable-programs',
            '--disable-doc',
            '--disable-debug',
            '--disable-network',
            '--disable-avdevice',
            '--disable-avfilter',
            '--disable-postproc',
            '--disable-static',
            '--enable-shared',
            '--enable-pic',
            '--enable-jni',
            '--enable-mediacodec',
        ]
        if arch.arch in ('x86', 'x86_64'):
            # Avoid a host NASM dependency; retain compiler/inline assembly.
            flags.append('--disable-x86asm')

        with current_directory(self.get_build_dir(arch.arch)):
            shprint(sh.Command('./configure'), *flags, _env=env)
            shprint(sh.make, '-j' + str(cpu_count()), _env=env)
            shprint(sh.make, 'install', _env=env)


recipe = FFmpegQtRecipe()
