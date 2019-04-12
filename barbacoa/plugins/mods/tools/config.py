# -*- coding: utf-8 -*-
import os
import pytoml as toml


def load_config(hub, config):
    if os.path.exists(config):
        with open(config, 'rb') as configfile:
            hub._._._config = toml.load(configfile)
    else:
        hub._._._config = {}


def get(hub, option, default=None, seperator=':'):
    config = hub._._._config
    levels = option.split(seperator)

    for level in levels:
        if level not in config:
            return default
        config = config[level]

    return config


def get_default_queue(hub):
    return hub._._.get('barbacoa:queue', 'default')


def get_default_storage(hub):
    return hub._._.get('barbacoa:storage', 'default')


def get_default_timeout(hub):
    return hub._._.get('barbacoa:timeout', 10)


def get_storage(hub, queue, seperator=':'):
    if queue is None:
        queue = hub._._.get_default_queue()
    return hub._._.get(seperator.join(['barbacoa', 'queues', queue, 'storage']), seperator=seperator)


def get_queue(hub, queue, seperator=':'):
    if queue is None:
        queue = hub._._.get_default_queue()
    return hub._._.get(seperator.join(['barbacoa', 'queues', queue, 'queue']), seperator=seperator)


def get_task_queue(hub, task, seperator=':'):
    return hub._._.get(
        seperator.join(['barbacoa', 'tasks', task, 'queue']),
        default=hub._._.get_default_queue(),
        seperator=seperator
    )


def get_task_storage(hub, task, seperator=':'):
    return hub._._.get(
        seperator.join(['barbacoa', 'tasks', task, 'storage']),
        default=hub._._.get_default_storage(),
        seperator=seperator
    )


def get_task_timeout(hub, task, seperator=':'):
    return hub._._.get(
        seperator.join(['barbacoa', 'tasks', task, 'timeout']),
        default=hub._._.get_default_timeout(),
        seperator=seperator
    )


def get_queues(hub):
    yield from hub._._.get('barbacoa:queues')
