from pythonforandroid.recipe import PyProjectRecipe


class SetuptoolsRecipe(PyProjectRecipe):
    hostpython_prerequisites = ['setuptools']
    version = '80.9.0'


recipe = SetuptoolsRecipe()
