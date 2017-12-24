===============
Implement SNAFU
===============

Some implementation notes about SNAFU, in a series of questions. Nobody ever
asked, but I want to answer them.

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


How are executables linked?
---------------------------

They are not. Scripts are *copied*. ``.py`` files works as well because they
have appropriate shebang lines, and can be handled by the py launcher, as
specified in `PEP 397`_.

.. _`PEP 397`: https://www.python.org/dev/peps/pep-0397/

A few wrapper executables (shims_) are distributed with SNAFU, and are
published into ``PATH`` to stub a few special executables, such as
``python.exe`` and ``pip.exe``. When invoked, these shims rely on the registry
to launch their real conterparts, and bridge all user interaction to them.

The shims minimise the need to expose internal DLLs, and, in the case of
``pip.exe`` etc., provide a chance to hook into extra machinery when you alter
Python installations. This is inspired by pyenv_ and Chocolatey_, and provides
a more seamless experience.

.. _shims: https://en.wikipedia.org/wiki/Shim_(computing)
.. _pyenv: https://github.com/pyenv/pyenv
.. _Chocolatey: https://chocolatey.org


Why the name?
-------------

Because Python is hard, Windows is harder, and setting up Windows for Python
development is SNAFU. Or it’s Supernatrual Administration for You. Mosky says
it sounds kind of like snake, so there’s that.
