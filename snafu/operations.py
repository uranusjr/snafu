import ctypes
import itertools
import pathlib
import shutil
import subprocess
import time
import warnings

import click

from . import __version__
from . import configs, metadata, releases, termui, utils, versions


def download_installer(version):
    click.echo('Downloading {}'.format(version.url))
    return utils.download_file(version.url, check=version.check_installer)


def get_version(name):
    force_32 = not metadata.can_install_64bit()
    try:
        version = versions.get_version(name, force_32=force_32)
    except versions.VersionNotFoundError:
        click.echo('No such version: {}'.format(name), err=True)
        click.get_current_context().exit(1)
    if version.name != name:
        click.echo('Note: Selecting {} instead of {}'.format(
            version.name, name,
        ))
    return version


def check_installation(version, *, installed=True, on_exit=None):
    try:
        installation = version.get_installation()
    except FileNotFoundError:
        if not installed:   # Expected to be absent. Return None.
            return None
        message = '{} is not installed.'
    else:
        if installed:   # Expected to be installed. Return the installation.
            return installation
        message = '{} is already installed.'
    click.echo(message.format(version), err=True)
    if on_exit:
        on_exit()
    click.get_current_context().exit(1)


def publish_shortcut(target, command, *args, overwrite, quiet):
    if not overwrite and target.exists():
        return
    if not quiet:
        click.echo('  {}'.format(target.name))
    args = (
        'cscript', '//NOLOGO', str(configs.get_linkexe_script_path()),
        str(command), str(target),
    ) + args
    subprocess.check_call(args, shell=True)


def publish_file(source, target, *, overwrite, quiet):
    if not overwrite and target.exists():
        return
    if not quiet:
        click.echo('  {}'.format(target.name))
    shutil.copy2(str(source), str(target))


def publish_python_command(installation, target, *, overwrite, quiet=False):
    publish_shortcut(
        target, installation.python, overwrite=overwrite, quiet=quiet,
    )


def publish_pip_command(installation, target, *, overwrite, quiet=False):
    publish_file(installation.pip, target, overwrite=overwrite, quiet=quiet)


def publish_version_scripts(version, target_dir, *, quiet, overwrite=False):
    if not quiet:
        click.echo('Publishing {}...'.format(version))

    installation = version.get_installation()
    scripts_dir = installation.scripts_dir

    target = target_dir.joinpath('python{}.lnk'.format(version.major_version))
    publish_python_command(
        installation, target,
        quiet=quiet, overwrite=overwrite,
    )

    if scripts_dir.is_dir():
        blacklisted_stems = {
            # Always use commands like "pip3", never "pip".
            'easy_install', 'pip',
            # Fully qualified pip is already populated on installation.
            'pip{}'.format(version.arch_free_name),
        }
        for path in scripts_dir.iterdir():
            if path.stem in blacklisted_stems:
                continue
            if not path.is_file():
                continue
            target = target_dir.joinpath(path.name)
            publish_file(path, target, quiet=quiet, overwrite=overwrite)


def activate(versions, *, allow_empty=False, quiet=False):
    if not allow_empty and not versions:
        click.echo('No active versions.', err=True)
        click.get_current_context().exit(1)

    # TODO: Be smarter and calculate diff, not rebuilding every time.
    scripts_dir = configs.get_scripts_dir_path()

    # Remove old stuffs.
    if not quiet:
        click.echo('Removing scripts.')
    for p in scripts_dir.iterdir():
        p.unlink()

    # Populate new stuffs.
    for version in versions:
        publish_version_scripts(version, scripts_dir, quiet=quiet)
    configs.get_python_versions_path().write_text(
        '\n'.join(version.name for version in versions),
    )


def link_commands(version):
    installation = version.get_installation()
    for path in version.python_commands:
        click.echo('Publishing {}'.format(path.name))
        publish_python_command(installation, path, overwrite=True, quiet=True)
    for path in version.pip_commands:
        click.echo('Publishing {}'.format(path.name))
        publish_pip_command(installation, path, overwrite=True, quiet=True)


def safe_unlink(p):
    if p.exists():
        try:
            p.unlink()
        except OSError as e:
            click.echo('Failed to remove {} ({})'.format(p, e), err=True)


def unlink_commands(version):
    for p in itertools.chain(version.python_commands, version.pip_commands):
        click.echo('Unlinking {}'.format(p.name))
        safe_unlink(p)


def get_active_names():
    try:
        content = configs.get_python_versions_path().read_text()
    except FileNotFoundError:
        return ()
    return tuple(v for v in content.split() if v)


def get_versions(*, installed_only):
    vers = versions.get_versions()
    names = set(v.name for v in vers)

    def should_include(version):
        if installed_only and not version.is_installed():
            return False
        # On a 32-bit host, hide 64-bit names if there is a 32-bit counterpart.
        if (not metadata.can_install_64bit() and
                not version.name.endswith('-32') and
                '{}-32'.format(version.name) in names):
            return False
        return True

    return [v for v in vers if should_include(v)]


def update_active_versions(*, remove=frozenset()):
    current_active_names = set(get_active_names())
    active_names = [n for n in current_active_names]
    for version in remove:
        try:
            active_names.remove(version.name)
        except ValueError:
            continue
        click.echo('Deactivating {}'.format(version))
    if len(current_active_names) != len(active_names):
        activate([get_version(n) for n in active_names], allow_empty=True)


def install_self_upgrade(path):
    click.echo('Installing upgrade from {}'.format(path))
    click.echo('SNAFU will terminate now to let the installer run.')
    click.echo('Come back after the installation finishes. See ya later!')

    time.sleep(1)   # Let the user read the message.
    ctypes.windll.shell32.ShellExecuteW(None, 'open', str(path), '', None, 1)
    # SNAFU's installer requests elevation, so subprocess won't work, and we
    # need some Win32 API magic here. (Notice we use 'open', not 'runas'. The
    # installer requests elevation on its own; we don't do that for it.)
    # The process launched is in a detached state so SNAFU can end here,
    # releasing files to let the installer override.


def self_upgrade(*, installer, pre):
    if installer:
        if pre:
            click.echo('Ignoring --pre flag for pgrading self with --file')
        install_self_upgrade(pathlib.Path(installer))
        return

    with warnings.catch_warnings():
        warnings.showwarning = termui.warn
        release = releases.get_new_release(__version__, includes_pre=pre)
    if not release:
        click.echo('Current verion {} is up to date.'.format(__version__))
        return

    arch = 'win32' if metadata.is_python_32bit() else 'amd64'
    asset = release.get_asset(arch)
    if asset is None:
        click.echo('No suitable asset to download in {}'.format(release))
        return

    url = asset.browser_download_url
    path = utils.download_file(url, check=asset.check_download)
    install_self_upgrade(path)
