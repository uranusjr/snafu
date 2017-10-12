import contextlib

import click

from snafu import operations


@click.command()
def main():
    for version in operations.get_versions(installed_only=True):
        with contextlib.suppress(FileNotFoundError):
            operations.link_commands(version)


if __name__ == '__main__':
    main()
