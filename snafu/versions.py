import enum
import hashlib
import json
import os
import pathlib
import re
import subprocess

import attr

from . import configs, metadata


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


VERSIONS_DIR_PATH = pathlib.Path(__file__).with_name('versions').resolve()


def load_version_data(name):
    try:
        with VERSIONS_DIR_PATH.joinpath('{}.json'.format(name)).open() as f:
            data = json.load(f)
    except FileNotFoundError:
        raise VersionNotFoundError(name)
    return data


@attr.s
class Version:

    name = attr.ib()
    url = attr.ib()
    md5_sum = attr.ib()
    version_info = attr.ib(convert=tuple)

    def __str__(self):
        return 'Python {}'.format(self.name)

    @property
    def major_version(self):
        return str(self.version_info[0])

    @property
    def launcher(self):
        scriptd_dir = configs.get_scripts_dir_path()
        return scriptd_dir.joinpath('python{}.cmd'.format(self.name))

    @property
    def installation(self):
        return metadata.get_install_path(self.name)

    def is_installed(self):
        try:
            exists = metadata.get_install_path(self.name).exists()
        except FileNotFoundError:
            return False
        return exists

    def save_installer(self, data, into_path):
        checksum = hashlib.md5(data).hexdigest()
        if checksum != self.md5_sum:
            raise DownloadIntegrityError('expect {}, got {}'.format(
                self.md5_sum, checksum,
            ))
        with into_path.open('wb') as f:
            f.write(data)

    def get_target_for_install(self):
        return pathlib.Path(
            os.environ['LocalAppData'], 'Programs', 'Python',
            'Python{}'.format(self.name.replace('.', '')),
        )

    def get_scripts_dir_path(self):
        return self.installation.joinpath('Scripts')


class CPythonMSIVersion(Version):

    @classmethod
    def load(cls, name, data, *, force_32):
        variant = data['x86' if force_32 else 'amd64']
        return cls(
            name=name,
            version_info=data['version_info'],
            url=variant['url'],
            md5_sum=variant['md5_sum'],
        )

    def install(self, cmd):
        dirpath = self.get_target_for_install()
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

    @classmethod
    def load(cls, name, data, *, force_32):
        if force_32 and not name.endswith('-32'):
            name = '{}-32'.format(name)
            data = load_version_data(name)
        return cls(
            name=name,
            version_info=data['version_info'],
            url=data['url'],
            md5_sum=data['md5_sum'],
        )

    def install(self, cmd):
        dirpath = self.get_target_for_install()
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


def get_version(name, *, force_32):
    data = load_version_data(name)
    installer_type = InstallerType(data['$schema'])
    klass = {
        InstallerType.cpython_msi: CPythonMSIVersion,
        InstallerType.cpython: CPythonVersion,
    }[installer_type]
    return klass.load(name, data, force_32=force_32)


VERSION_NAME_RE = re.compile(r'^\d+\.\d+(:?\-32)?$')


def get_versions():
    return [
        get_version(p.stem, force_32=False)
        for p in VERSIONS_DIR_PATH.iterdir()
        if p.suffix == '.json' and VERSION_NAME_RE.match(p.stem)
    ]
