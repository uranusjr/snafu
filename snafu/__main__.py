import pathlib
import sys

import click

from . import operations, versions


class SnafuGroup(click.Group):
    """Force command name to 'snafu'.
    """
    def make_context(self, info_name, *args, **kwargs):
        return super().make_context('snafu', *args, **kwargs)


@click.group(cls=SnafuGroup)
def cli():
    pass


@cli.command(help='Install a Python version.')
@click.argument('version')
@click.option('--file', 'from_file', type=click.Path(exists=True))
def install(version, from_file):
    version = operations.get_version(version)
    operations.check_status(version, False)

    if from_file is None:
        installer_path = operations.download_installer(version)
    else:
        installer_path = pathlib.Path(from_file)

    click.echo('Running installer {}'.format(installer_path))
    dirpath = version.install(str(installer_path))

    for launcher in version.launchers:
        click.echo('Publishing {}'.format(launcher.name))
        operations.publish_python(
            version, launcher, overwrite=True, quiet=True,
        )

    click.echo('{} is installed succesfully to {}'.format(
        version, dirpath,
    ))


@cli.command(help='Uninstall a Python version.')
@click.argument('version')
@click.option('--file', 'from_file', type=click.Path(exists=True))
def uninstall(version, from_file):
    version = operations.get_version(version)
    operations.check_status(version, True)

    try:
        uninstaller_path = version.get_cached_uninstaller()
    except FileNotFoundError:
        if from_file is None:
            uninstaller_path = operations.download_installer(version)
        else:
            uninstaller_path = pathlib.Path(from_file)

    click.echo('Running uninstaller {}'.format(uninstaller_path))
    version.uninstall(str(uninstaller_path))

    for launcher in version.launchers:
        click.echo('Unlinking {}'.format(launcher.name))
        launcher.unlink()

    click.echo('{} is uninstalled succesfully.'.format(version))


@cli.command(
    help='Link pythonX.Y command for a Python version.',
    short_help='Link pythonX.Y command.',
)
@click.argument('version')
def link(version):
    version = operations.get_version(version)
    operations.check_status(version, True)

    for launcher in version.launchers:
        operations.publish_python(
            version, launcher, overwrite=True, quiet=True,
        )
        click.echo('Published {}'.format(launcher.name))


@cli.command(
    help='Remove pythonX.Y command for a Python version.',
    short_help='Remove pythonX.Y command.',
)
@click.argument('version')
def unlink(version):
    version = operations.get_version(version)
    operations.check_status(version, True)

    for launcher in version.launchers:
        launcher.unlink()
        click.echo('Unpublished {}'.format(launcher.name))


@cli.command(
    help='Set pythonX commands to, and link scripts for Python versions.',
    short_help='Set versions as active.',
)
@click.argument('version', nargs=-1)
def activate(version):
    if not version:
        version = operations.get_active_names()
    versions = [operations.get_version(v) for v in version]
    for version in versions:
        operations.check_status(version, True)
    if not versions:
        click.echo('No active versions."', err=True)
        sys.exit(1)
    # TODO: Be smarter and calculate diff, instead of rebuilding every time.
    operations.deactivate()
    operations.activate(versions)


@cli.command(
    help='Remove pythonX and linked Python script commands.',
    short_help='Deactivate all versions.',
)
def deactivate():
    operations.deactivate()


@cli.command(
    help='Prints where the executable of Python version is.',
    short_help='Print python.exe location.',
)
@click.argument('version')
def where(version):
    version = operations.get_version(version)
    operations.check_status(version, True)
    click.echo(str(version.installation.joinpath('python.exe')))


@cli.command(name='list', help='List Python versions (installed or all).')
@click.option('--all', 'list_all', is_flag=True)
def list_(list_all):
    vers = versions.get_versions()
    active_names = set(operations.get_active_names())
    seen = False
    for v in vers:
        marker = ' '
        if not list_all and not v.is_installed():
            continue
        if v.name in active_names:
            marker = '*'
        elif v.is_installed():
            marker = 'o'
        # TODO: Show '+' if there is a newer version.
        click.echo('{} {}'.format(marker, v.name))
        seen = True
    if not list_all and not seen:
        click.echo(
            'No installed versions. Use --all to list all available versions '
            'for installation.',
            err=True,
        )


if __name__ == '__main__':
    cli()
