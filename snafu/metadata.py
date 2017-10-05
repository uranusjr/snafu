import contextlib
import functools
import pathlib
import struct
import winreg


@contextlib.contextmanager
def open_python_key():
    key = winreg.OpenKey(
        winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER),
        r'Software\Python\PythonCore',
    )
    yield key
    winreg.CloseKey(key)


def get_installed_version_names():
    with open_python_key() as python_key:
        count, _, _ = winreg.QueryInfoKey(python_key)
        return [
            winreg.EnumKey(python_key, i)
            for i in range(count)
        ]


def get_install_path(name):
    with open_python_key() as python_key:
        key = winreg.OpenKey(python_key, r'{}\InstallPath'.format(name))
        install_path = winreg.QueryValue(key, '')
        winreg.CloseKey(key)
    return pathlib.Path(install_path).resolve()


@functools.lru_cache(maxsize=1)
def can_install_64bit():
    # Check the size of a C pointer to determine architecture.
    # https://github.com/kennethreitz-archive/its.py/blob/master/its.py
    return struct.calcsize('P') * 8 >= 64
