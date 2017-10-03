import enum
import hashlib
import json
import os
import pathlib
import subprocess

import attr


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

    def save_installer(self, data, into_path):
        checksum = hashlib.md5(data).hexdigest()
        if checksum != self.md5_sum:
            raise DownloadIntegrityError('expect {}, got {}'.format(
                self.md5_sum, checksum,
            ))
        with into_path.open('wb') as f:
            f.write(data)


class CPythonMSIVersion(Version):
    def install(self, cmd):
        pass


class CPythonVersion(Version):

    def install(self, cmd):
        dirpath = pathlib.Path(
            os.environ['LocalAppData'], 'Programs', 'Python',
            'Python{}'.format(self.name.replace('.', '')),
        )
        subprocess.check_call([
            cmd, '/passive', 'InstallAllUsers=0',
            'DefaultJustForMeTargetDir={}'.format(dirpath),
            'Include_launcher=1', 'InstallLauncherAllUsers=1',
            'AssociateFiles=0', 'PrependPath=0', 'Shortcuts=0',
            'Include_test=0', 'Include_tools=0',
        ])
        return dirpath

    def uninstall(self, cmd):
        subprocess.check_call([cmd, '/uninstall'])


def get_version(name):
    path = pathlib.Path(__file__).with_name('{}.json'.format(name))
    try:
        with path.open() as f:
            data = json.load(f)
    except FileNotFoundError:
        raise VersionNotFoundError(name)

    installer_type = InstallerType(data.pop('installer_type'))
    klass = {
        InstallerType.cpython_msi: CPythonMSIVersion,
        InstallerType.cpython: CPythonVersion,
    }[installer_type]

    return klass(name=name, **data)
