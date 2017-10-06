import contextlib
import pathlib
import sys
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
    with open_environment_key(winreg.KEY_SET_VALUE) as key:
        winreg.SetValueEx(key, 'Path', 0, vtype, ';'.join(values))


def get_snafu_path_values(instdir):
    return [
        str(instdir.joinpath('cmd')),
        str(instdir.joinpath('scripts')),
    ]


def install(instdir):
    values, vtype = get_path_values()
    for val in get_snafu_path_values(instdir):
        if val not in values:
            values.append(val)
    set_path_values(values, vtype)


def uninstall(instdir):
    values, vtype = get_path_values()
    values = [v for v in values if v not in get_snafu_path_values(instdir)]
    set_path_values(values, vtype)


if __name__ == '__main__':
    if len(sys.argv) > 2 and '--uninstall' in sys.argv[2:]:
        uninstall(pathlib.Path(sys.argv[1]))
    else:
        install(pathlib.Path(sys.argv[1]))