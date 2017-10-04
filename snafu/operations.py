import atexit
import pathlib
import shutil
import sys
import tempfile

import click
import requests

from . import versions


def download_installer(version):
    response = requests.get(version.url, stream=True)

    installer_name = version.url.rsplit('/', 1)[-1]
    total = response.headers.get('content-length', '')
    chunks = []

    if total.isdigit():
        length = int(total)
    else:
        length = None
    with click.progressbar(length=length, label=installer_name) as b:
        for chunk in response.iter_content(chunk_size=4096):
            chunks.append(chunk)
            if length is not None:
                b.update(len(chunk))

    data = b''.join(chunks)

    # TODO: Maybe we should cache the installer to a consistent location
    # instead, so we don't need to download again when uninstalling?
    tempdir_path = pathlib.Path(tempfile.mkdtemp())
    atexit.register(shutil.rmtree, str(tempdir_path), ignore_errors=True)

    installer_path = tempdir_path.joinpath(installer_name)
    version.save_installer(data, installer_path)

    return installer_path


def get_version(name):
    # TODO: If the host is 32-bit and the user requests a 64-bit version,
    # automatically correct (and echo a message) it to the 32-bit variant.
    try:
        return versions.get_version(name)
    except versions.VersionNotFoundError:
        click.echo('No such version: {}'.format(name), err=True)
        sys.exit(1)


def check_status(version, expection):
    if version.is_installed() == expection:
        return
    if expection:
        message = '{} is not installed.'
    else:
        message = '{} is already installed.'
    click.echo(message.format(version), err=True)
    sys.exit(1)


def publish_python(version, target, *, overwrite, quiet=False):
    if not overwrite and target.exists():
        return
    if not quiet:
        click.echo('  {}'.format(target.name))
    target.write_text('@py -{} %*'.format(version.name))


def publish_script(source, target, *, overwrite):
    if not overwrite and target.exists():
        return
    click.echo('  {}'.format(target.name))
    shutil.copy2(str(source.resolve()), str(target))


def publish_scripts(version, target_dir, *, overwrite=False):
    click.echo('Publishing {}...'.format(version))

    target = target_dir.joinpath('python{}.cmd'.format(version.major_version))
    publish_python(version, target, overwrite=overwrite)

    install_dir_path = version.get_install_dir_path()
    for path in install_dir_path.joinpath('Scripts').iterdir():
        if path.stem in ('easy_install', 'pip'):
            # Special case: do not publish versionless pip and easy_install.
            continue
        target = target_dir.joinpath(path.name)
        publish_script(path, target, overwrite=overwrite)
