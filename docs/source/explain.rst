=============
Explain SNAFU
=============

The idea of SNAFU formed gradually from problems I faced when working on
multiple development machines, constantly switching between Windows and macOS.
I long a more consistent development experience, and a good way to manage my
Python environment on Windows.

I tried out quite a few solutions. While a lot of them work for myself (to
varying degree), none of them make me feel comfortable because *I can’t teach
anybody about them*, which means they are all somehow wrong. Eventually I
decided I need a complete managing system, which became SNAFU.

Below are some questions I either faced when discussing the Python setup
problem with others, or through introspection. Each question represents an
alternative solution I tried, but eventually couldn’t feel satisfied with. I
hope they will answer *why* I think SNAFU is the best solution, and you should
adapt it as well.


Why Not “Add Python to PATH”?
=============================

The standard CPython installer offers this option. It is not checked by
default, but a lot of online tutorials tell you to do so. The CPython core
team is correct; it shouldn’t be checked under most cercumstances.

CPython’s standard Windows build, unlike on Un\*x, does not provide the
“altinstall” build option. Every CPython distribution on Windows has only one
Python executable, called ``python.exe``, not versioned names such as
``python3.6.exe``.

Adding Python to ``PATH`` stops being a good idea the moment you install a
second Python. You can only access one Python at a time, and installed scripts
from different versions start to mix, which is a bad thing. [#]_ It also
become very tedious and delicate very quickly to manipulate the ``PATH``
environment variable.

.. [#] This is not a Windows-only problem, but also exactly why tutorials these
       days don’t recommand installing Python via `python.org`_, but with
       platform-specific tools instead. Windows is the only mainstream
       operation system without a good Python verions management tool.

.. _`python.org`: https://www.python.org

Why Not the Python Launcher (``py.exe``)?
=========================================

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

Why Not Install to All Users?
=============================

Authentication on Windows is difficult to manage, especially in the console.
There really is no way to elevate priviledge inside a command prompt, and it
is against common workflow to require opening a new console when you need to
``pip install`` something.

It is useful to have a system-wide Python setup. For developers, however, it
is always recommended to install a seperate copy of Python for yourself, so
you can manage it directly, without special priviledge.

Why not Anaconda?
=================

I considered Anaconda very hardly, but eventually decided against it. It is
important to me that I need to feel comforatble teaching a solution to a
relative beginner. *Hey, let’s learn Python, but don’t download from
`python.org`_, but this other website!* This just feels wrong to me. I also
have spent too much time answering beginners whether they should use Conda or
Pip. I need to stick with CPython.

Anaconda is incredibly useful for those who need it, but for other people,
maybe not so much. And since Anaconda also conforms to `PEP 397`_, there’s
nothing theoratically preventing SNAFU to co-live with Anaconda.
