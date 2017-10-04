import enum
import hashlib
import json
import os
import pathlib
import re
import subprocess

import attr

from . import metadata


class VersionNotFoundError(ValueError):
    pass


class DownloadIntegrityError(ValueError):
    pass


class InstallerType(enum.Enum):
    # Old MSI installer format used by CPython until the 3.4 line.
    # Usage: https://www.python.org/download/releases/2.5/msi/
    cpython_msi = 'cpython_msi'

    # New Python installer introduced in CPython 3.5.
    # Usage: https://docs.python.org/3/using/windows.html#installing-without-ui
    cpython = 'cpython'


@attr.s
class Version:

    name = attr.ib()
    url = attr.ib()
    md5_sum = attr.ib()
    version_info = attr.ib(convert=tuple)

    def __str__(self):
        return 'Python {}'.format(self.name)

    @property
    def launcher_names(self):
        return [
            'python{0}'.format(*self.version_info),
            'python{0}.{1}'.format(*self.version_info),
        ]

    def is_installed(self):
        return metadata.is_installed(self.name)

    def save_installer(self, data, into_path):
        checksum = hashlib.md5(data).hexdigest()
        if checksum != self.md5_sum:
            raise DownloadIntegrityError('expect {}, got {}'.format(
                self.md5_sum, checksum,
            ))
        with into_path.open('wb') as f:
            f.write(data)

    def get_install_dir_path(self):
        return pathlib.Path(
            os.environ['LocalAppData'], 'Programs', 'Python',
            'Python{}'.format(self.name.replace('.', '')),
        )

    def get_scripts_dir_path(self):
        return self.get_install_dir_path().joinpath('Scripts')


class CPythonMSIVersion(Version):

    def install(self, cmd):
        dirpath = self.get_install_dir_path()
        parts = [   # Argument ordering is very important.
            # Options and required parameters.
            'msiexec', '/i', '"{}"'.format(cmd),

            # Optional parameters and flags.
            '/qb', 'TARGETDIR="{}"'.format(dirpath),
            'ADDLOCAL=DefaultFeature,TclTk,Documentation',

            # This does not do what you think. DO NOT SUPPLY IT.
            # The installer is per-user by default.
            # 'ALLUSERS=0',
        ]
        subprocess.check_call(
            ' '.join(parts),
            shell=True,     # So we don't need to know where msiexec is.
        )
        return dirpath

    def uninstall(self, cmd):
        subprocess.check_call('msiexec /x "{}" /qb'.format(cmd), shell=True)


class CPythonVersion(Version):

    def install(self, cmd):
        dirpath = self.get_install_dir_path()
        subprocess.check_call([
            cmd, '/passive', 'InstallAllUsers=0',
            'DefaultJustForMeTargetDir={}'.format(dirpath),
            'AssociateFiles=0', 'PrependPath=0', 'Shortcuts=0',
            'Include_launcher=0', 'Include_test=0', 'Include_tools=0',
            'InstallLauncherAllUsers=0',
        ])
        return dirpath

    def uninstall(self, cmd):
        subprocess.check_call([cmd, '/uninstall'])


VERSIONS_DIR_PATH = pathlib.Path(__file__).with_name('versions').resolve()


def get_version(name):
    try:
        with VERSIONS_DIR_PATH.joinpath('{}.json'.format(name)).open() as f:
            data = json.load(f)
    except FileNotFoundError:
        raise VersionNotFoundError(name)

    installer_type = InstallerType(data.pop('installer_type'))
    klass = {
        InstallerType.cpython_msi: CPythonMSIVersion,
        InstallerType.cpython: CPythonVersion,
    }[installer_type]

    return klass(name=name, **data)


VERSION_NAME_RE = re.compile(r'^\d+\.\d+(:?\-32)?$')


def get_versions():
    return [
        get_version(p.stem)
        for p in VERSIONS_DIR_PATH.iterdir()
        if p.suffix == '.json' and VERSION_NAME_RE.match(p.stem)
    ]
