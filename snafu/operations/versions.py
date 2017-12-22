import click

from .common import (
    check_installation, get_active_names, get_versions, version_command,
)


@version_command()
def where(version):
    installation = check_installation(version)
    click.echo(str(installation.python))


def list_(list_all):
    vers = get_versions(installed_only=(not list_all))
    active_names = set(get_active_names())

    for v in vers:
        marker = ' '
        if v.name in active_names:
            marker = '*'
        elif v.is_installed():
            marker = 'o'
        # TODO: Show '+' for upgradable.
        # How should we show an upgradable *and* active version?
        click.echo('{} {}'.format(marker, v.name))

    if not list_all and not vers:
        click.echo(
            'No installed versions. Use --all to list all available versions '
            'for installation.',
            err=True,
        )
