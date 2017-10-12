import pathlib
import uuid

import pytest

import snafu.installations


@pytest.fixture
def instpath(tmpdir):
    return pathlib.Path(str(tmpdir.mkdir(str(uuid.uuid4()))))


@pytest.fixture
def installation(instpath):
    return snafu.installations.Installation(instpath)


def test_scripts_dir(instpath, installation):
    assert installation.scripts_dir == instpath.joinpath('Scripts')


def test_python(instpath, installation):
    assert installation.python == instpath.joinpath('python.exe')


def test_pip(instpath, installation):
    assert installation.pip == instpath.joinpath('Scripts', 'pip.exe')
