#!/bin/bash

alembic -c stackexchange_app/alembic.ini upgrade head

python stackexchange_app/main.py
