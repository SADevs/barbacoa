# -*- coding: utf-8 -*-
'''
The main interface for management of the aio loop
'''
# Import python libs
import asyncio
import functools

__virtualname__ = 'loop'


def __virtual__(hub):
    return True


def create(hub):
    '''
    Create the loop at hub.loop.loop
    '''
    if not hasattr(hub.tools, '_loop'):
        hub.tools._loop = asyncio.get_event_loop()
    return hub.tools._loop


def call_soon(hub, fun, *args, **kwargs):
    '''
    Schedule a coroutine to be called when the loop has time. This needs
    to be called after the creation fo the loop
    '''
    hub._._.call_soon(functools.partial(fun, *args, **kwargs))


def create_task(hub, coro):
    '''
    Schedule a coroutine to be called when the loop has time. This needs
    to be called after the creation fo the loop
    '''
    asyncio.ensure_future(coro)


def entry(hub):
    '''
    The entry coroutine to start a run forever loop
    '''
    hub._._.create().run_forever()


def close(hub):
    hub._._.create().close()


def start(hub, coro):
    '''
    Start a loop that will run until complete
    '''
    return hub._._.create().run_until_complete(coro)


async def sleep(hub, time):
    await asyncio.sleep(time)


def wait(hub, coros, timeout=None):
    loop = hub._._.create()
    if not isinstance(coros, list):
        coros = [coros]
    return asyncio.wait(coros, loop=loop, timeout=timeout, return_when=asyncio.ALL_COMPLETED)


def create_future(hub):
    return asyncio.Future()
