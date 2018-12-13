import os
import importlib

try:
    import pkg_resources
except ImportError:
    HAS_PKGRESOURCES = False
else:
    HAS_PKGRESOURCES = True


def dir_list(pypath=None):
    ret = []
    if pypath is None:
        pypath = []
    if isinstance(pypath, str):
        pypath = pypath.split(',')
    for path in pypath:
        try:
            mod = importlib.import_module(path)
            ret.append(os.path.dirname(mod.__file__))
        except ImportError:
            if HAS_PKGRESOURCES:
                for entry in pkg_resources.iter_entry_points('barbacoa.loader', path):
                    ret.append(os.path.dirname(entry.load().__file__))
    return ret
