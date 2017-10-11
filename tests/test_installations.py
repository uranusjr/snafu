import pathlib
import uuid

import pytest

import snafu.installations


@pytest.fixture
def installation_path(tmpdir):
    return pathlib.Path(str(tmpdir.mkdir(str(uuid.uuid4()))))


@pytest.fixture
def installation(installation_path):
    return snafu.installations.Installation(installation_path)


def test_scripts_dir(installation_path, installation):
    assert installation.scripts_dit == installation_path.join('Scripts')


def test_python(installation_path, installation):
    assert installation.python == installation_path.join('python.exe')


def test_pip(installation_path, installation):
    assert installation.python == installation_path.join('Scripts', 'pip.exe')
