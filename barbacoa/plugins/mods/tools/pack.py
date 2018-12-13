# -*- coding: utf-8 -*-
'''
Control and add subsystems to the running hub
'''
# pylint: disable=protected-access


def add(hub, modname, **kwargs):
    '''
    Add a new subsystem to the hub
    '''
    # Make sure that unintended funcs are not called with the init
    if kwargs.get('init') is True:
        kwargs['init'] = 'init.new'
    hub._add_subsystem(modname, **kwargs)


def remove(hub, packname):
    '''
    Remove a pack from the hub, run the shutdown if needed
    '''
    if hasattr(hub, packname):
        hub._remove_subsystem(packname)


def load_all(hub, packname):
    '''
    Load al modules under a given pack
    '''
    if hasattr(hub, packname):
        pack = getattr(hub, packname)
        pack._load_all()
        return True
    else:
        return False
