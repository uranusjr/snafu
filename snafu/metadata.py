import pathlib
import winreg


def get_python_key():
    return winreg.OpenKey(
        winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER),
        r'Software\Python\PythonCore',
    )


def get_installed_version_names():
    i = 0
    names = []
    python_key = get_python_key()
    while True:
        try:
            names.append(winreg.EnumKey(python_key, i))
        except OSError:
            break
        i += 1
    return names


def is_installed(name):
    try:
        key = winreg.OpenKey(get_python_key(), name)
    except FileNotFoundError:
        return False
    return True


def get_installation_root_path(name):
    try:
        key = winreg.OpenKey(get_python_key(), r'{}\InstallPath'.format(name))
    except FileNotFoundError:
        return None
    return pathlib.Path(winreg.QueryValue(key, ''))
