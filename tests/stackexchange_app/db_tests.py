import pytest
from stackexchange_app import db

TOPIC = {
    'topic': 'python',
    'questions_count': 2
}

TOPICS = [
    {
        'topic': 'java',
        'questions_count': 10
    },
    {
        'topic': 'js',
        'questions_count': 30
    }
]

QUESTIONS = [
    {
        'stackexchange_id': 123,
        'title': 'title1',
        'link': 'https://link1',
        'creation_date': '2020-09-01'
    },
    {
        'stackexchange_id': 321,
        'title': 'title2',
        'link': 'https://link2',
        'creation_date': '2020-09-02'
    }
]


@pytest.mark.asyncio
async def test_insert_topic(postgres_engine):
    topic = await db.Topic.insert_topic(postgres_engine, TOPIC)
    assert isinstance(topic, db.Topic)
    assert topic.id == 1
    assert topic.topic == 'python'
    assert topic.questions_count == 2


@pytest.mark.asyncio
async def test_select_topic_by_id(postgres_engine):
    topic = await db.Topic.insert_topic(postgres_engine, TOPIC)
    topic = await db.Topic.select_by_id(postgres_engine, 1)
    assert isinstance(topic, db.Topic)
    assert topic.id == 1
    assert topic.topic == 'python'
    assert topic.questions_count == 2


@pytest.mark.asyncio
async def test_select_topic_by_topic(postgres_engine):
    topic = await db.Topic.insert_topic(postgres_engine, TOPIC)
    topic = await db.Topic.select_by_topic(postgres_engine, TOPIC['topic'])
    assert isinstance(topic, db.Topic)
    assert topic.id == 1
    assert topic.topic == 'python'
    assert topic.questions_count == 2


@pytest.mark.asyncio
async def test_topic_count(postgres_engine):
    for topic in TOPICS:
        await db.Topic.insert_topic(postgres_engine, topic)
    count = await db.Topic.count(postgres_engine)
    assert count == 2


@pytest.mark.asyncio
async def test_get_topics_page(postgres_engine):
    topics = TOPICS[:]
    topics.append(TOPIC)
    for topic in topics:
        await db.Topic.insert_topic(postgres_engine, topic)
    page = await db.Topic.get_topics_page(postgres_engine, limit=2, offset=1, order='desc')
    assert len(page) == 2
    assert page[0].id == 2


@pytest.mark.asyncio
async def test_insert_questions(postgres_engine):
    questions = await db.Question.insert_questions(postgres_engine, QUESTIONS)
    assert len(questions) == 2
    assert isinstance(questions[0], db.Question)


@pytest.mark.asyncio
async def test_select_questions_by_stackexchange_ids(postgres_engine):
    await db.Question.insert_questions(postgres_engine, QUESTIONS)
    selected = await db.Question.select_by_stackexchange_ids(postgres_engine, [123, 321])
    assert len(selected) == 2


@pytest.mark.asyncio
async def test_insert_questions_page(postgres_engine):
    topic = await db.Topic.insert_topic(postgres_engine, TOPIC)
    questions = await db.Question.insert_questions(postgres_engine, QUESTIONS)
    page = []
    for q in questions:
        page.append(
            {
                'number': 1,
                'size': 25,
                'order': 'desc',
                'question_id': q.stackexchange_id,
                'topic_id': topic.id
            }
        )
    questions_page = await db.Page.insert_questions_page(postgres_engine, page)
    assert len(questions_page) == 2


@pytest.mark.asyncio
async def test_select_questions_by_topic_id(postgres_engine):
    topic = await db.Topic.insert_topic(postgres_engine, TOPIC)
    questions = await db.Question.insert_questions(postgres_engine, QUESTIONS)
    page = []
    for q in questions:
        page.append(
            {
                'number': 1,
                'size': 25,
                'order': 'desc',
                'question_id': q.stackexchange_id,
                'topic_id': topic.id
            }
        )
    await db.Page.insert_questions_page(postgres_engine, page)
    selected_questions = await db.Question.select_by_topic_id(postgres_engine, topic.id, 1, 25, 'desc')
    assert len(selected_questions) == 2


@pytest.mark.asyncio
async def test_select_pages(postgres_engine):
    topic = await db.Topic.insert_topic(postgres_engine, TOPIC)
    questions = await db.Question.insert_questions(postgres_engine, QUESTIONS)
    page = []
    for q in questions:
        page.append(
            {
                'number': 1,
                'size': 25,
                'order': 'desc',
                'question_id': q.stackexchange_id,
                'topic_id': topic.id
            }
        )
    await db.Page.insert_questions_page(postgres_engine, page)
    pages = await db.Page.select_pages(postgres_engine)
    assert len(pages) == 1


@pytest.mark.asyncio
async def test_update_topic(postgres_engine):
    topic = await db.Topic.insert_topic(postgres_engine, TOPIC)
    await db.Topic.update_topic(postgres_engine, topic.id, 10000)
    topic = await db.Topic.select_by_id(postgres_engine, topic.id)
    assert topic.questions_count == 10000
