.. _develop:

===================
Contribute to SNAFU
===================

Development of SNAFU happens on `GitHub <https://github.com/uranusjr/snafu>`__.


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

Run In-Development SNAFU
------------------------

::

    pipenv run python -m snafu [COMMAND] ...


This should have the same behaviour as an installed SNAFU command, but run
inside the Pipenv-managed virtual environment.

Build Installer
---------------

::

    pipenv run invoke installers.build

You can only build installers of your host’s architecture. Cross compilation
is certainly possible, but I haven’t found the need to set it up.

After the command finishes you should get an EXE in the ``installers``
directory.

Build Documentation
-------------------

::

    pipenv run invoke docs.build

Documentation is managed with Sphinx_, and hosted on `Read the Docs`_ with a
custom domain.

.. _Sphinx: http://sphinx-doc.org
.. _`Read the Docs`: https://readthedocs.org

Source Code Guideline
---------------------

Try to follow the code style. For Python code, run the linter to check for
issues before submitting::

    pipenv run flake8 .

Format of text files are managed with EditorConfig_. I recommend using one of
the editor plugins to automatically format files. If you can’t/don’t want to
do so, please at least make sure you’re using the correct format before sending
in pull requests.

.. _EditorConfig: http://editorconfig.org
