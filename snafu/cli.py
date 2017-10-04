import click

from . import configs, operations


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
