# -*- coding: utf-8 -*-

# Import Python Libs
import os
import collections

PY_END = ('.py', '.pyc', '.pyo')
SKIP_DIRNAMES = ('__pycache__',)


def scan(directories, recurse=False):
    '''
    Return a list of importable files
    '''
    ret = collections.OrderedDict()
    for dir_ in directories:
        if recurse:
            for dir_, dirs_, files in os.walk(dir_):
                for fn_ in files:
                    _apply_scan(ret, dir_, fn_)
            ret.update(scan(dirs_, recurse=True))
        else:
            for fn_ in os.listdir(dir_):
                _apply_scan(ret, dir_, fn_)
    return ret


def _apply_scan(ret, dir_, fn_):
    '''
    Convert the scan data into
    '''
    if fn_.startswith('_'):
        return
    if os.path.basename(dir_) in SKIP_DIRNAMES:
        return
    full = os.path.join(dir_, fn_)
    if '.' not in full:
        return
    bname = full[:full.rindex('.')]
    if fn_.endswith(PY_END):
        ret[bname] = {'path': full}
