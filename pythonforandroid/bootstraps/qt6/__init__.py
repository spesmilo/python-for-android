from pythonforandroid.toolchain import Bootstrap


class Qt6Bootstrap(Bootstrap):
    name = 'qt6'

    recipe_depends = list(
        set(Bootstrap.recipe_depends).union({'genericndkbuild', 'qt6'})
    )


bootstrap = Qt6Bootstrap()
