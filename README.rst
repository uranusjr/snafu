=========================
SNAFU the Python Manager
=========================

.. image:: https://ci.appveyor.com/api/projects/status/jjix3jifn79maf8q?svg=true
    :target: https://ci.appveyor.com/project/uranusjr/snafu
    :alt: Build status

SNAFU is a Python installer manager for Windows. It fetches and installs Python
of a version you specify, and manages the Path environment variable for you.


Specification
==============

(This is an overview of what the end result should look like. Most things are
not implemented yet.)

Distribution
------------

Find installers in `Releases <https://github.com/uranusjr/snafu/releases>`__. Install, and restart your shell.

Installing Pythons
------------------

Install Python 3.6::

    snafu install 3.6

This should install the *latest patch version* of CPython 3.6. We don’t support
installing patch versions. This is because there is no good way to deal with
patch versions on Windows (the py launcher only supports major and minor
versioning), and you should always use the latest patch anyway.

After installing a version, `pythonX.Y` will be available as a command.

If you’re on a 64-bit OS, the 64-bit version is installed by default. To
install a 32-bit version on a 64-bit machine, use the `-32` suffix::

    snafu install 3.6-32

If you install both 32- and 64-bit Pythons, `pythonX.Y` will point to the
64-bit version, and `pythonX.Y-32` 32-bit.

(Note: Due to restrictions in the standard Python installer, versions up to
3.4 are available in *either* 64- or 32-bit, not both.)

On 32-bit hosts, only 32-bit Pythons are available. Not suffixes are needed.

Set Default Python Version
--------------------------

Set Python 3.5 as default::

    snafu activate 3.5

This does two things:

1. `python3` is mapped to Python 3.5.
2. Scripts in `Python35\\Scripts` are linked into PATH.

Special case: `python`, `pip` and `easy_install` are never linked, to avoid any
confusion. Use `python3`, `pip3`, `pip3.5`, etc. instead.

You can activate multiple versions together::

    snafu activate 2.7 3.5

In such case, the version at the front takes precedence if there are
conflicting commands, e.g. if both 2.7 and 3.5 has `virtualenv` installed,
the 2.7 version will be linked.

Uninstalling
------------

To uninstall a version::

    snafu uninstall 3.5

Listing Versions
----------------

List installed versions::

    snafu list

List all versions available, including those not installed::

    snafu list --all

This results in something like this::

    o 2.7
    o 3.4
      3.5
    * 3.6

* The ``o`` prefix means the version is installed.
* ``*`` signifies an active version.
* No prefix if the version is not installed.

The installation status is detected through the Windows registry.


Architecture (Implementation Details)
=====================================

How are Pythons installed?
--------------------------

The official CPython installers are downloaded, and executed in a
non-interactive manner. For more details check out the relevant documentation:

* https://www.python.org/download/releases/2.5/msi/
* https://docs.python.org/3/using/windows.html#installing-without-ui


Where are Pythons installed?
----------------------------

``%LOCALAPPDATA%\Programs\Python\<version>``. This is the standard
“only-for-me” installation location for Python 3.5+, and we retrofit this rule
to older versions as well for consistency.


How are Executables linked?
---------------------------

Script executables are *copied*. `.py` files works as well because they have
appropriate shebang lines, and can be handled by the py launcher, as specified
in `PEP 397 <https://www.python.org/dev/peps/pep-0397/>`_.

The python launchers (python.exe) cannot be copied as-is because they require
additional DLL files to work, so they are exposed with one-liner BATCH files
like this::

    @%LOCALAPPDATA%\Programs\Python\Python35\python.exe %*


Why the Name?
-------------

Because Python is hard, Windows is harder, and setting up Windows for Python
development is SNAFU. Or it’s Supernatrual Administration for You.
