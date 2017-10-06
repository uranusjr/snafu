import json
import pathlib


def get_value(key):
    with pathlib.Path(__file__).with_name('installation.json').open() as f:
        data = json.load(f)
    return data[key]


def get_scripts_dir_path():
    value = get_value('scripts_dir')
    path = pathlib.Path(__file__).parent.joinpath(value)
    path.mkdir(parents=True, exist_ok=True)
    return path.resolve()


def get_cmd_dir_path():
    value = get_value('cmd_dir')
    path = pathlib.Path(__file__).parent.joinpath(value)
    path.mkdir(parents=True, exist_ok=True)
    return path.resolve()
