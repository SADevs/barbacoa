# -*- coding: utf-8 -*-
import json
import os
import subprocess

version_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'version.json')

if os.path.isfile(version_file):
    with open(version_file, 'r') as vfile:
        version_data = json.load(vfile)
else:
    version_data = {'version': subprocess.run(['git', 'describe']).stdout.strip()}
    with open(version_file, 'w') as vfile:
        json.dump(version_data, vfile)

__version__ = version_data['version']
