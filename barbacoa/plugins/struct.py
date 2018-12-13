# -*- coding: utf-8 -*-

# Import Python Libs
import collections
import inspect
import os

# Import Plugins Libs
import barbacoa.plugins.dirs
import barbacoa.plugins.exc
import barbacoa.plugins.loader
import barbacoa.plugins.scanner


class Hub(object):
    context = {}

    def __init__(self):
        self._subs = collections.OrderedDict()
        self._add_subsystem('tools', pypath='barbacoa.plugins.mods.tools')

    def _add_subsystem(self, modname, subname=None, pypath=None, virtual=True, recurse=False, mod_basename='hub.pack'):
        subname = subname or modname
        self._subs[modname] = Pack(self, modname, subname, pypath, virtual, recurse)

    def _remove_subsystem(self, subname):
        if subname in self._systems:
            self._subs.pop(subname)
            return True
        return False

    def __getattr__(self, item):
        if item.startswith('_'):
            return self.__getattribute__(item)
        if item in self._subs:
            return self._subs[item]
        return self.__getattribute__(item)

    def __iter__(self):
        return iter(self._subs.keys())

    @property
    def _(self):
        '''
        This function allows for hub to pack introspective calls.
        This should only ever be called from within a hub module, otherwise
        it should stack trace, or return heaven knows what...
        '''
        dirname = os.path.dirname(inspect.stack()[1].filename)
        for sub in self._subs:
            if dirname in self._subs[sub]._dirs:
                return self._subs[sub]
        raise barbacoa.plugins.exc.PackLookupError('Called from outside a hub!')


class Pack(object):
    def __init__(self, parent, modname, subname=None, pypath=None, virtual=True,
                 recurse=False, mod_basename='hub.pack'):
        self._parent = parent
        self._modname = modname
        self._subname = subname or modname
        self._pypath = pypath
        self._virtual = virtual
        self._recurse = recurse
        self._loaded_all = False
        self._loaded = {}
        self._vmap = {}
        self._load_errors = {}
        self._mod_basename = mod_basename
        self.__prepare__()

    def __prepare__(self):
        self._dirs = barbacoa.plugins.dirs.dir_list(self._pypath or self._subname)
        self._scan = barbacoa.plugins.scanner.scan(self._dirs, self._recurse)

    @property
    def __name__(self):
        return '{}.{}'.format(self._mod_basename, self._modname)

    def __iter__(self):
        if self._loaded_all is False:
            self._load_all()
        return iter(self._loaded.values())

    def _load_all(self):
        if self._loaded_all is True:
            return
        for bname in self._scan:
            if self._scan[bname].get('loaded'):
                continue
            self._load_item(bname)
        self._loaded_all = True

    @property
    def _(self):
        fn = inspect.stack()[1].filename
        vname = self._vmap[fn]
        return getattr(self, vname.split('.')[-1])

    def __getattr__(self, item):
        if item.startswith('_'):
            return self.__getattribute__(item)
        if item in self._loaded:
            return self._loaded[item]
        return self._find_mod(item)

    def __contains__(self, item):
        try:
            return hasattr(self, item)
        except barbacoa.plugins.exc.PackLookupError:
            return False

    def _apply_wrapper(self, mod):
        for func_name, func in inspect.getmembers(mod, inspect.isfunction):
            if func_name.startswith('_'):
                continue
            setattr(mod, func_name, Wrapper(self._parent, func))
        self._vmap[mod.__file__] = mod.__name__
        return mod

    def _find_mod(self, item):
        '''
        find the module named item
        '''
        for bname in self._scan:
            if self._scan[bname].get('loaded'):
                continue
            self._load_item(bname)
            if item in self._loaded:
                return self._loaded[item]
        # Let's see if the module being lookup is in the load errors dictionary
        if item in self._load_errors:
            # Return the LoadError
            raise barbacoa.plugins.exc.PackLoadError(self._load_errors[item])

    def _load_item(self, bname):
        mname = '.'.join([self.__name__, os.path.basename(bname).split(".")[0]])
        if bname not in self._scan:
            raise Exception('Bad call to load item: {mname}')
        mod = barbacoa.plugins.loader.load_mod(mname, self._scan[bname]['path'])
        vret = barbacoa.plugins.loader.load_virtual(self._parent, self._virtual, mod, bname)
        if 'error' in vret:
            self._load_errors[vret['name']] = vret['error']
            return
        self._loaded[vret['name']] = self._apply_wrapper(mod)
        self._scan[bname]['loaded'] = True


class Wrapper(object):
    def __init__(self, parent, func):
        self.parent = parent
        self.func = func
        self.func_name = func.__name__
        self.__name__ = func.__name__

    def __call__(self, *args, **kwargs):
        if args and (args[0] is self.parent or isinstance(args[0], self.parent.__class__)):
            # The hub(parent) is being passed directly, remove it from args
            # since we'll inject it further down
            args = list(args)[1:]
        args = [self.parent] + list(args)
        return self.func(*args, **kwargs)

    def __repr__(self):
        return '<{} func={}.{}>'.format(self.__class__.__name__, self.func.__module__, self.func_name)
