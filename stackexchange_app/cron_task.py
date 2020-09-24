from celery import Celery
import asyncio
import json
from stackexchange_app.settings import CACHE_URL, DEFAULT_SORT, CRON_TASK_DELAY
from stackexchange_app.socket_server import producer
import logging
from celery.schedules import crontab
from stackexchange_app import db, data_manager as dm

log = logging.getLogger(__name__)

app = Celery('background_app', broker=CACHE_URL)


class DbManager:
    def __init__(self):
        self._app = {}

    async def __aenter__(self):
        await db.init_pg(self._app)
        return self._app['db']

    async def __aexit__(self, exc_type, exc, tb):
        await db.close_pg(self._app)


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(
        crontab(minute=CRON_TASK_DELAY),
        background_handler.s()
    )


async def db_change_watcher():
    log.info('Start task')
    producer({'ping': 'pong'})
    async with DbManager() as engine:
        pages = await db.Page.select_pages(engine)
        for page in pages:
            topic = await db.Topic.select_by_id(engine, page['topic_id'])
            page_params = dm.PageParams(
                page=page['number'],
                size=page['size'],
                sort=DEFAULT_SORT,
                order=page['order']
            )
            loaded_topic, questions = await dm.load_from_stackexchange(
                query=topic.topic,
                page_params=page_params
            )
            if topic.questions_count != loaded_topic['questions_count']:
                await db.Topic.update_topic(
                    engine,
                    topic.id,
                    loaded_topic['questions_count']
                )
                message = {
                    'topic': topic.topic
                }
                await producer(json.dumps(message))

            new_questions = await dm.save_questions(engine, questions)
            log.info(
                f'Worker added questions to "{topic.topic}": {new_questions}')
            await dm.save_questions_page(
                engine=engine,
                topic_id=topic.id,
                questions=questions,
                page_params=page_params
            )


@app.task
def background_handler():
    coro = db_change_watcher()
    asyncio.run(coro)
