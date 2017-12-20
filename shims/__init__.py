import pathlib
import os

import invoke


TOP_LEVEL = [
    'shim',
    'snafu',
]


CURDIR = pathlib.Path(__file__, '..')


def _run_for_each(ctx, cmd):
    for p in TOP_LEVEL:
        # Can't use Path.resolve() because it can return a UNC path, which
        # ctx.cd() does not accept.
        with ctx.cd(os.path.abspath(CURDIR.joinpath(p))):
            ctx.run(cmd)


@invoke.task()
def build(ctx, release=False, verbose=False):
    build_params = [
        '--release' * release,
        '--verbose' * verbose,
    ]
    _run_for_each(ctx, 'cargo build {}'.format(' '.join(build_params)))


@invoke.task()
def clean(ctx):
    _run_for_each(ctx, 'cargo clean')


@invoke.task()
def test(ctx):
    _run_for_each(ctx, 'cargo test')
