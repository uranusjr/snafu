import functools

import click

from snafu import metadata, versions


def check_installation(version, *, installed=True, on_exit=None):
    try:
        installation = version.get_installation()
    except FileNotFoundError:
        if not installed:   # Expected to be absent. Return None.
            return None
        message = '{} is not installed.'
    else:
        if installed:   # Expected to be installed. Return the installation.
            return installation
        message = '{} is already installed.'
    click.echo(message.format(version), err=True)
    if on_exit:
        on_exit()
    click.get_current_context().exit(1)


def get_active_names():
    try:
        return metadata.get_active_python_versions()
    except FileNotFoundError:
        return []


def get_version(name):
    force_32 = not metadata.can_install_64bit()
    try:
        version = versions.get_version(name, force_32=force_32)
    except versions.VersionNotFoundError:
        click.echo('No such version: {}'.format(name), err=True)
        click.get_current_context().exit(1)
    if version.name != name:
        click.echo('Note: Selecting {} instead of {}'.format(
            version.name, name,
        ))
    return version


def version_command(*, plural=False, wild_versions=()):
    if wild_versions:
        def _get_version(n):
            if n in wild_versions:
                return n
            return get_version(n)
    else:
        _get_version = get_version

    def decorator(f):

        @functools.wraps(f)
        def wrapped(*args, version, **kw):
            if plural:
                kw['versions'] = [_get_version(n) for n in version]
            else:
                kw['version'] = _get_version(version)
            return f(*args, **kw)

        return wrapped

    return decorator
