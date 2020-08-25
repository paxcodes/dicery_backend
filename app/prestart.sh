#! /usr/bin/env sh
set -e

LOG_LEVEL=trace

# Let the DB start
python /app/dicery_backend/backend_pre_start.py

# Run migrations
alembic upgrade head
