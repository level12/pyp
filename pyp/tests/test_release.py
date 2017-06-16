from plumbum import local
import pytest

from pyp.libs import release

git = local['git']

setup_py_contents = """
import os.path as osp
from setuptools import setup, find_packages

cdir = osp.abspath(osp.dirname(__file__))

version_fpath = osp.join(cdir, 'something', 'version.py')
version_globals = {}
with open(version_fpath) as fo:
    exec(fo.read(), version_globals)

setup(
    name='SomeThing',
    url='http://some.thing/',
    version=version_globals['VERSION'],
)
"""

changelog_contents = """
Changelog
=========

1.0 released in the past
------------------------

- some stuff
"""


def create_project(tmpdir, bail_after=None, setuppy_empty=False):
    setuppy = tmpdir.join('setup.py')
    tmpdir.join('something').ensure(dir=True)
    version_py = tmpdir.join('something', 'version.py')
    version_py.write('VERSION = "1.1"')
    tmpdir.join('changelog.rst').write(changelog_contents)

    if setuppy_empty:
        setuppy.ensure(file=True)
    else:
        setuppy.write(setup_py_contents)

    git_c = git['-C', tmpdir.strpath]

    git_c('init')
    if bail_after == 'git init':
        return

    git_c('add', '.')
    git_c('commit', '-m', 'initial commit')


class TestVerify:

    def test_no_setuppy(self, tmpdir):
        with pytest.raises(release.Error) as excinfo:
            release.verify(tmpdir.strpath)

        exc_msg = excinfo.value.args[0]

        assert 'No "setup.py" file found in source directory: ' in exc_msg
        assert exc_msg.endswith(tmpdir.strpath)

    def test_no_git(self, tmpdir):
        setuppy = tmpdir.join('setup.py')
        setuppy.ensure(file=True)

        with pytest.raises(release.ExecuteError) as excinfo:
            release.verify(tmpdir.strpath)

        exc = excinfo.value

        assert exc.executable.endswith('git')
        assert exc.args[-2:] == ['status', '--porcelain']
        assert 'Not a git repository' in exc.stderr

    def test_unclean(self, tmpdir):
        create_project(tmpdir, 'git init')

        with pytest.raises(release.Error) as excinfo:
            release.verify(tmpdir.strpath)

        assert excinfo.value.args[0] == 'Git repo is not clean'


class TestRelease:

    def run_release(self, tmpdir, version='1.2'):
        return release.release(tmpdir.strpath, 'something', version)

    def test_version_update(self, tmpdir):
        create_project(tmpdir)
        self.run_release(tmpdir)

        project = release.status(tmpdir.strpath)
        assert project.version == '1.2'

    def test_changelog_update(self, tmpdir):
        create_project(tmpdir)
        self.run_release(tmpdir)

        project = release.status(tmpdir.strpath)
        assert project.version == '1.2'


class TestStatus:

    def test_empty_setuppy(self, tmpdir):
        create_project(tmpdir, setuppy_empty=True)

        with pytest.raises(release.Error) as excinfo:
            release.status(tmpdir.strpath)

        msg = excinfo.value.args[0]
        assert msg == 'Could not get name, url, and version from setup.py.  Got: '

    def test_ok(self, tmpdir):
        create_project(tmpdir)

        project = release.status(tmpdir.strpath)

        assert project.name == 'SomeThing'
        assert project.url == 'http://some.thing/'
        assert project.version == '1.1'
