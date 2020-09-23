from sqlalchemy_utils import create_database, drop_database
from contextlib import contextmanager
import uuid
from yarl import URL
from alembic.config import Config
import os
from types import SimpleNamespace
import urllib.parse
import math
from stackexchange_app.settings import (
    PROJECT_PATH,
    ASC,
    DESC
)

from stackexchange_app import __name__ as project_name


def make_alembic_config(cmd_opts: SimpleNamespace,
                        base_path: str = PROJECT_PATH) -> Config:
    # Replace path to alembic.ini file to absolute
    if not os.path.isabs(cmd_opts.config):
        cmd_opts.config = os.path.join(base_path, cmd_opts.config)

    config = Config(file_=cmd_opts.config, ini_section=cmd_opts.name,
                    cmd_opts=cmd_opts)

    # Replace path to alembic folder to absolute
    alembic_location = config.get_main_option('script_location')
    if not os.path.isabs(alembic_location):
        config.set_main_option('script_location',
                               os.path.join(base_path, alembic_location))
    if cmd_opts.pg_url:
        config.set_main_option('sqlalchemy.url', cmd_opts.pg_url)

    return config


def alembic_config_from_url(pg_url) -> Config:
    """
    Provides Python object, representing alembic.ini file.
    """
    cmd_options = SimpleNamespace(
        config='stackexchange_app/alembic.ini', name='alembic', pg_url=pg_url,
        raiseerr=False, x=None,
    )

    return make_alembic_config(cmd_options)


@contextmanager
def tmp_database(db_url: URL, suffix: str = '', **kwargs):
    tmp_db_name = '.'.join([uuid.uuid4().hex, project_name, suffix])
    tmp_db_url = str(db_url.with_path(tmp_db_name))
    create_database(tmp_db_url, **kwargs)

    try:
        yield tmp_db_url
    finally:
        drop_database(tmp_db_url)


def build_order_link(pagesize, order):
    params = {
        'pagesize': pagesize,
        'order': ASC if order == DESC else DESC
    }

    return urllib.parse.urlencode(params)


def build_page_link(page, pagesize, order):
    params = {
        'page': page,
        'pagesize': pagesize,
        'order': order
    }

    return urllib.parse.urlencode(params)


def pagination(total_count, page, pagesize, order):
    pages_count = math.ceil(total_count / pagesize)
    for i in range(1, pages_count + 1):
        yield {
            'number': i,
            'current': i == page,
            'link': build_page_link(i, pagesize, order)
        }
