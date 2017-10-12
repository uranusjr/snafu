import click

import contextlib
import ctypes
import ctypes.wintypes
import pathlib
import winreg


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
            value, vtype = winreg.QueryValueEx(key, 'Path')
        except FileNotFoundError:
            return [], 1
    if not value:
        return [], 1
    return value.split(';'), vtype


def set_path_values(values, vtype):
    joined_value = ';'.join(values)
    with open_environment_key(winreg.KEY_SET_VALUE) as key:
        winreg.SetValueEx(key, 'Path', 0, vtype, joined_value)
    print('Set Path={}'.format(joined_value))


def get_snafu_path_values(instdir):
    return [
        str(instdir.joinpath('cmd')),
        str(instdir.joinpath('scripts')),
    ]


def install(instdir):
    values, vtype = get_path_values()
    current_values = list(values)
    for val in get_snafu_path_values(instdir):
        if val not in values:
            values.append(val)
    if current_values != values:
        set_path_values(values, vtype)
        return True
    return False


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
