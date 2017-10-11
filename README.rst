=========================
SNAFU the Python Manager
=========================

.. image:: https://ci.appveyor.com/api/projects/status/jjix3jifn79maf8q?svg=true
    :target: https://ci.appveyor.com/project/uranusjr/snafu
    :alt: Build status

SNAFU is a Python installer manager for Windows. It fetches and installs Python
of a version you specify, and manages the Path environment variable for you.


Basics
======

Distribution
------------

Find installers in `Releases <https://github.com/uranusjr/snafu/releases>`__.
Install, and restart your shell.

Installing Pythons
------------------

Install Python 3.6::

    snafu install 3.6

This should install the *latest patch version* of CPython 3.6. We don’t support
installing patch versions. This is because there is no good way to deal with
patch versions on Windows (the py launcher only supports major and minor
versioning), and you should always use the latest patch anyway.

After installing a version, ``pythonX.Y`` will be available as a command.

If you’re on a 64-bit OS, the 64-bit version is installed by default. To
install a 32-bit version on a 64-bit machine, use the `-32` suffix::

    snafu install 3.6-32

If you install both 32- and 64-bit Pythons, ``pythonX.Y`` will point to the
64-bit version, and ``pythonX.Y-32`` 32-bit.

(Note: Due to restrictions in the standard Python installer, versions up to
3.4 are available in *either* 64- or 32-bit, not both.)

On 32-bit hosts, only 32-bit Pythons are available. Not suffixes are needed.

Set Default Python Version
--------------------------

Set Python 3.5 as default::

    snafu use 3.5

This does two things:

1. `python3` is mapped to Python 3.5.
2. Scripts in `Python35\\Scripts` are linked into PATH.

Special case: ``python``, ``pip`` and ``easy_install`` are never linked, to
avoid ambiguity between Python 2 and 3. Use ``python3``, ``pip3``, ``pip3.5``,
etc. instead.

You can activate multiple versions together::

    snafu use 3.5
    snafu use 2.7

The version used first (3.5 in this example) takes precedence if there are
conflicting commands, e.g. if both 2.7 and 3.5 have ``virtualenv`` installed,
the 3.5 version will be linked.

Check the current using order::

    > snafu use
    3.6 3.5 2.7

If you wish to reset the order, or remove version links altogether, use the
``--reset`` option::

    > snafu use --reset 3.6
    ...
    > snafu use
    3.6

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


Development Guide
=================

Requirements
------------

* Windows
* Python 3.6
* Pipenv_

.. _Pipenv: https://pipenv.org

Optional Dependencies
---------------------

* Rust_ 1.9.0 for MSVC and Visual Studio 2015 if you want to run commands that
  link comamnds and scripts (e.g. ``install``, ``activate``, and ``link``).
* NSIS_ 3.x and Rust_ 1.9.0 if you want to build the installer. Commands
  ``cargo`` and ``makensis`` need to be available in your shell.

.. _Rust: https://www.rust-lang.org/en-US/
.. _`NSIS`: http://nsis.sourceforge.net/Download

Project Setup
-------------

Download and enter the project::

    git clone https://github.com/uranusjr/snafu.git
    cd snafu

Set up environment::

    pipenv install --dev

Run Tests
---------

::

    pipenv run -- pytest tests

Unfortunately there are only very limited tests right now.

Run SNAFU
---------

::

    pipenv run -- python -m snafu [COMMAND] ...


This should have the same behaviour as an installed SNAFU command, but run
inside the Pipenv-managed virtual environment.

Build the Installer
-------------------

::

    pipenv run -- python installers\build.py

You can only build installers of your host’s architecture. Cross compilation
is certainly possible (the only slightly tricky part is Rust compilation), but
I just haven’t found the need to set it up.

After the command finishes you should get an EXE in the ``installers``
directory. There are some other options available in ``build.py`` you can
check them out yourself.

Development Guideline
---------------------

Try to follow the code style. For Python code, run the linter to check for
issues before submitting::

    pipenv run -- flake8 .

I’m not that familiar with Rust myself, so any suggestions are welcome at that
front! :D


Frequently Asked Questions
==========================

Why Not Just Use the Option “Add Python to PATH”?
-------------------------------------------------

CPython’s standard Windows build, unlike on UNIX-like systems, does not provide
the “altinstall” option. This means every Python distribution on Windows only
has one Python executable called ``python.exe``, without version names such as
``python3.6.exe``.

Adding Python to PATH stops being a good idea the moment you need a *second*
installtion. You can only access one Python at a time, and installed scripts
from different versions start to mix, which is a bad thing.[#]_ The PATH
environment variable is also very tedious and delicate to manipulate.

.. [#] This is not a Windows-only problem, but also exactly why tutorials these
       days don’t recommand installing Python via `python.org`_, but with
       platform-specific tools instead.

.. _`python.org`: https://www.python.org

Wyy Not Use the Py Launcher?
----------------------------

Python introduced `PEP 397`_ partly to solve the ``python.exe`` problem (also
to interpret the shebang_ line on Windows). It installs a ``py.exe`` to your
PATH, and instead of invoking ``python.exe`` directly, you should use, for
example::

    py -3.5 foo.py

to run ``foo.py`` with Python 3.5.

This is such a good idea *SNAFU installs the Py Launcher during setup*, and I
encourage you to use it. But SNAFU also solves a few additional use cases that
``py.exe`` doesn’t:

* Availability of versioned Python executables, e.g. ``python3.6.exe``.
* Managing commands other than ``python.exe``.

SNAFU’s implementation also relies on a lot of the same values read by
``py.exe``, so you can view SNAFU as an extension to it, not a replacement.

.. _`PEP 397`: https://www.python.org/dev/peps/pep-0397/
.. _shebang: https://en.wikipedia.org/wiki/Shebang_(Unix)


Architecture (Implementation Details)
=====================================

How are Pythons installed?
--------------------------

The official CPython installers are downloaded, and executed in a
non-interactive manner. Check out the relevant documentation for more details:

* https://www.python.org/download/releases/2.5/msi/
* https://docs.python.org/3/using/windows.html#installing-without-ui


Where are Pythons installed?
----------------------------

``%LOCALAPPDATA%\Programs\Python\<version>``. This is the standard
“only-for-me” installation location for Python 3.5+, and we retrofit this rule
to older versions as well for consistency.


How are Executables linked?
---------------------------

Script executables are *copied*. ``.py`` files works as well because they have
appropriate shebang lines, and can be handled by the py launcher, as specified
in `PEP 397`_.

The ``python.exe`` programs cannot be copied as-is because they require
additional DLL files, and are shimmed instead. A ``*.shim`` file is created
to describe how a program should be run, and a small binary is used to proxy
the invocation.


Why the Name?
-------------

Because Python is hard, Windows is harder, and setting up Windows for Python
development is SNAFU. Or it’s Supernatrual Administration for You.
