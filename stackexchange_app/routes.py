from .views import index, topic, search_page, search_handler 
from .settings import PROJECT_PATH


def setup_routes(app):
    app.router.add_get('/', index)
    app.router.add_get('/search', search_page)
    app.router.add_post('/search', search_handler)
    app.router.add_get('/topic/{topic_id}', topic)
    app.router.add_static('/static/',
                          path=PROJECT_PATH / 'stackexchange_app' / 'static',
                          name='static')
