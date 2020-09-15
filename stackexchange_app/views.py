from aiohttp import web
import aiohttp_jinja2
from stackexchange_app import data_manager
from stackexchange_app.settings import ASC, PAGESIZES, DEFAULT_PAGESIZE
from stackexchange_app.utils import build_order_link, pagination


@aiohttp_jinja2.template('index.html')
async def index(request):
    page = int(request.rel_url.query.get('page', 1))
    pagesize = int(request.rel_url.query.get('pagesize', DEFAULT_PAGESIZE))
    order = request.rel_url.query.get('order', ASC)
    topics, count = await data_manager.get_topics(
        engine=request.app['db'],
        page=page,
        pagesize=pagesize,
        order=order
    )

    return {
        'topics': [dict(topic) for topic in topics],
        'order_link': build_order_link(page, pagesize, order),
        'order': order,
        'pagesize': pagesize,
        'count': count,
        'pagination': pagination(count, page, pagesize, order),
        'pagesizes': PAGESIZES
    }


@aiohttp_jinja2.template('search.html')
async def search_page(request):
    return {}


async def search_handler(request):
    data = await request.post()
    query = data.get('query')
    if not query:
        return web.HTTPFound('/search')

    topic = await data_manager.get_topic(
        engine=request.app['db'],
        topic=query
    )
    if topic:
        print(topic)
        topic_id = dict(topic).get('id')
    else:
        topic_id = await data_manager.get_first_page(
            engine=request.app['db'],
            topic=query
        )
    return web.HTTPFound(f'/topic/{topic_id}')


# @aiohttp_jinja2.template('topic.html')
async def topic(request):
    return web.Response(
        text="Hello, {}".format(request.match_info['topic_id']))
