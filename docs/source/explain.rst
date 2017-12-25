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

Why Not Chocolatey?
===================

Chocolatey_ is a package manager on Windows. A lot of SNAFU’s ideas are
inspired by it: standard Windows installers, interaction-free installation,
and shims for execution in command prompts. It is a very good tool, and I use
it on my Windows machine—alongside SNAFU.

.. _Chocolatey: https://chocolatey.org

What SNAFU is to Chocolatey is similar to Pyenv to Homebrew and API etc. The
aims are similar, but slightly different, so we can take an approach tailored
to Python distribution.

Also I’m not very satisfied with Chocolatey’s user story. The setup is slightly
complicated (due to Powershell’s execution policy), and requires administration
priviledge to install packages. This is because it is fulfilling a different
goal from SNAFU’s, but still makes me feel uncomforatble enough not to teach
it to others.


Why Not Anaconda?
=================

I considered Anaconda very hardly, but eventually decided against it. The
tipping point is how Anaconda manages Python versions similar to virtualenvs,
with manipulation of ``PATH`` and other environment variables. This is the
wrong way to do it, [#]_ and to this day there is still no first-party
Powershell support. [#]_

.. [#] |virtualenv-wrong|_
.. [#] |conda-powershell-issue|_

.. |virtualenv-wrong| replace:: Virtualenv’s ``bin/activate`` is doing it wrong
.. _virtualenv-wrong: https://gist.github.com/datagrok/2199506

.. |conda-powershell-issue| replace:: Powershell activate and deactivate
.. _conda-powershell-issue: <https://github.com/conda/conda/issues/626

There is also no simple way (AFAIK) to run a particular version of Python in
Anaconda with just one command (except specifying the absolute path to
``python.exe``). You always need to activate the environment (and remember to
deactivate afterwards). It just feels so tedious to me.

In the end, the activate/deactivate approach requires more from the user
mentally. It is an extra thing to wrap your head around; tedious for the
experienced, and sometimes even too difficult for newcomers. This is why
Pipenv_ catches on so fast—virtualenv is wonderful, but everybody has issues
with the user interface they long for a better solution.

.. _Pipenv: https://pipenv.org

Anaconda is incredibly useful for those who need it, but its version management
tooling is simply not good enough. Fortunately, since Anaconda already conforms
to `PEP 397`_, there’s nothing theoratically preventing SNAFU to co-live with
Anaconda, so people can use SNAFU to manage Anaconda versions instead.
