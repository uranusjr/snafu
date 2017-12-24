import os

import invoke


DOCSDIR = os.path.dirname(os.path.abspath(__file__))


@invoke.task()
def build(ctx, builder='html'):
    with ctx.cd(DOCSDIR):
        ctx.run('sphinx-build -b {} source build'.format(builder))


@invoke.task()
def clean(ctx):
    with ctx.cd(DOCSDIR):
        ctx.run('sphinx-build -M clean source build')


@invoke.task()
def watch(ctx, port='', open_browser=False):
    cmd = [
        'sphinx-autobuild',
        'source',
        'build',
        '--port={}'.format(port) * bool(port),
        '--watch={}'.format(os.path.dirname(DOCSDIR)),
        '--open-browser' * open_browser,
    ]
    with ctx.cd(DOCSDIR):
        ctx.run(' '.join(cmd))
