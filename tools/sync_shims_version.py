import pathlib

import toml


ROOT = pathlib.Path(__file__).parent.parent


def get_snafu_version():
    with ROOT.joinpath('snafu', '__init__.py').open() as f:
        for line in f:
            if line.startswith('__version__'):
                return eval(line[len('__version__ = '):])


def main():
    cargo = ROOT.joinpath('shims', 'Cargo.toml')
    with cargo.open() as f:
        data = toml.load(f)
    version = get_snafu_version()
    print('Setting version to {!r}'.format(version))
    data['package']['version'] = version
    with cargo.open('w') as f:
        toml.dump(data, f)


if __name__ == '__main__':
    main()
