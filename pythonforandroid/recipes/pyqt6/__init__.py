import sh
from os.path import join
from pathlib import Path
import copy
import toml

from pythonforandroid.logger import shprint, info
from pythonforandroid.recipe import PyProjectRecipe, Recipe
from pythonforandroid.toolchain import current_directory


class PyQt6Recipe(PyProjectRecipe):
    version = '6.10.1'
    url = "https://pypi.python.org/packages/source/P/PyQt6/pyqt6-{version}.tar.gz"
    name = 'pyqt6'

    depends = ['qt6', 'pyjnius', 'setuptools', 'pyqt6sip', 'hostpython3']
    hostpython_prerequisites = ['sip', 'pyqt_builder']

    BINDINGS = ['QtCore', 'QtNetwork', 'QtGui', 'QtQml', 'QtQuick', 'QtMultimedia']

    def get_recipe_env(self, arch, **kwargs):
        env = super().get_recipe_env(arch)

        recipe = self.get_recipe('hostqt6', self.ctx)
        env['LD_LIBRARY_PATH'] = join(recipe.get_install_dir(), 'lib')

        recipe = self.get_recipe('qt6', self.ctx)
        qt6_env = recipe.get_recipe_env(arch)
        env['QT_EXT_PATH'] = qt6_env['QT_EXT_PATH']

        return env

    def update_pyproject_toml(self, arch):
        build_dir = self.get_build_dir(arch.arch)
        project_dict = {}
        with open(join(build_dir, 'pyproject.toml'), 'r') as f:
            project_dict = toml.load(f)

        info(repr(project_dict))
        if 'tool' not in project_dict:
            project_dict['tool'] = {'sip': {}}

        project_dict['tool']['sip']['project'] = {
            'android-abis': [arch.arch],
            'py-pylib-dir': self.ctx.python_recipe.link_root(arch.arch),
            'py-include-dir': self.ctx.python_recipe.include_root(arch.arch),
            'py-pylib-shlib': 'python{}'.format(self.ctx.python_recipe.link_version),
            'target-dir': self.ctx.get_python_install_dir(arch.arch)
        }

        project_dict['tool']['sip']['bindings'] = {}
        for binding in self.BINDINGS:
            project_dict['tool']['sip']['bindings'][binding] = {
                'extra-link-args': [
                    '-L{}'.format(self.ctx.python_recipe.link_root(arch.arch)),
                    '-lpython{}'.format(self.ctx.python_recipe.link_version)
                ],
                'disabled-features': ['PyQt_Wayland', 'PyQt_XCB']
            }

        with open(join(build_dir, 'pyproject.toml'), 'w') as f:
            toml.dump(project_dict, f)

    # def prebuild_arch(self, arch):
    #     super().prebuild_arch(arch)
    #     self.update_pyproject_toml(arch)

    def build_arch(self, arch):
        # super().build_arch(arch)  # NOTE: bypassing super().build_arch() might lead to issues..
        self.update_pyproject_toml(arch)
        self.install_hostpython_prerequisites()
        env = self.get_recipe_env(arch)
        env['PATH'] = ':'.join([env['QT_EXT_PATH'], env['PATH']])
        build_dir = self.get_build_dir(arch.arch)
        with current_directory(build_dir):
            info("compiling pyqt6")

            hostpython = self.get_recipe('hostpython3', self.ctx)
            pythondir = hostpython.get_path_to_python()
            # site_packages = join(pythondir, 'Lib', 'site-packages')
            site_packages = join(hostpython.site_dir)
            env = copy.copy(env)
            env['PYTHONPATH'] = ':'.join([
                pythondir,
                site_packages,
                env.get('PYTHONPATH', '')
            ])

            buildcmd = sh.Command(self.ctx.hostpython)
            sip_install = join(hostpython.site_bin, 'sip-install')
            info(f'ENV: {env}')
            buildcmd = buildcmd.bake(sip_install)
            buildcmd = buildcmd.bake('--confirm-license', '--qt-shared', '--verbose')
            buildcmd = buildcmd.bake('--no-tools', '--no-qml-plugin', '--no-designer-plugin', '--no-dbus-python')
            buildcmd = buildcmd.bake('--no-distinfo')

            for include in self.BINDINGS:
                buildcmd = buildcmd.bake('--enable', include)

            shprint(buildcmd, _env=env, _tail=50, _critical=True)

            with open(join(build_dir, 'compile_finished'), 'w') as fp:
                fp.write('')

    def should_build(self, arch):
        build_dir = self.get_build_dir(arch.arch)
        return not Path(join(build_dir, 'compile_finished')).is_file()


recipe = PyQt6Recipe()
