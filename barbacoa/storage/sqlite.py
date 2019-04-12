# -*- coding: utf-8 -*-
import json

try:
    import sqlalchemy
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
    storage = hub.tools.config.get_storage(queue)
    metadata = sqlalchemy.MetaData()
    if not hasattr(hub._._, '_engines'):
        hub._._._engines = {}
    if queue not in hub._._._engines:
        engine = sqlalchemy.create_engine(
            storage, strategy=sqlalchemy_aio.ASYNCIO_STRATEGY,
        )
        hub._._._engines[queue] = engine
    if not hasattr(hub._._, '_tables'):
        hub._._._tables = {}
    if queue not in hub._._._tables:
        hub._._._tables[queue] = sqlalchemy.Table(
            'jobs', metadata,
            sqlalchemy.Column('id', sqlalchemy.types.Integer, primary_key=True, nullable=False),
            sqlalchemy.Column('uuid', sqlalchemy.types.String(length=36)),
            sqlalchemy.Column('task', sqlalchemy.types.Text),
            sqlalchemy.Column('kwargs', JSONType, nullable=False),
            sqlalchemy.Column('result', JSONType, nullable=True),
        )
        try:
            await engine.execute(sqlalchemy.schema.CreateTable(hub._._._tables[queue]))
        except sqlalchemy.exc.OperationalError:
            pass
    return hub._._._engines[queue]


async def add_task(hub, taskid, task, kwargs=None, queue=None):
    engine = await hub._._.create_engine(queue)
    conn = await engine.connect()
    table = hub._._._tables[queue]

    await conn.execute(table.insert().values(uuid=taskid, task=task, kwargs=json.dumps(kwargs or {})))
    await conn.close()


async def set_result(hub, taskid, result, queue=None):
    engine = await hub._._.create_engine(queue)
    conn = await engine.connect()
    table = hub._._._tables[queue]
    await conn.execute(table.update().where(table.c.uuid == taskid).values(result=json.dumps(result)))
    await conn.close()


async def get_result(hub, taskid, queue=None):
    engine = await hub._._.create_engine(queue)
    conn = await engine.connect()
    table = hub._._._tables[queue]

    result = await conn.execute(table.select().where(table.c.uuid == taskid))
    data = await result.first()
    if not data:
        return {}
    return json.loads(data[-1])
