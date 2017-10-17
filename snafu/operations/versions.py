import click

from snafu import metadata, versions

from .common import check_installation, get_active_names, version_command


def get_versions(*, installed_only):
    vers = versions.get_versions()
    names = set(v.name for v in vers)

    def should_include(version):
        if installed_only and not version.is_installed():
            return False
        # On a 32-bit host, hide 64-bit names if there is a 32-bit counterpart.
        if (not metadata.can_install_64bit() and
                not version.name.endswith('-32') and
                '{}-32'.format(version.name) in names):
            return False
        return True

    return [v for v in vers if should_include(v)]


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
