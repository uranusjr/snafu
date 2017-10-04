import json
import pathlib
import shutil
import subprocess
import zipfile

import click
import pkg_resources
import requests


PYTHON_EMBED_URL = \
    'https://www.python.org/ftp/python/3.6.3/python-3.6.3-embed-amd64.zip'

PYTHON_INSTALLER_URL = \
    'https://www.python.org/ftp/python/3.6.3/python-3.6.3-amd64.exe'

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


def get_python_installer():
    installer_path = ROOT.joinpath(PYTHON_INSTALLER_URL.rsplit('/', 1)[-1])
    if not installer_path.exists():
        download_file(PYTHON_INSTALLER_URL, installer_path)
    return installer_path


def get_embed_bundle():
    bundle_path = ROOT.joinpath(PYTHON_EMBED_URL.rsplit('/', 1)[-1])
    if not bundle_path.exists():
        download_file(PYTHON_EMBED_URL, bundle_path)
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


def build_lib(container):
    libdir = container.joinpath('lib')
    libdir.mkdir()

    # Extract Python distribution.
    click.echo('Populating Embeddable Python.')
    with zipfile.ZipFile(str(get_embed_bundle())) as f:
        f.extractall(str(libdir))

    # Copy SNAFU.
    click.echo('Populate SNAFU.')
    shutil.copytree(
        str(ROOT.parent.joinpath('snafu')),
        str(libdir.joinpath('snafu')),
    )

    # Write SNAFU configurations.
    with libdir.joinpath('snafu', 'installation.json').open('w') as f:
        json.dump({'scripts_dir': '..\\..\\scripts'}, f)

    # Copy dependencies.
    click.echo('Populate dependencies...')
    for path in get_package_paths():
        click.echo('  {}'.format(path.stem))
        if path.is_dir():
            shutil.copytree(str(path), str(libdir.joinpath(path.name)))
        else:
            shutil.copy2(str(path), str(libdir.joinpath(path.name)))


def build_cmd(container):
    cmddir = container.joinpath('cmd')
    cmddir.mkdir()
    cmddir.joinpath('snafu.cmd').write_text('@{python} -m snafu %*'.format(
        python=container.joinpath('lib', 'python.exe'),
    ))


def build_python_setup(container):
    setup = get_python_installer()
    shutil.copy2(str(setup), str(container.joinpath('python-setup.exe')))


def build_files():
    container = ROOT.joinpath('snafu')
    if container.exists():
        shutil.rmtree(str(container))
    container.mkdir()
    build_lib(container)
    build_cmd(container)
    build_python_setup(container)


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
def build():
    build_files()
    build_installer()
    cleanup()


if __name__ == '__main__':
    build()
