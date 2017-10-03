import click

from . import metadata, operations, versions


@click.group()
def cli():
    pass


@cli.command()
@click.argument('version')
def install(version):
    version = versions.get_version(version)
    if version.is_installed():
        click.echo('{} is already installed!'.format(version), err=True)
        return

    click.echo('Downloading {}'.format(version.url))
    installer_path = operations.download_installer(version)

    click.echo('Running installer at {}'.format(installer_path))
    dirpath = version.install(str(installer_path))

    click.echo('{} is installed succesfully to {}'.format(
        version, dirpath,
    ))


@cli.command()
@click.argument('version')
def uninstall(version):
    version = versions.get_version(version)
    if not version.is_installed():
        click.echo('{} is not installed.'.format(version), err=True)
        return

    # TODO: Can we use the Windows built-in uninstalling mechanism instead?
    click.echo('Downloading {}'.format(version.url))
    installer_path = operations.download_installer(version)

    click.echo('Running installer at {}'.format(installer_path))
    version.uninstall(str(installer_path))

    click.echo('{} is uninstalled succesfully.'.format(version))
