import itertools
import os
import pathlib
import re
import subprocess

import attr


@attr.s
class Installation:

    path = attr.ib(convert=pathlib.Path)

    def __repr__(self):
        return '<Python Installation at "{}">'.format(self.path)

    @property
    def scripts_dir(self):
        return self.path.joinpath('Scripts')

    @property
    def python(self):
        return self.path.joinpath('python.exe')

    @property
    def pip(self):
        return self.scripts_dir.joinpath('pip.exe')

    def get_version_info(self):
        output = subprocess.check_output(
            [self.python, '--version'], shell=True,
        ).decode('ascii', 'ignore')
        match = re.match(r'^Python (\d+)\.(\d+)\.(\d+).*$', output.strip())
        if not match:
            raise RuntimeError(
                'Could not read installed version for {}'.format(self),
            )
        return tuple(int(g) for g in match.groups())

    def find_script(self, name):
        extensions = os.environ['PathExt'].split(';')
        command_filename_iter = itertools.chain(
            [name], ('{}{}'.format(name, ext) for ext in extensions),
        )
        scripts_dir = self.scripts_dir
        for fn in command_filename_iter:
            path = scripts_dir.joinpath(fn)
            if path.is_file():
                return path.resolve()
        raise FileNotFoundError(name)
