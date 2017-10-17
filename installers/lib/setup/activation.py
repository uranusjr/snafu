import contextlib

import click

from snafu import metadata, versions
from snafu.operations.common import get_active_names
from snafu.operations.link import activate


def get_version_or_none(name):
    force_32 = not metadata.can_install_64bit()
    with contextlib.suppress(versions.VersionNotFoundError):
        return versions.get_version(name, force_32=force_32)
    return None


@click.command()
def main():
    versions = [
        v for v in (
            get_version_or_none(name)
            for name in get_active_names()
        ) if v is not None
    ]
    activate(versions, allow_empty=True)


if __name__ == '__main__':
    main()
