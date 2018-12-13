# -*- coding: utf-8 -*-

# Import Python Libs
import importlib
import os


def load_mod(modname, path):
    '''
    Attempt to load the named python modules
    '''
    return importlib.machinery.SourceFileLoader(modname, path).load_module()


def load_virtual(parent, virtual, mod, bname):
    base_name = os.path.basename(bname)
    if '.' in base_name:
        base_name = base_name.split('.')[0]
    name = getattr(mod, '__virtualname__', base_name)
    if not virtual:
        return {'name': base_name}
    if not hasattr(mod, '__virtual__'):
        return {'name': name}

    ret = mod.__virtual__(parent)

    if isinstance(ret, tuple):
        vret, vmsg = ret
    else:
        vret, vmsg = ret, 'Failed to load {0}'.format(mod.__name__)

    if vret is True:
        return {'name': name}

    if vret is False:
        return {'name': base_name, 'vname': name, 'error': vmsg}

    return {'name': base_name, 'vname': name, 'error': 'Invalid response from __virtual__'}
