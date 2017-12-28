import enum
import hashlib
import json
import os
import pathlib
import re
import subprocess

import attr

from . import configs, installations, metadata


class VersionNotFoundError(ValueError):
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
    product_codes = attr.ib(default=attr.Factory(dict))
    forced_32 = attr.ib(default=False)

    def __str__(self):
        return 'Python {}'.format(self.name)

    @property
    def arch_free_name(self):
        return self.name.split('-', 1)[0]

    @property
    def script_version_names(self):
        # Use set to avoid duplicates.
        if self.forced_32:
            return {self.name, self.arch_free_name}
        return {self.name}

    @property
    def python_commands(self):
        dirpath = configs.get_cmd_dir_path()
        return [
            dirpath.joinpath('python{}.exe'.format(name))
            for name in self.script_version_names
        ]

    @property
    def pip_commands(self):
        dirpath = configs.get_cmd_dir_path()
        return [
            dirpath.joinpath('pip{}.exe'.format(name))
            for name in self.script_version_names
        ]

    @property
    def python_major_command(self):
        dirpath = configs.get_scripts_dir_path()
        return dirpath.joinpath('python{}.exe'.format(self.version_info[0]))

    def get_installation(self):
        path = metadata.get_install_path(self.name).resolve(strict=True)
        return installations.Installation(path=path)

    def is_installed(self):
        try:
            exists = metadata.get_install_path(self.name).exists()
        except FileNotFoundError:
            return False
        return exists

    def check_installer(self, data):
        checksum = hashlib.md5(data).hexdigest()
        assert checksum == self.md5_sum, \
            'expect checksum {}, got {}'.format(self.md5_sum, checksum)

    def get_target_for_install(self):
        return pathlib.Path(
            os.environ['LocalAppData'], 'Programs', 'Python',
            'Python{}'.format(self.name.replace('.', '')),
        )


class CPythonMSIVersion(Version):

    @classmethod
    def load(cls, name, data, *, force_32):
        variant = data['x86' if force_32 else 'amd64']
        return cls(
            name=name,
            version_info=data['version_info'],
            url=variant['url'],
            md5_sum=variant['md5_sum'],
            product_codes=variant.get('product_codes', {}),
        )

    def _run_installer(self, cmd, target_dirpath):
        features = ['DefaultFeature', 'PrivateCRT', 'TclTk', 'pip_feature']
        parts = [   # Argument ordering is very important.
            # Options and required parameters.
            'msiexec', '/i', '"{}"'.format(cmd),

            # Optional parameters and flags.
            '/qb', 'TARGETDIR="{}"'.format(target_dirpath),
            'ADDLOCAL={}'.format(','.join(features)),

            # This does not do what you think. DO NOT SUPPLY IT.
            # The installer is per-user by default.
            # 'ALLUSERS=0',
        ]
        subprocess.check_call(
            ' '.join(parts),
            shell=True,     # So we don't need to know where msiexec is.
        )

    def install(self, cmd):
        dirpath = self.get_target_for_install()
        self._run_installer(cmd, dirpath)
        return dirpath

    def upgrade(self, cmd):
        # There is no way to know what was installed from the previous MSI
        # installer; all we can do is installing what we want to the location
        # we want, and leave the old version installation untouched.
        self._run_installer(cmd, self.get_installation().path)

    def get_cached_uninstaller(self):
        info = self.get_installation().get_version_info()
        try:
            return self.product_codes['{0[0]}.{0[1]}.{0[2]}'.format(info)]
        except (IndexError, KeyError, TypeError):
            return metadata.find_uninstaller_id(self.name)

    def uninstall(self, cmd):
        subprocess.check_call('msiexec /x "{}" /qb'.format(cmd), shell=True)


class CPythonVersion(Version):

    @classmethod
    def load(cls, name, data, *, force_32):
        forced_32 = False
        if force_32 and not name.endswith('-32'):
            name = '{}-32'.format(name)
            data = load_version_data(name)
            forced_32 = True
        return cls(
            name=name,
            version_info=data['version_info'],
            url=data['url'],
            md5_sum=data['md5_sum'],
            forced_32=forced_32,
        )

    def install(self, cmd):
        dirpath = self.get_target_for_install()
        subprocess.check_call([
            cmd, '/passive', 'InstallAllUsers=0',
            'DefaultJustForMeTargetDir={}'.format(dirpath),
            'AssociateFiles=0', 'PrependPath=0', 'Shortcuts=0',
            'Include_doc=0', 'Include_launcher=0', 'Include_test=0',
            'Include_tools=0', 'InstallLauncherAllUsers=0',
        ])
        return dirpath

    def upgrade(self, cmd):
        # The installer handles all feature detection for us.
        subprocess.check_call([cmd, '/passive'])

    def get_cached_uninstaller(self):
        return metadata.get_bundle_cache_path(self.name)

    def uninstall(self, cmd):
        subprocess.check_call([cmd, '/uninstall', '/passive'])


def get_version(name, *, force_32):
    data = load_version_data(name)
    installer_type = InstallerType(data['type'])
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
