import atexit
import pathlib
import shutil
import sys
import tempfile

import click
import requests

from . import metadata, versions


def download_installer(version):
    click.echo('Downloading {}'.format(version.url))
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
    force_32 = not metadata.can_install_64bit()
    try:
        version = versions.get_version(name, force_32=force_32)
    except versions.VersionNotFoundError:
        click.echo('No such version: {}'.format(name), err=True)
        sys.exit(1)
    if version.name != name:
        click.echo('Note: Selecting {} instead of {}'.format(
            version.name, name,
        ))
    return version


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

    try:
        scripts_dir = version.get_scripts_dir_path()
    except FileNotFoundError:
        pass
    else:
        for path in scripts_dir.iterdir():
            if path.stem in ('easy_install', 'pip'):
                # Don't publish versionless pip and easy_install.
                continue
            target = target_dir.joinpath(path.name)
            publish_script(path, target, overwrite=overwrite)
