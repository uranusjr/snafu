import pytest

import snafu.versions


def test_get_version_cpython_msi():
    version = snafu.versions.get_version('3.4')
    assert version == snafu.versions.CPythonMSIVersion(
        name='3.4',
        url='https://www.python.org/ftp/python/3.4.3/python-3.4.3.amd64.msi',
        md5_sum='f6ade29acaf8fcdc0463e69a6e7ccf87',
        version_info=(3, 4, 3),
    )


def test_get_version_cpython():
    version = snafu.versions.get_version('3.5')
    assert version == snafu.versions.CPythonVersion(
        name='3.5',
        url='https://www.python.org/ftp/python/3.5.4/python-3.5.4-amd64.exe',
        md5_sum='4276742a4a75a8d07260f13fe956eec4',
        version_info=(3, 5, 4),
    )


def test_get_version_not_found():
    with pytest.raises(snafu.versions.VersionNotFoundError) as ctx:
        snafu.versions.get_version('2.8')
    assert str(ctx.value) == '2.8'
