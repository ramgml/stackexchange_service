import os
from pathlib import Path


POSTGRES_DB = os.getenv('POSTGRES_DB')
POSTGRES_USER = os.getenv('POSTGRES_USER')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')
POSTGRES_HOST = os.getenv('POSTGRES_HOST')
POSTGRES_PORT = os.getenv('POSTGRES_PORT')

PROJECT_PATH = Path(__file__).parent.parent.resolve()
DEFAULT_PG_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

DEFAULT_SORT = 'creation'
ASC = 'asc'
DESC = 'desc'

DEFAULT_PAGESIZE = 25
PAGESIZES = [25, 50, 100]

CACHE_EXPIRES = 60
CACHE_URL = os.getenv("CACHE_URL", default="redis://localhost:6379/0")
WS_SERVER_URL = os.getenv('WS_SERVER_URL', 'ws://localhost:4000')
CRON_TASK_DELAY = os.getenv('CRON_TASK_DELAY', '*/10')
