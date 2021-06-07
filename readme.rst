.. default-role:: code

pyp's Readme
######################################

.. image:: https://circleci.com/gh/level12/pyp.svg?&style=shield&circle-token=dbf883ece73be997f2cc36737eb33dd7b19dc2c5
    :target: https://circleci.com/gh/level12/pyp

.. image:: https://codecov.io/github/level12/pyp/coverage.svg?branch=master&token=na
    :target: https://codecov.io/github/level12/pyp?branch=master

Introduction
============

pyp (pronounced "pipe") helps you automate the release of python packages

Project Prep
============

There are a couple things you should do to make your project pyp compatible:

1) Make sure you are `single-sourcing the version`_ of the project using the same method
   as this project.  See our `setup.py` and `pyp/version.py`.
2) Create a `pyp.ini` file in the root of your project with the following content and uncomment
   defaults as needed::

    [pyp]
    # The relative path, from your project root, to the directory your project source lives.
    # Currently, this is how pyp finds the project's `version.py` file.
    source_dir = proj-app-dir
    # If your changelog file name is not changelog.rst, then you will also need:
    # changelog_fname = CHANGES.rst
    # If the header of you changelog file is not `Changelog\n=========\n`, then you will also need:
    # changelog_doc_header = 'Some Value'

.. _single-sourcing the version: https://packaging.python.org/guides/single-sourcing-package-version/#single-sourcing-the-version


Usage
=====

To release a package, you will:

1. Run `pyp status` to inspect the current state of the project and get any errors/warnings.
2. Run `pyp release [version]` to generate the changelog & bump the version
3. Inspect the changes from the previous command, alter changelog if needed, commit.
4. Run `pyp publish` to build an sdist, wheel and push them to pypi with Twine.  Also it will tag
   the most recent commit with the version push to remote (e.g. GitHub).
