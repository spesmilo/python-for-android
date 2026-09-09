from pythonforandroid.toolchain import Bootstrap


class Qt6Bootstrap(Bootstrap):
    name = 'qt6'

    recipe_depends = list(
        set(Bootstrap.recipe_depends).union({'genericndkbuild', 'qt6'})
    )

    # only build with this bootstrap when explicitly asked for
    can_be_chosen_automatically = False


bootstrap = Qt6Bootstrap()
