import toml
from os.path import join
from pythonforandroid.recipe import PyProjectRecipe
from pythonforandroid.logger import info


class SipRecipe(PyProjectRecipe):
    version = '6.15.1'
    url = "https://pypi.python.org/packages/source/s/sip/sip-{version}.tar.gz"
    name = 'sip'

    hostpython_prerequisites = ["setuptools>=77", "setuptools_scm>=8"]
    depends = ["python3", "packaging"]

    call_hostpython_via_targetpython = False
    install_in_hostpython = True
    install_in_targetpython = False
    site_packages_name = 'sipbuild'

    def build_arch(self, arch):
        build_dir = self.get_build_dir(arch.arch)
        with open(join(build_dir, 'pyproject.toml'), 'r') as f:
            project_dict = toml.load(f)
        info(repr(project_dict))
        if 'license' in project_dict['project']:
            del project_dict['project']['license']
        if 'license-files' in project_dict['project']:
            del project_dict['project']['license-files']
        project_dict['tool']['setuptools'] = {'packages': ['sipbuild']}
        with open(join(build_dir, 'pyproject.toml'), 'w') as f:
            toml.dump(project_dict, f)

        super().build_arch(arch)


recipe = SipRecipe()
