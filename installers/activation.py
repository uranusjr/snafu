import contextlib

import click

from snafu import operations, versions


def get_version_or_none(name):
    with contextlib.supress(versions.VersionNotFoundError):
        return versions.get_version(name)
    return None


@click.command()
def main():
    versions = [
        get_version_or_none(name)
        for name in operations.get_active_names()
    ]
    for version in versions:
        if version is None:
            continue
        operations.publish_version_scripts(version)


if __name__ == '__main__':
    main()
