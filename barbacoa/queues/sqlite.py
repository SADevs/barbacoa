# -*- coding: utf-8 -*-
import json
import datetime

try:
    import sqlalchemy
    import sqlalchemy.schema
    import sqlalchemy.types
    import sqlalchemy.orm.exc
    import sqlalchemy_aio

    class JSONType(sqlalchemy.types.PickleType):
        '''
        JSON DB type is used to store JSON objects in the database
        '''

        impl = sqlalchemy.types.BLOB

        def __init__(self, *args, **kwargs):
            super(JSONType, self).__init__(*args, **kwargs)

        def process_bind_param(self, value, dialect):
            if value is not None:
                value = json.dumps(value, ensure_ascii=True)
            return value

        def process_result_value(self, value, dialect):
            if value is not None:
                value = json.loads(value)
            return value

except ImportError:
    sqlalchemy_aio = None


def __virtual__(hub):
    if sqlalchemy_aio is None:
        return False, 'Install python modules: sqlalchemy, sqlalchemy_aio'
    return True


async def create_engine(hub, queue):
    que = hub.tools.config.get_queue(queue)
    metadata = sqlalchemy.MetaData()
    if not hasattr(hub._._, '_engines'):
        hub._._._engines = {}
    if queue not in hub._._._engines:
        engine = sqlalchemy.create_engine(
            que, strategy=sqlalchemy_aio.ASYNCIO_STRATEGY,
        )
        hub._._._engines[queue] = engine
    if not hasattr(hub._._, '_tables'):
        hub._._._tables = {}
    if queue not in hub._._._tables:
        hub._._._tables[queue] = sqlalchemy.Table(
            'tasks', metadata,
            sqlalchemy.Column('id', sqlalchemy.types.Integer, primary_key=True, nullable=False),
            sqlalchemy.Column('uuid', sqlalchemy.types.String(36), nullable=False),
            sqlalchemy.Column('name', sqlalchemy.types.Text, nullable=False),
            sqlalchemy.Column('ack', sqlalchemy.types.Integer, default=None, nullable=True),
            sqlalchemy.Column('task', JSONType, nullable=False),
        )
        try:
            await engine.execute(sqlalchemy.schema.CreateTable(hub._._._tables[queue]))
        except sqlalchemy.exc.OperationalError:
            pass
    return hub._._._engines[queue]


async def add_task(hub, taskid, task, kwargs=None, queue=None):
    if queue is None:
        queue = hub.tools.config.get_task_queue(task)
    engine = await hub._._.create_engine(queue)
    conn = await engine.connect()
    table = hub._._._tables[queue]

    await conn.execute(table.insert().values(uuid=str(taskid), name=task, task=json.dumps(kwargs or {})))
    await conn.close()


async def pop_task(hub, queue=None, timeout=None):
    engine = await hub._._.create_engine(queue)
    conn = await engine.connect()
    table = hub._._._tables[queue]

    result = await conn.execute(table.select().where(
        sqlalchemy.or_(
            table.c.ack.is_(None),
            table.c.ack < datetime.datetime.utcnow().timestamp(),
        )
    ).order_by(table.c.id.asc()))
    ret = await result.first()
    if ret is None:
        await conn.close()
        return {}
    if timeout is None:
        timeout = hub.tools.config.get_task_timeout(ret.name)
    ackdate = datetime.datetime.utcnow() + datetime.timedelta(seconds=timeout)
    await conn.execute(table.update().where(table.c.uuid == ret.uuid).values(
        ack=ackdate.timestamp()
    ))
    await conn.close()
    return {
        'uuid': ret[1],
        'fun': ret[2],
        'kwargs': json.loads(ret[4]),
    }


async def ack_task(hub, taskid, queue=None):
    engine = await hub._._.create_engine(queue)
    conn = await engine.connect()
    table = hub._._._tables[queue]

    await conn.execute(sqlalchemy.delete(table).where(table.c.uuid == taskid))
    await conn.close()
