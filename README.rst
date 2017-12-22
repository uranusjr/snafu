=========================
SNAFU the Python Manager
=========================

.. image:: https://ci.appveyor.com/api/projects/status/jjix3jifn79maf8q?svg=true&branch=master
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

    snafu use 3.5 2.7

The version used first (3.5 in this example) takes precedence if there are
conflicting commands, e.g. if both 2.7 and 3.5 have ``virtualenv`` installed,
the 3.5 version will be linked.

Check the current using order::

    > snafu use
    3.5 2.7

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
* Rust_

.. _Pipenv: https://pipenv.org
.. _Rust: https://www.rust-lang.org/en-US/install.html

Optional Dependencies
---------------------

* NSIS_ 3.x if you want to build shims and the installer. ``makensis``
  needs to be available in your shell.

.. _NSIS: http://nsis.sourceforge.net/Download


Project Setup
-------------

Download and enter the project::

    git clone https://github.com/uranusjr/snafu.git
    cd snafu

Set up environment::

    pipenv install --dev

Build the shims::

    pipenv run invoke shims.build

Run Tests
---------

::

    pipenv run pytest tests

Unfortunately there are only very limited tests right now.

Run SNAFU
---------

::

    pipenv run python -m snafu [COMMAND] ...


This should have the same behaviour as an installed SNAFU command, but run
inside the Pipenv-managed virtual environment.

Build the Installer
-------------------

::

    pipenv run invoke installers.build

You can only build installers of your host’s architecture. Cross compilation
is certainly possible, but I haven’t found the need to set it up.

After the command finishes you should get an EXE in the ``installers``
directory.

Development Guideline
---------------------

Try to follow the code style. For Python code, run the linter to check for
issues before submitting::

    pipenv run flake8 .


Frequently Asked Questions
==========================

Why Not Just Use the Option “Add Python to PATH”?
-------------------------------------------------

CPython’s standard Windows build, unlike on UNIX-like systems, does not provide
the “altinstall” option. This means every Python distribution on Windows only
has one Python executable called ``python.exe``, not versioned names such as
``python3.6.exe``.

Adding Python to PATH stops being a good idea the moment you need a *second*
installtion. You can only access one Python at a time, and installed scripts
from different versions start to mix, which is a bad thing. [#]_ The PATH
environment variable is also very tedious and delicate to manipulate.

.. [#] This is not a Windows-only problem, but also exactly why tutorials these
       days don’t recommand installing Python via `python.org`_, but with
       platform-specific tools instead. Windows is the only mainstream
       operation system without a good Python verions management tool.

.. _`python.org`: https://www.python.org

Why Not Use the Py Launcher?
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

A few wrapper executables (shims_) are distributed with SNAFU, and are
published into ``%PATH%`` to stub certain special executables, such as
``python.exe`` and ``pip.exe``. When invoked, these shims rely on the registry
to launch their real conterparts, and bridge all user interaction to them.

The shims minimise the need to expose internal DLLs, and, in the case of
``pip.exe`` etc., provide a chance to hook into extra machinery when you alter
Python installations. This is inspired by pyenv_ and Chocolatey_, and provides
a more seamless experience.

.. _shims: https://en.wikipedia.org/wiki/Shim_(computing)
.. _pyenv: https://github.com/pyenv/pyenv
.. _Chocolatey: https://chocolatey.org


Why the Name?
-------------

Because Python is hard, Windows is harder, and setting up Windows for Python
development is SNAFU. Or it’s Supernatrual Administration for You. Mosky says
it sounds kind of like snake, so there’s that.
