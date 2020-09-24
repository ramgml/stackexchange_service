from datetime import datetime
import aiopg.sa
from sqlalchemy import desc, asc, func, select, literal_column
from stackexchange_app import schema
from stackexchange_app.settings import DEFAULT_PG_URL


async def init_pg(app):
    engine = await aiopg.sa.create_engine(
        dsn=DEFAULT_PG_URL,
        minsize=1,
        maxsize=5
    )
    app['db'] = engine


async def close_pg(app):
    app['db'].close()
    await app['db'].wait_closed()


class Topic:
    def __init__(self, id_: int, topic: str, questions_count: int, created_at: datetime):
        self._id = id_
        self._topic = topic
        self._questions_count = questions_count
        self._created_at = created_at

    @property
    def id(self):
        return self._id

    @property
    def topic(self):
        return self._topic

    @property
    def questions_count(self):
        return self._questions_count

    @property
    def created_at(self):
        return self._created_at

    @staticmethod
    async def select_by_topic(engine, topic: str):
        async with engine.acquire() as conn:
            sql = schema.topic.select().where(schema.topic.c.topic == topic)
            cursor = await conn.execute(sql)
            result = await cursor.fetchone()
            if result is not None:
                return Topic(*result.as_tuple())
            return None

    @staticmethod
    async def select_by_id(engine, topic_id: int):
        async with engine.acquire() as conn:
            sql = schema.topic.select().where(schema.topic.c.id == topic_id)
            cursor = await conn.execute(sql)
            result = await cursor.fetchone()
            if result is not None:
                return Topic(*result.as_tuple())
            return None

    @staticmethod
    async def insert_topic(engine, topic: dict):
        async with engine.acquire() as conn:
            sql = schema.topic.insert().values(topic).\
                returning(literal_column('*'))
            cursor = await conn.execute(sql)
            result = await cursor.fetchone()
            return Topic(*result.as_tuple())

    @staticmethod
    async def count(engine):
        async with engine.acquire() as conn:
            sql = select([func.count(schema.topic.c.id)])
            cursor = await conn.execute(sql)
            return await cursor.scalar()

    @staticmethod
    async def get_topics_page(engine, limit=25, offset=0, sort='created_at', order='desc'):
        async with engine.acquire() as conn:
            direction = desc if order == 'desc' else asc
            sql = schema.topic.select().offset(
                offset).limit(limit).order_by(direction(sort))
            cursor = await conn.execute(sql)
            topics = await cursor.fetchall()
            return [Topic(*t.as_tuple()) for t in topics]

    @staticmethod
    async def get_topics(engine):
        async with engine.acquire() as conn:
            sql = schema.topic.select()
            cursor = await conn.execute(sql)
            topics = await cursor.fetchall()
            return [Topic(*t.as_tuple()) for t in topics]

    @staticmethod
    async def update_topic(engine, topic_id, questions_count):
        async with engine.acquire() as conn:
            sql = schema.topic.update().where(schema.topic.c.id == topic_id).\
                values({'questions_count': questions_count})
            await conn.execute(sql)


class Question:
    def __init__(self, stackexchange_id, title, link, creation_date):
        self._stackexchange_id = stackexchange_id
        self._title = title
        self._link = link
        self._creation_date = creation_date

    @property
    def stackexchange_id(self):
        return self._stackexchange_id

    @property
    def title(self):
        return self._title

    @property
    def link(self):
        return self._link

    @property
    def creation_date(self):
        return self._creation_date

    @staticmethod
    async def select_by_stackexchange_ids(engine, stackexchange_ids: list):
        async with engine.acquire() as conn:
            sql = schema.question.select().where(
                schema.question.c.stackexchange_id.in_(stackexchange_ids))
            cursor = await conn.execute(sql)
            questions = await cursor.fetchall()
            return [Question(*q.as_tuple()) for q in questions]

    @staticmethod
    async def insert_questions(engine, questions: list):
        async with engine.acquire() as conn:
            sql = schema.question.insert().values(questions).\
                returning(literal_column('*'))
            cursor = await conn.execute(sql)
            questions = await cursor.fetchall()
            return [Question(*q.as_tuple()) for q in questions]

    @staticmethod
    async def select_by_topic_id(engine, topic_id: int, number: int, size: int, order: str):
        async with engine.acquire() as conn:
            join_stmt = schema.topic.join(
                schema.questions_page,
                schema.questions_page.c.topic_id == schema.topic.c.id,
                isouter=False
            ).join(
                schema.question,
                schema.questions_page.c.question_id == schema.question.c.stackexchange_id,
                isouter=False
            )
            sql = select([schema.question]).select_from(join_stmt).\
                where(schema.topic.c.id == topic_id).\
                where(schema.questions_page.c.order == order).\
                where(schema.questions_page.c.number == number).\
                where(schema.questions_page.c.size == size)
            cursor = await conn.execute(sql)
            questions = await cursor.fetchall()
            return [Question(*q.as_tuple()) for q in questions]


class Page:
    @staticmethod
    async def insert_questions_page(engine, questions_page: list):
        async with engine.acquire() as conn:
            sql = schema.questions_page.insert().values(questions_page).\
                returning(literal_column('*'))
            cursor = await conn.execute(sql)
            return await cursor.fetchall()

    @staticmethod
    async def select_pages(engine):
        async with engine.acquire() as conn:
            sql = schema.questions_page.select().distinct(
                schema.questions_page.c.number,
                schema.questions_page.c.size,
                schema.questions_page.c.order,
                schema.questions_page.c.topic_id
            )
            cursor = await conn.execute(sql)
            return await cursor.fetchall()
