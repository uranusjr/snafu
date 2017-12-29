import itertools
import json
import pathlib
import shutil
import struct
import subprocess
import zipfile

import invoke
import packaging.version
import pkg_resources
import requests

import shims


VERSION = '3.6.3'

DOWNLOAD_PREFIX = 'https://www.python.org/ftp/python'

KB_CODE = 'KB2999226'

WINVERS = [
    '6.0',      # Vista.
    '6.1',      # 7.
    '8-RT',     # 8.
    '8.1',      # 8.1.
]


def get_python_embed_url(architecture):
    return '{pref}/{vers}/python-{vers}-embed-{arch}.zip'.format(
        pref=DOWNLOAD_PREFIX,
        vers=VERSION,
        arch=architecture,
    )


def get_py_launcher_url(architecture):
    # I dug this URL out of Python's webinstaller build.
    # See this part in the build script for description.
    # https://github.com/python/cpython/blob/v3.6.3/Tools/msi/buildrelease.bat
    return '{pref}/{vers}/{arch}/launcher.msi'.format(
        pref=DOWNLOAD_PREFIX,
        vers=VERSION,
        arch=architecture,
    )


def get_kb_msu_url(architecture, wver, warc):
    return '{pref}/{vers}/{arch}/Windows{wver}-{code}-{warc}.msu'.format(
        pref=DOWNLOAD_PREFIX,
        vers=VERSION,
        arch=architecture,
        code=KB_CODE,
        wver=wver,
        warc=warc,
    )


def get_snafu_version():
    with ROOT.parent.joinpath('snafu', '__init__.py').open() as f:
        for line in f:
            if line.startswith('__version__'):
                vs = line[len('__version__ = '):]
                return packaging.version.parse(eval(vs))


def get_latest_python_name():

    def load_definition(p):
        with p.open() as f:
            data = json.load(f)
        data['name'] = p.stem
        return data

    definitions = [
        load_definition(p)
        for p in ROOT.parent.joinpath('snafu', 'versions').iterdir()
        if p.suffix == '.json'
    ]

    # 1. Prefer newer versions.
    # 2. Prefer shorter names because they look "more default".
    latest_definition = max(
        definitions,
        key=lambda d: (d['version_info'], -len(d['name'])),
    )
    return latest_definition['name']


ROOT = pathlib.Path(__file__).resolve(strict=True).parent

ASSETSDIR = ROOT.joinpath('assets')
ASSETSDIR.mkdir(exist_ok=True)

SHIMSDIR = ROOT.parent.joinpath('shims')


def download_file(url, path):
    print('Downloading {}'.format(url))
    response = requests.get(url, stream=True)
    response.raise_for_status()
    path.write_bytes(response.content)


def get_py_launcher(arch):
    installer_path = ASSETSDIR.joinpath('py-{vers}-{arch}.msi'.format(
        vers=VERSION,
        arch=arch,
    ))
    if not installer_path.exists():
        download_file(get_py_launcher_url(arch), installer_path)
    return installer_path


def get_embed_bundle(arch):
    url = get_python_embed_url(arch)
    bundle_path = ASSETSDIR.joinpath(url.rsplit('/', 1)[-1])
    if not bundle_path.exists():
        download_file(url, bundle_path)
    return bundle_path


def get_kb_msu(arch, winver, winarc):
    url = get_kb_msu_url(arch, winver, winarc)
    msu_path = ASSETSDIR.joinpath(url.rsplit('/', 1)[-1])
    if not msu_path.exists():
        download_file(url, msu_path)
    return msu_path


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
    # TODO: This only works for pure Python packages.
    # This will fail if we need binary dependencies (e.g. pypiwin32) in the
    # future because the host will only have either 32- or 64-bit binary, but
    # we need both to build installers for each architecture. We should instead
    # download wheels from PyPI, and extract to get the packages.
    paths = []
    for name in get_dependency_names():
        dist = pkg_resources.get_distribution(name)
        top_level = pathlib.Path(dist.egg_info).joinpath('top_level.txt')
        paths.extend(
            build_package_path(dist.location, n)
            for n in top_level.read_text().split('\n') if n
        )
    return paths


def build_lib_python(libdir, arch):
    pythondir = libdir.joinpath('python')
    pythondir.mkdir()

    # Extract Python distribution.
    print('Populating Embeddable Python.')
    with zipfile.ZipFile(str(get_embed_bundle(arch))) as f:
        f.extractall(str(pythondir))

    # Copy SNAFU.
    print('Populate SNAFU.')
    shutil.copytree(
        str(ROOT.parent.joinpath('snafu')),
        str(pythondir.joinpath('snafu')),
    )

    # Write SNAFU configurations.
    with pythondir.joinpath('snafu', 'installation.json').open('w') as f:
        json.dump({
            'cmd_dir': '..\\..\\..\\cmd',
            'scripts_dir': '..\\..\\..\\scripts',
            'shims_dir': '..\\..\\shims',
        }, f)

    # Copy dependencies.
    print('Populate dependencies...')
    for path in get_package_paths():
        print('  {}'.format(path.stem))
        if path.is_dir():
            shutil.copytree(str(path), str(pythondir.joinpath(path.name)))
        else:
            shutil.copy2(str(path), str(pythondir.joinpath(path.name)))

    # Cleanup.
    print('Remove junks...')
    for p in pythondir.rglob('__pycache__'):
        shutil.rmtree(str(p))
    for p in pythondir.rglob('*.py[co]'):
        shutil.rmtree(str(p))


SCRIPT_EXTS = ('.py', '.vbs')


def build_lib_setup(libdir, arch):
    setupdir = libdir.joinpath('setup')
    setupdir.mkdir()

    winarcs = {
        'amd64': ['x64'],
        'win32': ['x86', 'x64'],
    }[arch]

    # Copy necessary updates.
    for winver, winarc in itertools.product(WINVERS, winarcs):
        msu_path = get_kb_msu(arch, winver, winarc)
        print('Copy {}'.format(msu_path.name))
        shutil.copy2(
            str(msu_path),
            setupdir.joinpath(msu_path.name),
        )

    # Copy Py launcher MSI.
    print('Copy py.msi')
    msi = get_py_launcher(arch)
    shutil.copy2(str(msi), str(setupdir.joinpath('py.msi')))

    # Copy setup scripts.
    print('Copy setup scripts...')
    for path in ROOT.joinpath('lib', 'setup').iterdir():
        if path.suffix not in SCRIPT_EXTS:
            continue
        name = path.name
        print('  {}'.format(name))
        shutil.copy2(str(path), str(setupdir.joinpath(name)))


def build_lib_shims(libdir):
    shimsdir = libdir.joinpath('shims')
    shimsdir.mkdir()
    print('Copy shims...')
    for path in SHIMSDIR.joinpath('shim', 'target', 'release').iterdir():
        if path.suffix != '.exe':
            continue
        name = path.name
        print('  {}'.format(name))
        shutil.copy2(str(path), str(shimsdir.joinpath(name)))


def build_lib(container, arch):
    libdir = container.joinpath('lib')
    libdir.mkdir()
    build_lib_python(libdir, arch)
    build_lib_setup(libdir, arch)
    build_lib_shims(libdir)


def build_cmd(container):
    cmddir = container.joinpath('cmd')
    cmddir.mkdir()
    print('Copying snafu shim.')
    shutil.copy2(
        str(SHIMSDIR.joinpath('snafu', 'target', 'release', 'snafu.exe')),
        str(cmddir.joinpath('snafu.exe')),
    )


def build_files(arch):
    container = ROOT.joinpath('snafu')
    if container.exists():
        shutil.rmtree(str(container))
    container.mkdir()
    build_lib(container, arch)
    build_cmd(container)


def build_installer(outpath):
    if outpath.exists():
        outpath.unlink()
    print('Building installer.')
    subprocess.check_call([
        'makensis',
        '/DPYTHONVERSION={}'.format(get_latest_python_name()),
        str(ROOT.joinpath('snafu.nsi')),
    ], shell=True)
    print('snafu-setup.exe -> {}'.format(outpath))
    shutil.move(str(ROOT.joinpath('snafu-setup.exe')), str(outpath))


def cleanup():
    container = ROOT.joinpath('snafu')
    if container.exists():
        shutil.rmtree(str(container))


def check_version(v):
    version = packaging.version.parse(v)
    # Not really a version...Likely a Git hash.
    if not isinstance(version, packaging.version.Version):
        return
    mod_v = get_snafu_version()
    if mod_v != version:
        raise AssertionError(
            f'module version does not match installer: {mod_v} != {version}'
        )


@invoke.task(pre=[invoke.call(shims.build, release=True)])
def build(ctx, version=None, clean=True):
    arch = {
        8: 'amd64',
        4: 'win32',
    }[struct.calcsize('P')]

    if version is None:
        version = 'dev'
    else:
        check_version(version)

    out = 'snafu-setup-{}-{}.exe'.format(arch, version.strip())
    outpath = pathlib.Path(out)
    if not outpath.is_absolute():
        outpath = ROOT.joinpath(outpath)

    build_files(arch)
    build_installer(outpath)
    if clean:
        cleanup()


@invoke.task(pre=[invoke.call(shims.clean)])
def clean(ctx):
    cleanup()
