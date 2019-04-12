# -*- coding: utf-8 -*-
import urllib.parse
import uuid


def get_queue_mod_from_url(hub, url):
    parsed_url = urllib.parse.urlparse(url)
    queue_type = parsed_url.scheme
    return getattr(hub.queues, queue_type)


def get_storage_mod_from_url(hub, url):
    parsed_url = urllib.parse.urlparse(url)
    storage_type = parsed_url.scheme
    return getattr(hub.storage, storage_type)


def get_task_queue_mod(hub, task):
    queue = hub._.config.get_task_queue(task)
    url = hub._.config.get_queue(queue)
    return hub._._.get_queue_mod_from_url(url)


def get_task_storage_mod(hub, task):
    storage = hub._.config.get_task_storage(task)
    url = hub._.config.get_queue(storage)
    return hub._._.get_storage_mod_from_url(url)


def get_storage_from_queue(hub, queue):
    url = hub._.config.get_storage(queue)
    return hub._._.get_storage_mod_from_url(url)


async def add_task(hub, task, kwargs=None, queue=None):
    taskid = uuid.uuid4()
    queuemod = hub._._.get_task_queue_mod(task)

    await queuemod.add_task(taskid=taskid, task=task, kwargs=kwargs, queue=queue)
    return taskid


async def get_task(hub, taskid, queue):
    storagemod = hub._._.get_storage_from_queue(queue)
    return await storagemod.get_result(taskid=taskid, queue=queue)


async def run_task(hub, task):
    queue = hub._.config.get_task_queue(task['fun'])
    storagemod = hub._._.get_task_storage_mod(task['fun'])

    kwargs = task['kwargs'] or {}
    mod, fun = task['fun'].split('.')

    job = getattr(getattr(hub.tasks, mod), fun)(**kwargs)
    timeout = hub._.config.get_task_timeout(task['fun'])

    done, _ = await hub.tools.loop.wait(job, timeout=timeout)

    data = done.pop().result()

    if not isinstance(data, dict):
        data = {'result': data}

    queuemod = hub._._.get_task_queue_mod(task['fun'])
    await queuemod.ack_task(taskid=task['uuid'], queue=queue)

    await storagemod.set_result(taskid=task['uuid'], result=data, queue=queue)


async def pop_tasks(hub, queue=None, sleep=1, jobs=10):
    while True:
        queueurl = hub.tools.config.get_queue(queue)
        queuemod = hub._._.get_queue_mod_from_url(queueurl)
        task = await queuemod.pop_task(queue=queue)
        if not task:
            await hub.tools.loop.sleep(1)
            continue

        storagemod = hub._._.get_task_storage_mod(task['fun'])
        await storagemod.add_task(taskid=task['uuid'], task=task['fun'], kwargs=task['kwargs'] or {}, queue=queue)

        hub.tools.loop.create_task(
            hub.tools.task.run_task(task)
        )

        await hub.tools.loop.sleep(sleep)
