from .views import index, topic, search_page, search_handler 


def setup_routes(app):
    app.router.add_get('/', index)
    app.router.add_get('/search', search_page)
    app.router.add_post('/get_topic', search_handler)
    app.router.add_get('/topic/{topic_id}', topic)
