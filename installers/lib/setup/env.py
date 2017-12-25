import collections
import contextlib
import ctypes
import ctypes.wintypes
import itertools
import pathlib
import winreg

import click


@contextlib.contextmanager
def open_environment_key(access=winreg.KEY_READ):
    key = winreg.OpenKey(
        winreg.HKEY_CURRENT_USER,
        'Environment',
        access=access,
    )
    yield key
    winreg.CloseKey(key)


def get_path_values():
    with open_environment_key() as key:
        try:
            value, vtype = winreg.QueryValueEx(key, 'PATH')
        except FileNotFoundError:
            return [], winreg.REG_SZ
    if not value:
        return [], winreg.REG_SZ
    return [v for v in value.split(';') if v], vtype


def set_path_values(values, vtype):
    joined_value = ';'.join(values)
    with open_environment_key(winreg.KEY_SET_VALUE) as key:
        winreg.SetValueEx(key, 'PATH', 0, vtype, joined_value)
    print('SET PATH={}'.format(joined_value))


def add_snafu_paths(instdir):
    old_paths, vtype = get_path_values()
    snafu_paths = get_snafu_path_values(instdir)

    path_index_m = collections.OrderedDict(zip(old_paths, itertools.count()))

    # If the order in PATH does not match what we want, delete existing
    # values and add again.
    current_indexes = [path_index_m.get(p, -1) for p in snafu_paths]
    if current_indexes != sorted(current_indexes):
        for p in snafu_paths:
            del path_index_m[p]

    for value in snafu_paths:
        path_index_m[value] = None  # Value irrelevant, we want only the key.

    new_paths = list(path_index_m.keys())
    if old_paths != new_paths:
        set_path_values(new_paths, vtype)
        return True
    return False


def get_snafu_path_values(instdir):
    return [
        str(instdir.joinpath('scripts')),
        str(instdir.joinpath('cmd')),
    ]


def install(instdir):
    return any([
        add_snafu_paths(instdir),
    ])


def uninstall(instdir):
    current_values, vtype = get_path_values()
    values = [
        v for v in current_values
        if v not in get_snafu_path_values(instdir)
    ]
    if current_values != values:
        set_path_values(values, vtype)
        return True
    return False


SendMessage = ctypes.windll.user32.SendMessageW
SendMessage.argtypes = (
    ctypes.wintypes.HWND, ctypes.wintypes.UINT,
    ctypes.wintypes.WPARAM, ctypes.wintypes.LPVOID,
)
SendMessage.restype = ctypes.wintypes.LPARAM    # Synonymous to LRESULT.
HWND_BROADCAST = 0xFFFF
WM_SETTINGCHANGE = 0x1A


def publish():
    SendMessage(HWND_BROADCAST, WM_SETTINGCHANGE, 0, 'Environment')


@click.command()
@click.argument('base', type=click.Path(exists=True, file_okay=False))
@click.option('--uninstall', 'uninstalling', is_flag=True)
def cli(base, uninstalling):
    path = pathlib.Path(base)
    if uninstalling:
        changed = uninstall(path)
    else:
        changed = install(path)
    if changed:
        publish()


if __name__ == '__main__':
    cli()
