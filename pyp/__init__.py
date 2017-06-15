from __future__ import absolute_import
from __future__ import unicode_literals

from pyp.version import VERSION


def cli_entry():
    print('Hello World!')
    print('From pyp version {}'.format(VERSION))
