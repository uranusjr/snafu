import click

import contextlib
import ctypes
import ctypes.wintypes
import os
import pathlib
import winreg


def get_parsed_environ(key):
    value = os.environ[key]
    return value.split(';')


@contextlib.contextmanager
def open_environment_key(access=winreg.KEY_READ):
    key = winreg.OpenKey(
        winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER),
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
    paths = set(get_parsed_environ('PATH'))
    values, vtype = get_path_values()
    current_length = len(values)
    for value in get_snafu_path_values(instdir):
        if value not in paths:
            values.append(value)
    if current_length != len(values):
        set_path_values(values, vtype)
        return True
    return False


def add_lnk_ext():
    if 'LNK' in get_parsed_environ('PATHEXT'):
        return False
    with open_environment_key(winreg.KEY_READ | winreg.KEY_SET_VALUE) as key:
        try:
            value, vtype = winreg.QueryValueEx(key, 'PATHEXT')
            parts = [v for v in value.split(';') if v]
        except FileNotFoundError:
            vtype = winreg.REG_EXPAND_SZ
            parts = ['%PATHEXT%']
        parts.append('.LNK')
        value = ';'.join(parts)
        winreg.SetValueEx(key, 'PATHEXT', 0, vtype, value)
    print('SET PATHEXT={}'.format(value))
    return True


def get_snafu_path_values(instdir):
    return [
        str(instdir.joinpath('cmd')),
        str(instdir.joinpath('scripts')),
    ]


def install(instdir):
    changed = []
    changed.append(add_lnk_ext())
    changed.append(add_snafu_paths(instdir))
    return any(changed)


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
