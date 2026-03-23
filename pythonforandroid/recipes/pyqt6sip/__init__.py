from pythonforandroid.recipe import PythonRecipe


class PyQt6SipRecipe(PythonRecipe):
    version = '13.10.3'
    url = "https://pypi.python.org/packages/source/P/PyQt6_sip/pyqt6_sip-{version}.tar.gz"
    name = 'pyqt6sip'

    hostpython_prerequisites = ['setuptools']

    call_hostpython_via_targetpython = False
    site_packages_name = 'PyQt6.sip'


recipe = PyQt6SipRecipe()
