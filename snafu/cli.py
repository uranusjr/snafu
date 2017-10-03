import click

from . import operations


@click.group()
def cli():
    pass


@cli.command()
@click.argument('version')
def install(version):
    version = operations.get_version(version)
    operations.check_status(version, False)

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
    version = operations.get_version(version)
    operations.check_status(version, True)

    # TODO: Can we use the Windows built-in uninstalling mechanism instead?
    click.echo('Downloading {}'.format(version.url))
    installer_path = operations.download_installer(version)

    click.echo('Running installer at {}'.format(installer_path))
    version.uninstall(str(installer_path))

    click.echo('{} is uninstalled succesfully.'.format(version))
