from __future__ import print_function

import datetime as dt
import os.path as osp

import click

from pyp.version import VERSION
from pyp.libs import release as releaselib
from pyp.libs.config import read_config


def cli_entry():
    pyp()


@click.group()
@click.pass_context
def pyp(ctx):
    pass


@pyp.command()
def version():
    click.echo('version: {}'.format(VERSION))


@pyp.command()
@click.argument('version')
@click.argument('repo_dpath', type=click.Path(exists=True), default='.')
@click.pass_context
def release(ctx, version, repo_dpath):
    try:
        releaselib.verify(repo_dpath)

        config = read_config(repo_dpath)
        if not config:
            ctx.fail('no pyp.ini file found')
        source_dir = config['source_dir']
        source_dpath = osp.join(repo_dpath, source_dir)

        release_date = dt.date.today()

        releaselib.release(repo_dpath, source_dpath, version, release_date)
    except releaselib.Error as e:
        ctx.fail(str(e))

    click.echo('Release made.  Review git repo changes, edit if needed, and commit.')
    click.echo('Next...run `pyp publish`.')


@pyp.command()
@click.pass_context
@click.argument('repo_dpath', type=click.Path(exists=True), default='.')
def publish(ctx, repo_dpath):
    try:
        releaselib.verify(repo_dpath)
        releaselib.publish(repo_dpath)
    except releaselib.Error as e:
        ctx.fail(str(e))

    click.echo('Project built, uploaded, tagged, and pushed')


@pyp.command()
@click.pass_context
@click.argument('repo_dpath', type=click.Path(exists=True), default='.')
def status(ctx, repo_dpath):
    try:
        releaselib.verify(repo_dpath)
        status = releaselib.status(repo_dpath)
    except releaselib.Error as e:
        ctx.fail(str(e))

    click.echo('Name: {}'.format(status.name))
    click.echo('URL: {}'.format(status.url))
    click.echo('Version: {}'.format(status.url))
