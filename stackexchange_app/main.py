import logging
from aiohttp import web
from aiohttp_cache import (
    setup_cache,
    RedisConfig
)
import os
import yarl
from stackexchange_app.routes import setup_routes
from stackexchange_app.db import init_pg, close_pg
import aiohttp_jinja2
import jinja2
from stackexchange_app.settings import PROJECT_PATH, CACHE_URL


app = web.Application()
redis_url = yarl.URL(CACHE_URL)
setup_cache(
    app,
    cache_type="redis",
    backend_config=RedisConfig(
        db=int(redis_url.path[1:]), host=redis_url.host, port=redis_url.port
    ),
)
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)
aiohttp_jinja2.setup(
    app,
    loader=jinja2.FileSystemLoader(
        str(PROJECT_PATH / 'stackexchange_app' / 'templates')
    )
)
setup_routes(app)
app.on_startup.append(init_pg)
app.on_cleanup.append(close_pg)


def main():
    try:
        web.run_app(app, host=os.getenv('HOST', '0.0.0.0'),
                    port=os.getenv('PORT', '8080'))
    except Exception as e:
        log.exception(e)
        raise e


if __name__ == '__main__':
    main()
