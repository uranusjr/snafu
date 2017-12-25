==============================================
SNAFU: Python Distribution Manager for Windows
==============================================

.. image:: https://ci.appveyor.com/api/projects/status/jjix3jifn79maf8q?svg=true&branch=master
    :target: https://ci.appveyor.com/project/uranusjr/snafu
    :alt: Build status

.. image:: https://readthedocs.org/projects/snafu/badge/?version=latest
    :target: https://snafu.readthedocs.io/en/latest/
    :alt: Documentation Status

SNAFU is a Python distribution manager for Windows. It helps you download,
configure, install, and manage Python installations [#]_, and provides
utilities that can be integrated into your Python-related development
workflows.

.. [#]: Only CPython distributions from `python.org`_ at the moment.

.. _`python.org`: https://python.org


Quick Start
===========

Find an installer in `Releases <https://github.com/uranusjr/snafu/releases>`_.
Download and install to get a ``snafu`` command in a newly-opened command
prompt.

Install Python 3.6::

    $ snafu install 3.6

Run Python::

    $ python3

Install Pipenv to Python 3.6::

    $ pip3.6 install pipenv

And use it immediately::

    $ pipenv --version
    pipenv, version 9.0.1

Install Python 3.5 (32-bit)::

    $ snafu install 3.5-32

Switch to a specific version::

    $ snafu use 3.5-32
    $ python3 --version
    Python 3.5.4

Switch back to 3.6::

    $ snafu use 3.6
    $ python3 --version
    Python 3.6.4
    $ python3.5 --version
    Python 3.5.4

Uninstall Python::

    $ snafu uninstall 3.5-32

Use ``--help`` to find more about SNAFU, or a specific command::

    $ snafu --help
    $ snafu install --help

Or read the `Documentation <https://snafu.readthedocs.io>`_.

Now you’re ready to use CPython on Windows like a first-class citizen, and
ignore people telling you to get a Mac.

🤔😉😆
