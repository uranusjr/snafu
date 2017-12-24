.. _manage:

==============
Manage Pythons
==============

The real benefits of SNAFU shows when you install more than one Python
versions. Instead of manipulating the ``PATH`` environment variable, simply
run the command with the appropriate version name.

.. code-block:: powershell

    # Python 3.6 (64-bit on available hosts, 32-bit otherwise).
    snafu install 3.6
    python3.6
    pip3.6

    # Python 3.5 (force 32-bit).
    snafu install 3.5-32
    python3.5-32
    pip3.5-32

    # Python 2.7.
    snafu install 2.7
    python2.7
    pip2.7

No more ``python.exe`` shadowing because you have multiple versions in
``PATH``.

Use Versions
============

When you have multiple Python versions installed, SNAFU only exposes the above
two executables by default. If you want to expose other commands of a given
Python version, You can tell SNAFU to *use* it: [#]_

::

    snafu use 3.6

.. [#] SNAFU does this automatically when you install your first ever Python
    version. This is why we had access to ``python3`` without using 3.6 in
    :ref:`install`.

So SNAFU publishes (almost) all commands available in Python 3.6, including

    * ``python3.exe``
    * ``pip3.exe``
    * ``easy_install-3.6.exe``
    * All other scripts you installed via ``pip install``.

As an exception, SNAFU blacklists ``python.exe``, ``pip.exe``, and
``easy_install.exe`` from being published, to encourage the best practice of
always using versioned Python and Pip commands.

You can use multiple versions together to expose scripts installed across
them::

    snafu use 3.6 2.7

This exposes commands from both Python 3.6 and 2.7, with 3.6 taking precedence,
i.e. if a given command exists in both versions, the 3.6 one will be called.

Manage Used Versions
====================

To see what versions are currently in use::

    snafu use

To reset using state (i.e. unuse all versions)::

    snafu use --reset
