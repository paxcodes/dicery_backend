#! /usr/bin/env bash
set -e

python /app/dicery_backend/tests_pre_start.py

bash ./scripts/test.sh "$@"