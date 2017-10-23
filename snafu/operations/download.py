import pathlib

import click

from snafu import utils

from .common import version_command


def download_installer(version):
    click.echo('Downloading {}'.format(version.url))
    return utils.download_file(version.url, check=version.check_installer)


@version_command()
def download(ctx, version, dest_dir, force):
    installer = download_installer(version)
    target = pathlib.Path(dest_dir).joinpath(installer.name)
    if target.exists() and not force:
        click.echo('Target exists: {}'.format(target), err=True)
        click.echo('NOTE: Use --force to overwrite destination.', err=True)
        ctx.exit(1)
    installer.rename(target)
    click.echo('{} installer is downloaded successfully to {}'.format(
        version, target,
    ))
