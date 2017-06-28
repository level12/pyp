from collections import namedtuple
from functools import wraps
import pathlib
import shutil

from plumbum import local
from plumbum.commands import processes
import six


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
        six.raise_from(ExecuteError(exc), exc)

    return repo_dpath


def git_log_revspan():
    retcode, stdout, stderr = git['describe', '--tags', '--abbrev=0'].run(retcode=(0, 128))
    if retcode == 128:
        assert 'No names found' in stderr, stderr
        # Ok, so there is no tag in this repo, use the next command to get the hash of the very
        # first commit.
        start_with = git('rev-list', '--max-parents=0', 'HEAD')
        # It's possible there are multiple first commits, we can't handle that situation.
        assert start_with.count('\n') == 1
    else:
        start_with = stdout
    return start_with.strip() + '..HEAD'


@repo_handler
def release(repo_dpath, src_dpath, version, release_date):
    # Write the new version
    with repo_dpath.joinpath(src_dpath, 'version.py').open('w') as version_fh:
        version_fh.write(u"VERSION = '{}'\n".format(version))

    project = _status()

    revspan = git_log_revspan()
    git_logs = git['log', '--first-parent']
    changelog = git_logs('--pretty=format:- %s (%h_)', revspan)

    commit_url = project.url.rstrip('/')
    links_git_format = '--pretty=format:.. _%h: {}/commit/%h'.format(commit_url)
    changelog_links = git_logs(links_git_format, revspan)

    release_date_str = release_date.strftime('%Y-%m-%d')
    changelog_release_header = u'{} released {}'.format(version, release_date_str)
    changelog_release_header += u'\n' + u'-' * len(changelog_release_header)
    changelog_doc_header = u'Changelog\n=========\n'

    with repo_dpath.joinpath('changelog.rst').open('r+') as changelog_fh:
        changelog_doc_content = changelog_fh.read()

        if changelog_doc_header not in changelog_doc_content:
            raise Error('Could not find changelog document header ({!r}) in changelog.rst'
                        .format(changelog_doc_header))
        current_content = changelog_doc_content.replace(changelog_doc_header, '')

        changelog_fh.seek(0)
        changelog_fh.write(changelog_doc_header + '\n')
        changelog_fh.write(changelog_release_header + '\n\n')
        changelog_fh.write(changelog + '\n\n')
        changelog_fh.write(changelog_links + '\n\n')
        changelog_fh.write(current_content)
        changelog_fh.truncate()


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


@repo_handler
def publish(repo_dpath):
    status = _status()

    build_dpath = repo_dpath.joinpath('build')
    dist_dpath = repo_dpath.joinpath('dist')

    if build_dpath.exists():
        shutil.rmtree(str(build_dpath))
    if dist_dpath.exists():
        shutil.rmtree(str(dist_dpath))

    python_setup('check', '--strict', '--metadata', '--restructuredtext')
    python_setup('--quiet', 'sdist', 'bdist_wheel')

    upload_files = [str(fpath) for fpath in dist_dpath.glob('*')]
    local['twine']('upload', *upload_files)

    git('tag', '-m', 'pyp publish', status.version)
    git('push', '--tags')
