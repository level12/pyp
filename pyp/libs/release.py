from collections import namedtuple
from functools import wraps
import pathlib

from plumbum import local
from plumbum.commands import processes

git = local['git']
python = local['python']
python_setup = python['setup.py']
ProjectStatus = namedtuple('ProjectStatus', ['name', 'url', 'version'])


class Error(Exception):
    pass


class ExecuteError(Error):
    def __init__(self, exc):
        self.exc = exc

    @property
    def executable(self):
        return self.exc.argv[0]

    @property
    def args(self):
        return self.exc.argv[1:]

    @property
    def stdout(self):
        return self.exc.stdout

    @property
    def stderr(self):
        return self.exc.stderr


def repo_handler(callable):
    @wraps(callable)
    def wrapper(repo_dpath, *args, **kwargs):
        with local.cwd(repo_dpath):
            repo_dpath = pathlib.Path(repo_dpath)
            return callable(repo_dpath, *args, **kwargs)
    return wrapper


@repo_handler
def verify(repo_dpath):
    setup_py = repo_dpath / 'setup.py'
    if not setup_py.exists():
        raise Error('No "setup.py" file found in source directory: {}'.format(repo_dpath))

    try:
        git_status = git('status', '--porcelain')
        if git_status:
            raise Error('Git repo is not clean')
    except processes.ProcessExecutionError as exc:
        raise ExecuteError(exc) from exc

    return repo_dpath


@repo_handler
def release(repo_dpath, src_dpath, version):
    # Write the new version
    with repo_dpath.joinpath(src_dpath, 'version.py').open('w') as version_fh:
        version_fh.write("VERSION = '{}'".format(version))

    project = _status()

    current_tag = git('describe', '--tags', '--abbrev=0')
    git_merges = git['log', '--merges']
    rev_span = current_tag + '..HEAD'
    changelog = git_merges('--pretty=format:"* %s (%h_)"', rev_span)
    changelog_links = git_merges('--pretty=format:".. _%h: {}/commit/%h"'.format(project.url), rev_span)
    today_str = dt.date.today().strftime('%Y-%m-%d')
    changelog_header = '{} - {}'.format(version, today_str)

    changelog_title_marker = '========='



@repo_handler
def status(repo_dpath):
    return _status()


def _status():
    result = python_setup('--name', '--url', '--version')
    lines = result.splitlines()
    if len(lines) != 3:
        msg = 'Could not get name, url, and version from setup.py.  Got: {}'.format(result)
        raise Error(msg)
    name, url, version = lines
    return ProjectStatus(name, url, version)
