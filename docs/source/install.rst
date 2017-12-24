.. _install:

==============
Install Python
==============

SNAFU installs a Python versions with a simple command, so you don’t need to
go through the tedious *find, download, double-click, next, done* routine.

Install ``<version>`` on you machine: [#]_

::

    snafu install <version>

.. [#] Use ``snafu list --all`` to find out what versions are available. See
    :ref:`list` for more information about the ``list`` command.

This automatically downloads the installer, and guides you through the
installation with minimal interaction. [#]_ If there’s need to install without
Internet connection, you can download the installer yourself before hand, and
run::

    snafu install --file=path\to\installer.exe <version>

to install directly from that installer. Either way, SNAFU sets up the Python
installation on its own, and let you start using it right away.

.. [#] Generally only to confirm the UAC dialog, if needed.

SNAFU provides some extra executables for you. Say you have install Python 3.6
after you set up SNAFU. Now you can launch Python with::

    python3

Install a package, say, Pipenv_, with::

    pip3 install pipenv

.. _Pipenv: https://docs.pipenv.org

and have the ``pipenv`` command available immediately after.

Upgrade Python
==============

SNAFU allows you to upgrade a Python installation to a newer micro version,
e.g. 3.6.3 to 3.6.4. Run the following command to upgrade an installed version
(if available)::

    snafu upgrade <version>

It takes some time for the developers to update the definition to a newer
version. If you find a newer version released on `python.org`_ that is not
available in SNAFU, :ref:`send a pull request <develop>` to update the
definition files!

.. _`python.org`: https://python.org

Uninstall Python
================

You probably guessed it::

    snafu uninstall <version>

Similar to installing, this does nothing too fancy, but just runs the
standard uninstaller. It does perform some additional cleanup if you are using
the version. See :ref:manage about how you can manage/use versions.
