import click

from . import configs, operations, versions


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
def install(version):
    version = operations.get_version(version)
    operations.check_status(version, False)

    installer_path = operations.download_installer(version)

    click.echo('Running installer {}'.format(installer_path))
    dirpath = version.install(str(installer_path))

    click.echo('Publishing {}'.format(version.launcher.name))
    operations.publish_python(
        version, version.launcher, overwrite=True, quiet=True,
    )

    click.echo('{} is installed succesfully to {}'.format(
        version, dirpath,
    ))


@cli.command()
@click.argument('version')
def uninstall(version):
    version = operations.get_version(version)
    operations.check_status(version, True)

    try:
        uninstaller_path = version.get_cached_uninstaller()
    except FileNotFoundError:
        uninstaller_path = operations.download_installer(version)

    click.echo('Running uninstaller {}'.format(uninstaller_path))
    version.uninstall(str(uninstaller_path))

    click.echo('Unlinking {}'.format(version.launcher.name))
    version.launcher.unlink()

    click.echo('{} is uninstalled succesfully.'.format(version))


@cli.command()
@click.argument('version')
def link(version):
    version = operations.get_version(version)
    operations.check_status(version, True)

    operations.publish_python(
        version, version.launcher, overwrite=True, quiet=True,
    )
    click.echo('Published {}'.format(version.launcher.name))


@cli.command()
@click.argument('version')
def unlink(version):
    version = operations.get_version(version)
    operations.check_status(version, True)

    version.launcher.unlink()
    click.echo('Unpublished {}'.format(version.launcher.name))


@cli.command()
@click.argument('version', nargs=-1, required=True)
def activate(version):
    versions = [operations.get_version(v) for v in version]
    for version in versions:
        operations.check_status(version, True)

    scripts_path = configs.get_scripts_dir_path()

    click.echo('Removing scripts.')
    for p in scripts_path.iterdir():
        p.unlink()

    for version in versions:
        operations.publish_scripts(version, scripts_path)


@cli.command()
def deactivate():
    click.echo('Removing scripts.')
    for p in configs.get_scripts_dir_path().iterdir():
        p.unlink()


@cli.command(name='list')
@click.option('--all', 'list_all', is_flag=True)
def list_(list_all):
    vers = versions.get_versions()
    for v in vers:
        marker = ' '
        if v.is_installed():
            marker = 'i'
        # TODO: Show upgrade marker if defined version is newer than installed.
        # TODO: Show * if the version is active.
        if not list_all and not v.is_installed():
            continue
        click.echo('{} {}'.format(marker, v.name))


if __name__ == '__main__':
    cli()
