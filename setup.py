import os.path as osp
import sys

from setuptools import setup, find_packages

PY2 = sys.version_info[0] == 2
cdir = osp.abspath(osp.dirname(__file__))
README = open(osp.join(cdir, 'readme.rst')).read()
CHANGELOG = open(osp.join(cdir, 'changelog.rst')).read()

version_fpath = osp.join(cdir, 'pyp', 'version.py')
version_globals = {}
with open(version_fpath) as fo:
    exec(fo.read(), version_globals)


require = [
    'click',
    'plumbum',
    'six',
    'twine',
]

if PY2:
    require += ['pathlib']


setup(
    name='pyp',
    version=version_globals['VERSION'],
    description='<short description>',
    long_description='\n\n'.join((README, CHANGELOG)),
    author='Randy Syring',
    author_email='randy.syring@level12.io',
    url='https://github.com/level12/pyp',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
    ],
    packages=find_packages(exclude=[]),
    include_package_data=True,
    zip_safe=False,
    install_requires=require,
    # List additional groups of dependencies here (e.g. development
    # dependencies). You can install these using the following syntax,
    # for example:
    # $ pip install -e .[dev,test]
    extras_require={
        # 'dev': ['restview'],
        'test': ['pytest'],
    },
    entry_points='''
        [console_scripts]
        pyp = pyp.cli:cli_entry
    ''',
)
