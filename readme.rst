.. default-role:: code

pyp's Readme
######################################

.. image:: https://circleci.com/gh/level12/pyp.svg?&style=shield&circle-token=dbf883ece73be997f2cc36737eb33dd7b19dc2c5
    :target: https://circleci.com/gh/level12/pyp

.. image:: https://codecov.io/github/level12/pyp/coverage.svg?branch=master&token=na
    :target: https://codecov.io/github/level12/pyp?branch=master

Introduction
============

pyp (pronounced "pipe") helps you do so stuff in python projects.  Currently, available commands
are:

* release: bumps the version, updates the changelog (you then edit and commit)
* publish:

    * git: tag, push
    * pypi: build sdist & wheel, upload

Project Prep
============

There are a couple things you should do to make your project pyp compatible:

1) Make sure you are `single-sourcing the version`_ of the project using the same method
   as this project.  See our `setup.py` and `pyp/version.py`.
2) Create a `pyp.ini` file in the root of your project with the following content::

    [pyp]
    # The relative path, from your project root, to the directory your project source lives.
    # Currently, this is how pyp finds the project's `version.py` file.
    source_dir = proj-app-dir

3) Make sure the document title of `changelog.rst` is exactly `Changelog\n=========\n`.

.. _single-sourcing the version: https://packaging.python.org/guides/single-sourcing-package-version/#single-sourcing-the-version
