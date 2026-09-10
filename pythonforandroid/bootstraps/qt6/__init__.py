from pythonforandroid.toolchain import Bootstrap, current_directory, info, info_main, shprint
from pythonforandroid.util import ensure_dir, rmdir
from os.path import join
import sh
import glob


class Qt6Bootstrap(Bootstrap):
    name = 'qt6'

    recipe_depends = list(
        set(Bootstrap.recipe_depends).union({'qt6'})
    )

    # only build with this bootstrap when explicitly asked for
    can_be_chosen_automatically = False

    def assemble_distribution(self):
        info_main('# Creating Android project from build and {} bootstrap'.format(
            self.name))

        # The bootstrap build dir contains the whole Qt source and build tree
        # (jni/qt6), so instead of copying it wholesale like the base class
        # does, only rsync an allowlist of files into the dist.
        rmdir(self.dist_dir)
        ensure_dir(self.dist_dir)

        file_include_patterns = [
            ('*', False),
            ('jni/*', False),
            ('jni/application/**', True),
            ('src/**', True),
            ('templates/**', True),
            ('gradle/**', True),
            ('**/*.so', True),
            ('**/qmldir', True),
        ]

        with current_directory(self.dist_dir):
            with open('bootstrap_distfiles.txt', 'w') as fileh:
                for pattern, recurse in file_include_patterns:
                    filenames = glob.glob(pattern, root_dir=self.build_dir, recursive=recurse)
                    for filename in filenames:
                        fileh.write(f'{filename}\n')
                    info(f'pattern {pattern}, recurse={recurse} yielded {len(filenames)} items')

            shprint(sh.rsync, '--files-from=bootstrap_distfiles.txt',
                    self.build_dir, '.')

            with open('local.properties', 'w') as fileh:
                fileh.write('sdk.dir={}'.format(self.ctx.sdk_dir))

            info('Copying python distribution')

            self.distribute_javaclasses(self.ctx.javaclass_dir,
                                        dest_dir=join("src", "main", "java"))

            for arch in self.ctx.archs:
                self._assemble_distribution_for_arch(arch)

            if 'sqlite3' not in self.ctx.recipe_build_order:
                with open('blacklist.txt', 'a') as fileh:
                    fileh.write('\nsqlite3/*\nlib-dynload/_sqlite3.so\n')

        # Not super().assemble_distribution(): the base class would copy the
        # whole build dir over the dist. Only do its final steps.
        self._copy_in_final_files()
        self.distribution.save_info(self.dist_dir)


bootstrap = Qt6Bootstrap()
