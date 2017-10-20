import functools
import pathlib

import click

from .common import (
    check_installation, download_installer,
    get_active_names, get_version, version_command,
)
from .link import (
    activate, link_commands, unlink_commands, update_active_versions,
)
from .releases import self_upgrade


@version_command()
def install(version, use, add, from_file):
    check_installation(
        version, installed=False,
        on_exit=functools.partial(link_commands, version),
    )

    if from_file is None:
        installer_path = download_installer(version)
    else:
        installer_path = pathlib.Path(from_file)

    click.echo('Running installer {}'.format(installer_path))
    dirpath = version.install(str(installer_path))

    link_commands(version)
    click.echo('{} is installed succesfully to {}'.format(
        version, dirpath,
    ))

    if not use and not add:
        return

    # Auto activation.
    versions = [version]
    if not add:
        versions = [
            get_version(n)
            for n in get_active_names()
        ] + versions
    activate(versions, allow_empty=False)


@version_command()
def uninstall(version, from_file):
    check_installation(version, on_exit=functools.partial(
        unlink_commands, version,
    ))
    update_active_versions(remove=[version])

    if from_file is not None:
        uninstaller_path = pathlib.Path(from_file)
    else:
        try:
            uninstaller_path = version.get_cached_uninstaller()
        except FileNotFoundError:
            uninstaller_path = download_installer(version)

    click.echo('Running uninstaller {}'.format(uninstaller_path))
    version.uninstall(str(uninstaller_path))
    unlink_commands(version)
    click.echo('{} is uninstalled succesfully.'.format(version))


@version_command(wild_versions=['self'])
def upgrade(ctx, version, pre, from_file):
    if version == 'self':
        self_upgrade(installer=from_file, pre=pre)
        return

    if pre:
        click.echo('Installing prereleases is not supported yet.', err=True)
        ctx.exit(1)

    installation_vi = check_installation(
        version, on_exit=functools.partial(link_commands, version),
    ).get_version_info()
    if installation_vi >= version.version_info:
        click.echo('Python {} is up to date.'.format(
            '.'.join(str(i) for i in installation_vi),
        ))
        return

    if from_file is None:
        installer_path = download_installer(version)
    else:
        installer_path = pathlib.Path(from_file)

    click.echo('Running installer {}'.format(installer_path))
    version.upgrade(str(installer_path))

    link_commands(version)
    click.echo('{} is upgraded succesfully at {}'.format(
        version, version.get_installation().path,
    ))
