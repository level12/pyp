from six.moves import configparser
from os import path as osp


def read_config(repo_dpath):
    pyp_config_fpath = osp.join(repo_dpath, 'pyp.ini')

    config = configparser.ConfigParser()
    files_found = config.read(pyp_config_fpath)
    if not files_found:
        return None
    return config['pyp']
