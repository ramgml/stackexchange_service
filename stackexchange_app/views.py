import logging
from aiohttp import web
import aiohttp_jinja2
from stackexchange_app import data_manager, db
from stackexchange_app.settings import ASC, DESC, PAGESIZES, DEFAULT_PAGESIZE, DEFAULT_SORT
from stackexchange_app.utils import build_order_link, pagination

log = logging.getLogger(__name__)


@aiohttp_jinja2.template('index.html')
async def index(request):
    page = int(request.rel_url.query.get('page', 1))
    pagesize = int(request.rel_url.query.get('pagesize', DEFAULT_PAGESIZE))
    order = request.rel_url.query.get('order', DESC)
    sort = 'created_at'

    page_params = data_manager.PageParams(
        page=page,
        size=pagesize,
        sort=sort,
        order=order
    )

    dm = data_manager.DataManager(request.app['db'])
    topics_page = dm.get_topics_page(page_params)
    topics = await topics_page.items()
    total_count = await topics_page.total_count()

    return {
        'topics': topics,
        'order_link': build_order_link(pagesize, order),
        'order': order,
        'pagesize': pagesize,
        'count': total_count,
        'pagination': pagination(total_count, page, pagesize, order),
        'pagesizes': PAGESIZES
    }


@aiohttp_jinja2.template('search.html')
async def search_page(request):
    return {}


async def search_handler(request):
    data = await request.post()
    query = str(data.get('query')).strip().lower()
    if not query:
        return web.HTTPFound('/search')

    topic = await db.Topic.select_by_topic(
        engine=request.app['db'],
        topic=query
    )

    if topic is None:
        dm = data_manager.DataManager(db_engine=request.app['db'])
        page_params = data_manager.PageParams(
            page=1,
            size=DEFAULT_PAGESIZE,
            sort=DEFAULT_SORT,
            order=DESC
        )
        topic = await dm.load_new_topic(
            query=query,
            page_params=page_params
        )
    return web.HTTPFound(f'/topic/{topic.id}')


@aiohttp_jinja2.template('questions.html')
async def topic(request):
    topic_id = request.match_info['topic_id']
    page = int(request.rel_url.query.get('page', 1))
    pagesize = int(request.rel_url.query.get('pagesize', DEFAULT_PAGESIZE))
    order = request.rel_url.query.get('order', DESC)
    sort = DEFAULT_SORT

    topic = await db.Topic.select_by_id(
        engine=request.app['db'],
        topic_id=topic_id
    )

    if topic is None:
        raise web.HTTPNotFound()

    page_params = data_manager.PageParams(
        page=page,
        size=pagesize,
        sort=sort,
        order=order
    )

    dm = data_manager.DataManager(request.app['db'])
    questions_page = dm.get_questions_page(topic, page_params)
    questions = await questions_page.items()
    total_count = topic.questions_count

    return {
        'questions': questions,
        'order_link': build_order_link(pagesize, order),
        'pagesizes': PAGESIZES,
        'page': page,
        'pagesize': pagesize,
        'count': total_count,
        'topic': topic.topic,
        'order': order,
        'pagination': pagination(total_count, page, pagesize, order)
    }
