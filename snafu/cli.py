import click

from .operations import download_installer
from .versions import get_version


@click.group()
def cli():
    pass


@cli.command()
@click.argument('version')
def install(version):
    version = get_version(version)
    # TODO: Early bail if the version is already installed.
    # (Use `upgrade` to install a newer patch version.)

    click.echo('Downloading {}'.format(version.url))
    installer_path = download_installer(version)

    click.echo('Running installer at {}'.format(installer_path))
    dirpath = version.install(str(installer_path))

    click.echo('Python {} is installed succesfully to {}'.format(
        version.name, dirpath,
    ))


@cli.command()
@click.argument('version')
def uninstall(version):
    version = get_version(version)
    # TODO: Early bail if the version is not installed.

    # TODO: Can we use the Windows built-in uninstalling mechanism instead?
    click.echo('Downloading {}'.format(version.url))
    installer_path = download_installer(version)

    click.echo('Running installer at {}'.format(installer_path))
    version.uninstall(str(installer_path))

    click.echo('Python {} is uninstalled succesfully.'.format(version.name))
