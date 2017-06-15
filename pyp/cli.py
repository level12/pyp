from __future__ import print_function

import click

from pyp.version import VERSION


@click.group()
@click.pass_context
def pyp(ctx):
    pass


@pyp.command()
def version():
    click.echo('version: {}'.format(VERSION))


@pyp.command()
@click.argument('name', default='World')
def hello(name):
    click.echo('Hello {}!'.format(name))


def cli_entry():
    pyp()
