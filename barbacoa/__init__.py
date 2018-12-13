# -*- coding: utf-8 -*-
"""
Asynchronous task manager using asyncio
"""
try:
    import setuptools_scm
    __version__ = setuptools_scm.get_version()
except ImportError:
    __version__ = '0.0.0'

import barbacoa.plugins.struct


# setup hub
hub = barbacoa.plugins.struct.Hub()
hub.tools.pack.add('backends')
hub.tools.pack.add('storage')
hub.tools.pack.add('queues')
hub.tools.pack.add('tasks')
