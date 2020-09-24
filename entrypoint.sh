#!/bin/bash

alembic -c stackexchange_app/alembic.ini upgrade head

python stackexchange_app/main.py &

python stackexchange_app/socket_server.py &

celery -A stackexchange_app.cron_task worker -B