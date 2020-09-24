import logging
from collections import namedtuple
from stackexchange_app.db import Topic, Question, Page
from stackexchange_client.client import StackExchange

log = logging.getLogger(__name__)


PageParams = namedtuple('PageParams', ['page', 'size', 'sort', 'order'])


class TopicsPage:
    __slots__ = ('_db_engine', '_page_params', '_total_count', '_items')

    def __init__(self, db_engine, page_params: PageParams):
        self._db_engine = db_engine
        self._page_params = page_params
        self._total_count = None
        self._items = []

    async def total_count(self):
        if self._total_count is None:
            self._total_count = await Topic.count(self._db_engine)
        return self._total_count

    async def items(self):
        if not self._items:
            offset = (self._page_params.page - 1) * self._page_params.size
            self._items = await Topic.get_topics_page(
                engine=self._db_engine,
                limit=self._page_params.size,
                offset=offset,
                order=self._page_params.order,
                sort=self._page_params.sort
            )
        return self._items


class QuestionsPage:
    __slots__ = ('_db_engine', '_topic', '_page_params', '_items')

    def __init__(self, db_engine, topic: Topic, page_params: PageParams):
        self._db_engine = db_engine
        self._topic = topic
        self._page_params = page_params
        self._items = []

    async def items(self):
        if not self._items:
            self._items = await Question.select_by_topic_id(
                engine=self._db_engine,
                topic_id=self._topic.id,
                number=self._page_params.page,
                size=self._page_params.size,
                order=self._page_params.order
            )

            if not self._items:
                topic, questions = await load_from_stackexchange(
                    query=self._topic.topic,
                    page_params=self._page_params
                )
                self._items = [Question(*q.values()) for q in questions]
                await save_questions(self._db_engine, questions)
                await save_questions_page(
                    engine=self._db_engine,
                    topic_id=self._topic.id,
                    questions=questions,
                    page_params=self._page_params
                )
        return self._items


async def save_topic(engine, topic_data: dict):
    return await Topic.insert_topic(engine, topic_data)


async def save_questions(engine, questions: list):
    stackexchange_ids = list(map(
        lambda q: q['stackexchange_id'], questions
    ))
    exist_questions = await Question.select_by_stackexchange_ids(engine, stackexchange_ids)
    exist_questions_ids = list(map(
        lambda q: q.stackexchange_id, exist_questions
    ))
    new_questions = list(filter(
        lambda q: q['stackexchange_id'] not in exist_questions_ids, questions
    ))
    if new_questions:
        return await Question.insert_questions(engine, new_questions)
    return []


async def save_questions_page(engine, topic_id: int, questions: list, page_params: PageParams):
    page = []
    for question in questions:
        page.append(
            {
                'number': page_params.page,
                'size': page_params.size,
                'order': page_params.order,
                'question_id': question['stackexchange_id'],
                'topic_id': topic_id
            }
        )
    if page:
        await Page.insert_questions_page(engine, page)


async def load_from_stackexchange(query: str, page_params: PageParams):
    response = await StackExchange.search(
        query,
        page=page_params.page,
        pagesize=page_params.size,
        sort=page_params.sort,
        order=page_params.order
    )
    topic = {
        'topic': query,
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
    return topic, questions


class DataManager:
    __slots__ = ('_db_engine')

    def __init__(self, db_engine):
        self._db_engine = db_engine

    async def load_new_topic(self, query, page_params: PageParams):
        topic, questions = await load_from_stackexchange(query, page_params)
        topic = await save_topic(self._db_engine, topic)
        await save_questions(self._db_engine, questions)
        await save_questions_page(
            engine=self._db_engine,
            topic_id=topic.id,
            questions=questions,
            page_params=page_params
        )
        return topic

    def get_topics_page(self, page_params: PageParams):
        return TopicsPage(self._db_engine, page_params)

    def get_questions_page(self, topic: Topic, page_params: PageParams):
        return QuestionsPage(self._db_engine, topic, page_params)
