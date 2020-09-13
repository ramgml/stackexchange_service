from stackexchange_app import db
from stackexchange_client import client


async def get_page(app, page, pagesize, order):
    pass


async def get_topic(connect, topic: str):
    query = db.get_topic(topic)
    result = await connect.execute(query)
    return result


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
            if search_response.items:
                pass
