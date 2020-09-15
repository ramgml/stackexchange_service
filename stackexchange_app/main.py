from aiohttp import web
import os
from stackexchange_app.routes import setup_routes
from stackexchange_app.db import init_pg, close_pg
import aiohttp_jinja2
import jinja2
from stackexchange_app.settings import PROJECT_PATH


app = web.Application()
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
    web.run_app(app, host=os.getenv('HOST', '0.0.0.0'),
                port=os.getenv('PORT', '8080'))


if __name__ == '__main__':
    main()
