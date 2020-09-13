from aiohttp import web
import os
from .routes import setup_routes
from .db import init_pg, close_pg


app = web.Application()
setup_routes(app)
app.on_startup.append(init_pg)
app.on_cleanup.append(close_pg)


def main():
    web.run_app(app, host=os.getenv('HOST', '0.0.0.0'),
                port=os.getenv('PORT', '8080'))


if __name__ == '__main__':
    main()
