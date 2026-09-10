from pythonforandroid.recipe import PyProjectRecipe


class KiwiSolverRecipe(PyProjectRecipe):
    site_packages_name = 'kiwisolver'
    version = '1.4.5'
    url = 'git+https://github.com/nucleic/kiwi'
    depends = ['cppy']
    need_stl_shared = True

    def get_recipe_env(self, arch, **kwargs):
        """Add the Python include path, refs: #3115."""
        env = super().get_recipe_env(arch, **kwargs)
        flags = " -I" + self.ctx.python_recipe.include_root(arch.arch)
        env["CFLAGS"] += flags
        env["CPPFLAGS"] += flags
        return env


recipe = KiwiSolverRecipe()
