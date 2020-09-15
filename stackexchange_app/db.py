import aiopg.sa
from sqlalchemy import desc, asc, func, select
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


def get_topics_page(limit=25, offset=0, sort='created_at', order='asc'):
    direction = desc if order == 'desc' else asc
    query = schema.topic.select().offset(
        offset).limit(limit).order_by(direction(sort))
    return query


def get_total_topics_count():
    query = select([func.count(schema.topic.c.id)])
    return query


def select_topic_by_topic(topic: str):
    query = schema.topic.select().where(schema.topic.c.topic == topic)
    return query


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
    direction = desc if order == 'desc' else asc
    query = schema.topic.select().select_from(join_stmt).\
        where(schema.topic.c.topic == topic).\
        where(schema.topics_questions.topic_number.between(page_start, page_end)).\
        order_by(direction(schema.question.creation_date))
    return query


def insert_topic(topic_data: dict):
    query = schema.topic.insert().values(topic_data)
    return query


async def insert_questions():
    query = schema.question.insert()
    return query


async def insert_topics_questions():
    return schema.topics_questions.insert()
