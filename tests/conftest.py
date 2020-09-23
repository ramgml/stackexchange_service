import pytest
from yarl import URL
from alembic.command import upgrade
import aiopg.sa
from stackexchange_app.utils import tmp_database, alembic_config_from_url
from stackexchange_app.settings import DEFAULT_PG_URL


@pytest.fixture(scope='session')
def pg_url():
    """
    Provides base PostgreSQL URL for creating temporary databases.
    """
    return URL(DEFAULT_PG_URL)


@pytest.fixture(scope='session')
def migrated_postgres_template(pg_url):
    """
    Creates temporary database and applies migrations.
    Database can be used as template to fast creation databases for tests.

    Has "session" scope, so is called only once per tests run.
    """
    with tmp_database(pg_url, 'template') as tmp_url:
        alembic_config = alembic_config_from_url(tmp_url)
        upgrade(alembic_config, 'head')
        yield tmp_url


@pytest.fixture
def migrated_postgres(pg_url, migrated_postgres_template):
    """
    Quickly creates clean migrated database using temporary database as base.
    Use this fixture in tests that require migrated database.
    """
    template_db = URL(migrated_postgres_template).name
    with tmp_database(pg_url, 'pytest', template=template_db) as tmp_url:
        yield tmp_url


@pytest.fixture
async def postgres_engine(migrated_postgres):
    engine = await aiopg.sa.create_engine(dsn=str(migrated_postgres))
    try:
        yield engine
    finally:
        engine.close()
        await engine.wait_closed()


@pytest.fixture
async def api_client(migrated_postgres, aiohttp_client):
    """
    Creates aiohttp application and client for it.
    """
    app = create_app(migrated_postgres)
    client = await aiohttp_client(app)
    try:
        yield client
    finally:
        await client.close()
