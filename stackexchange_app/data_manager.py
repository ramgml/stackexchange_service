from stackexchange_app import db
from stackexchange_client import client
from stackexchange_app import settings


def calc_offset(page, pagesize):
    return page * pagesize - pagesize


async def get_topics(engine, page, pagesize, order):
    async with engine.acquire() as conn:
        offset = calc_offset(page, pagesize)
        topics_query = db.get_topics_page(
            limit=pagesize,
            offset=offset,
            order=order
        )
        cursor = await conn.execute(topics_query)
        topics = await cursor.fetchall()

        count_query = db.get_total_topics_count()
        cursor = await conn.execute(count_query)
        count = await cursor.scalar()
        return topics, count


async def get_topic(engine, topic: str):
    async with engine.acquire() as conn:
        query = db.select_topic_by_topic(topic)
        cursor = await conn.execute(query)
        return await cursor.fetchone()


async def save_topic(connect, topic: dict):
    query = db.insert_topic(topic)
    result = await connect.execute(query)
    return result


async def get_or_create_topic(engine, topic: str):
    async with engine.acquire() as conn:
        existing_topic = await get_topic(conn, topic)
        if existing_topic is None:
            topic_data = {
                'topic': topic,
                'question_count': 0
            }
            saved_topic = await save_topic(conn, topic_data)
            return saved_topic


async def get_topic_questions(engine, topic: str, page, pagesize, sort, order):
    async with engine.acquire() as conn:
        existing_topic = await get_topic(conn, topic)
        if existing_topic is None:
            search_response = await client.search(topic, page=page, pagesize=pagesize, sort=sort, order=order)
            return search_response.items


async def save_questions(connect, questions: list):
    result = await connect.execute(db.insert_questions(), questions)
    return result


async def save_topics_questions(connect, topics_questions: list):
    result = await connect.execute(db.insert_topics_questions(), topics_questions)
    return result


async def get_first_page(engine, topic):
    response = await client.search(
        topic,
        page=1,
        pagesize=settings.DEFAULT_PAGESIZE,
        sort=settings.DEFAULT_SORT,
        order=settings.ASC
    )
    topic_data = {
        'topic': topic,
        'questions_count': response.total
    }
    questions = []
    for item in response.items:
        questions.append({
            'stackexchange_id': item.question_id,
            'title': item.title,
            'link': item.link,
            'creation_date': item.creation_date
        })
    async with engine.acquire() as conn:
        saved_topic_cursor = await save_topic(conn, topic_data)
        saved_questions_cursor = await save_questions(conn, questions)
        topic_id = dict(saved_topic_cursor.fetchrow()).get('id')
        topics_questions = []
        for idx, item in enumerate(saved_questions_cursor.fetchall()):
            topics_questions.append({
                'topic_id': topic_id,
                'question_id': dict(item).get('id'),
                'topic_number': idx + 1
            })
        await save_topics_questions(conn, topics_questions)
    return topic_id
