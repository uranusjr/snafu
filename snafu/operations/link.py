import filecmp
import itertools
import shutil

import click

from snafu import configs, metadata

from .common import (
    check_installation, get_active_names, get_version, version_command,
)


def publish_shim(name, target, *args, overwrite, quiet):
    if not overwrite and target.exists():
        return False
    if not quiet:
        click.echo('  {}'.format(target.name))
    shutil.copy2(str(configs.get_shim_path(name)), str(target))
    return True


def publish_file(source, target, *, overwrite, quiet):
    if not overwrite and target.exists():
        return False
    if not quiet:
        click.echo('  {}'.format(target.name))
    try:
        shutil.copy2(str(source), str(target))
    except OSError as e:
        click.echo('WARNING: Failed to copy {}.\n{}: {}'.format(
            source.name, type(e).__name__, e,
        ), err=True)
        return False
    return True


def publish_python_command(target, *, overwrite, quiet=False):
    publish_shim('python', target, overwrite=overwrite, quiet=quiet)


def publish_pip_command(target, *, overwrite, quiet=False):
    publish_shim('pip', target, overwrite=overwrite, quiet=quiet)


def safe_unlink(p):
    if p.exists():
        try:
            p.unlink()
        except OSError as e:
            click.echo('Failed to remove {} ({})'.format(p, e), err=True)


def collect_version_scripts(versions):
    names = set()
    scripts = []
    shims = []
    for version in versions:
        version_scripts_dir = version.get_installation().scripts_dir
        if not version_scripts_dir.is_dir():
            continue
        for path in version_scripts_dir.iterdir():
            blacklisted_stems = {
                # Encourage people to always use qualified commands.
                'easy_install', 'pip',
                # Fully qualified pip is already populated on installation.
                'pip{}'.format(version.arch_free_name),
            }
            shimmed_stems = {
                # Major version names, e.g. "pip3".
                'pip{}'.format(version.version_info[0]),
                # Fully-qualified easy_install.
                'easy_install-{}'.format(version.arch_free_name),
            }
            if path.name in names or path.stem in blacklisted_stems:
                continue
            names.add(path.name)
            if path.stem in shimmed_stems:
                shims.append(path.name)
            else:
                scripts.append(path)
    return scripts, shims


def activate(versions, *, allow_empty=False, quiet=False):
    if not allow_empty and not versions:
        click.echo('No active versions.', err=True)
        click.get_current_context().exit(1)

    source_scripts, shims = collect_version_scripts(versions)
    scripts_dir = configs.get_scripts_dir_path()

    using_scripts = set()

    if source_scripts or shims or versions:
        if not quiet:
            click.echo('Publishing scripts....')
        for source in source_scripts:
            target = scripts_dir.joinpath(source.name)
            if not source.is_file():
                continue
            using_scripts.add(target)
            if target.exists() and filecmp.cmp(str(source), str(target)):
                continue    # Identical files. skip.
            publish_file(source, target, overwrite=True, quiet=quiet)
        for shim in shims:
            target = scripts_dir.joinpath(shim)
            using_scripts.add(target)
            publish_pip_command(target, overwrite=False, quiet=quiet)
        for version in versions:
            command = version.python_major_command
            using_scripts.add(command)
            publish_python_command(command, overwrite=False, quiet=True)

    metadata.set_active_python_versions(version.name for version in versions)

    stale_scripts = set(scripts_dir.iterdir()) - using_scripts
    if stale_scripts:
        if not quiet:
            click.echo('Cleaning stale scripts...')
        for script in stale_scripts:
            if not quiet:
                click.echo('  {}'.format(script.name))
            safe_unlink(script)


def link_commands(version):
    for path in version.python_commands:
        click.echo('Publishing {}'.format(path.name))
        publish_python_command(path, overwrite=True, quiet=True)
    for path in version.pip_commands:
        click.echo('Publishing {}'.format(path.name))
        publish_pip_command(path, overwrite=True, quiet=True)


def unlink_commands(version):
    for p in itertools.chain(version.python_commands, version.pip_commands):
        click.echo('Unlinking {}'.format(p.name))
        safe_unlink(p)


def update_active_versions(*, remove=frozenset()):
    current_active_names = set(get_active_names())
    active_names = [n for n in current_active_names]
    for version in remove:
        try:
            active_names.remove(version.name)
        except ValueError:
            continue
        click.echo('Deactivating {}'.format(version))
    if len(current_active_names) != len(active_names):
        activate([get_version(n) for n in active_names], allow_empty=True)


@version_command(plural=True)
def use(ctx, versions, add):
    if add is None and not versions:
        # Bare "snafu use": Display active versions.
        names = get_active_names()
        if names:
            click.echo(' '.join(names))
        else:
            click.echo('Not using any versions.', err=True)
        return

    for version in versions:
        check_installation(version)

    active_versions = [
        get_version(name)
        for name in get_active_names()
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

    if versions:
        click.echo('Using: {}'.format(', '.join(v.name for v in versions)))
    else:
        click.echo('Not using any versions.')
    activate(versions, allow_empty=(not add))


def link(ctx, command, link_all, force):
    if not link_all and not command:    # This mistake is more common.
        click.echo(ctx.get_usage(), color=ctx.color)
        click.echo('\nError: Missing argument "command".', color=ctx.color)
        ctx.exit(1)
    if link_all and command:
        click.echo('--all cannot be used with a command.', err=True)
        ctx.exit(1)

    active_names = get_active_names()
    if not active_names:
        click.echo('Not using any versions.', err=True)
        click.echo('HINT: Use "snafu use" to use a version first.', err=True)
        ctx.exit(1)

    if link_all:
        activate([get_version(n) for n in active_names])
        return

    command_name = command  # Better variable names.
    command = None
    for version_name in active_names:
        version = get_version(version_name)
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
    ok = publish_file(command, target, overwrite=True, quiet=True)
    if ok:
        click.echo('Linked {} from {}'.format(target_name, version))
