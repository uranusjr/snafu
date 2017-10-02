=========================
SNAFU the Python Manager
=========================

SNAFU is a Python installer manager for Windows. It fetches and installs Python
of a version you specify, and manages the Path environment variable for you.


Specification
==============

(This is a overview of what the end result should look like. Most things are
not implemented yet.)

Distribution
------------

Scripts and library should be bundled with the
`Embeddable <https://blogs.msdn.microsoft.com/pythonengineering/?p=563>`__
CPython distribution and built into a `snafu.exe`, so the user can just install
and run this without knowing the whole thing is implemented in Python.

I’m still poundering whether I should put the executable somewhere in PATH,
*add* it to the PATH, or just leave this to the user. This can be discussed
and decided on later.

Installing Pythons
------------------

Install Python 3.6::

    snafu install 3.6

This should install the *latest patch version* of CPython 3.6. Note that unlike
pyenv, we don’t support installing patch versions. This is because there is no
good way to deal with patch versions on Windows (the py launcher only supports
major and minor versioning), and you should always use the latest patch anyway.

If this is the first ever Python installed, the command should automatically
install the py launcher as well. The py launcher is generally not re-installed,
but may be updated if you’re installing a newer version of Python.

After installing a version, `pythonX.Y` will be available as a command. (This
can probably be done with a `.bat` file + launcher).

The 64-bit version is installed by default, unless you’re on a 32-bit OS. To
install a 32-bit version on a 64-bit machine, use a `-32` suffix::

    snafu install 3.6-32

The 64- and 32-bit versions can co-exist. In such case, `pythonX.Y` points to
the 64-bit version, while `pythonX.Y-32` 32-bit.

Set Default Python Version
--------------------------

Set Python 3.5 as default::

    snafu activate 3.5

This does two things:

1. `python3` is mapped to Python 3.5. (Note: there is no `python3-32` because
   it’s too tedious to manage).
2. Scripts in `Python35\Scripts` are *linked* into PATH.

Special case: `pip.exe` is **never** linked, to avoid any confusion. Use
`pip3`, `pip3.5`, etc. instead.

There is also no `python` command. You should not use it anyway (and should
always use `python2` or `python3` instead).

You can activate multiple versions together::

    snafu activate 2.7 3.5

In such case, the version at the front takes precedence if there are
conflicting commands, e.g. if both 2.7 and 3.5 has `virtualenv` installed,
the 2.7 version will be linked.

Uninstalling
------------

To uninstall a version::

    snafu uninstall 3.5

Uninstalling an active version results in broken links. (A possible improvement
candidate in the future.)


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

``%APPLOCALDATA%\Programs\Python\Python36`` (for Python 3.6). This is the
standard “only-for-me” installation location for Python 3.5+, and we retrofit
this rule to older versions as well for consistency.


How are Executables linked?
---------------------------

With .bat one-liners like this::

    @%APPLOCALDATA%\Programs\Python\Python35\python.exe %*


Why SNAFU?
----------

Because Python is hard, Windows is harder, and setting up Windows for Python
development is SNAFU. Or it’s Supernatrual Administration for You.
