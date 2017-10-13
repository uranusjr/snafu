import contextlib
import pathlib
import struct
import sys
import winreg


@contextlib.contextmanager
def open_python_key():
    key = winreg.OpenKey(
        winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER),
        'Software\\Python\\PythonCore',
    )
    yield key
    winreg.CloseKey(key)


def get_install_path(name):
    with open_python_key() as python_key:
        key = winreg.OpenKey(python_key, '{}\\InstallPath'.format(name))
        install_path = winreg.QueryValue(key, None)
        winreg.CloseKey(key)
    return pathlib.Path(install_path).resolve()


def find_uninstaller_id(name):
    # Look for EVERY entry in the uninstaller list to find one that looks like
    # the matching version's uninstaller. This is crazy, but the best way I
    # can think of right now. And it's still faster than downloading the MSI.
    key = winreg.OpenKey(
        winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE),
        'Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall',
    )

    match = None
    subkey_count, _, _ = winreg.QueryInfoKey(key)
    for i in range(subkey_count):
        sub_name = winreg.EnumKey(key, i)
        subkey = winreg.OpenKey(key, sub_name)
        try:
            display_name, _ = winreg.QueryValueEx(subkey, 'DisplayName')
            publisher, _ = winreg.QueryValueEx(subkey, 'Publisher')
        except FileNotFoundError:
            continue
        finally:
            winreg.CloseKey(subkey)
        if (display_name.startswith('Python {}.'.format(name)) and
                publisher == 'Python Software Foundation'):
            match = sub_name
            break

    winreg.CloseKey(key)

    if not match:
        raise FileNotFoundError
    return match


def get_bundle_cache_path(name):
    key = winreg.OpenKey(
        winreg.ConnectRegistry(None, winreg.HKEY_CLASSES_ROOT),
        'Installer\\Dependencies\\CPython-{}'.format(name),
    )
    guid = winreg.QueryValue(key, '')
    winreg.CloseKey(key)

    for reg in (winreg.HKEY_CURRENT_USER, winreg.HKEY_LOCAL_MACHINE):
        registry = winreg.ConnectRegistry(None, reg)
        key_parts = [
            'Software', 'Microsoft', 'Windows',
            'CurrentVersion', 'Uninstall', guid,
        ]
        try:
            key = winreg.OpenKey(registry, '\\'.join(key_parts))
            value, _ = winreg.QueryValueEx(key, 'BundleCachePath')
            path = pathlib.Path(value).resolve()
        except FileNotFoundError:
            continue
        else:
            return path
        finally:
            winreg.CloseKey(key)
    raise FileNotFoundError


def can_install_64bit():
    # Check the size of a C pointer to determine architecture.
    # https://github.com/kennethreitz-archive/its.py/blob/master/its.py
    return struct.calcsize('P') * 8 >= 64


def is_python_32bit():
    # Check int size for Python bitness.
    # Be aware this is different from `can_install_64bit()`, which checks
    # whether the HOST is 64-bit. If you install a 32-bit Python on a 64-bit
    # host, this function identifies it as 32-bit, but `can_install_64bit()`
    # would still return True.
    return sys.maxsize <= 2 ** 32
