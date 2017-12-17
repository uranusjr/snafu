import json
import pathlib


def get_value(key):
    with pathlib.Path(__file__).with_name('installation.json').open() as f:
        data = json.load(f)
    return data[key]


def get_directory(key):
    path = pathlib.Path(__file__).parent.joinpath(get_value(key))
    path.mkdir(parents=True, exist_ok=True)
    return path.resolve(strict=True)


def get_scripts_dir_path():
    return get_directory('scripts_dir')


def get_cmd_dir_path():
    return get_directory('cmd_dir')


def get_linkexe_script_path():
    return get_directory('utils_dir').joinpath('linkexe.vbs')


def get_shim_path(name):
    if not name.endswith('.exe'):
        name = '{}.exe'.format(name)
    return get_directory('shims_dir').joinpath(name)
