# -*- coding: utf-8 -*-
"""
Asynchronous task manager using asyncio
"""
import json
import os
import subprocess
import sys

import barbacoa.plugins.struct

VERSION_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'version.json')
GIT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '.git')


def version(v):
    return tuple(map(int, [num for num in v.replace('-', '.').split('.') if num.isdigit()]))


def get_version_data():
    if not os.path.isdir(GIT_PATH ):
        return {'version': '0.0.0'}
    return {'version': subprocess.run(['git', 'describe'], stdout=subprocess.PIPE).stdout.strip().decode()}


def write_version_data(version_data):
    version_data['version'] = '.'.join(map(str, version(version_data['version'])))
    with open(VERSION_FILE, 'w') as vfile:
        json.dump(version_data, vfile)


def read_version_data():
    with open(VERSION_FILE, 'r') as vfile:
        version_data = json.load(vfile)
    return version_data

if os.path.isfile(VERSION_FILE):
    version_data = read_version_data()
    new_version_data = get_version_data()
    if version(new_version_data['version']) > version(version_data['version']):
        write_version_data(new_version_data)
        version_data = new_version_data
else:
    version_data = get_version_data()
    write_version_data(version_data)

__version__ = version_data['version']

# setup hub
hub = barbacoa.plugins.struct.Hub()
hub.tools.pack.add('backends')
hub.tools.pack.add('storage')
hub.tools.pack.add('queues')
hub.tools.pack.add('tasks')
