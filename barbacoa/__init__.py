# -*- coding: utf-8 -*-
'''
Asynchronous task manager using asyncio
'''
import click
import operator
import os
import pkg_resources
import time
import xdg

# Import Barbacoa Libs
import barbacoa.plugins.struct

# Import libs for packaging if they are available
try:
    import setuptools_scm
    __version__ = setuptools_scm.get_version()
except ImportError:
    try:
        __version__ = pkg_resources.get_distribution(__name__).version
    except pkg_resources.DistributionNotFound:
        # package is not installed
        __version__ = None


async def add_task(future, task, kwargs=None):
    future.set_result(await hub.tools.task.add_task(
        task=task,
        kwargs=kwargs or {},
    ))


async def get_task(future, taskid):
    for queue in hub.tools.config.get_queues():
        result = await hub.tools.task.get_task(taskid, queue)
        if result:
            future.set_result(result)


@click.group()
@click.option('config', '--config', '-c', required=False, type=click.Path(exists=False),
              default=os.path.join(xdg.XDG_CONFIG_HOME, 'barbacoa', 'config'))
def cli(config):
    hub.tools.config.load_config(config)


@cli.command()
@click.argument('task', required=True)
@click.argument('kwargs', nargs=-1)
def add(task, kwargs):
    if kwargs is None:
        kwargs = []
    cmdkwargs = {key: value for key, value in map(operator.methodcaller('split', '='), kwargs)}
    future = hub.tools.loop.create_future()
    hub.tools.loop.start(add_task(future, task, cmdkwargs))
    hub.tools.loop.close()
    print('TaskId: {0}'.format(future.result()))


@cli.command()
@click.argument('taskid', required=True)
def get(taskid):
    future = hub.tools.loop.create_future()
    hub.tools.loop.start(get_task(future, taskid))
    hub.tools.loop.close()
    print('Result: {0}'.format(future.result()))


@cli.command()
def worker():
    for queue in hub.tools.config.get_queues():
        hub.tools.loop.create_task(
            hub.tools.task.pop_tasks(queue=queue)
        )
        time.sleep(1)
    hub.tools.loop.entry()
    hub.tools.loop.close()


# setup hub
hub = barbacoa.plugins.struct.Hub()
hub.tools.pack.add('storage')
hub.tools.pack.add('queues')
hub.tools.pack.add('tasks')
