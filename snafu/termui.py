import operator

import click


ETAD_LENGH = len('  0d 00:00:00')
PERC_LENGH = len('  100%')
MISC_LENGH = len('  [') + len(']')


def progressbar(*, length, label, width=36):
    kwargs = {
        'bar_template': '%(label)s  [%(bar)s]  %(info)s',
        'info_sep': '  ',
        'label': label,
        'length': length,
        'show_eta': True,
        'show_percent': True,
    }

    DISCARDABLE_PARTS = sorted([
        (len(label), {'label': ''}),
        (ETAD_LENGH, {'show_eta': False}),
        (PERC_LENGH, {'show_percent': False}),
    ], key=operator.itemgetter(0), reverse=True)

    # The extra 1 column is needed to hold the cursor.
    available = click.get_terminal_size()[0] - 1

    # Hide parts until the bar fits terminal.
    total = MISC_LENGH + len(label) + width + PERC_LENGH + ETAD_LENGH
    for length, update in DISCARDABLE_PARTS:
        if total < available:
            break
        kwargs.update(update)
        total -= length

    return click.progressbar(**kwargs)


def warn(message, category, filename, lineno, file=None, line=None):
    click.echo('WARNING: {}'.format(message), err=True)
