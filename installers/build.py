import json
import pathlib
import shutil
import subprocess
import zipfile

import click
import pkg_resources
import requests


VERSION = '3.6.3'

DOWNLOAD_PREFIX = 'https://www.python.org/ftp/python'


def get_python_embed_url(architecture):
    return '{pre}/{vers}/python-{vers}-embed-{arch}.zip'.format(
        pref=DOWNLOAD_PREFIX,
        vers=VERSION,
        arch=architecture,
    )


def get_py_launcher_url(architecture):
    # I dug this URL out of Python's webinstaller build.
    # See this part in the build script for description.
    # https://github.com/python/cpython/blob/v3.6.3/Tools/msi/buildrelease.bat
    return '{pre}/{vers}/python/{vers}/{arch}/launcher.msi'.format(
        pref=DOWNLOAD_PREFIX,
        vers=VERSION,
        arch=architecture,
    )


ROOT = pathlib.Path(__file__).parent.resolve()


def download_file(url, path):
    click.echo('Downloading {}'.format(url))
    response = requests.get(url, stream=True)

    installer_name = url.rsplit('/', 1)[-1]
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

    path.write_bytes(b''.join(chunks))


def get_py_launcher(arch):
    installer_path = ROOT.joinpath('py-{vers}-{arch}.msi'.format(
        vers=VERSION,
        arch=arch,
    ))
    if not installer_path.exists():
        download_file(get_py_launcher_url(arch), installer_path)
    return installer_path


def get_embed_bundle(arch):
    url = get_python_embed_url(arch)
    bundle_path = ROOT.joinpath(url.rsplit('/', 1)[-1])
    if not bundle_path.exists():
        download_file(url, bundle_path)
    return bundle_path


def get_dependency_names():
    lock_path = ROOT.parent.joinpath('Pipfile.lock')
    with lock_path.open() as f:
        data = json.load(f)
    return data['default'].keys()


class PackageResolutionError(ValueError):
    pass


def build_package_path(location, name):
    path = pathlib.Path(location, name)
    if path.is_dir():
        return path
    path = pathlib.Path(location, '{}.py'.format(name))
    if path.is_file():
        return path
    raise PackageResolutionError(name)


def get_package_paths():
    paths = []
    for name in get_dependency_names():
        dist = pkg_resources.get_distribution(name)
        top_level = pathlib.Path(dist.egg_info).joinpath('top_level.txt')
        paths.extend(
            build_package_path(dist.location, n)
            for n in top_level.read_text().split('\n') if n
        )
    return paths


def build_python(arch, container):
    pythondir = container.joinpath('lib', 'python')
    pythondir.mkdir()

    # Extract Python distribution.
    click.echo('Populating Embeddable Python.')
    with zipfile.ZipFile(str(get_embed_bundle(arch))) as f:
        f.extractall(str(pythondir))

    # Copy SNAFU.
    click.echo('Populate SNAFU.')
    shutil.copytree(
        str(ROOT.parent.joinpath('snafu')),
        str(pythondir.joinpath('snafu')),
    )

    # Write SNAFU configurations.
    with pythondir.joinpath('snafu', 'installation.json').open('w') as f:
        json.dump({
            'cmd_dir': '..\\..\\cmd',
            'scripts_dir': '..\\..\\scripts',
        }, f)

    # Copy dependencies.
    click.echo('Populate dependencies...')
    for path in get_package_paths():
        click.echo('  {}'.format(path.stem))
        if path.is_dir():
            shutil.copytree(str(path), str(pythondir.joinpath(path.name)))
        else:
            shutil.copy2(str(path), str(pythondir.joinpath(path.name)))


def build_snafusetup(arch, container):
    snafusetupdir = container.joinpath('lib', 'snafusetup')

    # Copy Py launcher MSI.
    click.echo('Copy py.msi')
    msi = get_py_launcher(arch)
    shutil.copy2(str(msi), str(snafusetupdir.joinpath('py.msi')))

    # Copy environment setup script.
    click.echo('Copy env.py')
    shutil.copy2(
        str(ROOT.joinpath('env.py')),
        str(snafusetupdir.joinpath('env.py')),
    )


def build_lib(arch, container):
    build_python(arch, container)
    build_snafusetup(arch, container)


def build_files(arch):
    container = ROOT.joinpath('snafu')
    if container.exists():
        shutil.rmtree(str(container))
    build_lib(arch, container)


def build_installer():
    exe = ROOT.joinpath('snafu-setup.exe')
    if exe.exists():
        exe.unlink()
    click.echo('Building installer.')
    subprocess.check_call(
        'makensis "{nsi}"'.format(nsi=ROOT.joinpath('snafu.nsi')),
        shell=True,
    )


def cleanup():
    container = ROOT.joinpath('snafu')
    shutil.rmtree(str(container))


@click.command()
@click.argument('arch', type=click.Choices(['win32', 'amd64']))
def build(arch):
    build_files(arch)
    build_installer()
    cleanup()


if __name__ == '__main__':
    build()
