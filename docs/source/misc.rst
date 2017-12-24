.. _misc:

======================
Miscellaneous Commands
======================

Upgrade SNAFU Itself
====================

A special ``upgrade`` syntax to upgrade not a Python version, but SNAFU
itself::

    snafu upgrade self

This simply downloads the official installer and runs it.


.. _list:

List Pythons
============

This lists Python versions installed in your system::

    snafu list

To list *all* Python versions available, including uninstalled ones, use::

    snafu list --all

Either way, the output would be something like this::

    o 2.7
    o 3.4
      3.5
    * 3.6

* The ``o`` prefix means the version is installed.
* ``*`` signifies an active version.
* No prefix if the version is not installed.


Download Python
===============

::

    snafu download <version>

downloads the installer without exicuting it. The installer is saved to the
current working directory by default, but you can also specify another
directory with the ``--dest`` option.


Find where the Python installation really is
============================================

::

    snafu where <version>

prints where the installed ``python.exe`` really is, usually something
like::

    C:\Users\username\AppData\Local\Programs\Python\PythonXY\python.exe

This is useful when you need to pass the real executable somewhere else, e.g.
set the path to an environment variable in a Powershell script.


Link individual scripts
=======================

::

    snafu link <command>

links the specified command to your ``PATH``. Nice to have when you accidetally
break the system. There are ``--overwrite=yes`` and ``--all`` you can use for
even better profit.
