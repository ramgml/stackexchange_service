import aiopg.sa
from sqlalchemy import desc, asc
from stackexchange_app import schema
from stackexchange_app.utils import DEFAULT_PG_URL


async def init_pg(app):
    engine = await aiopg.sa.create_engine(
        dsn=DEFAULT_PG_URL,
        minsize=1,
        maxsize=5,
        loop=app.loop
    )
    app['db'] = engine


async def close_pg(app):
    app['db'].close()
    await app['db'].wait_closed()


def get_topic(topic: str, page_start: int, page_end: int, order: str):
    join_stmt = schema.topic.join(
        schema.topics_questions,
        schema.topic.c.id == schema.topics_questions.c.topic_id,
        isouter=True
    ).join(
        schema.question,
        schema.question.c.question.id == schema.topic_questions.question_id,
        isouter=True
    )
    order_mode = desc if order == 'desc' else asc
    query = schema.topic.select().select_from(join_stmt).\
        where(schema.topic.c.topic == topic).\
        where(schema.topics_questions.topic_number.between(page_start, page_end)).\
        order_by(order_mode(schema.question.creation_date))
    return query


def insert_topic(topic_data: dict):
    query = schema.topic.insert().values(topic_data)
    return query


async def insert_questions(engine, questions_data: list):
    async with engine.acquire() as conn:
        await conn.execute(schema.question.insert(), questions_data)


async def insert_topics_questions(engine, topics_questions_data: list):
    async with engine.acquire() as conn:
        await conn.execute(schema.topics_questions.insert(), topics_questions_data)
