import functools
import pathlib

import click

from . import configs, operations
from . import __version__


class SnafuGroup(click.Group):
    """Force command name to 'snafu'.
    """
    def make_context(self, info_name, *args, **kwargs):
        return super().make_context('snafu', *args, **kwargs)


@click.group(cls=SnafuGroup, invoke_without_command=True)
@click.option('--version', is_flag=True, help='Print version and exit.')
@click.pass_context
def cli(ctx, version):
    if ctx.invoked_subcommand is None:
        if version:
            click.echo('SNAFU {}'.format(__version__))
        else:
            click.echo(ctx.get_help(), color=ctx.color)
            ctx.exit(1)


@cli.command(help='Install a Python version.')
@click.argument('version')
@click.option('--use', is_flag=True, help='Use version after installation.')
@click.option('--add', is_flag=True, help='Add scripts after installation.')
@click.option('--file', 'from_file', type=click.Path(exists=True))
def install(version, use, add, from_file):
    operations.check_installation(
        version, installed=False,
        on_exit=functools.partial(operations.link_commands, version),
    )

    if from_file is None:
        installer_path = operations.download_installer(version)
    else:
        installer_path = pathlib.Path(from_file)

    click.echo('Running installer {}'.format(installer_path))
    dirpath = version.install(str(installer_path))

    operations.link_commands(version)
    click.echo('{} is installed succesfully to {}'.format(
        version, dirpath,
    ))

    if not use and not add:
        return

    # Auto activation.
    versions = [version]
    if not add:
        versions = [
            operations.get_version(n)
            for n in operations.get_active_names()
        ] + versions
    operations.activate(versions, allow_empty=False)


@cli.command(help='Uninstall a Python version.')
@click.argument('version')
@click.option('--file', 'from_file', type=click.Path(exists=True))
def uninstall(version, from_file):
    version = operations.get_version(version)
    operations.check_installation(version, on_exit=functools.partial(
        operations.unlink_commands, version,
    ))
    operations.update_active_versions(remove=[version])

    if from_file is not None:
        uninstaller_path = pathlib.Path(from_file)
    else:
        try:
            uninstaller_path = version.get_cached_uninstaller()
        except FileNotFoundError:
            uninstaller_path = operations.download_installer(version)

    click.echo('Running uninstaller {}'.format(uninstaller_path))
    version.uninstall(str(uninstaller_path))
    operations.unlink_commands(version)
    click.echo('{} is uninstalled succesfully.'.format(version))


def is_prerelease():
    import packaging.version
    from . import __version__
    return packaging.version.parse(__version__).is_prerelease


@cli.command(help='Upgrade an installed Python version.')
@click.argument('version')
@click.option('--pre', is_flag=True, default=is_prerelease)
@click.option('--file', 'from_file', type=click.Path(exists=True))
@click.pass_context
def upgrade(ctx, version, pre, from_file):
    if version == 'self':
        operations.self_upgrade(installer=from_file, pre=pre)
        return

    if pre:
        click.echo('Installing prereleases is not supported yet.', err=True)
        ctx.exit(1)

    version = operations.get_version(version)
    installation_vi = operations.check_installation(
        version, on_exit=functools.partial(operations.link_commands, version),
    ).get_version_info()
    if installation_vi >= version.version_info:
        click.echo('Python {} is up to date.'.format(
            '.'.join(str(i) for i in installation_vi),
        ))
        return

    if from_file is None:
        installer_path = operations.download_installer(version)
    else:
        installer_path = pathlib.Path(from_file)

    click.echo('Running installer {}'.format(installer_path))
    version.upgrade(str(installer_path))

    operations.link_commands(version)
    click.echo('{} is upgraded succesfully at {}'.format(
        version, version.get_installation().path,
    ))


@cli.command(help='Set active Python versions.')
@click.argument('version', nargs=-1)
@click.option('--add', is_flag=True)
@click.option(
    '--yes', is_flag=True,
    help='Always answer "yes" when prompted for confirmation.',
)
@click.pass_context
def use(ctx, version, add, yes):
    if not add and not version:
        # Bare "snafu use": Display active versions.
        names = operations.get_active_names()
        if names:
            click.echo(' '.join(names))
        else:
            click.echo('Not using any versions.', err=True)
        return

    versions = [operations.get_version(n) for n in version]
    for version in versions:
        operations.check_installation(version)

    active_versions = [
        operations.get_version(name)
        for name in operations.get_active_names()
    ]
    if add:
        active_names = set(v.name for v in active_versions)
        new_versions = []
        for v in versions:
            if v.name in active_names:
                click.echo('Already using {}.'.format(v), err=True)
            else:
                new_versions.append(v)
        versions = active_versions + new_versions

    if active_versions == versions:
        click.echo('No version changes.', err=True)
        return
    if not yes:
        prompt = 'Confirm using {}'.format(', '.join(v.name for v in versions))
        click.confirm(prompt, abort=True, default=add)
    operations.activate(versions, allow_empty=(not add))


@cli.command(
    help='Prints where the executable of Python version is.',
    short_help='Print python.exe location.',
)
@click.argument('version')
def where(version):
    version = operations.get_version(version)
    installation = operations.check_installation(version)
    click.echo(str(installation.python))


@cli.command(name='list', help='List Python versions (installed or all).')
@click.option('--all', 'list_all', is_flag=True)
def list_(list_all):
    vers = operations.get_versions(installed_only=(not list_all))
    active_names = set(operations.get_active_names())

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


@cli.command(help='Link a command from active versions.')
@click.argument('command', required=False)
@click.option('--all', 'link_all', is_flag=True)
@click.option('--force', is_flag=True)
@click.pass_context
def link(ctx, command, link_all, force):
    if not link_all and not command:    # This mistake is more common.
        click.echo(ctx.get_usage(), color=ctx.color)
        click.echo('\nError: Missing argument "command".', color=ctx.color)
        ctx.exit(1)
    if link_all and command:
        click.echo('--all cannot be used with a command.', err=True)
        ctx.exit(1)

    active_names = operations.get_active_names()
    if link_all:
        operations.activate([operations.get_version(n) for n in active_names])
        return

    command_name = command  # Better variable names.
    command = None
    for version_name in active_names:
        version = operations.get_version(version_name)
        try:
            command = version.get_installation().find_script(command_name)
        except FileNotFoundError:
            continue
        break
    if command is None:
        click.echo('Command "{}" not found. Looked in {}: {}'.format(
            command_name,
            'version' if len(active_names) == 1 else 'versions',
            ', '.join(active_names),
        ), err=True)
        ctx.exit(1)

    target_name = command.name
    target = configs.get_scripts_dir_path().joinpath(target_name)
    if target.exists() and not force:
        if target.read_bytes() == command.read_bytes():
            # If the two files are identical, we're good anyway.
            return
        click.echo('{} exists. Use --force to overwrite.', err=True)
        ctx.exit(1)
    operations.publish_file(command, target, overwrite=True, quiet=True)
    click.echo('Linked {} from {}'.format(target_name, version))


if __name__ == '__main__':
    cli()
