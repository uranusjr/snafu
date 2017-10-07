import pathlib

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


@cli.command()
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


@cli.command()
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


@cli.command()
@click.argument('version')
def link(version):
    version = operations.get_version(version)
    operations.check_status(version, True)

    for launcher in version.launchers:
        operations.publish_python(
            version, launcher, overwrite=True, quiet=True,
        )
        click.echo('Published {}'.format(launcher.name))


@cli.command()
@click.argument('version')
def unlink(version):
    version = operations.get_version(version)
    operations.check_status(version, True)

    for launcher in version.launchers:
        launcher.unlink()
        click.echo('Unpublished {}'.format(launcher.name))


@cli.command()
@click.argument('version', nargs=-1)
def activate(version):
    if not version:
        version = operations.get_active_names()
    versions = [operations.get_version(v) for v in version]
    for version in versions:
        operations.check_status(version, True)
    # TODO: Be smarter and calculate diff, instead of rebuilding every time.
    operations.deactivate()
    operations.activate(versions)


@cli.command()
def deactivate():
    operations.deactivate()


@cli.command(name='list')
@click.option('--all', 'list_all', is_flag=True)
def list_(list_all):
    vers = versions.get_versions()
    active_names = set(operations.get_active_names())
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


if __name__ == '__main__':
    cli()
