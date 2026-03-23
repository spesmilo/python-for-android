import toml
from os.path import join
from pythonforandroid.recipe import PyProjectRecipe
from pythonforandroid.logger import info

class PyQtBuilderRecipe(PyProjectRecipe):
    version = '1.19.1'
    url = "https://pypi.python.org/packages/source/P/PyQt-builder/pyqt_builder-{version}.tar.gz"
    name = 'pyqt_builder'

    depends = ['sip']

    call_hostpython_via_targetpython = False
    install_in_hostpython = True
    install_in_targetpython = False
    site_packages_name = 'pyqtbuild'

    def build_arch(self, arch):
        build_dir = self.get_build_dir(arch.arch)
        with open(join(build_dir, 'pyproject.toml'), 'r') as f:
            project_dict = toml.load(f)
        info(repr(project_dict))
        if 'license' in project_dict['project']:
            del project_dict['project']['license']
        if 'license-files' in project_dict['project']:
            del project_dict['project']['license-files']
        project_dict['tool']['setuptools'] = {'packages': [
            'pyqtbuild', 'pyqtbuild.bundle', 'pyqtbuild.bundle.dlls',
            'pyqtbuild.bundle.packages', 'pyqtbuild.bundle.qt_wheel_distinfo'
        ]}

        with open(join(build_dir, 'pyproject.toml'), 'w') as f:
            toml.dump(project_dict, f)

        super().build_arch(arch)

recipe = PyQtBuilderRecipe()
